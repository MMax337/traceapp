from django.test import TestCase
from django.urls import reverse, resolve
from routes.views import (
    index, route_list, route_create, route_detail, 
    route_delete, create_anonymous_route
)

class UrlsTests(TestCase):
    """Testy dla URLi aplikacji."""
    
    def test_index_url(self):
        """Test URLa strony głównej."""
        url = reverse('index')
        self.assertEqual(url, '/')
        
        resolver = resolve(url)
        self.assertEqual(resolver.func, index)
    
    def test_route_list_url(self):
        """Test URLa listy tras."""
        url = reverse('route_list')
        self.assertEqual(url, '/routes/')
        
        resolver = resolve(url)
        self.assertEqual(resolver.func, route_list)
    
    def test_route_create_url(self):
        """Test URLa tworzenia trasy."""
        url = reverse('route_create')
        self.assertEqual(url, '/routes/create/')
        
        resolver = resolve(url)
        self.assertEqual(resolver.func, route_create)
    
    def test_route_detail_url(self):
        """Test URLa szczegółów trasy."""
        url = reverse('route_detail', args=[1])
        self.assertEqual(url, '/routes/1/')
        
        resolver = resolve(url)
        self.assertEqual(resolver.func, route_detail)
    
    def test_route_delete_url(self):
        """Test URLa usuwania trasy."""
        url = reverse('route_delete', args=[1])
        self.assertEqual(url, '/routes/1/delete/')
        
        resolver = resolve(url)
        self.assertEqual(resolver.func, route_delete)
    
    def test_create_anonymous_route_url(self):
        """Test URLa tworzenia anonimowej trasy."""
        url = reverse('create_anonymous_route')
        self.assertEqual(url, '/routes/create/anonymous')  # Poprawiony oczekiwany URL