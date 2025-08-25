from django import forms
from .models import Resume, Skill, Experience, Education, Project, Certificate

class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['full_name', 'email', 'phone', 'linkedin', 'github', 'summary']


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'category']


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['job_title', 'company', 'location', 'start_date', 'end_date', 'description']


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['school', 'degree', 'start_date', 'end_date', 'location']


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'technologies', 'date']


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['name', 'issuer', 'issue_date']
