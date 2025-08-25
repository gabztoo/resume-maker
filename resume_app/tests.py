from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from .models import Resume


class ResumeViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.resume = Resume.objects.create(
            full_name="Maria Silva",
            phone="+55 11 99999-9999",
            email="maria@example.com",
            linkedin="mariasilva",
            github="mariadev",
            summary="Profissional de tecnologia com experiência em Django e LaTeX."
        )

    def test_homepage_loads(self):
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Preencha seu Currículo")

    def test_generate_tex_without_pdflatex(self):
        url = reverse('generate_pdf', args=[self.resume.id]) + "?format=tex"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf-8')
        # Verifica nome e que os links foram normalizados
        self.assertIn("Maria Silva", content)
        self.assertIn("https://www.linkedin.com/in/mariasilva", content)
        self.assertIn("https://github.com/mariadev", content)

    @patch('resume_app.views.shutil.which', return_value=None)
    def test_generate_pdf_missing_pdflatex_returns_help(self, mock_which):
        url = reverse('generate_pdf', args=[self.resume.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 503)
        txt = resp.content.decode('utf-8')
        self.assertIn("pdflatex", txt)
        self.assertIn("?format=tex", txt)
