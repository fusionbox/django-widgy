from django.contrib.auth.models import User
from django.test.client import Client

from modeltests.core_tests.tests.base import HttpTestCase

class TestAdminPages(HttpTestCase):
    
    def setup(self):
        self.client = Client()
        self.client.login(username='testuser', password='asdfasdf') 
        
    def test_admin_page(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        
    def test_open_page_node_list(self):
        response = self.client.get('/admin/pages/page/')
        self.assertEqual(response.status_code, 200)
        
    def test_add_widgy_page(self):
        response = self.client.get('/admin/widgy_mezzanine/widgypage/add/')
        self.assertEqual(response.status_code, 200)
        
    def test_open_auth_user_page(self):
        response = self.client.get('/admin/auth/user/')
        self.assertEqual(response.status_code, 200)
        
    def test_open_auth_group_page(self):
        response = self.client.get('/admin/auth/group/')
        self.assertEqual(response.status_code, 200)
        
    def test_site_sites(self):
        response = self.client.get('/admin/sites/site/')
        self.assertEqual(response.status_code, 200)
    
    def test_open_filer_folders(self):
        response = self.client.get('/admin/filer/folder/')
        self.assertEqual(response.status_code, 200)
        
    def test_open_settings(self):
        response = self.client.get('/admin/conf/setting/')
        self.assertEqual(response.status_code, 200)
        
    def test_open_comments(self):
        response = self.client.get('/admin/generic/threadedcomment/')
        self.assertEqual(response.status_code, 200)