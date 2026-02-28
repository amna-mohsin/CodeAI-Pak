"""
Enhanced AI helper functions for CodeAI Pakistan
BILINGUAL SUPPORT - English & Urdu
Updated for NEW Google GenAI SDK (google-genai package)
IMPROVED VERSION: Adds strong language enforcement while keeping ALL original functions

Place this file at: backend/utils/enhanced_ai_helpers.py
"""

import json
import re
from typing import Dict, List, Any, Optional

# ============================================================================
# ENHANCED LANGUAGE PROMPT TEMPLATES (IMPROVED)
# ============================================================================

# NEW: System instructions for stronger enforcement
SYSTEM_INSTRUCTIONS = {
    'en': """You are a code analysis assistant. You MUST respond ONLY in English.
All explanations, descriptions, and messages must be in English.
Keep technical terms and code in English.""",
    
    'ur': """آپ کوڈ تجزیہ کے معاون ہیں۔ آپ کو صرف اردو میں جواب دینا ہے۔
تمام وضاحتیں، تفصیلات، اور پیغامات اردو میں ہونے چاہئیں۔
تکنیکی اصطلاحات اور کوڈ کو انگریزی میں رکھیں۔"""
}

# Original + Enhanced instructions
LANGUAGE_INSTRUCTIONS = {
    'en': {
        'instruction': 'Respond in English.',
        'json_note': 'Return ONLY valid JSON with all text in English.',
        # NEW: Stronger reminders
        'strong_reminder': """CRITICAL: Respond in ENGLISH ONLY.
- All descriptions must be in English
- All messages must be in English  
- All explanations must be in English
- Keep code and technical terms in English"""
    },
    'ur': {
        'instruction': 'جواب اردو میں دیں۔ تکنیکی اصطلاحات انگریزی میں رکھیں۔',
        'json_note': 'صرف درست JSON واپس کریں جس میں تمام متن اردو میں ہو۔ تکنیکی اصطلاحات اور کوڈ انگریزی میں رکھیں۔',
        # NEW: Stronger reminders
        'strong_reminder': """اہم: صرف اردو میں جواب دیں۔
- تمام تفصیلات اردو میں ہونی چاہئیں
- تمام پیغامات اردو میں ہونے چاہئیں
- تمام وضاحتیں اردو میں ہونی چاہئیں
- کوڈ اور تکنیکی اصطلاحات انگریزی میں رکھیں"""
    }
}

def get_language_instruction(language_code: str = 'en') -> str:
    """Get language instruction for prompts"""
    return LANGUAGE_INSTRUCTIONS.get(language_code, LANGUAGE_INSTRUCTIONS['en'])['instruction']

def get_json_instruction(language_code: str = 'en') -> str:
    """Get JSON instruction for prompts"""
    return LANGUAGE_INSTRUCTIONS.get(language_code, LANGUAGE_INSTRUCTIONS['en'])['json_note']

# NEW: Get system instruction
def get_system_instruction(language_code: str = 'en') -> str:
    """Get system instruction for the model"""
    return SYSTEM_INSTRUCTIONS.get(language_code, SYSTEM_INSTRUCTIONS['en'])

# NEW: Get strong reminder
def get_strong_reminder(language_code: str = 'en') -> str:
    """Get strong language reminder"""
    return LANGUAGE_INSTRUCTIONS.get(language_code, LANGUAGE_INSTRUCTIONS['en'])['strong_reminder']


# ============================================================================
# NEW: IMPROVED API CALL WRAPPER
# ============================================================================

def _call_gemini_with_language_enforcement(
    gemini_client,
    prompt: str,
    output_language: str = 'en',
    model: str = "gemini-2.0-flash-exp"
):
    """
    NEW: Call Gemini with strong language enforcement
    
    This wrapper adds:
    1. System instructions
    2. Language reminders
    3. Lower temperature for consistency
    """
    try:
        # Get system instruction
        system_instruction = get_system_instruction(output_language)
        
        # Add strong reminder at start of prompt
        strong_reminder = get_strong_reminder(output_language)
        enhanced_prompt = f"{strong_reminder}\n\n{prompt}"
        
        # Call with system instruction and lower temperature
        response = gemini_client.models.generate_content(
            model=model,
            contents=enhanced_prompt,
            config={
                'system_instruction': system_instruction,
                'temperature': 0.3,  # Lower = more consistent
            }
        )
        
        return response
    except Exception as e:
        # Fallback to standard call if system_instruction not supported
        print(f"System instruction not supported, using standard call: {e}")
        return gemini_client.models.generate_content(
            model=model,
            contents=prompt
        )


# ============================================================================
# FEATURE 1: CODE QUALITY ANALYZER (IMPROVED)
# ============================================================================

def analyze_code_quality_comprehensive(
    code: str,
    language: str,
    gemini_client,
    output_language: str = 'en'
) -> Dict[str, Any]:
    """
    Comprehensive code quality analysis using NEW Gemini SDK
    IMPROVED: Now uses system instructions and validation
    
    Args:
        code: Source code to analyze
        language: Programming language (Python, Java, etc.)
        gemini_client: genai.Client instance (NEW SDK)
        output_language: 'en' for English, 'ur' for Urdu
    
    Returns:
        Quality analysis results with scores and issues
    """
    
    if not gemini_client:
        return _fallback_quality_analysis(code, language, output_language)
    
    try:
        lang_instruction = get_language_instruction(output_language)
        json_instruction = get_json_instruction(output_language)
        lang_name = "English" if output_language == 'en' else "اردو (Urdu)"
        
        prompt = f"""{lang_instruction}

Analyze this {language} code comprehensively for quality metrics.

IMPORTANT: Respond in {lang_name}. {json_instruction}

Return JSON with this exact structure:
{{
  "overall_score": <int 0-100>,
  "maintainability_score": <int 0-100>,
  "reliability_score": <int 0-100>,
  "security_score": <int 0-100>,
  "readability_score": <int 0-100>,
  "complexity_analysis": {{
    "cyclomatic_complexity": <int>,
    "cognitive_complexity": <int>,
    "nesting_depth": <int>,
    "complexity_rating": "<Low|Medium|High>"
  }},
  "issues": [
    {{
      "severity": "<high|medium|low>",
      "message": "<description in {'Urdu' if output_language == 'ur' else 'English'}>",
      "line": <int>,
      "category": "<maintainability|reliability|security|readability>"
    }}
  ],
  "suggestions": [
    "<improvement suggestion in {'Urdu' if output_language == 'ur' else 'English'}>"
  ],
  "code_smells": [
    {{
      "type": "<smell type>",
      "description": "<description in {'Urdu' if output_language == 'ur' else 'English'}>",
      "line": <int>
    }}
  ],
  "best_practices_violations": [
    {{
      "rule": "<rule name>",
      "description": "<description in {'Urdu' if output_language == 'ur' else 'English'}>",
      "line": <int>
    }}
  ]
}}

CODE:
{code[:8000]}"""

        # IMPROVED: Use new wrapper with system instructions
        response = _call_gemini_with_language_enforcement(
            gemini_client, prompt, output_language
        )
        
        result = _extract_json_from_response(response)
        
        if result:
            # IMPROVED: Validate language
            if _validate_language(result, output_language):
                return result
            else:
                print(f"Warning: Language validation failed, using fallback")
                
        return _fallback_quality_analysis(code, language, output_language)
            
    except Exception as e:
        print(f"Gemini quality analysis error: {e}")
        return _fallback_quality_analysis(code, language, output_language)


def _fallback_quality_analysis(code: str, language: str, output_language: str = 'en') -> Dict[str, Any]:
    """Fallback analysis when Gemini is unavailable"""
    lines = len([l for l in code.splitlines() if l.strip()])
    complexity = min(100, len(re.findall(r'\b(if|elif|else|for|while|switch|case)\b', code)) * 5)
    
    messages = {
        'en': {
            'requires_api': 'Code analysis requires Gemini API',
            'enable_api': 'Enable Gemini API for detailed analysis',
            'add_docs': 'Add more documentation',
            'refactor': 'Consider refactoring complex functions'
        },
        'ur': {
            'requires_api': 'کوڈ کا تجزیہ Gemini API کی ضرورت ہے',
            'enable_api': 'تفصیلی تجزیہ کے لیے Gemini API فعال کریں',
            'add_docs': 'مزید دستاویزات شامل کریں',
            'refactor': 'پیچیدہ فنکشنز کو دوبارہ ترتیب دینے پر غور کریں'
        }
    }
    
    msg = messages.get(output_language, messages['en'])
    
    return {
        "overall_score": 70,
        "maintainability_score": 75,
        "reliability_score": 70,
        "security_score": 65,
        "readability_score": 70,
        "complexity_analysis": {
            "cyclomatic_complexity": complexity // 5,
            "cognitive_complexity": complexity // 4,
            "nesting_depth": 3,
            "complexity_rating": "Medium"
        },
        "issues": [
            {
                "severity": "medium",
                "message": msg['requires_api'],
                "line": 1,
                "category": "general"
            }
        ],
        "suggestions": [
            msg['enable_api'],
            msg['add_docs'],
            msg['refactor']
        ],
        "code_smells": [],
        "best_practices_violations": []
    }


# ============================================================================
# FEATURE 2: BUG DETECTOR & TEST GENERATOR (IMPROVED)
# ============================================================================

def detect_bugs_and_generate_tests(
    code: str,
    language: str,
    gemini_client,
    output_language: str = 'en'
) -> Dict[str, Any]:
    """
    Detect bugs and generate comprehensive unit tests using NEW SDK
    IMPROVED: Now uses system instructions and validation
    
    Args:
        code: Source code to analyze
        language: Programming language
        gemini_client: genai.Client instance
        output_language: 'en' for English, 'ur' for Urdu
    """
    
    if not gemini_client:
        return _fallback_bug_detection(code, language, output_language)
    
    try:
        lang_instruction = get_language_instruction(output_language)
        json_instruction = get_json_instruction(output_language)
        lang_name = "English" if output_language == 'en' else "اردو (Urdu)"
        
        # Step 1: Detect bugs
        bug_prompt = f"""{lang_instruction}

Analyze this {language} code for bugs, errors, and potential issues.

IMPORTANT: Respond in {lang_name}. {json_instruction}

Return JSON:
{{
  "bugs": [
    {{
      "type": "<bug type>",
      "severity": "<critical|high|medium|low>",
      "line": <int>,
      "description": "<detailed description in {'Urdu' if output_language == 'ur' else 'English'}>",
      "impact": "<potential impact in {'Urdu' if output_language == 'ur' else 'English'}>",
      "fix_suggestion": "<how to fix in {'Urdu' if output_language == 'ur' else 'English'}>"
    }}
  ],
  "potential_runtime_errors": [
    {{
      "type": "<error type>",
      "line": <int>,
      "description": "<description in {'Urdu' if output_language == 'ur' else 'English'}>"
    }}
  ],
  "logic_errors": [
    {{
      "description": "<description in {'Urdu' if output_language == 'ur' else 'English'}>",
      "line": <int>
    }}
  ],
  "null_safety_issues": [
    {{
      "description": "<description in {'Urdu' if output_language == 'ur' else 'English'}>",
      "line": <int>
    }}
  ],
  "memory_issues": [
    {{
      "description": "<description in {'Urdu' if output_language == 'ur' else 'English'}>",
      "line": <int>
    }}
  ]
}}

CODE:
{code[:7000]}"""

        # IMPROVED: Use new wrapper
        bug_response = _call_gemini_with_language_enforcement(
            gemini_client, bug_prompt, output_language
        )
        bug_results = _extract_json_from_response(bug_response)
        
        # Step 2: Generate tests (always in English for code)
        test_framework = _get_test_framework(language)
        test_prompt = f"""Generate comprehensive unit tests for this {language} code using {test_framework}.

Include:
- Test for normal cases
- Edge cases
- Error conditions
- Boundary conditions

Return ONLY valid JSON:
{{
  "test_code": "<complete test code>",
  "test_count": <int>,
  "coverage_areas": [
    "<area covered>"
  ],
  "test_descriptions": [
    {{
      "test_name": "<name>",
      "description": "<what it tests>",
      "importance": "<high|medium|low>"
    }}
  ]
}}

CODE:
{code[:6000]}"""

        # Tests always in English
        test_response = _call_gemini_with_language_enforcement(
            gemini_client, test_prompt, 'en'
        )
        test_results = _extract_json_from_response(test_response)
        
        # Combine results
        all_bugs = []
        if bug_results:
            all_bugs.extend(bug_results.get('bugs', []))
            all_bugs.extend([
                {"type": "Runtime Error", "severity": "high", **err}
                for err in bug_results.get('potential_runtime_errors', [])
            ])
            all_bugs.extend([
                {"type": "Logic Error", "severity": "medium", **err}
                for err in bug_results.get('logic_errors', [])
            ])
        
        return {
            "bugs_found": len(all_bugs),
            "bugs": all_bugs,
            "tests_generated": test_results.get('test_count', 0) if test_results else 0,
            "test_code": test_results.get('test_code', '') if test_results else '',
            "coverage_estimate": min(85, len(all_bugs) * 5 + 50),
            "test_descriptions": test_results.get('test_descriptions', []) if test_results else [],
            "coverage_areas": test_results.get('coverage_areas', []) if test_results else [],
            "critical_issues": [b for b in all_bugs if b.get('severity') in ['critical', 'high']],
            "bug_categories": bug_results if bug_results else {}
        }
        
    except Exception as e:
        print(f"Bug detection error: {e}")
        return _fallback_bug_detection(code, language, output_language)


def _fallback_bug_detection(code: str, language: str, output_language: str = 'en') -> Dict[str, Any]:
    """Fallback bug detection"""
    messages = {
        'en': {
            'null_detected': 'Potential null reference detected',
            'may_cause': 'May cause runtime errors',
            'add_checks': 'Add null checks',
            'tests_placeholder': f'# {language} tests would be generated with Gemini API'
        },
        'ur': {
            'null_detected': 'ممکنہ null حوالہ پایا گیا',
            'may_cause': 'رن ٹائم errors کا سبب بن سکتا ہے',
            'add_checks': 'null چیک شامل کریں',
            'tests_placeholder': f'# {language} ٹیسٹس Gemini API کے ساتھ تیار کیے جائیں گے'
        }
    }
    
    msg = messages.get(output_language, messages['en'])
    basic_bugs = []
    
    if 'null' in code.lower() or 'none' in code.lower():
        basic_bugs.append({
            "type": "Null Safety",
            "severity": "medium",
            "line": 0,
            "description": msg['null_detected'],
            "impact": msg['may_cause'],
            "fix_suggestion": msg['add_checks']
        })
    
    return {
        "bugs_found": len(basic_bugs),
        "bugs": basic_bugs,
        "tests_generated": 0,
        "test_code": msg['tests_placeholder'],
        "coverage_estimate": 0,
        "test_descriptions": [],
        "coverage_areas": [],
        "critical_issues": [],
        "bug_categories": {}
    }


def _get_test_framework(language: str) -> str:
    """Get appropriate test framework for language"""
    frameworks = {
        "Python": "pytest",
        "Java": "JUnit 5",
        "JavaScript": "Jest",
        "TypeScript": "Jest",
        "C++": "Google Test",
        "C#": "NUnit",
        "Go": "testing package",
    }
    return frameworks.get(language, "appropriate testing framework")


# ============================================================================
# FEATURE 3: DOCUMENTATION GENERATOR (IMPROVED)
# ============================================================================

def generate_comprehensive_documentation(
    code: str,
    language: str,
    gemini_client,
    include_urdu: bool = True,
    primary_language: str = 'en'
) -> Dict[str, Any]:
    """
    Generate comprehensive documentation using NEW SDK
    IMPROVED: Now uses system instructions
    
    Args:
        code: Source code
        language: Programming language
        gemini_client: genai.Client instance
        include_urdu: Whether to generate Urdu documentation
        primary_language: Primary output language ('en' or 'ur')
    """
    
    if not gemini_client:
        return _fallback_documentation(code, language, primary_language)
    
    try:
        # Generate documentation in primary language
        lang_instruction = get_language_instruction(primary_language)
        lang_name = "English" if primary_language == 'en' else "اردو (Urdu)"
        
        doc_prompt = f"""{lang_instruction}

Generate comprehensive API documentation for this {language} code in Markdown format.

IMPORTANT: Respond in {lang_name}.

Include:
1. Overview/Introduction
2. Installation/Setup (if applicable)
3. API Reference (all functions/classes/methods)
4. Usage Examples
5. Parameters and Return Values
6. Error Handling
7. Best Practices

Keep code snippets and technical terms in English.

Return ONLY valid JSON:
{{
  "documentation": "<complete markdown documentation in {'Urdu' if primary_language == 'ur' else 'English'}>",
  "api_reference": [
    {{
      "name": "<function/class name>",
      "type": "<function|class|method>",
      "description": "<description in {'Urdu' if primary_language == 'ur' else 'English'}>",
      "parameters": [
        {{
          "name": "<param name>",
          "type": "<type>",
          "description": "<description in {'Urdu' if primary_language == 'ur' else 'English'}>",
          "required": <true|false>
        }}
      ],
      "returns": {{
        "type": "<type>",
        "description": "<description in {'Urdu' if primary_language == 'ur' else 'English'}>"
      }},
      "examples": [
        "<code example>"
      ]
    }}
  ],
  "usage_examples": [
    {{
      "title": "<example title in {'Urdu' if primary_language == 'ur' else 'English'}>",
      "code": "<code>",
      "description": "<description in {'Urdu' if primary_language == 'ur' else 'English'}>"
    }}
  ],
  "completeness_score": <int 0-100>
}}

CODE:
{code[:8000]}"""

        # IMPROVED: Use new wrapper
        response = _call_gemini_with_language_enforcement(
            gemini_client, doc_prompt, primary_language
        )
        doc_results = _extract_json_from_response(response)
        
        result = {
            "documentation_english": "",
            "documentation_urdu": "",
            "api_reference": doc_results.get('api_reference', []) if doc_results else [],
            "usage_examples": doc_results.get('usage_examples', []) if doc_results else [],
            "completeness_score": doc_results.get('completeness_score', 0) if doc_results else 0,
            "sections_generated": []
        }
        
        # Assign to correct language field
        if primary_language == 'en':
            result["documentation_english"] = doc_results.get('documentation', '') if doc_results else ''
            
            # Generate Urdu if requested
            if include_urdu and doc_results:
                urdu_prompt = f"""اس تکنیکی دستاویزات کا اردو میں ترجمہ کریں۔ کوڈ snippets اور تکنیکی اصطلاحات کو انگریزی میں رکھیں۔ Markdown فارمیٹنگ برقرار رکھیں۔

Documentation to translate:
{doc_results.get('documentation', '')[:5000]}

صرف ترجمہ شدہ اردو دستاویزات markdown format میں واپس کریں۔"""

                urdu_response = _call_gemini_with_language_enforcement(
                    gemini_client, urdu_prompt, 'ur'
                )
                result["documentation_urdu"] = urdu_response.text if hasattr(urdu_response, 'text') else ""
        else:
            # Primary language is Urdu
            result["documentation_urdu"] = doc_results.get('documentation', '') if doc_results else ''
            
            # Generate English version
            if doc_results:
                english_prompt = f"""Translate this technical documentation to English. Keep code snippets as is. Maintain markdown formatting.

Documentation to translate:
{doc_results.get('documentation', '')[:5000]}

Return ONLY the translated English documentation in markdown format."""

                english_response = _call_gemini_with_language_enforcement(
                    gemini_client, english_prompt, 'en'
                )
                result["documentation_english"] = english_response.text if hasattr(english_response, 'text') else ""
        
        return result
        
    except Exception as e:
        print(f"Documentation generation error: {e}")
        return _fallback_documentation(code, language, primary_language)


def _fallback_documentation(code: str, language: str, output_language: str = 'en') -> Dict[str, Any]:
    """Fallback documentation generation"""
    
    templates = {
        'en': f"# {language} Code Documentation\n\nGenerate with Gemini API for comprehensive documentation.",
        'ur': f"# {language} کوڈ دستاویزات\n\nمکمل دستاویزات کے لیے Gemini API استعمال کریں۔"
    }
    
    if output_language == 'en':
        return {
            "documentation_english": templates['en'],
            "documentation_urdu": "",
            "api_reference": [],
            "usage_examples": [],
            "completeness_score": 0,
            "sections_generated": []
        }
    else:
        return {
            "documentation_english": "",
            "documentation_urdu": templates['ur'],
            "api_reference": [],
            "usage_examples": [],
            "completeness_score": 0,
            "sections_generated": []
        }


# ============================================================================
# FEATURE 4: README GENERATOR (IMPROVED)
# ============================================================================

def generate_readme(
    code: str,
    language: str,
    filename: str,
    gemini_client,
    project_name: str = None,
    output_language: str = 'en'
) -> Dict[str, Any]:
    """
    Generate comprehensive README.md using NEW SDK
    IMPROVED: Now uses system instructions
    
    Args:
        code: Source code
        language: Programming language
        filename: File name
        gemini_client: genai.Client instance
        project_name: Optional project name
        output_language: 'en' for English, 'ur' for Urdu
    """
    
    if not gemini_client:
        return _fallback_readme(filename, language, output_language)
    
    try:
        lang_instruction = get_language_instruction(output_language)
        lang_name = "English" if output_language == 'en' else "اردو (Urdu)"
        
        prompt = f"""{lang_instruction}

Generate a comprehensive README.md for this {language} project.

IMPORTANT: Respond in {lang_name}.

File: {filename}
Project Name: {project_name or filename}

Include these sections:
1. Project Title with description
2. Features (extract from code)
3. Installation Instructions
4. Usage Examples
5. API Documentation
6. Requirements/Dependencies
7. Configuration (if applicable)
8. Contributing Guidelines
9. License
10. Contact/Support

Keep code examples in English. Write descriptions in {'Urdu' if output_language == 'ur' else 'English'}.

Return ONLY valid JSON:
{{
  "readme_content": "<complete README.md content in markdown>",
  "badges": [
    {{
      "name": "<badge name>",
      "markdown": "<badge markdown>",
      "url": "<badge url>"
    }}
  ],
  "sections_included": [
    "<section name>"
  ],
  "features_extracted": [
    "<feature description in {'Urdu' if output_language == 'ur' else 'English'}>"
  ],
  "dependencies_detected": [
    "<dependency>"
  ],
  "suggested_license": "<license type>"
}}

CODE:
{code[:8000]}"""

        # IMPROVED: Use new wrapper
        response = _call_gemini_with_language_enforcement(
            gemini_client, prompt, output_language
        )
        result = _extract_json_from_response(response)
        
        if result:
            return {
                "readme_content": result.get('readme_content', ''),
                "badges": result.get('badges', []),
                "sections_included": result.get('sections_included', []),
                "features": result.get('features_extracted', []),
                "dependencies": result.get('dependencies_detected', []),
                "license": result.get('suggested_license', 'MIT')
            }
        else:
            return _fallback_readme(filename, language, output_language)
            
    except Exception as e:
        print(f"README generation error: {e}")
        return _fallback_readme(filename, language, output_language)


def _fallback_readme(filename: str, language: str, output_language: str = 'en') -> Dict[str, Any]:
    """Fallback README generation"""
    
    templates = {
        'en': f"""# {filename}

A {language} project.

## Installation

```bash
# Add installation instructions
```

## Usage

```{language.lower()}
# Add usage examples
```

## Features

- Feature 1
- Feature 2
- Feature 3

## License

MIT License
""",
        'ur': f"""# {filename}

ایک {language} پروجیکٹ۔

## انسٹالیشن

```bash
# انسٹالیشن کی ہدایات شامل کریں
```

## استعمال

```{language.lower()}
# استعمال کی مثالیں شامل کریں
```

## خصوصیات

- خصوصیت 1
- خصوصیت 2
- خصوصیت 3

## لائسنس

MIT License
"""
    }
    
    sections = {
        'en': ["Title", "Installation", "Usage", "Features", "License"],
        'ur': ["عنوان", "انسٹالیشن", "استعمال", "خصوصیات", "لائسنس"]
    }
    
    return {
        "readme_content": templates.get(output_language, templates['en']),
        "badges": [],
        "sections_included": sections.get(output_language, sections['en']),
        "features": [],
        "dependencies": [],
        "license": "MIT"
    }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def _extract_json_from_response(response) -> Optional[Dict]:
    """Extract and parse JSON from NEW Gemini SDK response"""
    try:
        # NEW SDK: response.text contains the generated text
        text = response.text if hasattr(response, 'text') else str(response)
        
        if not text:
            return None
        
        # Clean markdown code fences
        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines)
        
        # Try to parse JSON
        return json.loads(text)
        
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Response text: {text[:200] if 'text' in locals() else 'N/A'}")
        return None
    except Exception as e:
        print(f"Response extraction error: {e}")
        return None


# NEW: Language validation function
def _validate_language(response_dict: Dict, expected_language: str) -> bool:
    """
    Validate if response is in expected language
    Returns True if language seems correct
    """
    if not response_dict:
        return False
    
    # Sample some text from response
    sample_texts = []
    
    def extract_text(obj, depth=0):
        if depth > 3:  # Limit recursion depth
            return
        if isinstance(obj, str) and len(obj) > 10:  # Only meaningful text
            sample_texts.append(obj)
        elif isinstance(obj, dict):
            for v in obj.values():
                extract_text(v, depth + 1)
                if len(sample_texts) >= 5:
                    return
        elif isinstance(obj, list):
            for item in obj:
                extract_text(item, depth + 1)
                if len(sample_texts) >= 5:
                    return
    
    extract_text(response_dict)
    
    if not sample_texts:
        return True  # No text to validate
    
    # Check for language markers
    if expected_language == 'ur':
        # Check for Urdu characters (Arabic script Unicode range)
        urdu_pattern = re.compile(r'[\u0600-\u06FF]')
        urdu_count = sum(1 for text in sample_texts if urdu_pattern.search(text))
        # At least 60% should have Urdu characters
        return urdu_count >= len(sample_texts) * 0.6
    else:
        # Check for English (absence of Urdu characters in main text)
        urdu_pattern = re.compile(r'[\u0600-\u06FF]')
        english_count = sum(1 for text in sample_texts if not urdu_pattern.search(text))
        # At least 80% should be English-only
        return english_count >= len(sample_texts) * 0.8


# ============================================================================
# MAIN UNIFIED ANALYSIS FUNCTION (BILINGUAL)
# ============================================================================

def analyze_code_all_features(
    code: str,
    language: str,
    filename: str,
    gemini_client,
    features: List[str] = None,
    output_language: str = 'en'
) -> Dict[str, Any]:
    """
    Run all analysis features at once using NEW SDK
    
    Args:
        code: Source code
        language: Programming language
        filename: File name
        gemini_client: genai.Client instance
        features: List of features to run
        output_language: 'en' or 'ur'
    """
    
    if features is None:
        features = ['quality', 'bugs', 'docs', 'readme']
    
    results = {
        "filename": filename,
        "language": language,
        "analysis_timestamp": None
    }
    
    if 'quality' in features:
        print(f"Running quality analysis in {output_language}...")
        results['quality_analysis'] = analyze_code_quality_comprehensive(
            code, language, gemini_client, output_language
        )
    
    if 'bugs' in features:
        print(f"Running bug detection in {output_language}...")
        results['bug_detection'] = detect_bugs_and_generate_tests(
            code, language, gemini_client, output_language
        )
    
    if 'docs' in features:
        print(f"Generating documentation in {output_language}...")
        results['documentation'] = generate_comprehensive_documentation(
            code, language, gemini_client, 
            include_urdu=(output_language == 'ur'), 
            primary_language=output_language
        )
    
    if 'readme' in features:
        print(f"Generating README in {output_language}...")
        results['readme'] = generate_readme(
            code, language, filename, gemini_client, 
            output_language=output_language
        )
    
    return results
