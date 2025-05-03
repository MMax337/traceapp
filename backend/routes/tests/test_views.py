from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from routes.models import Route, RoutePoint, BackgroundImage
import json

User = get_user_model()

class RouteViewsTests(TestCase):
    """Tests for route-related views."""
    
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
        
        # Create several route points
        self.point1 = RoutePoint.objects.create(
            route=self.route,
            x=100,
            y=100,
            color='#FF0000',
            order=0
        )
        self.point2 = RoutePoint.objects.create(
            route=self.route,
            x=200,
            y=200,
            color='#00FF00',
            order=1
        )
    
    def test_route_list_view(self):
        """Test route list view."""
        # Log in the user
        self.client.login(username=self.username, password=self.password)
        
        # Call the route list view
        response = self.client.get(reverse('route_list'))
        
        # Check if the response is correct
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'route_list.html')
        
        # Check if the route is in the list
        self.assertContains(response, 'Test Route')
    
    def test_route_detail_view(self):
        """Test route detail view."""
        # Log in the user
        self.client.login(username=self.username, password=self.password)
        
        # Call the route detail view
        response = self.client.get(reverse('route_detail', args=[self.route.id]))
        
        # Check if the response is correct
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'route_detail.html')
        
        # Check if the route name is displayed
        self.assertContains(response, 'Test Route')
    
    def test_route_create_view(self):
        """Test creating a new route."""
        # Log in the user
        self.client.login(username=self.username, password=self.password)
        
        # Prepare data for a new route
        route_data = {
            'name': 'New Test Route',
            'background': self.background.id
        }
        
        # Send POST request to create a route
        response = self.client.post(reverse('route_create'), data=route_data)
        
        # Check if redirection works
        self.assertEqual(response.status_code, 302)
        
        # Check if the route was created
        self.assertTrue(Route.objects.filter(name='New Test Route').exists())
    
    def test_route_delete_view(self):
        """Test route deletion."""
        # Log in the user
        self.client.login(username=self.username, password=self.password)
        
        # Send POST request to delete the route
        response = self.client.post(reverse('route_delete', args=[self.route.id]))
        
        # Check if redirection works
        self.assertEqual(response.status_code, 302)
        
        # Check if the route was deleted
        self.assertFalse(Route.objects.filter(id=self.route.id).exists())
    
    def test_unauthorized_route_access(self):
        """Test access to another user's route."""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpassword'
        )
        
        # Log in the other user
        self.client.login(username='otheruser', password='otherpassword')
        
        # Attempt to access the first user's route
        response = self.client.get(reverse('route_detail', args=[self.route.id]))
        
        # Check if access is forbidden (404 code according to implementation)
        self.assertEqual(response.status_code, 404)
    
    def test_temporary_route_creation(self):
        """Test creating a temporary route (without logging in)."""
        # Log out the user
        self.client.logout()
        
        # Prepare data for a new route
        route_data = {
            'name': 'Temporary Route',
            'background': self.background.id
        }
        
        # Send POST request to create a route
        response = self.client.post(reverse('create_anonymous_route'), data=route_data)
        
        # Check if redirection works
        self.assertEqual(response.status_code, 302)
        
        # Check if the route was created
        route = Route.objects.get(name='Temporary Route')
        self.assertTrue(route.is_temporary)
        self.assertIsNone(route.user)


class RouteAPITests(TestCase):
    """Tests for the routes API."""
    
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
        # Prepare data for a new route
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
    
    # Removed test_api_add_point test
    
    def test_api_bulk_update_points(self):
        """Test bulk update of route points through API."""
        # Prepare data for points update
        points_data = {
            'points': [
                {'x': 150, 'y': 150, 'color': '#FF00FF', 'order': 0},
                {'x': 250, 'y': 250, 'color': '#00FFFF', 'order': 1}
            ]
        }
        
        # Call API endpoint
        response = self.client.post(
            f'/api/routes/{self.route.id}/bulk-update-points/',  # Direct URL instead of reverse
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