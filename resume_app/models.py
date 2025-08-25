from django.db import models

class Resume(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    linkedin = models.CharField(blank=True, null=True)
    github = models.CharField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)  # Resumo profissional

    def __str__(self):
        return self.full_name


class Skill(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="skills")
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, blank=True, null=True)  # ex: Linguagens, Ferramentas

    def __str__(self):
        return f"{self.name} ({self.category})"


class Experience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="experiences")
    job_title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)  # null = atualmente
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.job_title} - {self.company}"


class Education(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="educations")
    school = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.degree} - {self.school}"


class Project(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    technologies = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.title


class Certificate(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="certificates")
    name = models.CharField(max_length=200)
    issuer = models.CharField(max_length=200, blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name
