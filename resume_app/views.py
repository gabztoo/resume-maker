# resume_app/views.py
from django.db import connection
import os
import subprocess
import tempfile
import shutil
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect # Adicionei o render e redirect
from jinja2 import Environment, FileSystemLoader


# Importe TODOS os seus modelos aqui
from .models import Resume, Experience, Skill, Project, Education, Certification
from .forms import ResumeForm # Supondo que você tenha um form

def latex_escape(text):
    if not text:
        return ""
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        "\\": r"\textbackslash{}",
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text


# Função para escapar caracteres especiais do LaTeX (está perfeita)
def escape_latex(text):
    """
    Escapa caracteres especiais para uso seguro em um documento LaTeX.
    Implementado caractere a caractere para evitar re-escapar as barras
    inseridas durante o próprio processo de escape (evita gerar
    "\\textbackslash{}_" a partir de "\\_").
    """
    if text is None:
        return ""
    s = str(text)
    mapping = {
        '&': r"\&",
        '%': r"\%",
        '$': r"\$",
        '#': r"\#",
        '_': r"\_",
        '{': r"\{",
        '}': r"\}",
        '~': r"\textasciitilde{}",
        '^': r"\textasciicircum{}",
        '\\': r"\textbackslash{}",
    }
    out_chars = []
    for ch in s:
        out_chars.append(mapping.get(ch, ch))
    return ''.join(out_chars)

# Sua view para criar/editar o currículo (exemplo)
def create_resume(request):
    from django.forms import inlineformset_factory

    # Definição dos formsets inline (campos exatamente conforme os models)
    SkillFormSet = inlineformset_factory(
        Resume, Skill,
        fields=['name', 'category', 'description'],
        extra=0, can_delete=True
    )
    ExperienceFormSet = inlineformset_factory(
        Resume, Experience,
        fields=['title', 'company', 'location', 'start_date', 'end_date', 'date_range', 'description'],
        extra=0, can_delete=True
    )
    EducationFormSet = inlineformset_factory(
        Resume, Education,
        fields=['institution', 'degree', 'location', 'start_date', 'end_date', 'date_range'],
        extra=0, can_delete=True
    )
    ProjectFormSet = inlineformset_factory(
        Resume, Project,
        fields=['title', 'start_date', 'end_date', 'date_range', 'subtitle', 'tech_stack', 'url'],
        extra=0, can_delete=True
    )
    CertificationFormSet = inlineformset_factory(
        Resume, Certification,
        fields=['name', 'institution', 'date', 'number'],
        extra=0, can_delete=True
    )

    if request.method == 'POST':
        form = ResumeForm(request.POST)
        if form.is_valid():
            # Salva o formulário e pega o objeto criado
            try:
                resume = form.save()
            except Exception as e:
                # Se for erro de migração (coluna inexistente), tente migrar automaticamente e salvar de novo
                from django.db.utils import OperationalError as DjangoOperationalError
                if isinstance(e, DjangoOperationalError) and 'no column named' in str(e).lower():
                    try:
                        from django.core.management import call_command
                        # Executa migrações e tenta novamente
                        call_command('migrate', '--noinput')
                        resume = form.save()
                    except Exception as e2:
                        # Retorna mensagem útil ao usuário
                        return HttpResponse(
                            "Erro de banco de dados: colunas ausentes. Tentamos aplicar as migrações automaticamente, mas falhou.\n\n"
                            "Como resolver:\n"
                            "1) Pare o servidor.\n"
                            "2) Rode: python .\\resume-maker\\manage.py migrate\n"
                            "3) Recarregue a página e tente novamente.",
                            content_type='text/plain; charset=utf-8',
                            status=500,
                        )
                else:
                    # Erro inesperado: propaga
                    raise

            # Instancia e valida os formsets vinculados a este resume
            skills_formset = SkillFormSet(request.POST, instance=resume, prefix='skills')
            exp_formset = ExperienceFormSet(request.POST, instance=resume, prefix='experiences')
            edu_formset = EducationFormSet(request.POST, instance=resume, prefix='education')
            proj_formset = ProjectFormSet(request.POST, instance=resume, prefix='projects')
            cert_formset = CertificationFormSet(request.POST, instance=resume, prefix='certifications')

            if (skills_formset.is_valid() and exp_formset.is_valid() and
                edu_formset.is_valid() and proj_formset.is_valid() and cert_formset.is_valid()):
                skills_formset.save()
                exp_formset.save()
                edu_formset.save()
                proj_formset.save()
                cert_formset.save()
                # Redireciona para gerar o PDF
                return redirect('generate_pdf', resume_id=resume.id)
            else:
                # Reexibe o formulário com erros dos formsets
                context = {
                    'form': form,
                    'skills_formset': skills_formset,
                    'exp_formset': exp_formset,
                    'edu_formset': edu_formset,
                    'proj_formset': proj_formset,
                    'cert_formset': cert_formset,
                }
                return render(request, 'resume_form.html', context)
    else:
        form = ResumeForm()
        # Formsets vazios na primeira carga, com uma instância temporária para estrutura consistente
        temp_resume = Resume()
        skills_formset = SkillFormSet(instance=temp_resume, prefix='skills')
        exp_formset = ExperienceFormSet(instance=temp_resume, prefix='experiences')
        edu_formset = EducationFormSet(instance=temp_resume, prefix='education')
        proj_formset = ProjectFormSet(instance=temp_resume, prefix='projects')
        cert_formset = CertificationFormSet(instance=temp_resume, prefix='certifications')

    return render(request, 'resume_form.html', {
        'form': form,
        'skills_formset': skills_formset,
        'exp_formset': exp_formset,
        'edu_formset': edu_formset,
        'proj_formset': proj_formset,
        'cert_formset': cert_formset,
    })



# View de geração de PDF ATUALIZADA

def generate_pdf(request, resume_id):
    print("DEBUG: usando banco ->", connection.settings_dict['NAME'])
    print("DEBUG IDs disponíveis:", list(Resume.objects.values_list("id", flat=True)))
    resume = get_object_or_404(Resume, pk=resume_id)

    # 1. Obter os dados do banco de dados
    resume = get_object_or_404(Resume, pk=resume_id)

    # Buscando os dados relacionados
    experiences = resume.experiences.all()
    skills = resume.skills.all()
    projects = resume.projects.all()
    education = resume.education.all()
    certifications = resume.certifications.all()

    # Verificação antecipada: se faltar coluna (db desatualizado), migra automaticamente e recarrega
    try:
        list(experiences[:1])
        list(skills[:1])
        list(projects[:1])
        list(education[:1])
        list(certifications[:1])
    except Exception as e:
        from django.db.utils import OperationalError as DjangoOperationalError
        if isinstance(e, DjangoOperationalError) and ('no such column' in str(e).lower() or 'has no column named' in str(e).lower()):
            try:
                from django.core.management import call_command
                call_command('migrate', '--noinput')
                # Reconsultar após migrar
                experiences = resume.experiences.all()
                skills = resume.skills.all()
                projects = resume.projects.all()
                education = resume.education.all()
                certifications = resume.certifications.all()
            except Exception:
                return HttpResponse(
                    "Erro de banco de dados: colunas ausentes. Tentamos aplicar as migrações automaticamente, mas falhou.\n\n"
                    "Como resolver:\n"
                    "1) Pare o servidor.\n"
                    "2) Rode: python .\\resume-maker\\manage.py migrate\n"
                    "3) Recarregue a página e tente novamente.",
                    content_type='text/plain; charset=utf-8',
                    status=500,
                )
        else:
            raise

    # 2. Configurar o ambiente Jinja2 para carregar o template
    template_dir = os.path.join(settings.BASE_DIR, 'resume_app', 'latex_templates')
    env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=False,
            # Evita conflito entre Jinja2 e comandos LaTeX como {#1} e sequências como "{%" em comentários do LaTeX
            comment_start_string='((#',
            comment_end_string='#))',
            block_start_string='((*',
            block_end_string='*))',
            variable_start_string='[[',
            variable_end_string=']]'
        )  # autoescape=False é seguro aqui

    # Adicionar os filtros ao ambiente Jinja2
    env.filters['escape_latex'] = escape_latex

    def bullet_lines(value):
        if not value:
            return []
        s = str(value).replace('\r\n', '\n').replace('\r', '\n')
        out = []
        for raw in s.split('\n'):
            line = raw.strip()
            if not line:
                continue
            # remove marcadores comuns no início
            if line.startswith('•'):
                line = line[1:].strip()
            elif line[:2] in ('- ', '* '):
                line = line[2:].strip()
            elif line.startswith('-') or line.startswith('*'):
                line = line[1:].strip()
            out.append(line)
        return out

    env.filters['bullet_lines'] = bullet_lines

    template = env.get_template('curriculo_template.tex')

    # Construir URLs completas para LinkedIn e GitHub (aceita username ou URL completa)
    def normalize_url(value: str, prefix: str) -> str:
        if not value:
            return ''
        v = str(value).strip()
        if v.startswith('http://') or v.startswith('https://'):
            return v
        return prefix + v

    linkedin_url = normalize_url(resume.linkedin, 'https://www.linkedin.com/in/')
    github_url = normalize_url(resume.github, 'https://github.com/')

    # 3. Preparar o contexto com TODOS os dados
    context = {
        'resume': resume,
        'experiences': experiences,
        'skills': skills,
        'projects': projects,
        'education': education,
        'certifications': certifications,
        'linkedin_url': linkedin_url,
        'github_url': github_url,
    }

    # 4. Renderizar o template com os dados
    rendered_latex = template.render(context)

    # Permitir retorno de .tex para testes/depuração sem exigir LaTeX instalado
    if request.GET.get('format') == 'tex':
        response = HttpResponse(rendered_latex, content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="curriculo_{resume.full_name.replace(" ", "_")}.tex"'
        return response

    # 5. Verificar se o compilador LaTeX está disponível
    pdflatex_cmd = getattr(settings, 'PDFLATEX_CMD', 'pdflatex')
    if shutil.which(pdflatex_cmd) is None:
        # Guia amigável e link direto para baixar o .tex
        help_msg = (
            "Erro: o comando 'pdflatex' não foi encontrado no PATH do sistema.\n\n"
            "Como resolver:\n"
            "- Instale uma distribuição LaTeX (Windows: MiKTeX; Linux/macOS: TeX Live).\n"
            "- Após instalar, feche e reabra o terminal e verifique com: pdflatex --version\n\n"
            "Enquanto isso, você pode baixar o arquivo .tex gerado aqui: "
            f"/generate_pdf/{resume.id}/?format=tex"
        )
        return HttpResponse(help_msg, content_type='text/plain; charset=utf-8', status=503)

    # 6. Usar um diretório temporário para compilar o PDF
    with tempfile.TemporaryDirectory() as temp_dir:
        tex_file_path = os.path.join(temp_dir, 'resume.tex')
        with open(tex_file_path, 'w', encoding='utf-8') as f:
            f.write(rendered_latex)

        # 7. Chamar o compilador pdflatex (duas passagens)
        for i in range(2):
            try:
                subprocess.run(
                    [pdflatex_cmd, '-interaction=nonstopmode', '-output-directory', temp_dir,
                     os.path.basename(tex_file_path)],
                    cwd=temp_dir,  # <- roda dentro da pasta temporária
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
            except FileNotFoundError:
                # Este caso deve ser raro pois já checamos com shutil.which
                return HttpResponse("Erro: o comando 'pdflatex' não foi encontrado. Verifique se uma distribuição LaTeX (como MiKTeX) está instalada e no PATH do sistema.", status=500)
            except subprocess.CalledProcessError as e:
                error_log = (
                    "Erro ao compilar o LaTeX. Verifique o log abaixo para encontrar o problema no arquivo .tex:\n\n"
                    + (e.stdout or '')
                    + "\n\n" + (e.stderr or '')
                )
                return HttpResponse(error_log, content_type='text/plain', status=500)
            except subprocess.TimeoutExpired as e:
                timeout_msg = (
                    "A compilação do LaTeX excedeu o tempo limite (60s) e foi interrompida.\n\n"
                    "Dicas:\n"
                    "- Verifique se o pacote LaTeX necessário está instalado (ex.: MiKTeX/TeX Live).\n"
                    "- Tente baixar o .tex para compilar manualmente: "
                    f"/generate_pdf/{resume.id}/?format=tex\n\n"
                    "Saída parcial:\n\n"
                    + (getattr(e, 'stdout', '') or '')
                    + "\n\n" + (getattr(e, 'stderr', '') or '')
                )
                return HttpResponse(timeout_msg, content_type='text/plain; charset=utf-8', status=504)

        # 7. Ler o arquivo PDF gerado e servir na resposta
        pdf_file_path = os.path.join(temp_dir, 'resume.pdf')
        if os.path.exists(pdf_file_path):
            with open(pdf_file_path, 'rb') as f:
                pdf_content = f.read()

            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="curriculo_{resume.full_name.replace(" ", "_")}.pdf"'
            return response
        else:
            return HttpResponse("Falha ao gerar o arquivo PDF. O log de compilação pode ter mais detalhes.", status=500)