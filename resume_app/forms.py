from django import forms
from .models import Resume, Skill, Experience, Education, Project, Certification

class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['full_name', 'email', 'phone', 'linkedin', 'github', 'summary']


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['resume', 'category', 'description']


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
        fields = ['resume', 'title', 'date_range', 'subtitle','tech_stack']


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['resume', 'name']
