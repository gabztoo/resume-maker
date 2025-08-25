# resume_app/views.py

import os
import subprocess
import tempfile
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404 # Adicionei o render
from jinja2 import Environment, FileSystemLoader

# Importe TODOS os seus modelos aqui
from .models import Resume, Experience, Skill, Project, Education, Certification
from .forms import ResumeForm # Supondo que você tenha um form

# Função para escapar caracteres especiais do LaTeX (está perfeita)
def escape_latex(text):
    """
    Escapa caracteres especiais para uso seguro em um documento LaTeX.
    """
    if text is None:
        return ""
    # Adicionei a conversão para string para garantir
    return str(text).replace('&', '\\&').replace('%', '\\%').replace('$', '\\$') \
                    .replace('#', '\\#').replace('_', '\\_').replace('{', '\\{') \
                    .replace('}', '\\}').replace('~', '\\textasciitilde{}') \
                    .replace('^', '\\textasciicircum{}').replace('\\', '\\textbackslash{}')

# Sua view para criar/editar o currículo (exemplo)
def create_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST)
        if form.is_valid():
            # Salva o formulário e pega o objeto criado
            resume = form.save()
            
            # --- PONTO PRINCIPAL DA MUDANÇA ---
            # Em vez de retornar uma mensagem, redirecione para a view de PDF
            # O primeiro argumento é o NOME da sua URL
            # O segundo é o parâmetro que a URL espera (resume_id)
            return redirect('generate_pdf', resume_id=resume.id)
            # ------------------------------------
    else:
        form = ResumeForm()
    return render(request, 'resume_form.html', {'form': form})



# View de geração de PDF ATUALIZADA
def generate_pdf(request, resume_id):
    # 1. Obter os dados do banco de dados
    resume = get_object_or_404(Resume, pk=resume_id)
    
    # --- PONTO PRINCIPAL DA MUDANÇA ---
    # Buscando os dados de modelos relacionados ao currículo.
    # O '.all()' busca todos os objetos que têm uma chave estrangeira para este 'resume'.
    # O nome 'experience_set' é criado automaticamente pelo Django.
    # Se você definiu um 'related_name' no seu ForeignKey, use esse nome.
    experiences = resume.experience_set.all()
    skills = resume.skill_set.all()
    projects = resume.project_set.all()
    education = resume.education_set.all()
    certifications = resume.certification_set.all()
    # ------------------------------------
    
    # 2. Configurar o ambiente Jinja2 para carregar o template
    template_dir = os.path.join(settings.BASE_DIR, 'resume_app', 'latex_templates')
    env = Environment(loader=FileSystemLoader(template_dir), autoescape=False) # autoescape=False é seguro aqui
    
    # Adicionar o filtro de escape ao ambiente Jinja2
    env.filters['escape_latex'] = escape_latex
    
    template = env.get_template('curriculo_template.tex')

    # 3. Preparar o contexto com TODOS os dados
    context = {
        'resume': resume,
        'experiences': experiences,
        'skills': skills,
        'projects': projects,
        'education': education,
        'certifications': certifications,
    }

    # 4. Renderizar o template com os dados
    rendered_latex = template.render(context)
    
    # 5. Usar um diretório temporário para compilar o PDF (seu código aqui está perfeito)
    with tempfile.TemporaryDirectory() as temp_dir:
        tex_file_path = os.path.join(temp_dir, 'resume.tex')
        with open(tex_file_path, 'w', encoding='utf-8') as f:
            f.write(rendered_latex)

        # 6. Chamar o compilador pdflatex
        for i in range(2):
            try:
                subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', '-output-directory', temp_dir, tex_file_path],
                    check=True,
                    capture_output=True,
                    text=True,
                )
            except FileNotFoundError:
                return HttpResponse("Erro: o comando 'pdflatex' não foi encontrado. Verifique se uma distribuição LaTeX (como MiKTeX) está instalada e no PATH do sistema.", status=500)
            except subprocess.CalledProcessError as e:
                error_log = f"Erro ao compilar o LaTeX. Verifique o log abaixo para encontrar o problema no arquivo .tex:\n\n{e.stdout}"
                return HttpResponse(error_log, content_type='text/plain', status=500)

        # 7. Ler o arquivo PDF gerado e servir na resposta
        pdf_file_path = os.path.join(temp_dir, 'resume.pdf')
        if os.path.exists(pdf_file_path):
            with open(pdf_file_path, 'rb') as f:
                pdf_content = f.read()
            
            response = HttpResponse(pdf_content, content_type='application/pdf')
            # Usei f-string para o nome do arquivo, é um pouco mais limpo
            response['Content-Disposition'] = f'attachment; filename="curriculo_{resume.full_name.replace(" ", "_")}.pdf"'
            return response
        else:
            return HttpResponse("Falha ao gerar o arquivo PDF. O log de compilação pode ter mais detalhes.", status=500)