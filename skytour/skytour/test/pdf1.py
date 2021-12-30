import io
from django.http import FileResponse
from reportlab.pdfgen import canvas

def test1():
    buffer = io.BytesIO()

    p = canvas.Canvas(buffer)
    p.drawString(100, 100, "Hello World")
    p.showPage() # finish the page
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='hello.pdf')
