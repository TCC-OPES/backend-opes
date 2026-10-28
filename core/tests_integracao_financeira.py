from django.test import SimpleTestCase
from django.urls import reverse, resolve
from rest_framework_simplejwt.views import TokenRefreshView

class RotasFinanceirasTests(SimpleTestCase):
    def test_health(self):
        from django.test import Client
        r = Client().get('/api/health/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['api_version'], 'opes-financeiro-v2')

    def test_recorrencias_protegidas_e_existentes(self):
        from django.test import Client
        for path in ['/api/recorrencias/', '/api/recorrencias/ocorrencias/?inicio=2026-10-01&fim=2026-10-31']:
            response = Client().get(path)
            self.assertEqual(response.status_code, 401, path)

    def test_refresh_registrado(self):
        self.assertIs(resolve('/api/token/refresh/').func.view_class, TokenRefreshView)
