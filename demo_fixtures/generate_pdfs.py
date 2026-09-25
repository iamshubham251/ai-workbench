import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_pdf(path, title, lines):
    c = canvas.Canvas(path, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, 750, title)
    
    c.setFont("Helvetica", 12)
    y = 710
    for line in lines:
        c.drawString(72, y, line)
        y -= 20
    
    c.save()

def main():
    out_dir = "C:\\Users\\Shubham\\OneDrive\\Desktop\\ai-workbench\\demo_fixtures"
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. APPROVE CASE
    create_pdf(os.path.join(out_dir, "demo_inspection_approve.pdf"), "Inspection Report: Pipeline Alpha (Approve)", [
        "Date: 2026-09-25",
        "Inspector: John Doe",
        "Subject: Cooling System Valve Alpha",
        "",
        "Findings:",
        "- Visual Inspection: No visible cracks or leaks.",
        "- Pressure reading: 98 PSI.",
        "- Temperature reading: 45 °C.",
        "- Valve seal integrity: Intact.",
        "",
        "Conclusion: Equipment is operating optimally within safe thresholds."
    ])

    create_pdf(os.path.join(out_dir, "demo_sop_approve.pdf"), "SOP: Cooling System Thresholds", [
        "Standard Operating Procedure: Cooling System",
        "",
        "Acceptable Operating Ranges:",
        "1. Pressure: Must be between 90 PSI and 110 PSI.",
        "2. Temperature: Must not exceed 50 °C.",
        "3. Seal Integrity: Must be intact with no leaks.",
        "",
        "If all conditions are met, the equipment is approved for continued operation."
    ])
    
    # 2. REVIEW CASE
    create_pdf(os.path.join(out_dir, "demo_inspection_review.pdf"), "Inspection Report: Generator Beta (Review)", [
        "Date: 2026-09-25",
        "Inspector: Jane Smith",
        "Subject: Backup Generator Beta",
        "",
        "Findings:",
        "- Visual Inspection: Minor surface rust observed on the casing.",
        "- Oil Level: Normal.",
        "- Battery Voltage: Not tested (multimeter unavailable).",
        "- Last maintenance date: Unknown.",
        "",
        "Conclusion: Incomplete data. Recommend further manual inspection."
    ])

    create_pdf(os.path.join(out_dir, "demo_sop_review.pdf"), "SOP: Backup Generator Maintenance", [
        "Standard Operating Procedure: Generator Safety",
        "",
        "Inspection Requirements:",
        "1. Oil Level must be Normal.",
        "2. Battery Voltage must be measured and above 12.5V.",
        "3. If any data point is missing or 'Unknown', the equipment status is undetermined.",
        "",
        "Action: If data is missing, the decision MUST be REVIEW for manual intervention."
    ])
    
    # 3. REJECT CASE
    create_pdf(os.path.join(out_dir, "demo_inspection_reject.pdf"), "Inspection Report: Boiler Gamma (Reject)", [
        "Date: 2026-09-25",
        "Inspector: Bob Johnson",
        "Subject: High-Pressure Boiler Gamma",
        "",
        "Findings:",
        "- Visual Inspection: Hairline fracture detected on the main exhaust valve.",
        "- Pressure reading: 125 PSI.",
        "- Temperature reading: 95 °C.",
        "",
        "Conclusion: Critical structural failure imminent. Immediate shutdown required."
    ])

    create_pdf(os.path.join(out_dir, "demo_sop_reject.pdf"), "SOP: Boiler Safety Parameters", [
        "Standard Operating Procedure: Boiler Gamma",
        "",
        "Critical Safety Limits:",
        "1. Maximum allowable pressure: 110 PSI.",
        "2. Maximum allowable temperature: 90 °C.",
        "3. Structural integrity: Any fractures or cracks are immediate grounds for failure.",
        "",
        "Action: If any critical safety limit is breached, the decision MUST be REJECT.",
        "Equipment must be flagged for immediate shutdown and repair."
    ])

if __name__ == "__main__":
    main()
