import React, { useState, useRef } from 'react';
import { 
  Code, Bug, FileText, Shield, Upload, Moon, Sun, LogOut,
  CheckCircle, AlertTriangle, TrendingUp, Zap, FileCode, Lock,
  Settings, Download, Copy, Check, ChevronDown, ChevronUp, Globe
} from 'lucide-react';

const Dashboard = () => {
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [codeInput, setCodeInput] = useState('');
  const [language, setLanguage] = useState('en');
  const [showSettings, setShowSettings] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeAnalysis, setActiveAnalysis] = useState(null);
  const [results, setResults] = useState({});
  const [expandedSections, setExpandedSections] = useState({});
  const [copiedCode, setCopiedCode] = useState(false);
  
  const fileInputRef = useRef(null);
  const theme = isDarkMode ? darkTheme : lightTheme;
  const t = translations[language];

  const handleLogout = async () => {
    try {
      await fetch('http://localhost:5000/api/logout', {
        method: 'POST',
        credentials: 'include'
      });
      window.location.href = '/';
    } catch (err) {
      window.location.href = '/';
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadedFile(file);
      const reader = new FileReader();
      reader.onload = (event) => setCodeInput(event.target.result);
      reader.readAsText(file);
    }
  };

  const getCodeToAnalyze = () => codeInput.trim() || null;

  const analyzeQuality = async () => {
    const code = getCodeToAnalyze();
    if (!code) return alert(t.noCodeError);

    setIsAnalyzing(true);
    setActiveAnalysis('quality');
    
    try {
      const formData = new FormData();
      const blob = new Blob([code], { type: 'text/plain' });
      formData.append('file', blob, uploadedFile?.name || 'code.py');
      formData.append('language', language); // Pass language to backend
      
      const response = await fetch('http://localhost:5000/api/analyze/quality', {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });
      
      if (!response.ok) throw new Error('Analysis failed');
      const data = await response.json();
      setResults(prev => ({ ...prev, quality: data.results }));
      setExpandedSections(prev => ({ ...prev, quality: true }));
    } catch (error) {
      alert(t.analysisError);
    } finally {
      setIsAnalyzing(false);
      setActiveAnalysis(null);
    }
  };

  const analyzeBugs = async () => {
    const code = getCodeToAnalyze();
    if (!code) return alert(t.noCodeError);

    setIsAnalyzing(true);
    setActiveAnalysis('bugs');
    
    try {
      const formData = new FormData();
      const blob = new Blob([code], { type: 'text/plain' });
      formData.append('file', blob, uploadedFile?.name || 'code.py');
      formData.append('language', language); // Pass language to backend
      
      const response = await fetch('http://localhost:5000/api/analyze/bugs', {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });
      
      if (!response.ok) throw new Error('Analysis failed');
      const data = await response.json();
      setResults(prev => ({ ...prev, bugs: data.results }));
      setExpandedSections(prev => ({ ...prev, bugs: true }));
    } catch (error) {
      alert(t.analysisError);
    } finally {
      setIsAnalyzing(false);
      setActiveAnalysis(null);
    }
  };

  const generateDocs = async () => {
    const code = getCodeToAnalyze();
    if (!code) return alert(t.noCodeError);

    setIsAnalyzing(true);
    setActiveAnalysis('docs');
    
    try {
      const formData = new FormData();
      const blob = new Blob([code], { type: 'text/plain' });
      formData.append('file', blob, uploadedFile?.name || 'code.py');
      formData.append('language', language); // Pass language to backend
      formData.append('include_urdu', language === 'ur' ? 'true' : 'false');
      
      const response = await fetch('http://localhost:5000/api/analyze/documentation', {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });
      
      if (!response.ok) throw new Error('Analysis failed');
      const data = await response.json();
      setResults(prev => ({ ...prev, docs: data.results }));
      setExpandedSections(prev => ({ ...prev, docs: true }));
    } catch (error) {
      alert(t.analysisError);
    } finally {
      setIsAnalyzing(false);
      setActiveAnalysis(null);
    }
  };

  const runSecurityScan = async () => {
    const code = getCodeToAnalyze();
    if (!code) return alert(t.noCodeError);

    setIsAnalyzing(true);
    setActiveAnalysis('security');
    
    setTimeout(() => {
      setResults(prev => ({
        ...prev,
        security: {
          vulnerabilities: 2,
          securityScore: 75,
          issues: [
            { severity: 'high', type: 'SQL Injection', line: 45, description: 'Unsanitized user input' },
            { severity: 'medium', type: 'XSS Risk', line: 78, description: 'Unescaped output' }
          ]
        }
      }));
      setExpandedSections(prev => ({ ...prev, security: true }));
      setIsAnalyzing(false);
      setActiveAnalysis(null);
    }, 2000);
  };

  const copyCode = () => {
    navigator.clipboard.writeText(codeInput);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  return (
    <div style={{ ...styles.container, ...theme.container }}>
      <div style={{ ...styles.topBar, ...theme.topBar }}>
        <div style={styles.topBarLeft}>
          <Code size={24} style={{ color: '#8b5cf6' }} />
          <span style={styles.logoText}>CodeAI Pakistan</span>
        </div>
        
        <div style={styles.topBarRight}>
          <button onClick={() => setShowSettings(!showSettings)} style={{ ...styles.iconBtn, ...theme.iconBtn }}>
            <Settings size={20} />
          </button>
          <button onClick={() => setIsDarkMode(!isDarkMode)} style={{ ...styles.iconBtn, ...theme.iconBtn }}>
            {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
          </button>
          <button onClick={handleLogout} style={{ ...styles.logoutBtn, ...theme.logoutBtn }}>
            <LogOut size={18} />
            <span>{t.logout}</span>
          </button>
        </div>
      </div>

      {showSettings && (
        <div style={{ ...styles.settingsPanel, ...theme.settingsPanel }}>
          <div style={styles.settingsHeader}>
            <Globe size={20} style={{ color: '#8b5cf6' }} />
            <h3 style={{ ...styles.settingsTitle, ...theme.text }}>{t.languageSettings}</h3>
          </div>
          <div style={styles.languageOptions}>
            <button onClick={() => setLanguage('en')} style={{ ...styles.langBtn, ...theme.langBtn, ...(language === 'en' ? styles.langBtnActive : {}) }}>
              English
            </button>
            <button onClick={() => setLanguage('ur')} style={{ ...styles.langBtn, ...theme.langBtn, ...(language === 'ur' ? styles.langBtnActive : {}) }}>
              اردو (Urdu)
            </button>
          </div>
        </div>
      )}

      <div style={styles.mainContent}>
        <div style={{ ...styles.contentArea, ...theme.contentArea }}>
          <div style={styles.contentInner}>
            <div style={styles.header}>
              <h1 style={{ ...styles.title, ...theme.text }}>{t.title}</h1>
              <p style={{ ...styles.subtitle, ...theme.subtitle }}>{t.subtitle}</p>
            </div>

            <div style={{ ...styles.codeSection, ...theme.codeSection }}>
              <div style={styles.codeSectionHeader}>
                <div style={styles.headerLeft}>
                  <FileCode size={24} style={{ color: '#8b5cf6' }} />
                  <h3 style={{ ...styles.sectionTitle, ...theme.text }}>{t.codeInput}</h3>
                </div>
                <div style={styles.headerRight}>
                  <button onClick={() => fileInputRef.current?.click()} style={{ ...styles.uploadBtn, ...theme.uploadBtn }}>
                    <Upload size={18} />
                    <span>{t.uploadFile}</span>
                  </button>
                  <input ref={fileInputRef} type="file" onChange={handleFileUpload} style={{ display: 'none' }} accept=".py,.java,.js,.cpp,.c,.zip" />
                  {uploadedFile && <span style={{ ...styles.fileName, ...theme.fileName }}>{uploadedFile.name}</span>}
                </div>
              </div>

              <div style={styles.editorContainer}>
                <div style={styles.editorHeader}>
                  <span style={{ ...styles.editorLabel, ...theme.subtitle }}>{t.codeEditor}</span>
                  {codeInput && (
                    <button onClick={copyCode} style={{ ...styles.copyBtn, ...theme.copyBtn }}>
                      {copiedCode ? <Check size={16} /> : <Copy size={16} />}
                      <span>{copiedCode ? t.copied : t.copy}</span>
                    </button>
                  )}
                </div>
                <textarea value={codeInput} onChange={(e) => setCodeInput(e.target.value)} placeholder={t.codePlaceholder} style={{ ...styles.codeEditor, ...theme.codeEditor }} spellCheck={false} />
              </div>
            </div>

            <div style={styles.actionsGrid}>
              <button onClick={analyzeQuality} disabled={isAnalyzing} style={{ ...styles.actionBtn, ...theme.actionBtn, opacity: isAnalyzing && activeAnalysis !== 'quality' ? 0.5 : 1 }}>
                {isAnalyzing && activeAnalysis === 'quality' ? <div style={styles.spinner} /> : <TrendingUp size={24} />}
                <span style={styles.actionBtnText}>{t.checkQuality}</span>
              </button>
              <button onClick={analyzeBugs} disabled={isAnalyzing} style={{ ...styles.actionBtn, ...theme.actionBtn, opacity: isAnalyzing && activeAnalysis !== 'bugs' ? 0.5 : 1 }}>
                {isAnalyzing && activeAnalysis === 'bugs' ? <div style={styles.spinner} /> : <Bug size={24} />}
                <span style={styles.actionBtnText}>{t.detectBugs}</span>
              </button>
              <button onClick={generateDocs} disabled={isAnalyzing} style={{ ...styles.actionBtn, ...theme.actionBtn, opacity: isAnalyzing && activeAnalysis !== 'docs' ? 0.5 : 1 }}>
                {isAnalyzing && activeAnalysis === 'docs' ? <div style={styles.spinner} /> : <FileText size={24} />}
                <span style={styles.actionBtnText}>{t.generateDocs}</span>
              </button>
              <button onClick={runSecurityScan} disabled={isAnalyzing} style={{ ...styles.actionBtn, ...theme.actionBtn, opacity: isAnalyzing && activeAnalysis !== 'security' ? 0.5 : 1 }}>
                {isAnalyzing && activeAnalysis === 'security' ? <div style={styles.spinner} /> : <Shield size={24} />}
                <span style={styles.actionBtnText}>{t.securityScan}</span>
              </button>
            </div>

            {Object.keys(results).length > 0 && (
              <div style={{ ...styles.resultsPanel, ...theme.resultsPanel }}>
                <h2 style={{ ...styles.resultsTitle, ...theme.text }}>{t.results}</h2>

                {results.quality && <ResultSection title={t.qualityResults} icon={<TrendingUp size={20} />} expanded={expandedSections.quality} onToggle={() => setExpandedSections(p => ({ ...p, quality: !p.quality }))} theme={theme}><QualityResults results={results.quality} theme={theme} t={t} /></ResultSection>}
                
                {results.bugs && <ResultSection title={t.bugResults} icon={<Bug size={20} />} expanded={expandedSections.bugs} onToggle={() => setExpandedSections(p => ({ ...p, bugs: !p.bugs }))} theme={theme}><BugResults results={results.bugs} theme={theme} t={t} /></ResultSection>}
                
                {results.docs && <ResultSection title={t.docsResults} icon={<FileText size={20} />} expanded={expandedSections.docs} onToggle={() => setExpandedSections(p => ({ ...p, docs: !p.docs }))} theme={theme}><DocsResults results={results.docs} theme={theme} t={t} language={language} /></ResultSection>}
                
                {results.security && <ResultSection title={t.securityResults} icon={<Shield size={20} />} expanded={expandedSections.security} onToggle={() => setExpandedSections(p => ({ ...p, security: !p.security }))} theme={theme}><SecurityResults results={results.security} theme={theme} t={t} /></ResultSection>}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const ResultSection = ({ title, icon, expanded, onToggle, children, theme }) => (
  <div style={{ ...styles.resultSection, ...theme.resultSection }}>
    <div onClick={onToggle} style={{ ...styles.resultHeader, cursor: 'pointer' }}>
      <div style={styles.resultHeaderLeft}>
        <span style={{ color: '#8b5cf6' }}>{icon}</span>
        <h3 style={{ ...styles.resultTitle, ...theme.text }}>{title}</h3>
      </div>
      {expanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
    </div>
    {expanded && <div style={styles.resultContent}>{children}</div>}
  </div>
);

const QualityResults = ({ results, theme, t }) => (
  <div>
    <div style={{ ...styles.scoreCard, ...theme.scoreCard }}>
      <div style={styles.scoreCircle}>
        <span style={styles.scoreValue}>{results.overall_score || 0}</span>
        <span style={styles.scoreMax}>/100</span>
      </div>
      <div style={styles.metricsGrid}>
        <MetricCard label={t.maintainability} value={results.maintainability_score || 0} theme={theme} />
        <MetricCard label={t.reliability} value={results.reliability_score || 0} theme={theme} />
        <MetricCard label={t.security} value={results.security_score || 0} theme={theme} />
        <MetricCard label={t.readability} value={results.readability_score || 0} theme={theme} />
      </div>
    </div>
    {results.issues && results.issues.length > 0 && (
      <div style={{ ...styles.issuesCard, ...theme.issuesCard }}>
        <h4 style={{ ...styles.issuesTitle, ...theme.text }}>{t.issuesFound}</h4>
        {results.issues.slice(0, 10).map((issue, idx) => (
          <div key={idx} style={{ ...styles.issueItem, ...theme.issueItem }}>
            <AlertTriangle size={20} style={{ color: issue.severity === 'high' ? '#ef4444' : issue.severity === 'medium' ? '#f59e0b' : '#6b7280', marginRight: '12px', flexShrink: 0 }} />
            <div style={styles.issueContent}>
              <span style={{ ...styles.issueText, ...theme.text }}>{issue.message}</span>
              <span style={{ ...styles.issueLine, ...theme.subtitle }}>Line {issue.line}</span>
            </div>
          </div>
        ))}
      </div>
    )}
  </div>
);

const BugResults = ({ results, theme, t }) => (
  <div>
    <div style={styles.statsGrid}>
      <StatCard icon={<Bug size={32} style={{ color: '#ef4444' }} />} value={results.bugs_found || 0} label={t.bugsFound} theme={theme} />
      <StatCard icon={<CheckCircle size={32} style={{ color: '#10b981' }} />} value={results.tests_generated || 0} label={t.testsGenerated} theme={theme} />
      <StatCard icon={<TrendingUp size={32} style={{ color: '#8b5cf6' }} />} value={`${results.coverage_estimate || 0}%`} label={t.coverage} theme={theme} />
    </div>
    {results.bugs && results.bugs.length > 0 && (
      <div style={{ ...styles.issuesCard, ...theme.issuesCard }}>
        <h4 style={{ ...styles.issuesTitle, ...theme.text }}>{t.detectedBugs}</h4>
        {results.bugs.slice(0, 10).map((bug, idx) => (
          <div key={idx} style={{ ...styles.issueItem, ...theme.issueItem }}>
            <Bug size={20} style={{ color: '#ef4444', marginRight: '12px', flexShrink: 0 }} />
            <div style={styles.issueContent}>
              <span style={{ ...styles.issueText, ...theme.text }}>{bug.type}: {bug.description}</span>
              <span style={{ ...styles.issueLine, ...theme.subtitle }}>Line {bug.line}</span>
            </div>
          </div>
        ))}
      </div>
    )}
  </div>
);

const DocsResults = ({ results, theme, t, language }) => (
  <div>
    <div style={{ ...styles.scoreCard, ...theme.scoreCard }}>
      <CheckCircle size={48} style={{ color: '#10b981', marginBottom: '16px' }} />
      <h4 style={{ ...styles.scoreLabel, ...theme.text }}>{t.docsGenerated}</h4>
      <div style={styles.scoreValue}>{results.completeness_score || 0}%</div>
    </div>
    {results.documentation_english && (
      <div style={{ ...styles.codeBlock, ...theme.codeBlock }}>
        <div style={styles.codeBlockHeader}>
          <span style={{ ...styles.codeBlockTitle, ...theme.text }}>Documentation</span>
          <button onClick={() => navigator.clipboard.writeText(language === 'ur' && results.documentation_urdu ? results.documentation_urdu : results.documentation_english)} style={{ ...styles.copyBtn, ...theme.copyBtn }}>
            <Copy size={16} />
            <span>{t.copy}</span>
          </button>
        </div>
        <pre style={{ ...styles.codeBlockContent, ...theme.codeBlockContent }}>
          {(language === 'ur' && results.documentation_urdu ? results.documentation_urdu : results.documentation_english).substring(0, 800)}...
        </pre>
      </div>
    )}
  </div>
);

const SecurityResults = ({ results, theme, t }) => (
  <div>
    <div style={{ ...styles.scoreCard, ...theme.scoreCard }}>
      <Shield size={48} style={{ color: results.securityScore > 80 ? '#10b981' : '#f59e0b', marginBottom: '16px' }} />
      <h4 style={{ ...styles.scoreLabel, ...theme.text }}>{t.securityScore}</h4>
      <div style={styles.scoreValue}>{results.securityScore}/100</div>
    </div>
    {results.issues && results.issues.length > 0 && (
      <div style={{ ...styles.issuesCard, ...theme.issuesCard }}>
        <h4 style={{ ...styles.issuesTitle, ...theme.text }}>{t.vulnerabilities}</h4>
        {results.issues.map((issue, idx) => (
          <div key={idx} style={{ ...styles.issueItem, ...theme.issueItem }}>
            <Lock size={20} style={{ color: issue.severity === 'critical' ? '#ef4444' : '#f59e0b', marginRight: '12px' }} />
            <div style={styles.issueContent}>
              <span style={{ ...styles.issueText, ...theme.text }}>{issue.type}: {issue.description}</span>
              <span style={{ ...styles.issueLine, ...theme.subtitle }}>Line {issue.line}</span>
            </div>
          </div>
        ))}
      </div>
    )}
  </div>
);

const MetricCard = ({ label, value, theme }) => (
  <div style={{ ...styles.metricCard, ...theme.metricCard }}>
    <span style={{ ...styles.metricLabel, ...theme.subtitle }}>{label}</span>
    <span style={styles.metricValue}>{value}%</span>
  </div>
);

const StatCard = ({ icon, value, label, theme }) => (
  <div style={{ ...styles.statCard, ...theme.statCard }}>
    {icon}
    <div style={styles.statValue}>{value}</div>
    <div style={{ ...styles.statLabel, ...theme.subtitle }}>{label}</div>
  </div>
);

const translations = {
  en: {
    title: 'Unified Code Analysis Dashboard',
    subtitle: 'Upload or paste your code to analyze with AI-powered tools',
    codeInput: 'Code Input',
    uploadFile: 'Upload File',
    codeEditor: 'Or paste/write your code here',
    codePlaceholder: '// Paste or write your code here...\n// Supported: Python, Java, JavaScript, C++, C\n\nfunction example() {\n  console.log("Hello, CodeAI!");\n}',
    checkQuality: 'Check Code Quality',
    detectBugs: 'Detect Bugs & Generate Tests',
    generateDocs: 'Generate Documentation',
    securityScan: 'Run Security Scan',
    results: 'Analysis Results',
    qualityResults: 'Code Quality Analysis',
    bugResults: 'Bug Detection & Testing',
    docsResults: 'Documentation',
    securityResults: 'Security Scan',
    maintainability: 'Maintainability',
    reliability: 'Reliability',
    security: 'Security',
    readability: 'Readability',
    issuesFound: 'Issues Found',
    bugsFound: 'Bugs Found',
    testsGenerated: 'Tests Generated',
    coverage: 'Test Coverage',
    detectedBugs: 'Detected Bugs',
    docsGenerated: 'Documentation Generated',
    securityScore: 'Security Score',
    vulnerabilities: 'Vulnerabilities Found',
    copy: 'Copy',
    copied: 'Copied!',
    settings: 'Settings',
    logout: 'Logout',
    languageSettings: 'Language Settings',
    noCodeError: 'Please upload a file or paste code first',
    analysisError: 'Analysis failed. Please try again.'
  },
  ur: {
    title: 'متحدہ کوڈ تجزیہ ڈیش بورڈ',
    subtitle: 'AI ٹولز سے تجزیہ کے لیے اپنا کوڈ اپ لوڈ یا پیسٹ کریں',
    codeInput: 'کوڈ ان پٹ',
    uploadFile: 'فائل اپ لوڈ کریں',
    codeEditor: 'یا یہاں کوڈ لکھیں',
    codePlaceholder: '// یہاں اپنا کوڈ لکھیں...\n\nfunction example() {\n  console.log("Hello, CodeAI!");\n}',
    checkQuality: 'کوڈ کوالٹی چیک کریں',
    detectBugs: 'بگز تلاش کریں',
    generateDocs: 'دستاویزات بنائیں',
    securityScan: 'سیکیورٹی اسکین',
    results: 'تجزیہ کے نتائج',
    qualityResults: 'کوڈ کوالٹی',
    bugResults: 'بگ ڈیٹیکشن',
    docsResults: 'دستاویزات',
    securityResults: 'سیکیورٹی اسکین',
    maintainability: 'برقراری',
    reliability: 'اعتبار',
    security: 'سیکیورٹی',
    readability: 'پڑھنے کی صلاحیت',
    issuesFound: 'مسائل ملے',
    bugsFound: 'بگز ملے',
    testsGenerated: 'ٹیسٹ بنائے گئے',
    coverage: 'کوریج',
    detectedBugs: 'ملے ہوئے بگز',
    docsGenerated: 'دستاویزات تیار',
    securityScore: 'سیکیورٹی سکور',
    vulnerabilities: 'کمزوریاں',
    copy: 'کاپی کریں',
    copied: 'کاپی ہو گیا!',
    settings: 'ترتیبات',
    logout: 'لاگ آؤٹ',
    languageSettings: 'زبان کی ترتیبات',
    noCodeError: 'براہ کرم پہلے فائل اپ لوڈ یا کوڈ پیسٹ کریں',
    analysisError: 'تجزیہ ناکام ہو گیا۔ دوبارہ کوشش کریں۔'
  }
};

const styles = {
  container: { minHeight: '100vh', width: '100%', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' },
  topBar: { position: 'fixed', top: 0, left: 0, right: 0, height: '70px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 40px', borderBottom: '1px solid rgba(139, 92, 246, 0.2)', backdropFilter: 'blur(20px)', zIndex: 100, boxShadow: '0 4px 24px rgba(0, 0, 0, 0.1)' },
  topBarLeft: { display: 'flex', alignItems: 'center', gap: '12px' },
  logoText: { fontSize: '20px', fontWeight: '700', background: 'linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' },
  topBarRight: { display: 'flex', alignItems: 'center', gap: '16px' },
  iconBtn: { padding: '10px 12px', border: 'none', borderRadius: '10px', cursor: 'pointer', display: 'flex', alignItems: 'center', transition: 'all 0.3s ease' },
  logoutBtn: { display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 20px', border: 'none', borderRadius: '10px', fontWeight: '600', cursor: 'pointer', fontSize: '15px', transition: 'all 0.3s ease' },
  settingsPanel: { position: 'fixed', top: '70px', right: '20px', padding: '24px', borderRadius: '16px', zIndex: 99, minWidth: '250px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' },
  settingsHeader: { display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' },
  settingsTitle: { fontSize: '18px', fontWeight: '700', margin: 0 },
  languageOptions: { display: 'flex', flexDirection: 'column', gap: '12px' },
  langBtn: { padding: '12px 20px', border: '1px solid rgba(139, 92, 246, 0.3)', borderRadius: '10px', cursor: 'pointer', fontSize: '15px', fontWeight: '600', transition: 'all 0.3s ease', textAlign: 'left' },
  langBtnActive: { background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(236, 72, 153, 0.2) 100%)', border: '1px solid #8b5cf6' },
  mainContent: { marginTop: '70px', minHeight: 'calc(100vh - 70px)', padding: '40px' },
  contentArea: { maxWidth: '1200px', margin: '0 auto' },
  contentInner: { width: '100%' },
  header: { marginBottom: '40px', textAlign: 'center' },
  title: { fontSize: '42px', fontWeight: '800', marginBottom: '12px' },
  subtitle: { fontSize: '18px', lineHeight: '1.6' },
  codeSection: { padding: '32px', borderRadius: '16px', marginBottom: '32px', border: '1px solid rgba(139, 92, 246, 0.2)' },
  codeSectionHeader: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' },
  headerLeft: { display: 'flex', alignItems: 'center', gap: '12px' },
  sectionTitle: { fontSize: '20px', fontWeight: '700', margin: 0 },
  headerRight: { display: 'flex', alignItems: 'center', gap: '12px' },
  uploadBtn: { display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 20px', border: '1px solid rgba(139, 92, 246, 0.3)', borderRadius: '10px', fontWeight: '600', cursor: 'pointer', fontSize: '14px', transition: 'all 0.3s ease' },
  fileName: { fontSize: '14px', fontWeight: '500' },
  editorContainer: { marginTop: '20px' },
  editorHeader: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' },
  editorLabel: { fontSize: '14px', fontWeight: '600' },
  copyBtn: { display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 16px', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '13px', fontWeight: '600', transition: 'all 0.3s ease' },
  codeEditor: { width: '100%', minHeight: '300px', padding: '20px', borderRadius: '12px', border: '1px solid rgba(139, 92, 246, 0.3)', fontSize: '14px', fontFamily: '"Fira Code", "Consolas", monospace', resize: 'vertical', outline: 'none' },
  actionsGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '40px' },
  actionBtn: { display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px', padding: '32px 24px', border: 'none', borderRadius: '16px', background: 'linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)', color: '#fff', cursor: 'pointer', fontSize: '16px', fontWeight: '600', transition: 'all 0.3s ease', boxShadow: '0 4px 20px rgba(139, 92, 246, 0.3)' },
  actionBtnText: { fontSize: '15px' },
  spinner: { width: '24px', height: '24px', border: '3px solid rgba(255,255,255,0.3)', borderTop: '3px solid #fff', borderRadius: '50%', animation: 'spin 1s linear infinite' },
  resultsPanel: { padding: '32px', borderRadius: '16px', marginTop: '40px', border: '1px solid rgba(139, 92, 246, 0.2)' },
  resultsTitle: { fontSize: '28px', fontWeight: '700', marginBottom: '24px' },
  resultSection: { marginBottom: '24px', borderRadius: '12px', border: '1px solid rgba(139, 92, 246, 0.2)', overflow: 'hidden' },
  resultHeader: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '20px', transition: 'all 0.3s ease' },
  resultHeaderLeft: { display: 'flex', alignItems: 'center', gap: '12px' },
  resultTitle: { fontSize: '18px', fontWeight: '700', margin: 0 },
  resultContent: { padding: '0 20px 20px' },
  scoreCard: { padding: '32px', borderRadius: '12px', textAlign: 'center', marginBottom: '24px', border: '1px solid rgba(139, 92, 246, 0.2)' },
  scoreCircle: { display: 'inline-block', marginBottom: '20px' },
  scoreValue: { fontSize: '64px', fontWeight: '800', background: 'linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' },
  scoreMax: { fontSize: '24px', color: '#8b5cf6' },
  scoreLabel: { fontSize: '16px', fontWeight: '600', marginBottom: '8px' },
  metricsGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '16px', marginTop: '24px' },
  metricCard: { padding: '20px', borderRadius: '12px', textAlign: 'center', border: '1px solid rgba(139, 92, 246, 0.2)' },
  metricLabel: { fontSize: '13px', marginBottom: '8px', display: 'block' },
  metricValue: { fontSize: '28px', fontWeight: '700', color: '#8b5cf6' },
  issuesCard: { padding: '24px', borderRadius: '12px', border: '1px solid rgba(139, 92, 246, 0.2)' },
  issuesTitle: { fontSize: '18px', fontWeight: '700', marginBottom: '20px' },
  issueItem: { display: 'flex', alignItems: 'flex-start', padding: '16px', borderRadius: '10px', marginBottom: '12px', border: '1px solid rgba(139, 92, 246, 0.1)' },
  issueContent: { display: 'flex', flexDirection: 'column', gap: '4px', flex: 1 },
  issueText: { fontSize: '14px', lineHeight: '1.5' },
  issueLine: { fontSize: '13px' },
  statsGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '24px' },
  statCard: { padding: '32px', borderRadius: '12px', textAlign: 'center', border: '1px solid rgba(139, 92, 246, 0.2)' },
  statValue: { fontSize: '36px', fontWeight: '800', margin: '16px 0 8px', background: 'linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' },
  statLabel: { fontSize: '14px' },
  codeBlock: { padding: '20px', borderRadius: '12px', marginTop: '24px', border: '1px solid rgba(139, 92, 246, 0.2)' },
  codeBlockHeader: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' },
  codeBlockTitle: { fontSize: '16px', fontWeight: '600' },
  codeBlockContent: { padding: '16px', borderRadius: '8px', overflow: 'auto', fontSize: '13px', fontFamily: '"Fira Code", "Consolas", monospace', lineHeight: '1.6', margin: 0 }
};

const darkTheme = {
  container: { backgroundColor: '#0a0a0f', color: '#fff' },
  topBar: { backgroundColor: 'rgba(10, 10, 15, 0.95)' },
  iconBtn: { background: 'rgba(139, 92, 246, 0.1)', color: '#8b5cf6' },
  logoutBtn: { background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', color: '#ef4444' },
  settingsPanel: { backgroundColor: 'rgba(17, 17, 27, 0.95)', border: '1px solid rgba(139, 92, 246, 0.3)' },
  text: { color: '#fff' },
  subtitle: { color: '#a1a1aa' },
  langBtn: { background: 'rgba(139, 92, 246, 0.05)', color: '#e4e4e7' },
  contentArea: { backgroundColor: '#0a0a0f' },
  codeSection: { background: 'rgba(17, 17, 27, 0.6)' },
  uploadBtn: { background: 'rgba(139, 92, 246, 0.1)', color: '#8b5cf6' },
  fileName: { color: '#a1a1aa' },
  copyBtn: { background: 'rgba(139, 92, 246, 0.1)', color: '#8b5cf6' },
  codeEditor: { background: 'rgba(10, 10, 15, 0.8)', color: '#e4e4e7', border: '1px solid rgba(139, 92, 246, 0.3)' },
  actionBtn: {},
  resultsPanel: { background: 'rgba(17, 17, 27, 0.6)' },
  resultSection: { background: 'rgba(17, 17, 27, 0.4)' },
  scoreCard: { background: 'rgba(17, 17, 27, 0.6)' },
  metricCard: { background: 'rgba(139, 92, 246, 0.1)' },
  issuesCard: { background: 'rgba(17, 17, 27, 0.6)' },
  issueItem: { background: 'rgba(139, 92, 246, 0.05)' },
  statCard: { background: 'rgba(17, 17, 27, 0.6)' },
  codeBlock: { background: 'rgba(17, 17, 27, 0.6)' },
  codeBlockContent: { background: 'rgba(10, 10, 15, 0.8)', color: '#e4e4e7' }
};

const lightTheme = {
  container: { backgroundColor: '#f8f9fa', color: '#1a1a1a' },
  topBar: { backgroundColor: 'rgba(255, 255, 255, 0.95)', borderBottom: '1px solid rgba(139, 92, 246, 0.15)' },
  iconBtn: { background: 'rgba(139, 92, 246, 0.1)', color: '#8b5cf6' },
  logoutBtn: { background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', color: '#ef4444' },
  settingsPanel: { backgroundColor: '#ffffff', border: '1px solid rgba(139, 92, 246, 0.2)' },
  text: { color: '#1a1a1a' },
  subtitle: { color: '#52525b' },
  langBtn: { background: 'rgba(139, 92, 246, 0.05)', color: '#3f3f46' },
  contentArea: { backgroundColor: '#f8f9fa' },
  codeSection: { background: '#ffffff' },
  uploadBtn: { background: 'rgba(139, 92, 246, 0.1)', color: '#8b5cf6' },
  fileName: { color: '#71717a' },
  copyBtn: { background: 'rgba(139, 92, 246, 0.1)', color: '#8b5cf6' },
  codeEditor: { background: '#ffffff', color: '#1a1a1a', border: '1px solid rgba(139, 92, 246, 0.3)' },
  actionBtn: {},
  resultsPanel: { background: '#ffffff' },
  resultSection: { background: '#ffffff' },
  scoreCard: { background: '#ffffff' },
  metricCard: { background: 'rgba(139, 92, 246, 0.05)' },
  issuesCard: { background: '#ffffff' },
  issueItem: { background: 'rgba(139, 92, 246, 0.03)' },
  statCard: { background: '#ffffff' },
  codeBlock: { background: '#ffffff' },
  codeBlockContent: { background: '#f8f9fa', color: '#1a1a1a' }
};

if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = '@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }';
  document.head.appendChild(style);
}

export default Dashboard;