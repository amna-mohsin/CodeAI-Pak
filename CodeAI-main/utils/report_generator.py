"""
PDF report generation for CodeAI Pakistan
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

def generate_pdf_report(report_data: dict, output_path: str):
    """Generate a comprehensive PDF report from analysis data"""
    
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1,  # Center
        textColor=colors.HexColor('#2dd4bf')
    )
    story.append(Paragraph("CodeAI Pakistan - Analysis Report", title_style))
    story.append(Spacer(1, 12))
    
    # File information
    file_info_style = ParagraphStyle(
        'FileInfo',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=6
    )
    story.append(Paragraph(
        f"<b>File:</b> {report_data.get('filename', 'Unknown')}", 
        file_info_style
    ))
    story.append(Paragraph(
        f"<b>Language:</b> {report_data.get('language', 'Unknown')}", 
        file_info_style
    ))
    story.append(Paragraph(
        f"<b>Analysis Date:</b> {report_data.get('timestamp', 'Unknown')}", 
        file_info_style
    ))
    story.append(Spacer(1, 20))
    
    # Scores section
    scores = report_data.get('scores', {})
    story.append(Paragraph("Quality Metrics", styles['Heading2']))
    
    # Create scores table
    score_data = [
        ['Metric', 'Score', 'Status'],
        ['Overall Quality', 
         f"{scores.get('overall', 0)}/100", 
         'High' if scores.get('overall', 0) >= 80 else 'Medium' if scores.get('overall', 0) >= 60 else 'Low'],
        ['Code Coverage', 
         f"{scores.get('estimated_coverage', 0)}%", 
         'Pass' if scores.get('estimated_coverage', 0) >= 70 else 'Fail'],
        ['Complexity', 
         f"{scores.get('complexity', 0)}/100", 
         'Low' if scores.get('complexity', 0) <= 30 else 'Medium' if scores.get('complexity', 0) <= 60 else 'High'],
        ['Quality Level', 
         str(scores.get('quality_level', 'Unknown')), 
         ''],
    ]
    
    # Add Gemini scores if available
    if scores.get('gemini_quality_score'):
        score_data.extend([
            ['AI Quality Score', f"{scores.get('gemini_quality_score', 0)}/100", ''],
            ['Maintainability', f"{scores.get('maintainability_score', 0)}/100", ''],
            ['Readability', f"{scores.get('readability_score', 0)}/100", ''],
            ['Best Practices', f"{scores.get('best_practices_score', 0)}/100", ''],
        ])
    
    score_table = Table(score_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(score_table)
    story.append(Spacer(1, 20))
    
    # Bug Analysis
    bug_analysis = scores.get('bug_analysis', {})
    if bug_analysis:
        story.append(Paragraph("Bug Analysis", styles['Heading2']))
        bug_data = [
            ['Detection Efficiency', f"{bug_analysis.get('detection_efficiency', 0)}%"],
            ['Total Bugs Found', str(bug_analysis.get('total_bugs', 0))],
            ['Severity', str(bug_analysis.get('severity', 'Unknown'))],
        ]
        
        bug_table = Table(bug_data, colWidths=[2*inch, 3*inch])
        bug_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(bug_table)
        story.append(Spacer(1, 20))
    
    # Time Complexity
    time_complexity = scores.get('time_complexity', {})
    if time_complexity:
        story.append(Paragraph("Time Complexity Analysis", styles['Heading2']))
        story.append(Paragraph(
            f"<b>Dominant Complexity:</b> {time_complexity.get('dominant', 'Unknown')}", 
            styles['Normal']
        ))
        story.append(Paragraph(
            f"<b>Confidence:</b> {time_complexity.get('confidence', 0)}%", 
            styles['Normal']
        ))
        story.append(Spacer(1, 20))
    
    # Bug Report
    if report_data.get('bug_report'):
        story.append(Paragraph("Bug Report", styles['Heading2']))
        bug_report_text = report_data.get('bug_report', '')[:1000]
        story.append(Paragraph(bug_report_text, styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Documentation
    if report_data.get('docs'):
        story.append(Paragraph("Generated Documentation", styles['Heading2']))
        docs_text = report_data.get('docs', '')[:1000]
        story.append(Paragraph(docs_text, styles['Normal']))
    
    # Build PDF
    doc.build(story)