# resume_app/views.py
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import Resume # Supondo que você tenha um modelo Resume

def generate_pdf(request, resume_id):
    # 1. Obtenha os dados do currículo do banco de dados
    try:
        resume = Resume.objects.get(pk=resume_id)
    except Resume.DoesNotExist:
        return HttpResponse("Currículo não encontrado.", status=404)

    # 2. Renderize o template HTML com os dados
    # (Você precisará criar um template HTML para o PDF, ex: resume_pdf_template.html)
    html_string = render_to_string('resume_pdf_template.html', {'resume': resume})

    # 3. Use o WeasyPrint para converter o HTML em PDF
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()

    # 4. Crie a resposta HTTP com o arquivo PDF
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="curriculo_{resume_id}.pdf"'

    return response