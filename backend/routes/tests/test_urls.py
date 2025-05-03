from django.test import TestCase
from django.urls import reverse, resolve
from routes.views import (
    index, route_list, route_create, route_detail, 
    route_delete, create_anonymous_route
)

class UrlsTests(TestCase):
    """Tests for application URLs."""
    
    def test_index_url(self):
        """Test URL for the main page."""
        url = reverse('index')
        self.assertEqual(url, '/')
        
        resolver = resolve(url)
        self.assertEqual(resolver.func, index)
    
    def test_route_list_url(self):
        """Test URL for the routes list."""
        url = reverse('route_list')
        self.assertEqual(url, '/routes/')
        
        resolver = resolve(url)
        self.assertEqual(resolver.func, route_list)
    
    def test_route_create_url(self):
        """Test URL for route creation."""
        url = reverse('route_create')
        self.assertEqual(url, '/routes/create/')
        
        resolver = resolve(url)
        self.assertEqual(resolver.func, route_create)
    
    def test_route_detail_url(self):
        """Test URL for route details."""
        url = reverse('route_detail', args=[1])
        self.assertEqual(url, '/routes/1/')
        
        resolver = resolve(url)
        self.assertEqual(resolver.func, route_detail)
    
    def test_route_delete_url(self):
        """Test URL for route deletion."""
        url = reverse('route_delete', args=[1])
        self.assertEqual(url, '/routes/1/delete/')
        
        resolver = resolve(url)
        self.assertEqual(resolver.func, route_delete)
    
    def test_create_anonymous_route_url(self):
        """Test URL for anonymous route creation."""
        url = reverse('create_anonymous_route')
        self.assertEqual(url, '/routes/create/anonymous')  # Corrected expected URL