"""
Flask app.py with BILINGUAL SUPPORT for English & Urdu
Updated routes to pass language parameter to Gemini
Add this section to your existing app.py (replace the analysis routes)
"""

# ============================================================================
# BILINGUAL ANALYSIS ROUTES - Updated
# ============================================================================

@app.route("/api/analyze/quality", methods=["POST"])
@login_required
def analyze_code_quality():
    """Comprehensive code quality analysis with language support"""
    try:
        f = request.files.get("file")
        output_language = request.form.get("language", "en")  # 'en' or 'ur'
        
        if not f:
            return jsonify({"error": "No file uploaded"}), 400

        filename = f.filename
        ext = os.path.splitext(filename)[1].lower()
        
        if ext not in LANG_MAP:
            return jsonify({"error": f"Unsupported file type '{ext}'."}), 400
        
        language = detect_language(filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        f.save(save_path)

        with open(save_path, "r", encoding="utf-8", errors="ignore") as fh:
            code = fh.read()

        from utils.enhanced_ai_helpers import analyze_code_quality_comprehensive
        
        # Pass output_language parameter
        results = analyze_code_quality_comprehensive(
            code, language, gemini_client, output_language
        )
        
        submission_data = {
            "user_id": session['user_id'],
            "username": session['username'],
            "filename": filename,
            "language": language,
            "analysis_type": "quality",
            "output_language": output_language,
            "timestamp": datetime.now(UTC).isoformat(),
            "results": results
        }
        
        submission_id = create_submission(submission_data)
        results["submission_id"] = submission_id
        
        return jsonify({
            "success": True,
            "results": results,
            "filename": filename,
            "language": language,
            "output_language": output_language
        })
        
    except Exception as e:
        print(f"Quality analysis error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/analyze/bugs", methods=["POST"])
@login_required
def detect_bugs_and_tests():
    """Bug detection and test generation with language support"""
    try:
        f = request.files.get("file")
        output_language = request.form.get("language", "en")  # 'en' or 'ur'
        
        if not f:
            return jsonify({"error": "No file uploaded"}), 400

        filename = f.filename
        ext = os.path.splitext(filename)[1].lower()
        
        if ext not in LANG_MAP:
            return jsonify({"error": f"Unsupported file type '{ext}'"}), 400
        
        language = detect_language(filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        f.save(save_path)

        with open(save_path, "r", encoding="utf-8", errors="ignore") as fh:
            code = fh.read()

        from utils.enhanced_ai_helpers import detect_bugs_and_generate_tests
        
        # Pass output_language parameter
        results = detect_bugs_and_generate_tests(
            code, language, gemini_client, output_language
        )
        
        test_filename = f"test_{filename}"
        test_path = os.path.join(UPLOAD_FOLDER, test_filename)
        with open(test_path, "w", encoding="utf-8") as tf:
            tf.write(results.get('test_code', ''))
        
        results["test_file"] = test_filename
        
        submission_data = {
            "user_id": session['user_id'],
            "username": session['username'],
            "filename": filename,
            "language": language,
            "analysis_type": "bugs_and_tests",
            "output_language": output_language,
            "timestamp": datetime.now(UTC).isoformat(),
            "results": results
        }
        
        submission_id = create_submission(submission_data)
        results["submission_id"] = submission_id
        
        return jsonify({
            "success": True,
            "results": results,
            "filename": filename,
            "language": language,
            "output_language": output_language
        })
        
    except Exception as e:
        print(f"Bug detection error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/analyze/documentation", methods=["POST"])
@login_required
def generate_documentation_route():
    """Generate comprehensive documentation with language support"""
    try:
        f = request.files.get("file")
        output_language = request.form.get("language", "en")  # 'en' or 'ur'
        include_urdu = output_language == "ur" or request.form.get("include_urdu", "false").lower() == "true"
        
        if not f:
            return jsonify({"error": "No file uploaded"}), 400

        filename = f.filename
        ext = os.path.splitext(filename)[1].lower()
        
        if ext not in LANG_MAP:
            return jsonify({"error": f"Unsupported file type '{ext}'"}), 400
        
        language = detect_language(filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        f.save(save_path)

        with open(save_path, "r", encoding="utf-8", errors="ignore") as fh:
            code = fh.read()

        from utils.enhanced_ai_helpers import generate_comprehensive_documentation
        
        # Pass output_language parameter
        results = generate_comprehensive_documentation(
            code, language, gemini_client, 
            include_urdu=include_urdu,
            primary_language=output_language
        )
        
        # Save English documentation
        if results.get('documentation_english'):
            docs_filename_en = f"{os.path.splitext(filename)[0]}_docs_en.md"
            docs_path_en = os.path.join(UPLOAD_FOLDER, docs_filename_en)
            with open(docs_path_en, "w", encoding="utf-8") as df:
                df.write(results['documentation_english'])
            results["docs_file_english"] = docs_filename_en
        
        # Save Urdu documentation
        if results.get('documentation_urdu'):
            docs_filename_ur = f"{os.path.splitext(filename)[0]}_docs_ur.md"
            docs_path_ur = os.path.join(UPLOAD_FOLDER, docs_filename_ur)
            with open(docs_path_ur, "w", encoding="utf-8") as df:
                df.write(results['documentation_urdu'])
            results["docs_file_urdu"] = docs_filename_ur
        
        submission_data = {
            "user_id": session['user_id'],
            "username": session['username'],
            "filename": filename,
            "language": language,
            "analysis_type": "documentation",
            "output_language": output_language,
            "timestamp": datetime.now(UTC).isoformat(),
            "results": results
        }
        
        submission_id = create_submission(submission_data)
        results["submission_id"] = submission_id
        
        return jsonify({
            "success": True,
            "results": results,
            "filename": filename,
            "language": language,
            "output_language": output_language
        })
        
    except Exception as e:
        print(f"Documentation generation error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/analyze/readme", methods=["POST"])
@login_required
def generate_readme_route():
    """Generate README.md with language support"""
    try:
        f = request.files.get("file")
        project_name = request.form.get("project_name", None)
        output_language = request.form.get("language", "en")  # 'en' or 'ur'
        
        if not f:
            return jsonify({"error": "No file uploaded"}), 400

        filename = f.filename
        ext = os.path.splitext(filename)[1].lower()
        
        if ext not in LANG_MAP:
            return jsonify({"error": f"Unsupported file type '{ext}'"}), 400
        
        language = detect_language(filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        f.save(save_path)

        with open(save_path, "r", encoding="utf-8", errors="ignore") as fh:
            code = fh.read()

        from utils.enhanced_ai_helpers import generate_readme
        
        # Pass output_language parameter
        results = generate_readme(
            code, language, filename, gemini_client, 
            project_name, output_language
        )
        
        readme_suffix = "_ur" if output_language == "ur" else ""
        readme_filename = f"README{readme_suffix}.md"
        readme_path = os.path.join(UPLOAD_FOLDER, readme_filename)
        with open(readme_path, "w", encoding="utf-8") as rf:
            rf.write(results['readme_content'])
        
        results["readme_file"] = readme_filename
        
        submission_data = {
            "user_id": session['user_id'],
            "username": session['username'],
            "filename": filename,
            "language": language,
            "analysis_type": "readme",
            "output_language": output_language,
            "timestamp": datetime.now(UTC).isoformat(),
            "results": results
        }
        
        submission_id = create_submission(submission_data)
        results["submission_id"] = submission_id
        
        return jsonify({
            "success": True,
            "results": results,
            "filename": filename,
            "language": language,
            "output_language": output_language
        })
        
    except Exception as e:
        print(f"README generation error: {e}")
        return jsonify({"error": str(e)}), 500