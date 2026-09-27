import json
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


def make_pdf(scan_row):
    result = json.loads(scan_row["result_json"])

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    y = height - 50

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "VulnScan Lite - Security Report")
    y -= 30

    c.setFont("Helvetica", 12)
    c.drawString(50, y, "URL: " + scan_row["url"])
    y -= 20
    c.drawString(50, y, "Score: " + str(result["score"]) + " (" + result["grade"] + ")")
    y -= 35

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Passed Checks")
    y -= 20
    c.setFont("Helvetica", 11)
    for p in result["passed_checks"]:
        c.drawString(60, y, "- " + p)
        y -= 15

    y -= 15
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Failed Checks")
    y -= 20
    c.setFont("Helvetica", 11)
    for f in result["failed_checks"]:
        c.drawString(60, y, "- " + f["check"] + ": " + f["why"])
        y -= 15
        c.drawString(70, y, "fix (nginx): " + f["nginx"][:80])
        y -= 20
        if y < 60:
            c.showPage()
            y = height - 50

    y -= 10
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, y, result["disclaimer"])

    c.save()
    buf.seek(0)
    return buf.read()
