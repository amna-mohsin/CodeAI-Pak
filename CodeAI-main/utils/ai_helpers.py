"""
AI helper functions for code analysis
Handles integration with CodeT5 and Gemini models
"""

import json
import re
from typing import Dict, List, Any, Optional

def analyze_code_with_ai(
    code: str, 
    language: str, 
    gen_pipeline, 
    gemini_model=None
) -> Dict[str, Any]:
    """
    Main AI analysis function
    Uses CodeT5 for base analysis and optionally Gemini for enhanced insights
    
    Returns dict with:
    - overall_score: int (0-100)
    - review_score, test_score, doc_score, ux_score: int
    - quality_level: str (High/Medium/Low)
    - time_complexity: dict
    - bug_analysis: dict
    - review, tests, docs: str
    - corrected_code: str (optional)
    - gemini_quality_score, maintainability_score, etc. (if Gemini available)
    """
    
    # Step 1: Generate code review with CodeT5
    review_prompt = (
        f"Perform a concise code review for {language} code. "
        f"Identify bugs, performance issues, and improvements.\n\n"
        f"CODE:\n{code[:4000]}"
    )
    
    try:
        review_out = gen_pipeline(
            review_prompt, 
            max_new_tokens=256, 
            do_sample=False
        )[0]["generated_text"]
    except Exception as e:
        review_out = f"[Analysis error: {str(e)}]"
    
    # Step 2: Generate tests with CodeT5
    if language == 'Python':
        tests_prompt = (
            "Generate pytest unit tests for this code. "
            "Include at least 3 test functions with assertions.\n\n"
            f"CODE:\n{code[:3000]}"
        )
    elif language == 'Java':
        tests_prompt = (
            "Generate JUnit 5 tests for this Java code. "
            "Use @Test annotations and assertions.\n\n"
            f"CODE:\n{code[:3000]}"
        )
    else:
        tests_prompt = f"Generate unit tests for {language}:\n\n{code[:3000]}"
    
    try:
        tests_out = gen_pipeline(
            tests_prompt, 
            max_new_tokens=384, 
            do_sample=False
        )[0]["generated_text"]
    except Exception as e:
        tests_out = f"[Test generation error: {str(e)}]"
    
    # Step 3: Generate documentation with CodeT5
    docs_prompt = f"Generate API documentation for:\n\n{code[:2500]}"
    
    try:
        docs_out = gen_pipeline(
            docs_prompt, 
            max_new_tokens=256, 
            do_sample=False
        )[0]["generated_text"]
    except Exception as e:
        docs_out = f"[Documentation error: {str(e)}]"
    
    # Step 4: Calculate base scores
    scores = calculate_scores(code, review_out, tests_out, docs_out)
    
    # Step 5: Analyze time complexity
    time_complexity = analyze_time_complexity(code)
    
    # Step 6: Detect bugs
    bug_analysis = detect_bugs(code, review_out, language)
    
    # Step 7: Determine quality level
    quality_level = classify_quality(scores, bug_analysis)
    
    results = {
        "overall_score": scores["overall"],
        "review_score": scores["review_score"],
        "test_score": scores["test_score"],
        "doc_score": scores["doc_score"],
        "ux_score": scores["ux_score"],
        "coverage": scores["estimated_coverage"],
        "quality_level": quality_level,
        "time_complexity": time_complexity,
        "bug_analysis": bug_analysis,
        "review": review_out,
        "tests": tests_out,
        "docs": docs_out,
    }
    
    # Step 8: Enhanced analysis with Gemini (if available)
    if gemini_model:
        try:
            gemini_results = gemini_enhanced_analysis(
                code, 
                language, 
                gemini_model
            )
            
            if gemini_results:
                results.update(gemini_results)
                
        except Exception as e:
            print(f"Gemini analysis error: {e}")
    
    return results

def calculate_scores(
    code: str, 
    review: str, 
    tests: str, 
    docs: str
) -> Dict[str, int]:
    """Calculate quality scores from AI outputs"""
    
    lines = max(1, len([l for l in code.splitlines() if l.strip()]))
    
    # Review score: based on helpful keywords
    review_keywords = len(re.findall(
        r'\b(bug|error|fix|issue|recommend|improve|suggest|warning)\b', 
        review, 
        flags=re.I
    ))
    review_score = min(100, 50 + review_keywords * 10)
    
    # Test score: based on assertions and test functions
    test_lines = len([l for l in tests.splitlines() if l.strip()])
    assertions = len(re.findall(r'\b(assert|self\.assert|@Test)\b', tests))
    test_score = min(100, int((assertions * 15 + test_lines * 2)))
    
    # Documentation score
    doc_lines = len([l for l in docs.splitlines() if l.strip()])
    has_examples = bool(re.search(
        r'\b(example|usage|args|returns|parameters)\b', 
        docs, 
        flags=re.I
    ))
    doc_score = min(100, doc_lines * 10 + (30 if has_examples else 0))
    
    # UX score: code readability
    long_lines = len([l for l in code.splitlines() if len(l) > 120])
    ux_penalty = min(40, long_lines * 5)
    ux_score = max(0, 100 - ux_penalty)
    
    # Weighted overall score
    weights = {
        "review": 0.30,
        "test": 0.25,
        "doc": 0.25,
        "ux": 0.20
    }
    
    overall = int(
        review_score * weights["review"] +
        test_score * weights["test"] +
        doc_score * weights["doc"] +
        ux_score * weights["ux"]
    )
    
    # Estimate coverage from test score
    estimated_coverage = min(100, int(test_score * 0.8))
    
    return {
        "review_score": review_score,
        "test_score": test_score,
        "doc_score": doc_score,
        "ux_score": ux_score,
        "overall": overall,
        "estimated_coverage": estimated_coverage
    }

def analyze_time_complexity(code: str) -> Dict[str, Any]:
    """Heuristic time complexity analysis"""
    
    loop_count = len(re.findall(r'\b(for|while|foreach)\b', code))
    nested_loops = bool(re.search(
        r'for[\s\S]{0,200}for|while[\s\S]{0,200}while', 
        code
    ))
    
    if nested_loops and loop_count >= 2:
        dominant = 'O(n²)'
        confidence = 75
    elif loop_count >= 1:
        dominant = 'O(n)'
        confidence = 70
    elif re.search(r'binary\s*search|\.sort\(', code, flags=re.I):
        dominant = 'O(n log n)'
        confidence = 65
    else:
        dominant = 'O(1)'
        confidence = 60
    
    return {
        "dominant": dominant,
        "confidence": confidence
    }

def detect_bugs(code: str, review: str, language: str) -> Dict[str, Any]:
    """Detect potential bugs from code and review"""
    
    # Count bug mentions in review
    bug_keywords = {
        'syntax_errors': len(re.findall(r'\b(syntax|parse)\b', review, flags=re.I)),
        'logic_errors': len(re.findall(r'\b(logic|algorithm|incorrect)\b', review, flags=re.I)),
        'runtime_errors': len(re.findall(r'\b(runtime|exception|null)\b', review, flags=re.I)),
        'security_issues': len(re.findall(r'\b(security|vulnerability|injection)\b', review, flags=re.I)),
        'performance_issues': len(re.findall(r'\b(performance|inefficient|slow)\b', review, flags=re.I))
    }
    
    # Language-specific patterns
    if language == 'Python':
        bug_keywords['runtime_errors'] += len(re.findall(
            r'\b(KeyError|IndexError|TypeError|ValueError)\b', 
            code
        ))
        bug_keywords['security_issues'] += len(re.findall(
            r'\b(eval\(|exec\(|pickle\.loads)\b', 
            code
        ))
    elif language == 'Java':
        bug_keywords['runtime_errors'] += len(re.findall(
            r'\b(NullPointerException|ArrayIndexOutOfBounds)\b', 
            code
        ))
    
    total_bugs = sum(bug_keywords.values())
    
    # Calculate detection efficiency (0-100)
    detection_efficiency = min(100, total_bugs * 15)
    
    # Determine severity
    if total_bugs >= 5 or bug_keywords['security_issues'] >= 1:
        severity = 'High'
    elif total_bugs >= 2:
        severity = 'Medium'
    else:
        severity = 'Low'
    
    return {
        "bug_categories": bug_keywords,
        "total_bugs": total_bugs,
        "detection_efficiency": detection_efficiency,
        "severity": severity
    }

def classify_quality(scores: Dict, bug_analysis: Dict) -> str:
    """Classify overall code quality level"""
    
    overall = scores["overall"]
    severity = bug_analysis.get("severity", "Low")
    
    if overall >= 80 and severity == "Low":
        return "High"
    elif overall >= 60 or (overall >= 50 and severity != "High"):
        return "Medium"
    else:
        return "Low"

def gemini_enhanced_analysis(
    code: str, 
    language: str, 
    gemini_model
) -> Optional[Dict[str, Any]]:
    """
    Use Gemini for enhanced quality analysis
    Returns additional metrics: quality_score, maintainability, readability, best_practices
    """
    
    try:
        prompt = (
            f"Analyze this {language} code comprehensively. "
            "Return ONLY valid JSON with these keys:\n"
            "- gemini_quality_score (0-100): overall quality\n"
            "- maintainability_score (0-100): how maintainable\n"
            "- readability_score (0-100): how readable\n"
            "- best_practices_score (0-100): adherence to best practices\n"
            "- corrected_code: improved version of the code (same language)\n"
            "Do not include any text outside JSON.\n\n"
            f"CODE:\n{code[:6000]}"
        )
        
        response = gemini_model.generate_content(prompt)
        text = getattr(response, "text", None)
        
        if not text and getattr(response, "candidates", None):
            parts = getattr(response.candidates[0].content, "parts", [])
            text = "".join(getattr(p, "text", "") for p in parts)
        
        if not text:
            return None
        
        # Clean markdown fences
        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines)
        
        result = json.loads(text)
        
        return {
            "gemini_quality_score": result.get("gemini_quality_score", 0),
            "maintainability_score": result.get("maintainability_score", 0),
            "readability_score": result.get("readability_score", 0),
            "best_practices_score": result.get("best_practices_score", 0),
            "corrected_code": result.get("corrected_code")
        }
        
    except Exception as e:
        print(f"Gemini enhanced analysis error: {e}")
        return None

def generate_bug_report(
    code: str, 
    language: str, 
    ai_results: Dict
) -> List[Dict[str, Any]]:
    """
    Generate structured bug report with English and Urdu descriptions
    
    Returns list of bugs:
    [
        {
            "error_type": str,
            "severity": str,
            "line_number": int,
            "description_en": str,
            "description_ur": str
        }
    ]
    """
    
    bugs = []
    bug_analysis = ai_results.get("bug_analysis", {})
    bug_categories = bug_analysis.get("bug_categories", {})
    severity = bug_analysis.get("severity", "Low")
    
    # Generate bugs from categories
    for category, count in bug_categories.items():
        if count > 0:
            # Simple English description
            desc_en = f"Found {count} {category.replace('_', ' ')} in the code"
            
            # TODO: Integrate with translator for Urdu
            # For now, placeholder
            desc_ur = f"{category} پائے گئے: {count}"
            
            bugs.append({
                "error_type": category,
                "severity": severity,
                "line_number": 0,  # TODO: Parse actual line numbers
                "description_en": desc_en,
                "description_ur": desc_ur
            })
    
    return bugs

def generate_documentation(
    code: str, 
    language: str, 
    ai_results: Dict,
    gemini_model=None
) -> Dict[str, str]:
    """
    Generate documentation in both English and Urdu
    
    Returns:
    {
        "english": str,
        "urdu": str
    }
    """
    
    english_docs = ai_results.get("docs", "")
    
    # TODO: Integrate with translator for Urdu version
    urdu_docs = "[Urdu documentation will be generated here]"
    
    return {
        "english": english_docs,
        "urdu": urdu_docs
    }