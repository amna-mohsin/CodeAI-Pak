# 🎯 Uraan — CodeAI Pakistan

<div align="center">

**An AI-Powered Code Analysis, Reporting & Visualization Platform**

*Analyze, debug, document, and learn from your code with AI intelligence*

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [API](#-api-endpoints) • [Contributing](#-contributing)

</div>

---

## 📖 About

**Uraan** (CodeAI Suite) is a comprehensive platform that leverages AI to analyze, review, and improve code quality. It combines intelligent code analysis (Codet5 + optional Gemini) with an intuitive web interface to help developers detect bugs, generate tests, create documentation (English & Urdu), and export professional reports.

### Why Uraan?

- 🤖 **AI-Powered**: Intelligent code analysis using Hugging Face CodeT5 and Google Gemini
- 🐛 **Bug Detection**: Automatic bug identification and suggested fixes
- 🧪 **Test Generation**: Automatic unit test generation for your code
- 📚 **Documentation**: Generate README, API docs, and comments (English & Urdu)
- 📊 **Professional Reports**: Export code analysis as PDF or JSON
- 🌍 **Bilingual Support**: Full English and Urdu output support
- 👤 **User Management**: Authentication, profiles, and admin dashboard
- ⚡ **REST API**: Headless API for automation and integration

---

## ✨ Features

### 🔍 Code Analysis
- **Quality Analysis** - Comprehensive code quality scoring and metrics
- **Bug Detection** - Identifies potential bugs and security issues
- **Complexity Analysis** - Time/space complexity estimation
- **Style Review** - Code style and best practices feedback

### 🛠️ Code Generation
- **Test Generation** - Auto-generate unit tests for functions
- **Documentation** - Create detailed API docs and comments
- **README Generator** - Auto-generate project README files
- **Code Fixes** - Suggest and generate corrected versions

### 📈 Reporting & Export
- **PDF Reports** - Professional PDF export with formatting
- **JSON Export** - Structured data export for integration
- **Admin Dashboard** - View statistics and submission history
- **Bilingual Output** - All reports available in English & Urdu

### 👥 User & Admin Features
- **User Authentication** - Secure login and registration
- **Admin Dashboard** - View analytics, stats, and trends
- **Submission History** - Track all code analyses
- **Performance Metrics** - Understand code quality trends

---

## 🛠️ Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Backend** | Python | 3.8+ |
| **Framework** | Flask | Latest |
| **Database** | MongoDB | 4.0+ |
| **Frontend** | React | 19.2+ |
| **Build Tool** | Vite | 7.2+ |
| **AI - Local** | Hugging Face CodeT5 | Latest |
| **AI - Cloud** | Google Gemini | 1.5-pro (optional) |

### Key Libraries & Frameworks

- **Backend**: Flask, Flask-Login, PyMongo, Transformers, ReportLab
- **Frontend**: React, React Router, Vite
- **AI/ML**: Hugging Face Transformers, Google GenAI
- **Database**: MongoDB with indexed collections

---

## 🚀 Installation

### Prerequisites

#### For Linux/macOS
- **Python**: 3.8 or higher
- **Node.js**: 18 or higher (for frontend)
- **pip** & **npm**: Package managers
- **MongoDB**: Running locally or accessible remotely
- **Git**: For cloning the repository

#### For Windows
- **Python**: 3.8+ (download from [python.org](https://www.python.org/))
- **Node.js**: 18+ (download from [nodejs.org](https://nodejs.org/))
- **MongoDB**: Community Edition or MongoDB Atlas (cloud)
- **Git**: Download from [git-scm.com](https://git-scm.com/)
- **PowerShell** or Command Prompt

---

## 🐧 Installation & Setup (Linux/macOS)

### Step 1: Clone Repository

```bash
git clone https://github.com/amna-mohsin/CodeAI-Pak.git
cd CodeAI-Pak
```

### Step 2: Set Up Python Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS: same command
```

### Step 3: Install Backend Dependencies

#### Main Backend (CodeAI-main)

```bash
cd CodeAI-main
pip install -r requirements.txt
cd ..
```

#### Auxiliary Backend (Optional)

```bash
cd backend
pip install -r requirements.txt
cd ..
```

### Step 4: Configure Environment Variables

Create `apikey.env` in the repository root:

```bash
cat > apikey.env << EOF
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=models/gemini-1.5-pro
MONGO_URI=mongodb://localhost:27017/
DB_NAME=codeai_pakistan
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development
EOF
```

**Note**: Leave `GOOGLE_API_KEY` blank if you don't have Gemini access; the app will use CodeT5 instead.

### Step 5: Verify MongoDB Connection

```bash
# Test connection (from CodeAI-main folder)
python test_connection.py
```

### Step 6: Run the Main Backend

```bash
cd CodeAI-main
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5000
```

Open: **http://localhost:5000**

### Step 7: (Optional) Run Auxiliary Backend

In a new terminal:

```bash
source .venv/bin/activate
cd backend
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5001
```

### Step 8: Run Frontend

In a new terminal:

```bash
cd codeai-frontend
npm install
npm run dev
```

Open: **http://localhost:5173**

---

## 🖥️ Installation & Setup (Windows - PowerShell)

### Step 1: Clone Repository

```powershell
git clone https://github.com/amna-mohsin/CodeAI-Pak.git
cd CodeAI-Pak
```

### Step 2: Create Python Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Note**: If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Backend Dependencies

#### Main Backend

```powershell
cd CodeAI-main
pip install -r requirements.txt
cd ..
```

#### Auxiliary Backend (Optional)

```powershell
cd backend
pip install -r requirements.txt
cd ..
```

### Step 4: Configure Environment Variables

Create `apikey.env` in repo root using PowerShell:

```powershell
@"
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=models/gemini-1.5-pro
MONGO_URI=mongodb://localhost:27017/
DB_NAME=codeai_pakistan
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development
"@ | Out-File -Encoding UTF8 apikey.env
```

### Step 5: Verify MongoDB Connection

```powershell
cd CodeAI-main
python test_connection.py
cd ..
```

### Step 6: Run the Main Backend

```powershell
cd CodeAI-main
$env:FLASK_APP = "app.py"
flask run --host=0.0.0.0 --port=5000
```

Open: **http://localhost:5000**

### Step 7: (Optional) Run Auxiliary Backend

Open **new PowerShell window**:

```powershell
cd CodeAI-Pak
.\.venv\Scripts\Activate.ps1
cd backend
$env:FLASK_APP = "app.py"
flask run --host=0.0.0.0 --port=5001
```

### Step 8: Run Frontend

Open **another new PowerShell window**:

```powershell
cd CodeAI-Pak
cd codeai-frontend
npm install
npm run dev
```

Open: **http://localhost:5173**

---

## 📖 Usage

### Getting Started

1. **Access the Application**
   - Open http://localhost:5173 (frontend)
   - Backend runs on http://localhost:5000

2. **Register / Login**
   - Create a new account or log in with existing credentials
   - Admin users can access the dashboard

3. **Upload Code**
   - Click "Upload Code" and select a Python or Java file
   - Supported: `.py`, `.java`

4. **Select Analysis Type**
   - **Quality Analysis**: Overall code quality scoring
   - **Bug Detection**: Find bugs and generate tests
   - **Documentation**: Generate API docs and comments
   - **README**: Auto-generate project README

5. **Choose Output Language**
   - **English**: Standard analysis and reports
   - **Urdu**: Bilingual output for documentation

6. **View & Download Reports**
   - View results in the browser
   - Download as PDF or JSON
   - Access previous submissions in history

---

## 🏗️ Project Structure

```
Uraan/
├── CodeAI-main/              # Main Flask application
│   ├── app.py               # Flask entry point, routes
│   ├── requirements.txt      # Python dependencies
│   ├── test_connection.py    # DB/env validation
│   ├── database/
│   │   ├── db_connector.py   # MongoDB connection
│   │   └── queries.py        # Database operations
│   ├── utils/
│   │   ├── ai_helpers.py     # AI integration (CodeT5, Gemini)
│   │   ├── report_generator.py  # PDF/JSON export
│   │   └── translator.py     # English ↔ Urdu translation
│   ├── templates/            # HTML templates
│   │   ├── index.html        # Main page
│   │   ├── login.html        # Login/register
│   │   ├── admin.html        # Admin dashboard
│   │   └── result.html       # Results display
│   ├── static/               # CSS, JS
│   │   ├── style.css
│   │   └── script.js
│   └── uploads/              # Generated reports (ignored)
│
├── backend/                  # Auxiliary Flask service
│   ├── app.py               # Bilingual endpoints
│   ├── requirements.txt      # Dependencies
│   ├── database/
│   │   ├── db_connector.py   # MongoDB connection
│   │   └── queries.py        # Database operations
│   └── utils/
│       ├── enhanced_ai_helpers.py  # Advanced AI features
│       └── comprehensive_pdf.py     # PDF generation
│
├── codeai-frontend/         # React + Vite frontend
│   ├── package.json         # npm dependencies
│   ├── vite.config.js       # Vite configuration
│   ├── index.html           # HTML entry point
│   ├── src/
│   │   ├── main.jsx         # React entry
│   │   ├── App.jsx          # Main component
│   │   ├── AuthPage.jsx     # Login/register
│   │   ├── Dashboard.jsx    # User dashboard
│   │   └── assets/          # Images, icons
│   └── public/              # Static files
│
├── .gitignore               # Git ignore patterns
├── README.md                # This file
└── LICENSE                  # MIT License
```

---

## 🔌 API Endpoints

### Authentication
- `GET /login` — Login page
- `GET /register` — Register page
- `POST /api/login` — Authenticate user
- `POST /api/logout` — Sign out

### Code Analysis (Main Backend)
- `POST /analyze` — Upload & analyze code (comprehensive)

### Bilingual Analysis (Auxiliary Backend)
- `POST /api/analyze/quality` — Code quality analysis
- `POST /api/analyze/bugs` — Bug detection + tests
- `POST /api/analyze/documentation` — Generate docs
- `POST /api/analyze/readme` — Generate README

### Admin
- `GET /api/admin/stats` — Dashboard statistics
- `GET /api/admin/export` — Export data as JSON

---

## 🔧 Configuration

### Environment Variables (`apikey.env`)

| Variable | Description | Example |
|---|---|---|
| `GOOGLE_API_KEY` | Google Gemini API key (optional) | `AIzaSyD...` |
| `GEMINI_MODEL` | Gemini model name | `models/gemini-1.5-pro` |
| `MONGO_URI` | MongoDB connection string | `mongodb://localhost:27017/` |
| `DB_NAME` | Database name | `codeai_pakistan` |
| `SECRET_KEY` | Flask session secret | `your-random-secret` |
| `FLASK_ENV` | Development or production | `development` |

### MongoDB Setup

**Local MongoDB:**
```bash
# macOS (Homebrew)
brew install mongodb-community
brew services start mongodb-community

# Linux (Ubuntu/Debian)
sudo apt install mongodb
sudo systemctl start mongodb
```

**Cloud MongoDB (MongoDB Atlas):**
1. Create account at [mongodb.com/atlas](https://mongodb.com/atlas)
2. Create a free cluster
3. Get connection string
4. Set in `apikey.env` as `MONGO_URI`

---

## 🐛 Troubleshooting

### MongoDB Connection Failed
**Error**: `Connection refused` or `unable to connect`

**Solution**:
- Check MongoDB is running: `mongosh` or `mongo` (CLI)
- Verify `MONGO_URI` in `apikey.env`
- Ensure MongoDB is accessible from your machine

### Gemini API Not Working
**Error**: `Invalid API key` or `quota exceeded`

**Solution**:
- Leave `GOOGLE_API_KEY` blank to use CodeT5 instead
- Get free Gemini key from [ai.google.dev](https://ai.google.dev)
- Check your quota: https://console.cloud.google.com

### Port Already in Use
**Error**: `Port 5000 already in use`

**Solution**:
```bash
# Linux/macOS: Find and kill process
lsof -i :5000
kill -9 <PID>

# Windows: PowerShell
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Python/Node Modules Not Installed
**Error**: `ModuleNotFoundError` or `Cannot find module`

**Solution**:
```bash
# Reinstall Python packages
pip install --force-reinstall -r CodeAI-main/requirements.txt

# Reinstall Node modules
cd codeai-frontend
rm -rf node_modules package-lock.json
npm install
```

### Frontend Cannot Connect to Backend
**Error**: `Failed to fetch` or CORS error

**Solution**:
- Ensure backend is running on `http://localhost:5000`
- Check frontend API base URL configuration
- Disable browser cache (DevTools → Settings → Disable cache)

---

## 📊 Supported Languages

| Language | File Extension | Support Level |
|---|---|---|
| Python | `.py` | ✅ Full |
| Java | `.java` | ✅ Full |
| JavaScript | `.js` | 🔄 Partial |
| C++ | `.cpp` | 🔄 Partial |

*Partial support means basic analysis; full support includes all AI features.*

---

## 🐛 Known Issues & Limitations

- **Large files**: Files >100KB may take longer to analyze
- **Real-time sync**: Reports don't auto-refresh; refresh manually
- **Gemini quota**: Free tier has usage limits (check quotas)
- **MongoDB indexing**: First startup creates indexes (may be slow)

---

## 🔮 Roadmap

### Upcoming Features
- [ ] Support for more languages (C#, Go, Rust)
- [ ] Dark mode and UI themes
- [ ] API rate limiting and quotas
- [ ] Team collaboration features
- [ ] Code comparison tools
- [ ] Performance benchmarking dashboard

### Future Enhancements
- [ ] Docker/Docker Compose setup
- [ ] GitHub Actions CI/CD integration
- [ ] WebSocket support for real-time updates
- [ ] Mobile app (React Native)
- [ ] VS Code extension
- [ ] Slack/Discord integration

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### How to Contribute

1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feature/YourFeature`
3. **Commit changes**: `git commit -m 'Add YourFeature'`
4. **Push to branch**: `git push origin feature/YourFeature`
5. **Open a Pull Request**

### Areas for Contribution

- 🤖 AI improvements (new algorithms, better prompts)
- 🌍 New language support
- 🎨 UI/UX enhancements
- 📚 Documentation and tutorials
- 🧪 Tests and quality assurance
- 🐛 Bug fixes and optimizations

---

## 👥 Authors

- **Amna Mohsin** — Backend architecture & AI integration
- **Hamna Ali Khan** — Frontend design & React implementation
- **Haseeb Yaqoob** — Backend services & database design
- **Aliza** — UI/UX design & debugging

---
## 📞 Contact & Social

* **GitHub**: https://github.com/amna-mohsin
* **LinkedIn**: https://www.linkedin.com/in/amna-m98/
* **Email**: For collaborations, reach out via GitHub

---

## 📝 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ using Flask, React, MongoDB, and AI**

[⬆ Back to Top](#-uraan--codeai-Pakistan)

</div>

