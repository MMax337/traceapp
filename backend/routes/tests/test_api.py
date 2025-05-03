from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from routes.models import Route, RoutePoint, BackgroundImage
import json

User = get_user_model()

class MinimalRouteAPITests(TestCase):
    """Minimal tests for route API - only those that are definitely available."""
    
    def setUp(self):
        # Create test client
        self.client = Client()
        
        # Create test user
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create_user(
            username=self.username,
            email='test@example.com',
            password=self.password
        )
        
        # Create background
        self.background = BackgroundImage.objects.create(
            name='Test Background',
            image=SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        )
        
        # Create route for user
        self.route = Route.objects.create(
            name='Test Route',
            background=self.background,
            user=self.user
        )
        
        # Get API token for user
        from rest_framework.authtoken.models import Token
        self.token = Token.objects.create(user=self.user)
        self.auth_header = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}
    
    def test_api_get_routes(self):
        """Test retrieving routes through API."""
        # Call API endpoint
        response = self.client.get(
            reverse('route-list'),
            **self.auth_header
        )
        
        # Check if response is correct
        self.assertEqual(response.status_code, 200)
        
        # Check if route is in the response
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Test Route')
    
    def test_api_create_route(self):
        """Test creating a route through API."""
        # Prepare data for new route
        route_data = {
            'name': 'API Test Route',
            'background': self.background.id
        }
        
        # Call API endpoint
        response = self.client.post(
            reverse('route-list'),
            data=json.dumps(route_data),
            content_type='application/json',
            **self.auth_header
        )
        
        # Check if response is correct
        self.assertEqual(response.status_code, 201)
        
        # Check if route was created
        data = json.loads(response.content)
        self.assertEqual(data['name'], 'API Test Route')
        self.assertTrue(Route.objects.filter(name='API Test Route').exists())
    
    def test_api_bulk_update_points(self):
        """Test bulk update of route points through API."""
        # Prepare data for points update
        points_data = {
            'points': [
                {'x': 150, 'y': 150, 'color': '#FF00FF', 'order': 0},
                {'x': 250, 'y': 250, 'color': '#00FFFF', 'order': 1}
            ]
        }
        
        # Call API endpoint (using direct URL)
        response = self.client.post(
            f'/api/routes/{self.route.id}/bulk-update-points/',
            data=json.dumps(points_data),
            content_type='application/json',
            **self.auth_header
        )
        
        # Check if response is correct
        self.assertEqual(response.status_code, 200)
    
        # Check if points were updated
        updated_points = RoutePoint.objects.filter(route=self.route).order_by('order')
        self.assertEqual(len(updated_points), 2)
        self.assertEqual(updated_points[0].x, 150)
        self.assertEqual(updated_points[1].x, 250)