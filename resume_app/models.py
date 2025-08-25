from django.db import models

class Resume(models.Model):
    full_name = models.CharField("Nome completo", max_length=200)
    phone = models.CharField("Telefone", max_length=50)
    email = models.EmailField("E-mail")
    linkedin = models.CharField("LinkedIn", max_length=200, help_text="Apenas o seu nome de usuário (ex: alexwebbx)")
    github = models.CharField("GitHub", max_length=200, help_text="Apenas o seu nome de usuário (ex: alexwebbx)")
    summary = models.TextField("Resumo")
    # Novos campos para alinhar com o template LaTeX
    location = models.CharField("Localização", max_length=200, blank=True, default="")
    website = models.CharField("Site", max_length=200, blank=True, default="")

    def __str__(self):
        return self.full_name

class Skill(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='skills')
    # Mantemos os campos antigos por compatibilidade, mas o template usa 'name'
    name = models.CharField("Nome", max_length=200, blank=True, null=True)
    category = models.CharField("Categoria", max_length=100, help_text="Ex: Linguagens de Programação", blank=True, default="")
    description = models.TextField("Descrição", help_text="Ex: Python, Django, C++", blank=True, default="")

    def __str__(self):
        return (self.name or self.category or "Skill") + f" for {self.resume.full_name}"

class Project(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField("Título", max_length=200)
    date_range = models.CharField("Período (livre)", max_length=100)
    subtitle = models.CharField("Subtítulo", max_length=200)
    tech_stack = models.CharField("Tecnologias", max_length=200)
    # Novo campo usado pelo template
    url = models.CharField("URL", max_length=300, blank=True, default="")
    # Datas separadas (preferidas no template)
    start_date = models.CharField("Data de início", max_length=100, blank=True, default="", help_text="Ex.: Jan 2020")
    end_date = models.CharField("Data de término", max_length=100, blank=True, default="", help_text="Ex.: Dez 2021 ou 'Atual'")

    def __str__(self):
        return self.title

class ProjectItem(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='items')
    description = models.TextField("Descrição")

    def __str__(self):
        return self.description[:80] # Mostra os primeiros 80 caracteres

class Experience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='experiences')
    title = models.CharField("Cargo", max_length=200)
    date_range = models.CharField("Período (livre)", max_length=100)
    company = models.CharField("Empresa", max_length=200)
    location = models.CharField("Localização", max_length=200)
    # Novo: descrição da experiência
    description = models.TextField("Descrição", blank=True, default="", help_text="Escreva uma por linha; cada linha vira um tópico (bullet) no PDF")
    # Datas separadas (preferidas no template)
    start_date = models.CharField("Data de início", max_length=100, blank=True, default="", help_text="Ex.: Jan 2020")
    end_date = models.CharField("Data de término", max_length=100, blank=True, default="", help_text="Ex.: Dez 2021 ou 'Atual'")

    def __str__(self):
        return f"{self.title} at {self.company}"

class ExperienceItem(models.Model):
    experience = models.ForeignKey(Experience, on_delete=models.CASCADE, related_name='items')
    description = models.TextField("Descrição")

    def __str__(self):
        return self.description[:80] # Mostra os primeiros 80 caracteres

class Education(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField("Instituição", max_length=200)
    location = models.CharField("Localização", max_length=200)
    degree = models.CharField("Formação", max_length=200)
    date_range = models.CharField("Período (livre)", max_length=100)
    # Datas separadas (preferidas no template)
    start_date = models.CharField("Data de início", max_length=100, blank=True, default="", help_text="Ex.: 2000")
    end_date = models.CharField("Data de término", max_length=100, blank=True, default="", help_text="Ex.: 2005")

    def __str__(self):
        return f"{self.degree} from {self.institution}"

class Certification(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField("Nome da certificação", max_length=200)
    # Novos campos para certificação
    institution = models.CharField("Instituição", max_length=200, blank=True, default="", help_text="Instituição/Local de estudo")
    date = models.CharField("Data", max_length=100, blank=True, default="", help_text="Quando foi concluído (ex.: 2022)")
    number = models.CharField("Número", max_length=100, blank=True, default="", help_text="Número do certificado")

    def __str__(self):
        return self.name