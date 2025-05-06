from django.http import HttpResponse, JsonResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
import json
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib.units import inch
import base64
import re
from collections import defaultdict

@csrf_exempt
def create_ats_friendly_resume(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data
            data = json.loads(request.body.decode('utf-8'))
            resume_data = data.get('resume_data', {})
            job_description = data.get('job_description', "")

            # Set up the PDF response
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="resume.pdf"'
            p = canvas.Canvas(response, pagesize=letter)

            # --- ATS-Optimized Styling ---
            styles = getSampleStyleSheet()
            normal = styles['Normal']
            normal.fontName = 'Helvetica'
            normal.fontSize = 11  # Slightly larger for better readability
            normal.leading = 12
            normal.spaceAfter = 6

            bold_style = ParagraphStyle(
                'Bold',
                parent=normal,
                fontName='Helvetica-Bold',
                spaceAfter=6
            )

            section_style = ParagraphStyle(
                'Section',
                parent=normal,
                fontName='Helvetica-Bold',
                fontSize=12,
                spaceAfter=12,
                spaceBefore=12
            )

            # --- Helper functions ---
            def draw_plain_text(canvas_obj, x, y, text, style=normal):
                """Draws plain text on the canvas."""
                para = Paragraph(text, style)
                para.wrapOn(canvas_obj, letter[0] - 2 * inch, letter[1])
                para.drawOn(canvas_obj, x, y - para.height)
                return y - para.height - style.spaceAfter

            def add_section_title(y, title):
                """Adds a plain section title."""
                return draw_plain_text(p, 100, y, title.upper(), section_style)

            def add_bullet_point(y, text):
                """Adds a plain bullet point."""
                return draw_plain_text(p, 120, y, f"• {text}", normal)

            # --- Populate the PDF with ATS-optimized content ---
            y = 750  # Initial vertical position

            # Header with name and contact info
            y = draw_plain_text(p, 100, y, resume_data.get('name', '').upper(), bold_style)
            
            contact_info = f"{resume_data.get('email', '')} | {resume_data.get('phone', '')}"
            if resume_data.get('linkedin'):
                contact_info += f" | LinkedIn: {resume_data['linkedin']}"
            if resume_data.get('portfolio'):
                contact_info += f" | Portfolio: {resume_data['portfolio']}"
            y = draw_plain_text(p, 100, y, contact_info, normal)
            y -= 20

            # Summary/Objective - optimized for keywords
            if resume_data.get('summary'):
                y = add_section_title(y, "PROFESSIONAL SUMMARY")
                summary = resume_data['summary']
                # Ensure summary ends with a period
                if not summary.strip().endswith('.'):
                    summary += '.'
                y = draw_plain_text(p, 100, y, summary, normal)
                y -= 10

            # Core Competencies/Key Skills section
            if resume_data.get('skills'):
                y = add_section_title(y, "CORE COMPETENCIES")
                skills_text = []
                for skill_type, skills in resume_data['skills'].items():
                    skills_text.extend(skills)
                # Group skills in chunks of 3-4 for better readability
                skill_groups = [skills_text[i:i+4] for i in range(0, len(skills_text), 4)]
                for group in skill_groups:
                    y = draw_plain_text(p, 100, y, " • " + " • ".join(group), normal)
                y -= 10

            # Professional Experience - optimized with action verbs
            if resume_data.get('experience'):
                y = add_section_title(y, "PROFESSIONAL EXPERIENCE")
                for exp in resume_data['experience']:
                    title = exp.get('title', '')
                    company = exp.get('company', '')
                    years = exp.get('years', '')
                    location = exp.get('location', '')
                    
                    # Format experience header
                    exp_header = f"{title.upper()}"
                    if company:
                        exp_header += f", {company}"
                    if location:
                        exp_header += f" ({location})"
                    if years:
                        exp_header += f" | {years}"
                    
                    y = draw_plain_text(p, 100, y, exp_header, bold_style)
                    
                    # Format responsibilities with action verbs
                    if exp.get('responsibilities'):
                        for resp in exp.get('responsibilities', []):
                            responsibility = resp.get('responsibility', '')
                            # Ensure responsibility starts with action verb
                            if responsibility and not responsibility[0].isupper():
                                responsibility = responsibility[0].upper() + responsibility[1:]
                            y = add_bullet_point(y, responsibility)
                    y -= 10

            # Education - plain format
            if resume_data.get('education'):
                y = add_section_title(y, "EDUCATION")
                for edu in resume_data['education']:
                    degree = edu.get('degree', '')
                    university = edu.get('university', '')
                    year = edu.get('year', '')
                    gpa = edu.get('gpa', '')
                    
                    edu_text = f"{degree.upper()}"
                    if university:
                        edu_text += f", {university}"
                    if year:
                        edu_text += f" ({year})"
                    if gpa:
                        edu_text += f" | GPA: {gpa}"
                    
                    y = draw_plain_text(p, 100, y, edu_text, bold_style)
                    
                    if edu.get('description'):
                        y = draw_plain_text(p, 100, y, edu['description'], normal)
                    y -= 10

            # Certifications
            if resume_data.get('certifications'):
                y = add_section_title(y, "CERTIFICATIONS")
                for cert in resume_data['certifications']:
                    cert_text = f"{cert.get('name', '').upper()}"
                    if cert.get('year'):
                        cert_text += f" ({cert.get('year')})"
                    if cert.get('issuer'):
                        cert_text += f", {cert.get('issuer')}"
                    y = draw_plain_text(p, 100, y, cert_text, normal)
                y -= 10

            # Projects - focused on technologies and outcomes
            if resume_data.get('projects'):
                y = add_section_title(y, "KEY PROJECTS")
                for proj in resume_data['projects']:
                    y = draw_plain_text(p, 100, y, f"{proj.get('name', '').upper()}", bold_style)
                    if proj.get('description'):
                        y = draw_plain_text(p, 100, y, proj['description'], normal)
                    if proj.get('technologies'):
                        y = draw_plain_text(p, 100, y, 
                                           f"Technologies: {', '.join(proj['technologies'])}", 
                                           normal)
                    y -= 10

            # Calculate ATS Score and detailed feedback
            ats_results = calculate_ats_score_with_feedback(resume_data, job_description)
            ats_score = ats_results['score']
            feedback = ats_results['feedback']
            missing_keywords = ats_results['missing_keywords']
            matched_keywords = ats_results['matched_keywords']

            # Finalize PDF
            p.showPage()
            p.save()
            pdf_bytes = response.getvalue()
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

            return JsonResponse({
                'pdf': pdf_base64,
                'ats_score': ats_score,
                'feedback': feedback,
                'missing_keywords': missing_keywords,
                'matched_keywords': matched_keywords,
                'status': 'success'
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def calculate_ats_score_with_feedback(resume_data, job_description):
    """Calculates ATS score and provides detailed feedback for improvement."""
    if not job_description:
        return {
            'score': 0,
            'feedback': ["No job description provided for ATS scoring."],
            'missing_keywords': [],
            'matched_keywords': []
        }

    # Extract keywords from job description (more sophisticated approach)
    job_text = job_description.lower()
    words = re.findall(r'\b[a-z]{3,}\b', job_text)  # Only words with 3+ letters
    word_freq = defaultdict(int)
    for word in words:
        if len(word) > 2:  # Ignore very short words
            word_freq[word] += 1
    
    # Remove common stop words
    stop_words = {'the', 'and', 'for', 'with', 'this', 'that', 'have', 'has', 'had', 
                 'you', 'your', 'will', 'would', 'should', 'they', 'their', 'them'}
    keywords = {word: count for word, count in word_freq.items() 
               if word not in stop_words and count > 1}
    
    # Also look for phrases (2-3 word sequences)
    phrases = re.findall(r'\b(?:\w+\b\s*){2,3}', job_text)
    phrase_freq = defaultdict(int)
    for phrase in phrases:
        phrase_freq[phrase] += 1
    important_phrases = {phrase: count for phrase, count in phrase_freq.items() 
                        if count > 1 and len(phrase.split()) > 1}

    # Combine keywords and phrases
    all_keywords = list(keywords.keys()) + list(important_phrases.keys())
    
    # Analyze resume content
    resume_text = ""
    
    # Helper function to collect resume text
    def add_to_resume_text(text):
        nonlocal resume_text
        if text:
            resume_text += f" {text.lower()}"
    
    # Process each section of the resume
    add_to_resume_text(resume_data.get('summary'))
    
    if resume_data.get('skills'):
        for skill_type, skills in resume_data['skills'].items():
            add_to_resume_text(" ".join(skills))
    
    if resume_data.get('experience'):
        for exp in resume_data['experience']:
            add_to_resume_text(exp.get('title'))
            add_to_resume_text(exp.get('company'))
            add_to_resume_text(exp.get('description'))
            if exp.get('responsibilities'):
                for resp in exp['responsibilities']:
                    add_to_resume_text(resp.get('responsibility'))
    
    if resume_data.get('education'):
        for edu in resume_data['education']:
            add_to_resume_text(edu.get('degree'))
            add_to_resume_text(edu.get('university'))
            add_to_resume_text(edu.get('description'))
    
    if resume_data.get('projects'):
        for proj in resume_data['projects']:
            add_to_resume_text(proj.get('name'))
            add_to_resume_text(proj.get('description'))
            if proj.get('technologies'):
                add_to_resume_text(" ".join(proj['technologies']))
    
    # Find matches and missing keywords
    matched_keywords = []
    missing_keywords = []
    
    for keyword in all_keywords:
        if keyword in resume_text:
            matched_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)
    
    # Calculate score
    total_keywords = len(all_keywords)
    matched_count = len(matched_keywords)
    score = round((matched_count / total_keywords) * 100) if total_keywords > 0 else 0
    
    # Generate detailed feedback
    feedback = []
    
    # General score feedback
    if score >= 80:
        feedback.append("Excellent! Your resume has strong alignment with the job description.")
    elif score >= 60:
        feedback.append("Good match. Your resume aligns well but could be improved further.")
    elif score >= 40:
        feedback.append("Moderate match. Your resume needs more optimization for this role.")
    else:
        feedback.append("Low match. Significant improvements needed to better align with this role.")
    
    # Section-specific feedback
    if not resume_data.get('summary'):
        feedback.append("Consider adding a professional summary that highlights your most relevant qualifications.")
    elif len(resume_data.get('summary', '').split()) < 20:
        feedback.append("Your summary could be more detailed. Aim for 3-4 sentences highlighting key qualifications.")
    
    if not resume_data.get('skills'):
        feedback.append("Add a skills section with relevant hard and soft skills from the job description.")
    elif len(matched_keywords) < total_keywords * 0.5:
        feedback.append("Your skills section could better match the job requirements. Add more relevant skills.")
    
    if not resume_data.get('experience'):
        feedback.append("No work experience listed. Include relevant experience, even if from internships or projects.")
    else:
        # Check for action verbs in experience descriptions
        action_verbs = {'managed', 'led', 'developed', 'created', 'implemented', 
                       'improved', 'increased', 'reduced', 'optimized', 'designed'}
        has_action_verbs = any(verb in resume_text for verb in action_verbs)
        if not has_action_verbs:
            feedback.append("Use more action verbs in your experience descriptions (e.g., 'managed', 'developed', 'implemented').")
    
    # Missing keywords feedback
    if missing_keywords:
        feedback.append(f"Consider adding these missing keywords: {', '.join(missing_keywords[:10])}" + 
                       ("..." if len(missing_keywords) > 10 else ""))
    
    # Formatting feedback
    feedback.append("Keep your resume format simple and clean for best ATS compatibility.")
    feedback.append("Use standard section headings like 'Professional Experience' and 'Education'.")
    
    return {
        'score': score,
        'feedback': feedback,
        'missing_keywords': missing_keywords,
        'matched_keywords': matched_keywords
    }