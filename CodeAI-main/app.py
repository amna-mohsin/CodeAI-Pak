import os
import re
import json
import tempfile
import shutil
from datetime import datetime, UTC
from functools import wraps
from flask import Flask, request, render_template, jsonify, send_file, redirect, url_for, session
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.security import generate_password_hash, check_password_hash
from transformers import pipeline
import google.generativeai as genai
from dotenv import load_dotenv
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors

# Import database and utility modules
from database.db_connector import get_db, init_db
from database.queries import (
    create_user, authenticate_user, get_user_by_username,
    create_submission, get_submissions, get_submission_stats,
    get_bug_statistics, get_recent_submissions
)
from utils.ai_helpers import analyze_code_with_ai, generate_bug_report, generate_documentation
from utils.report_generator import generate_pdf_report
from utils.translator import translate_to_urdu

# --------------------
# Flask setup
# --------------------
load_dotenv(dotenv_path=os.path.join(os.getcwd(), 'apikey.env'))
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB

# --------------------
# Initialize Database
# --------------------
init_db()

# --------------------
# Model pipeline
# --------------------
MODEL_NAME = "Salesforce/codet5-base"
gen_pipeline = pipeline("text2text-generation", model=MODEL_NAME, device=-1)

# Gemini setup
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "models/gemini-1.5-pro")
GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    try:
        gemini_model = genai.GenerativeModel(
            GEMINI_MODEL,
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.2,
            },
        )
    except Exception as e:
        print(f"Gemini initialization failed: {e}")
        gemini_model = None
else:
    gemini_model = None

# --------------------
# Language map
# --------------------
LANG_MAP = {
    ".py": "Python",
    ".java": "Java",
}
ALLOWED_EXT = ",".join(LANG_MAP.keys())

# --------------------
# Authentication Decorators
# --------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Check if this is an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
                return jsonify({"error": "Authentication required", "redirect": "/login"}), 401
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Check if this is an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
                return jsonify({"error": "Authentication required", "redirect": "/login"}), 401
            return redirect(url_for('login_page'))
        if session.get('role') != 'admin':
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
                return jsonify({"error": "Admin access required"}), 403
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function


# --------------------
# Helper functions
# --------------------
def detect_language(filename):
    _, ext = os.path.splitext(filename.lower())
    return LANG_MAP.get(ext, "Unknown")

def count_lines(code: str):
    return len([l for l in code.splitlines() if l.strip() != ""])

def estimate_complexity(code: str):
    tokens = len(re.findall(r'\b(if|elif|else|for|while|switch|case|try|except|catch)\b', code))
    return min(100, tokens * 5)

# --------------------
# Routes - Authentication
# --------------------

@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")


@app.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    user = authenticate_user(username, password)

    if user:
        session.permanent = True  # Add this line
        session["user_id"] = str(user["_id"])
        session["username"] = user["username"]
        session["role"] = user["role"]
        return jsonify({
            "success": True,
            "role": user["role"],
            "redirect": "/admin" if user["role"] == "admin" else "/"
        })
    else:
        return jsonify({"error": "Invalid credentials"}), 401


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})


@app.route("/api/register", methods=["POST"])
def register():
    """Register new user - can be restricted to admin-only in production"""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "user")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    if get_user_by_username(username):
        return jsonify({"error": "Username already exists"}), 409

    user_id = create_user(username, password, role)

    if user_id:
        return jsonify({"success": True, "user_id": user_id})
    else:
        return jsonify({"error": "Registration failed"}), 500
    



app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=3600  # 1 hour
)
# --------------------
# Routes - Main Pages
# --------------------
@app.route("/")
@login_required
def index():
    return render_template("index.html", allowed=ALLOWED_EXT)

@app.route("/admin")
@admin_required
def admin_dashboard():
    return render_template("admin.html")

# --------------------
# Routes - Analysis
# --------------------
@app.route("/analyze", methods=["POST"])
@login_required
def analyze():
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "No file uploaded"}), 400

    filename = f.filename
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in LANG_MAP:
        return jsonify({
            "error": f"Unsupported file type '{ext}'. Allowed: {ALLOWED_EXT}"
        }), 400
    
    language = detect_language(filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    f.save(save_path)

    with open(save_path, "r", encoding="utf-8", errors="ignore") as fh:
        code = fh.read()

    # AI Analysis using helper functions
    try:
        ai_results = analyze_code_with_ai(code, language, gen_pipeline, gemini_model)
        
        # Generate bug report with English and Urdu
        bugs = generate_bug_report(code, language, ai_results)
        
        # Generate documentation with English and Urdu
        documentation = generate_documentation(code, language, ai_results, gemini_model)
        
        # Calculate scores
        scores = {
            "lines": count_lines(code),
            "complexity": estimate_complexity(code),
            "overall": ai_results.get("overall_score", 0),
            "review_score": ai_results.get("review_score", 0),
            "test_score": ai_results.get("test_score", 0),
            "doc_score": ai_results.get("doc_score", 0),
            "ux_score": ai_results.get("ux_score", 0),
            "estimated_coverage": ai_results.get("coverage", 0),
            "quality_level": ai_results.get("quality_level", "Medium"),
            "time_complexity": ai_results.get("time_complexity", {}),
            "bug_analysis": ai_results.get("bug_analysis", {}),
        }
        
        # Add Gemini-specific scores if available
        if ai_results.get("gemini_quality_score"):
            scores["gemini_quality_score"] = ai_results["gemini_quality_score"]
            scores["maintainability_score"] = ai_results.get("maintainability_score", 0)
            scores["readability_score"] = ai_results.get("readability_score", 0)
            scores["best_practices_score"] = ai_results.get("best_practices_score", 0)

        timestamp = datetime.now(UTC).isoformat()
        
        # Store in MongoDB
        submission_data = {
            "user_id": session['user_id'],
            "username": session['username'],
            "filename": filename,
            "language": language,
            "code_snippet": code[:500],  # Store first 500 chars
            "timestamp": timestamp,
            "scores": scores,
            "bugs": bugs,
            "documentation": documentation,
            "corrected_code": ai_results.get("corrected_code"),
        }
        
        submission_id = create_submission(submission_data)
        
        # Prepare report
        report = {
            "filename": filename,
            "language": language,
            "timestamp": timestamp,
            "scores": scores,
            "review": ai_results.get("review", ""),
            "tests": ai_results.get("tests", ""),
            "docs": documentation.get("english", ""),
            "docs_urdu": documentation.get("urdu", ""),
            "bug_report": "\n".join([b["description_en"] for b in bugs]),
            "bug_report_urdu": "\n".join([b["description_ur"] for b in bugs]),
            "corrected_code": ai_results.get("corrected_code"),
            "submission_id": submission_id
        }

        # Generate JSON report
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json", 
                                         prefix="report_", dir=UPLOAD_FOLDER)
        tmp.write(json.dumps(report, indent=2).encode("utf-8"))
        tmp.close()

        # Generate PDF report
        pdf_filename = os.path.basename(tmp.name).replace('.json', '.pdf')
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
        try:
            generate_pdf_report(report, pdf_path)
            report["pdf_file"] = pdf_filename
        except Exception as e:
            print(f"PDF generation failed: {e}")
            report["pdf_file"] = None

        return jsonify({
            "report": report, 
            "report_file": os.path.basename(tmp.name),
            "pdf_file": report.get("pdf_file")
        })
        
    except Exception as e:
        print(f"Analysis error: {e}")
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

# --------------------
# Routes - Admin API
# --------------------
@app.route("/api/admin/stats", methods=["GET"])
@admin_required
def get_admin_stats():
    """Get dashboard statistics for admin"""
    try:
        # Query parameters for filtering
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        language = request.args.get('language')
        severity = request.args.get('severity')
        user_filter = request.args.get('user')
        
        filters = {
            'start_date': start_date,
            'end_date': end_date,
            'language': language,
            'severity': severity,
            'user': user_filter
        }
        
        # Get submission statistics
        submission_stats = get_submission_stats(filters)
        
        # Get bug statistics
        bug_stats = get_bug_statistics(filters)
        
        # Get recent submissions
        recent = get_recent_submissions(limit=10, filters=filters)
        
        return jsonify({
            "submission_stats": submission_stats,
            "bug_stats": bug_stats,
            "recent_submissions": recent
        })
        
    except Exception as e:
        print(f"Stats error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/export", methods=["GET"])
@admin_required
def export_admin_data():
    """Export admin data as JSON"""
    try:
        format_type = request.args.get('format', 'json')
        
        # Get all data
        filters = {}
        stats = get_submission_stats(filters)
        bugs = get_bug_statistics(filters)
        recent = get_recent_submissions(limit=100, filters=filters)
        
        export_data = {
            "exported_at": datetime.now(UTC).isoformat(),
            "stats": stats,
            "bugs": bugs,
            "submissions": recent
        }
        
        if format_type == 'json':
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json", 
                                             prefix="export_", dir=UPLOAD_FOLDER)
            tmp.write(json.dumps(export_data, indent=2).encode("utf-8"))
            tmp.close()
            return send_file(tmp.name, as_attachment=True, 
                           download_name=f"codeai_export_{datetime.now().strftime('%Y%m%d')}.json")
        
        return jsonify({"error": "Unsupported format"}), 400
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --------------------
# Routes - Translation
# --------------------
@app.route("/translate_to_urdu", methods=["POST"])
@login_required
def translate_endpoint():
    """Translate text to Urdu using Gemini API"""
    try:
        data = request.get_json()
        text = data.get("text", "")
        
        if not text or not text.strip():
            return jsonify({"error": "No text provided"}), 400
        
        translated = translate_to_urdu(text, gemini_model)
        
        if translated:
            return jsonify({"translated_text": translated})
        else:
            return jsonify({"error": "Translation failed"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --------------------
# Routes - Downloads
# --------------------
@app.route("/download/<report_name>")
@login_required
def download_report(report_name):
    filepath = os.path.join(UPLOAD_FOLDER, report_name)
    if not os.path.exists(filepath):
        return "Report not found", 404
    return send_file(filepath, as_attachment=True)

@app.route("/download_pdf/<pdf_name>")
@login_required
def download_pdf(pdf_name):
    filepath = os.path.join(UPLOAD_FOLDER, pdf_name)
    if not os.path.exists(filepath):
        return "PDF report not found", 404
    return send_file(filepath, as_attachment=True, mimetype='application/pdf')

# --------------------
# Error Handlers
# --------------------
@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({
        "error": "File too large",
        "message": "Max upload size is 10 MB"
    }), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

# --------------------
# Run
# --------------------
if __name__ == "__main__":
    # Create default admin user if not exists
    if not get_user_by_username("admin"):
        create_user("admin", "admin123", "admin")
        print("Default admin created: username='admin', password='admin123'")
    
    app.run(debug=False, host="0.0.0.0", port=5001)