from django import forms
from .models import Resume, Skill, Experience, Education, Project, Certification

class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['full_name', 'email', 'phone', 'location', 'website', 'linkedin', 'github', 'summary']
        labels = {
            'full_name': 'Nome completo:',
            'email': 'E-mail:',
            'phone': 'Telefone:',
            'location': 'Localização:',
            'website': 'Site:',
            'linkedin': 'LinkedIn:',
            'github': 'GitHub:',
            'summary': 'Resumo:',
        }
        help_texts = {
            'full_name': 'Seu nome completo como aparecerá no currículo.',
            'email': 'Use um e-mail profissional.',
            'phone': 'Inclua DDI e DDD. Ex.: +55 11 99999-9999',
            'location': 'Ex.: São Paulo, SP',
            'website': 'Ex.: https://seusite.com (opcional)',
            'linkedin': 'Apenas o seu nome de usuário (ex: alexwebbx) ou a URL completa.',
            'github': 'Apenas o seu nome de usuário (ex: alexwebbx) ou a URL completa.',
            'summary': 'Um resumo objetivo (2–4 linhas) sobre você.',
        }
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Seu nome completo'}),
            'email': forms.EmailInput(attrs={'placeholder': 'voce@exemplo.com'}),
            'phone': forms.TextInput(attrs={'placeholder': '+55 11 99999-9999'}),
            'location': forms.TextInput(attrs={'placeholder': 'Cidade, Estado'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://seusite.com'}),
            'linkedin': forms.TextInput(attrs={'placeholder': 'Apenas o seu nome de usuário (ex: alexwebbx)'}),
            'github': forms.TextInput(attrs={'placeholder': 'Apenas o seu nome de usuário (ex: alexwebbx)'}),
            'summary': forms.Textarea(attrs={'placeholder': 'Resumo profissional...', 'rows': 5}),
        }


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['resume', 'name']


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        # Usamos os nomes de campo EXATOS do models.py
        fields = ['title', 'company', 'location', 'date_range']


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        # Usamos os nomes de campo EXATOS do models.py
        fields = ['institution', 'degree', 'location', 'date_range']


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['resume', 'title', 'date_range', 'subtitle', 'tech_stack', 'url']


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['resume', 'name']
