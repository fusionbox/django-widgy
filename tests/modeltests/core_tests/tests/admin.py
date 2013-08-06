from django.contrib.auth.models import User
from django.test.client import Client

from modeltests.core_tests.tests.base import HttpTestCase
from modeltests.core_tests import urls

class TestLogin(HttpTestCase):
    urls = urls
    
    def setup(self):
        self.client = Client()
        self.client.login(username='testuser',password='asdfasdf') 
        
    def test_admin_login(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)