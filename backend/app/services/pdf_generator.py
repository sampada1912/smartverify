import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors


def _draw_header(c, title, subtitle):
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor("#1e3a8a")) # Deep Navy
    c.drawCentredString(300, 750, title)
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#475569"))
    c.drawCentredString(300, 735, subtitle)
    
    c.setStrokeColor(colors.HexColor("#cbd5e1"))
    c.setLineWidth(1)
    c.line(50, 725, 550, 725)
    
    # Prototype Notice
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(colors.HexColor("#94a3b8"))
    c.drawString(50, 715, "PROTOTYPE DEMONSTRATION RECORD - NOT AN OFFICIAL AICTE ISSUANCE")


def generate_previous_approval_pdf(filepath, institution_name, pid, intake, course, academic_year="2025-26", file_no="AICTE/EOA/2025/1-1092837482"):
    c = canvas.Canvas(filepath, pagesize=letter)
    _draw_header(c, "ALL INDIA COUNCIL FOR TECHNICAL EDUCATION", "Extension of Approval (EoA) Report")
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.black)
    c.drawString(50, 680, f"File No: {file_no}")
    c.drawString(400, 680, "Date: 15/07/2025")
    
    c.setFont("Helvetica", 10)
    y = 650
    lines = [
        f"Permanent Institute Id: {pid}",
        f"Name of the Institution: {institution_name}",
        f"Academic Year: {academic_year}",
        f"Programme: ENGINEERING_AND_TECHNOLOGY",
        f"Course: {course}",
        f"Approved Intake: {intake}",
        "Affiliating University: State Technical University",
        "Approval Status: Granted under Approval Process Handbook Regulations."
    ]
    for line in lines:
        c.drawString(50, y, line)
        y -= 22
        
    c.setStrokeColor(colors.HexColor("#e2e8f0"))
    c.rect(50, y - 50, 500, 40)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(60, y - 30, "Security Verification:")
    c.setFont("Helvetica", 8)
    c.drawString(60, y - 42, f"Digital Token: {file_no}-VALID-SEAL | Authorized Signatory, AICTE Western/Northern Regional Office")
    
    c.save()


def generate_affidavit_pdf(filepath, institution_name, pid, deponent_name="Dr. R. K. Sharma", stamp_no="STAMP-UP-2026-88192", date_str="10/01/2026"):
    c = canvas.Canvas(filepath, pagesize=letter)
    _draw_header(c, "NON-JUDICIAL STAMP PAPER - GOVERNMENT OF INDIA", "FORMAT-1 AFFIDAVIT / UNDERTAKING")
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.black)
    c.drawString(50, 680, f"Stamp Certificate No: {stamp_no}")
    c.drawString(400, 680, f"Date of Issue: {date_str}")
    
    c.setFont("Helvetica", 10)
    y = 640
    lines = [
        f"Permanent Institute Id: {pid}",
        f"Name of the Institution: {institution_name}",
        f"I, {deponent_name}, solemnly affirm and state on oath as under:",
        "1. That the institution strictly complies with all faculty, land, and building norms prescribed.",
        "2. That no capitation fee has been charged, and all submitted certificates are authentic.",
        "3. That all laboratories, library titles, and instructional facilities are fully operational."
    ]
    for line in lines:
        c.drawString(50, y, line)
        y -= 25
        
    c.setFont("Helvetica-Bold", 10)
    c.drawString(400, y - 40, "DEPONENT")
    c.setFont("Helvetica", 8)
    c.drawString(50, y - 60, "Sworn and verified before me, Public Notary, on this day.")
    c.save()


def generate_faculty_list_pdf(filepath, institution_name, pid, total_faculty=36, phd_faculty=12):
    c = canvas.Canvas(filepath, pagesize=letter)
    _draw_header(c, "INSTITUTION FACULTY DETAILS & CADRE RATIO", f"Cadre Ratio Audit Report - Academic Year 2026-27")
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.black)
    c.drawString(50, 680, f"Permanent Institute Id: {pid}")
    c.drawString(400, 680, "Date: 12/01/2026")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, 650, f"Name of the Institution: {institution_name}")
    c.drawString(50, 630, f"Total Faculty Count: {total_faculty}")
    c.drawString(50, 610, f"Ph.D Faculty Count: {phd_faculty}")
    c.drawString(50, 590, "Cadre Distribution: Professor: 4, Associate Professor: 8, Assistant Professor: 24")
    c.drawString(50, 570, "Faculty Student Ratio: Maintained as per prescribed norms (1:20)")
    
    # Draw sample table
    c.setStrokeColor(colors.HexColor("#94a3b8"))
    c.setLineWidth(0.5)
    y = 530
    c.line(50, y, 550, y)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(55, y - 15, "S.No")
    c.drawString(90, y - 15, "Faculty Name")
    c.drawString(220, y - 15, "Designation")
    c.drawString(350, y - 15, "Qualification")
    c.drawString(460, y - 15, "Joining Date")
    c.line(50, y - 20, 550, y - 20)
    
    sample_fac = [
        ("1", "Dr. A. Verma", "Professor & HOD", "Ph.D (CSE)", "15/07/2016"),
        ("2", "Dr. S. Mukherjee", "Associate Professor", "Ph.D (IT)", "01/08/2018"),
        ("3", "P. R. Nair", "Assistant Professor", "M.Tech (CSE)", "10/01/2021"),
        ("4", "K. L. Sharma", "Assistant Professor", "M.Tech (AI)", "05/02/2022"),
    ]
    row_y = y - 35
    c.setFont("Helvetica", 9)
    for row in sample_fac:
        c.drawString(55, row_y, row[0])
        c.drawString(90, row_y, row[1])
        c.drawString(220, row_y, row[2])
        c.drawString(350, row_y, row[3])
        c.drawString(460, row_y, row[4])
        row_y -= 20
        
    c.drawString(50, row_y - 20, f"... and {total_faculty - len(sample_fac)} other verified faculty members.")
    c.save()


def generate_noc_pdf(filepath, institution_name, pid, state_name="Uttar Pradesh", cert_no="NOC-2025-99882", issue_date="20/06/2025", valid_till="31/07/2027"):
    c = canvas.Canvas(filepath, pagesize=letter)
    _draw_header(c, f"GOVERNMENT OF {state_name.upper()}", "DIRECTORATE OF TECHNICAL EDUCATION - NO OBJECTION CERTIFICATE")
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.black)
    c.drawString(50, 680, f"Certificate No: {cert_no}")
    c.drawString(400, 680, f"Date of Issue: {issue_date}")
    
    c.setFont("Helvetica", 10)
    y = 640
    lines = [
        f"The State Government has No Objection to the Extension of Approval for:",
        f"Institution ID: {pid}",
        f"Name of the Institution: {institution_name}",
        f"Valid up to: {valid_till}",
        "This NOC is issued under state regulatory powers for the academic year 2026-27."
    ]
    for line in lines:
        c.drawString(50, y, line)
        y -= 25
        
    c.drawString(350, y - 30, "Director of Technical Education")
    c.save()


def generate_accreditation_pdf(filepath, institution_name, pid, cert_no="NBA-TIER1-4491", valid_till="30/06/2028", tier="Tier-I"):
    c = canvas.Canvas(filepath, pagesize=letter)
    _draw_header(c, "NATIONAL BOARD OF ACCREDITATION", "CERTIFICATE OF ACCREDITATION")
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.black)
    c.drawString(50, 680, f"Certificate No: {cert_no}")
    c.drawString(400, 680, "Date: 01/07/2025")
    
    c.setFont("Helvetica", 10)
    y = 640
    lines = [
        f"This is to certify that the Undergraduate Engineering Programme in Computer Science and Engineering",
        f"offered by {institution_name} (Permanent Institute Id: {pid})",
        f"has been evaluated under Washington Accord {tier} Format and is ACCREDITED.",
        f"Valid up to: {valid_till}",
        "Accreditation status is valid subject to continued compliance with NBA guidelines."
    ]
    for line in lines:
        c.drawString(50, y, line)
        y -= 25
    c.drawString(400, y - 30, "Member Secretary, NBA")
    c.save()


def generate_infrastructure_pdf(filepath, institution_name, pid, land_acres=5.2, built_up_sqm=12500):
    c = canvas.Canvas(filepath, pagesize=letter)
    _draw_header(c, "ARCHITECT & REVENUE INFRASTRUCTURE CERTIFICATE", "Land Area, Built-Up Space, and Instructional Readiness")
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.black)
    c.drawString(50, 680, f"Ref No: ARCH/INFRA/2026/{pid[:6]}")
    c.drawString(400, 680, "Date: 05/01/2026")
    
    c.setFont("Helvetica", 10)
    y = 640
    lines = [
        f"This is to certify that the campus of {institution_name} (Institution ID: {pid}) has been surveyed:",
        f"1. Total Land Area: {land_acres} Acres (Single contiguous piece, unrestricted ownership).",
        f"2. Total Built-up Area: {built_up_sqm:,.0f} sqm.",
        "3. Instructional Area: 6,800 sqm (Classrooms, Tutorial rooms, Computer Center).",
        "4. Administrative & Amenities Area: 3,200 sqm.",
        "5. Fire Safety and Barrier-free Accessibility Certificate: Approved."
    ]
    for line in lines:
        c.drawString(50, y, line)
        y -= 25
    c.drawString(350, y - 30, "Licensed Council Architect (Reg. CA/98/2219)")
    c.save()


def generate_payment_receipt_pdf(filepath, institution_name, pid, txn_id="TXN-AICTE-991823", amount="150000", date_str="14/01/2026"):
    c = canvas.Canvas(filepath, pagesize=letter)
    _draw_header(c, "AICTE PORTAL PAYMENT RECEIPT", "Technical Education Regulatory (TER) Processing Charges")
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.black)
    c.drawString(50, 680, f"Transaction ID: {txn_id}")
    c.drawString(400, 680, f"Date: {date_str}")
    
    c.setFont("Helvetica", 10)
    y = 640
    lines = [
        f"Permanent Institute Id: {pid}",
        f"Name of the Institution: {institution_name}",
        f"Payment Type: Extension of Approval Processing Fee (TER Charges)",
        f"Amount Paid: INR {amount}",
        "Payment Status: SUCCESSFUL",
        "Bank Reference / UTR Number: HDFC000192837482",
        "Receipt digitally generated by AICTE E-Governance Payment Gateway."
    ]
    for line in lines:
        c.drawString(50, y, line)
        y -= 25
    c.save()
