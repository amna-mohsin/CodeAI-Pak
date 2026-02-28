// Check authentication on page load
document.addEventListener("DOMContentLoaded", () => {
    // Check if user is logged in (skip for login/register pages)
    const currentPath = window.location.pathname;
    if (!currentPath.includes('login') && !currentPath.includes('register')) {
        const isLoggedIn = sessionStorage.getItem('isLoggedIn');
        if (!isLoggedIn) {
            console.log('No session found, redirecting to login');
            window.location.href = '/login';
            return;
        }
    }

    // Initialize dashboard if on dashboard page
    if (document.getElementById('uploadForm')) {
        initDashboard();
    }
});

function initDashboard() {
    // Cache DOM elements
    const elements = {
        fileInput: document.getElementById("fileInput"),
        fileLabel: document.getElementById("fileLabel"),
        uploadForm: document.getElementById("uploadForm"),
        analyzeBtn: document.getElementById("analyzeBtn"),
        resetBtn: document.getElementById("resetBtn"),
        errorMsg: document.getElementById("errorMsg"),
        progressCircle: document.getElementById("progressCircle"),
        circleText: document.getElementById("circleText"),
        qualityStat: document.getElementById("qualityStat"),
        coverageStat: document.getElementById("coverageStat"),
        resultsArea: document.getElementById("results"),
        welcomeState: document.getElementById("welcomeState"),
        bugReportPre: document.getElementById("bugReportPre"),
        correctedCodePre: document.getElementById("correctedCodePre"),
        barReview: document.getElementById("barReview"),
        barTest: document.getElementById("barTest"),
        barDoc: document.getElementById("barDoc"),
        barUx: document.getElementById("barUx"),
        numReview: document.getElementById("numReview"),
        numTest: document.getElementById("numTest"),
        numDoc: document.getElementById("numDoc"),
        numUx: document.getElementById("numUx"),
        downloadReport: document.getElementById("downloadReport"),
        downloadPdf: document.getElementById("downloadPdf"),
        geminiMetrics: document.getElementById("geminiMetrics"),
        qualityLevel: document.getElementById("qualityLevel"),
        timeComplexity: document.getElementById("timeComplexity"),
        translateBtn: document.getElementById("translateBtn")
    };

    // Validate required elements
    if (!elements.fileInput || !elements.uploadForm || !elements.analyzeBtn) {
        console.error('Missing required elements');
        return;
    }

    // Store current report data for translation
    let currentReport = null;

    // Utility functions
    const safeSetText = (element, text) => {
        if (element) element.textContent = text;
    };

    const safeSetDisplay = (element, display) => {
        if (element) element.style.display = display;
    };

    const showError = (message) => {
        if (elements.errorMsg) {
            elements.errorMsg.textContent = message;
            elements.errorMsg.style.display = "block";
            elements.errorMsg.focus();
        }
    };

    const hideError = () => {
        if (elements.errorMsg) {
            elements.errorMsg.style.display = "none";
        }
    };

    const setLoadingState = (loading) => {
        if (elements.analyzeBtn) {
            elements.analyzeBtn.disabled = loading;
            
            const btnText = elements.analyzeBtn.querySelector('.btn-text');
            const btnLoading = elements.analyzeBtn.querySelector('.btn-loading');
            
            if (btnText && btnLoading) {
                btnText.style.display = loading ? 'none' : 'inline';
                btnLoading.style.display = loading ? 'inline' : 'none';
            }
        }
    };

    const updateCircularProgress = (percentage) => {
        if (!elements.progressCircle) return;
        
        const circumference = 2 * Math.PI * 60; // radius is 60
        const offset = circumference - (percentage / 100) * circumference;
        
        elements.progressCircle.style.strokeDashoffset = offset;
        safeSetText(elements.circleText, `${percentage}%`);
    };

    // File input change handler
    if (elements.fileInput) {
        elements.fileInput.addEventListener("change", (e) => {
            const file = e.target.files[0];
            const labelText = elements.fileLabel?.querySelector('.text');
            
            if (file && labelText) {
                labelText.textContent = file.name;
                hideError();
            } else if (labelText) {
                labelText.textContent = "Choose file or drag here";
            }
        });
    }

    // Reset button handler
    if (elements.resetBtn) {
        elements.resetBtn.addEventListener("click", () => {
            if (elements.fileInput) elements.fileInput.value = "";
            
            const labelText = elements.fileLabel?.querySelector('.text');
            if (labelText) labelText.textContent = "Choose file or drag here";
            
            safeSetDisplay(elements.resultsArea, "none");
            safeSetDisplay(elements.welcomeState, "flex");
            safeSetDisplay(elements.geminiMetrics, "none");
            hideError();
            
            updateCircularProgress(0);
            safeSetText(elements.qualityStat, "—");
            safeSetText(elements.coverageStat, "—");
            safeSetText(elements.qualityLevel, "—");
            safeSetText(elements.timeComplexity, "—");
            
            currentReport = null;
            setLoadingState(false);
        });
    }

    // Translate to Urdu function
    async function translateToUrdu(text) {
        try {
            const response = await fetch('/translate_to_urdu', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });

            if (!response.ok) {
                throw new Error('Translation failed');
            }

            const data = await response.json();
            return data.translated_text || text;
        } catch (error) {
            console.error('Translation error:', error);
            showError('Translation failed. Please try again.');
            return text;
        }
    }

    // Translate button handler
    if (elements.translateBtn) {
        elements.translateBtn.addEventListener("click", async () => {
            if (!currentReport) {
                showError('No report available to translate');
                return;
            }

            elements.translateBtn.disabled = true;
            elements.translateBtn.textContent = '⏳ Translating...';

            try {
                // Translate bug report
                if (elements.bugReportPre && elements.bugReportPre.textContent) {
                    const originalBugReport = elements.bugReportPre.textContent;
                    if (originalBugReport !== '[no bug report]') {
                        const translatedBugReport = await translateToUrdu(originalBugReport);
                        elements.bugReportPre.textContent = translatedBugReport;
                    }
                }

                // Translate corrected code comments (if any)
                if (elements.correctedCodePre && elements.correctedCodePre.textContent) {
                    const originalCode = elements.correctedCodePre.textContent;
                    if (originalCode !== '[no corrected code]') {
                        // Only translate comments, not the actual code
                        const translatedCode = await translateToUrdu(originalCode);
                        elements.correctedCodePre.textContent = translatedCode;
                    }
                }

                elements.translateBtn.textContent = '✅ Translated!';
                
                setTimeout(() => {
                    elements.translateBtn.textContent = '🌐 Translate to Urdu';
                    elements.translateBtn.disabled = false;
                }, 2000);

            } catch (error) {
                console.error('Translation error:', error);
                elements.translateBtn.textContent = '🌐 Translate to Urdu';
                elements.translateBtn.disabled = false;
            }
        });
    }

    // Form submission handler
    if (elements.uploadForm) {
        elements.uploadForm.addEventListener("submit", async (ev) => {
            ev.preventDefault();
            hideError();
            
            if (!elements.fileInput.files.length) {
                showError("Please select a file first.");
                return;
            }

            const file = elements.fileInput.files[0];
            const maxSize = 10 * 1024 * 1024; // 10MB
            
            if (file.size > maxSize) {
                showError("File size too large. Maximum 10MB allowed.");
                return;
            }

            const formData = new FormData();
            formData.append("file", file);

            setLoadingState(true);
            hideError();

            try {
                const response = await fetch("/analyze", {
                    method: "POST",
                    body: formData,
                    credentials: 'same-origin'  // Important for session
                });

                // Check for auth errors
                if (response.status === 401) {
                    sessionStorage.removeItem('isLoggedIn');
                    window.location.href = '/login';
                    return;
                }

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const payload = await response.json();

                if (payload.error) {
                    throw new Error(payload.error);
                }

                const report = payload.report;
                currentReport = report;

                // Hide welcome state, show results
                safeSetDisplay(elements.welcomeState, "none");
                safeSetDisplay(elements.resultsArea, "block");

                // Update circular progress
                const overall = report.scores.overall || 0;
                const coverage = report.scores.estimated_coverage || 0;

                updateCircularProgress(overall);
                safeSetText(elements.qualityStat, `${overall}%`);
                safeSetText(elements.coverageStat, `${coverage}%`);

                // Enhanced metrics
                const s = report.scores || {};
                
                const setText = (el, val) => { if (el) el.textContent = val; };

                setText(elements.qualityLevel, s.quality_level || 'N/A');
                setText(document.getElementById('qualityLevelValue'), s.quality_level || 'N/A');

                const dominant = s.time_complexity && s.time_complexity.dominant;
                setText(elements.timeComplexity, dominant || 'N/A');
                setText(document.getElementById('timeComplexityValue'), dominant || 'N/A');

                const eff = s.bug_analysis && s.bug_analysis.detection_efficiency;
                setText(document.getElementById('bugEfficiencyValue'), 
                    (typeof eff === 'number') ? `${eff}%` : 'N/A');
                
                const sev = s.bug_analysis && s.bug_analysis.severity;
                setText(document.getElementById('bugSeverityValue'), sev || 'N/A');

                // Gemini metrics
                if (s.gemini_quality_score || s.maintainability_score || 
                    s.readability_score || s.best_practices_score) {
                    safeSetDisplay(elements.geminiMetrics, "block");
                    
                    setText(document.getElementById('geminiQualityValue'), 
                        s.gemini_quality_score ? `${s.gemini_quality_score}/100` : 'N/A');
                    setText(document.getElementById('maintainabilityValue'), 
                        s.maintainability_score ? `${s.maintainability_score}/100` : 'N/A');
                    setText(document.getElementById('readabilityValue'), 
                        s.readability_score ? `${s.readability_score}/100` : 'N/A');
                    setText(document.getElementById('bestPracticesValue'), 
                        s.best_practices_score ? `${s.best_practices_score}/100` : 'N/A');
                } else {
                    safeSetDisplay(elements.geminiMetrics, "none");
                }

                // Update breakdown bars
                const r = s.review_score || 0;
                const t = s.test_score || 0;
                const d = s.doc_score || 0;
                const u = s.ux_score || 0;

                if (elements.barReview) elements.barReview.style.width = `${r}%`;
                if (elements.barTest) elements.barTest.style.width = `${t}%`;
                if (elements.barDoc) elements.barDoc.style.width = `${d}%`;
                if (elements.barUx) elements.barUx.style.width = `${u}%`;

                setText(elements.numReview, `${r}%`);
                setText(elements.numTest, `${t}%`);
                setText(elements.numDoc, `${d}%`);
                setText(elements.numUx, `${u}%`);

                // Display bug report and corrected code
                setText(elements.bugReportPre, report.bug_report || "[no bug report]");
                setText(elements.correctedCodePre, report.corrected_code || "[no corrected code]");

                // Download links
                if (payload.report_file && elements.downloadReport) {
                    elements.downloadReport.href = `/download/${payload.report_file}`;
                    safeSetDisplay(elements.downloadReport, "inline-flex");
                }

                if (payload.pdf_file && elements.downloadPdf) {
                    elements.downloadPdf.href = `/download_pdf/${payload.pdf_file}`;
                    safeSetDisplay(elements.downloadPdf, "inline-flex");
                }

            } catch (error) {
                console.error("Analysis failed:", error);
                showError(`Analysis failed: ${error.message}`);
            } finally {
                setLoadingState(false);
            }
        });
    }
}

// Logout function (can be added to layout if needed)
async function logout() {
    try {
        const response = await fetch('/api/logout', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (response.ok) {
            // Clear session storage
            sessionStorage.clear();
            localStorage.clear();
            
            // Redirect to login
            window.location.href = '/login';
        } else {
            console.error('Logout failed');
            // Force redirect anyway
            sessionStorage.clear();
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Logout error:', error);
        // Force redirect on error
        sessionStorage.clear();
        window.location.href = '/login';
    }
}