"""
Comprehensive PDF Report Generator for CodeAI Pakistan
Updated for NEW Google GenAI SDK compatibility
Place at: backend/utils/comprehensive_pdf.py
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, 
    TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime


def generate_comprehensive_pdf(analysis_results: dict, output_path: str):
    """
    Generate comprehensive PDF report from complete analysis
    Compatible with NEW SDK results structure
    
    Args:
        analysis_results: Dict containing all analysis results
        output_path: Path to save PDF file
    """
    
    doc = SimpleDocTemplate(output_path, pagesize=A4, 
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#8b5cf6'),
        fontName='Helvetica-Bold'
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=15,
        spaceBefore=20,
        textColor=colors.HexColor('#6366f1'),
        fontName='Helvetica-Bold'
    )
    
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=10,
        spaceBefore=15,
        textColor=colors.HexColor('#8b5cf6'),
        fontName='Helvetica-Bold'
    )
    
    # Title
    story.append(Paragraph("CodeAI Pakistan", title_style))
    story.append(Paragraph("Comprehensive Code Analysis Report", styles['Heading2']))
    story.append(Spacer(1, 20))
    
    # File Information
    story.append(Paragraph("File Information", heading2_style))
    
    file_info = [
        ['Property', 'Value'],
        ['Filename', str(analysis_results.get('filename', 'Unknown'))],
        ['Language', str(analysis_results.get('language', 'Unknown'))],
        ['Analysis Date', str(analysis_results.get('timestamp', datetime.now().isoformat()))[:19]],
        ['Report Type', 'Comprehensive Analysis'],
    ]
    
    file_table = Table(file_info, colWidths=[2*inch, 4*inch])
    file_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f3f4f6')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db'))
    ]))
    story.append(file_table)
    story.append(Spacer(1, 30))
    
    # ========== CODE QUALITY ANALYSIS ==========
    if 'quality_analysis' in analysis_results:
        quality = analysis_results['quality_analysis']
        
        story.append(Paragraph("1. Code Quality Analysis", heading2_style))
        story.append(Spacer(1, 10))
        
        # Quality Scores
        score_data = [
            ['Metric', 'Score', 'Status'],
            ['Overall Quality', 
             f"{quality.get('overall_score', 0)}/100", 
             _get_status(quality.get('overall_score', 0))],
            ['Maintainability', 
             f"{quality.get('maintainability_score', 0)}/100", 
             _get_status(quality.get('maintainability_score', 0))],
            ['Reliability', 
             f"{quality.get('reliability_score', 0)}/100", 
             _get_status(quality.get('reliability_score', 0))],
            ['Security', 
             f"{quality.get('security_score', 0)}/100", 
             _get_status(quality.get('security_score', 0))],
            ['Readability', 
             f"{quality.get('readability_score', 0)}/100", 
             _get_status(quality.get('readability_score', 0))],
        ]
        
        score_table = Table(score_data, colWidths=[2*inch, 1.5*inch, 2*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(score_table)
        story.append(Spacer(1, 20))
        
        # Complexity Analysis
        if 'complexity_analysis' in quality:
            story.append(Paragraph("Complexity Metrics", heading3_style))
            complexity = quality['complexity_analysis']
            
            complexity_data = [
                ['Metric', 'Value'],
                ['Cyclomatic Complexity', str(complexity.get('cyclomatic_complexity', 0))],
                ['Cognitive Complexity', str(complexity.get('cognitive_complexity', 0))],
                ['Nesting Depth', str(complexity.get('nesting_depth', 0))],
                ['Complexity Rating', str(complexity.get('complexity_rating', 'Unknown'))],
            ]
            
            complexity_table = Table(complexity_data, colWidths=[3*inch, 2.5*inch])
            complexity_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(complexity_table)
            story.append(Spacer(1, 20))
        
        # Issues Found
        if quality.get('issues'):
            story.append(Paragraph("Issues Detected", heading3_style))
            
            for issue in quality['issues'][:10]:  # Limit to top 10
                severity_color = _get_severity_color(issue.get('severity', 'low'))
                # Escape special characters for PDF
                message = str(issue.get('message', 'No description')).replace('<', '&lt;').replace('>', '&gt;')
                issue_text = (
                    f"<font color='{severity_color}'><b>[{str(issue.get('severity', 'unknown')).upper()}]</b></font> "
                    f"{message} "
                    f"<i>(Line {issue.get('line', 'N/A')})</i>"
                )
                story.append(Paragraph(issue_text, styles['Normal']))
                story.append(Spacer(1, 8))
        
        story.append(PageBreak())
    
    # ========== BUG DETECTION & TESTS ==========
    if 'bug_detection' in analysis_results:
        bugs = analysis_results['bug_detection']
        
        story.append(Paragraph("2. Bug Detection &amp; Test Generation", heading2_style))
        story.append(Spacer(1, 10))
        
        # Summary
        summary_data = [
            ['Metric', 'Count/Value'],
            ['Bugs Found', str(bugs.get('bugs_found', 0))],
            ['Tests Generated', str(bugs.get('tests_generated', 0))],
            ['Coverage Estimate', f"{bugs.get('coverage_estimate', 0)}%"],
            ['Critical Issues', str(len(bugs.get('critical_issues', [])))],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ef4444')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fee2e2'))
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Bug Details
        if bugs.get('bugs'):
            story.append(Paragraph("Detected Bugs", heading3_style))
            
            for bug in bugs['bugs'][:15]:  # Limit to 15 bugs
                severity_color = _get_severity_color(bug.get('severity', 'low'))
                # Escape special characters
                description = str(bug.get('description', 'No description')).replace('<', '&lt;').replace('>', '&gt;')
                fix_suggestion = str(bug.get('fix_suggestion', 'See documentation')).replace('<', '&lt;').replace('>', '&gt;')
                
                bug_text = (
                    f"<font color='{severity_color}'><b>[{str(bug.get('type', 'Unknown'))}]</b></font> "
                    f"{description} "
                    f"<i>(Line {bug.get('line', 'N/A')})</i><br/>"
                    f"<b>Fix:</b> {fix_suggestion}"
                )
                story.append(Paragraph(bug_text, styles['Normal']))
                story.append(Spacer(1, 10))
        
        # Test Coverage Areas
        if bugs.get('coverage_areas'):
            story.append(Paragraph("Test Coverage Areas", heading3_style))
            for area in bugs['coverage_areas'][:10]:
                safe_area = str(area).replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(f"• {safe_area}", styles['Normal']))
            story.append(Spacer(1, 10))
        
        story.append(PageBreak())
    
    # ========== DOCUMENTATION ==========
    if 'documentation' in analysis_results:
        docs = analysis_results['documentation']
        
        story.append(Paragraph("3. Generated Documentation", heading2_style))
        story.append(Spacer(1, 10))
        
        # Documentation metrics
        doc_data = [
            ['Metric', 'Value'],
            ['Completeness Score', f"{docs.get('completeness_score', 0)}%"],
            ['API Functions Documented', str(len(docs.get('api_reference', [])))],
            ['Usage Examples', str(len(docs.get('usage_examples', [])))],
        ]
        
        doc_table = Table(doc_data, colWidths=[3*inch, 2.5*inch])
        doc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(doc_table)
        story.append(Spacer(1, 20))
        
        # API Reference Summary
        if docs.get('api_reference'):
            story.append(Paragraph("API Reference Summary", heading3_style))
            for api in docs['api_reference'][:10]:
                safe_name = str(api.get('name', 'Unknown')).replace('<', '&lt;').replace('>', '&gt;')
                safe_desc = str(api.get('description', 'No description'))[:200].replace('<', '&lt;').replace('>', '&gt;')
                api_text = (
                    f"<b>{safe_name}</b> "
                    f"<i>({api.get('type', 'function')})</i><br/>"
                    f"{safe_desc}"
                )
                story.append(Paragraph(api_text, styles['Normal']))
                story.append(Spacer(1, 8))
        
        story.append(PageBreak())
    
    # ========== README GENERATION ==========
    if 'readme' in analysis_results:
        readme = analysis_results['readme']
        
        story.append(Paragraph("4. README Generation", heading2_style))
        story.append(Spacer(1, 10))
        
        # README Summary
        sections = readme.get('sections_included', [])
        sections_str = ', '.join([str(s) for s in sections]) if sections else 'None'
        
        readme_data = [
            ['Component', 'Details'],
            ['Sections Included', sections_str],
            ['Features Detected', str(len(readme.get('features', [])))],
            ['Dependencies Found', str(len(readme.get('dependencies', [])))],
            ['Suggested License', str(readme.get('license', 'MIT'))],
        ]
        
        readme_table = Table(readme_data, colWidths=[2*inch, 3.5*inch])
        readme_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(readme_table)
        story.append(Spacer(1, 20))
        
        # Features
        if readme.get('features'):
            story.append(Paragraph("Detected Features", heading3_style))
            for feature in readme['features'][:8]:
                safe_feature = str(feature).replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(f"• {safe_feature}", styles['Normal']))
            story.append(Spacer(1, 10))
    
    # ========== RECOMMENDATIONS ==========
    story.append(PageBreak())
    story.append(Paragraph("5. Recommendations", heading2_style))
    story.append(Spacer(1, 10))
    
    recommendations = _generate_recommendations(analysis_results)
    for rec in recommendations:
        safe_rec = str(rec).replace('<', '&lt;').replace('>', '&gt;')
        story.append(Paragraph(f"• {safe_rec}", styles['Normal']))
        story.append(Spacer(1, 8))
    
    # Footer
    story.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph(
        f"Generated by CodeAI Pakistan | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        footer_style
    ))
    
    # Build PDF
    try:
        doc.build(story)
        print(f"✓ PDF generated successfully: {output_path}")
    except Exception as e:
        print(f"✗ PDF generation error: {e}")
        raise


def _get_status(score: int) -> str:
    """Get status text based on score"""
    try:
        score = int(score)
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Needs Improvement"
    except:
        return "Unknown"


def _get_severity_color(severity: str) -> str:
    """Get color for severity level"""
    colors_map = {
        'critical': '#dc2626',
        'high': '#ef4444',
        'medium': '#f59e0b',
        'low': '#6b7280'
    }
    return colors_map.get(str(severity).lower(), '#6b7280')


def _generate_recommendations(analysis_results: dict) -> list:
    """Generate recommendations based on analysis"""
    recommendations = []
    
    # Quality recommendations
    if 'quality_analysis' in analysis_results:
        quality = analysis_results['quality_analysis']
        overall = quality.get('overall_score', 0)
        
        try:
            overall = int(overall)
            if overall < 70:
                recommendations.append(
                    "Consider refactoring code to improve overall quality score"
                )
            
            if int(quality.get('maintainability_score', 0)) < 70:
                recommendations.append(
                    "Improve code maintainability by reducing complexity and adding comments"
                )
            
            if int(quality.get('security_score', 0)) < 70:
                recommendations.append(
                    "Address security concerns to improve security posture"
                )
        except:
            pass
    
    # Bug recommendations
    if 'bug_detection' in analysis_results:
        bugs = analysis_results['bug_detection']
        
        try:
            bugs_found = int(bugs.get('bugs_found', 0))
            if bugs_found > 5:
                recommendations.append(
                    f"Fix {bugs_found} detected bugs before deployment"
                )
            
            coverage = int(bugs.get('coverage_estimate', 0))
            if coverage < 70:
                recommendations.append(
                    "Increase test coverage to at least 70% for production code"
                )
            
            critical_issues = bugs.get('critical_issues', [])
            if critical_issues and len(critical_issues) > 0:
                recommendations.append(
                    f"Immediately address {len(critical_issues)} critical security/bug issues"
                )
        except:
            pass
    
    # Documentation recommendations
    if 'documentation' in analysis_results:
        docs = analysis_results['documentation']
        
        try:
            completeness = int(docs.get('completeness_score', 0))
            if completeness < 80:
                recommendations.append(
                    "Enhance documentation coverage for better code maintainability"
                )
        except:
            pass
    
    # General recommendations
    recommendations.extend([
        "Regularly run code analysis to maintain code quality",
        "Follow language-specific best practices and style guides",
        "Implement continuous integration with automated testing",
        "Keep dependencies up to date for security patches"
    ])
    
    return recommendations