from django.db import models

class Resume(models.Model):
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=50)
    email = models.EmailField()
    linkedin = models.CharField(max_length=200, help_text="Apenas o seu nome de usuário (ex: alexwebbx)")
    github = models.CharField(max_length=200, help_text="Apenas o seu nome de usuário (ex: alexwebbx)")
    summary = models.TextField()

    def __str__(self):
        return self.full_name

class Skill(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='skills')
    category = models.CharField(max_length=100, help_text="Ex: Programming Languages")
    description = models.TextField(help_text="Ex: Python, Django, C++")

    def __str__(self):
        return f"{self.category} for {self.resume.full_name}"

class Project(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    date_range = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=200)
    tech_stack = models.CharField(max_length=200)

    def __str__(self):
        return self.title

class ProjectItem(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='items')
    description = models.TextField()

    def __str__(self):
        return self.description[:80] # Mostra os primeiros 80 caracteres

class Experience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='experiences')
    title = models.CharField(max_length=200)
    date_range = models.CharField(max_length=100)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.title} at {self.company}"

class ExperienceItem(models.Model):
    experience = models.ForeignKey(Experience, on_delete=models.CASCADE, related_name='items')
    description = models.TextField()

    def __str__(self):
        return self.description[:80] # Mostra os primeiros 80 caracteres

class Education(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    date_range = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.degree} from {self.institution}"

class Certification(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name