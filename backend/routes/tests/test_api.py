from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from routes.models import Route, RoutePoint, BackgroundImage
import json

User = get_user_model()

class MinimalRouteAPITests(TestCase):
    """Minimalne testy dla API tras - tylko te, które są na pewno dostępne."""
    
    def setUp(self):
        # Utwórz klienta testowego
        self.client = Client()
        
        # Utwórz użytkownika testowego
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create_user(
            username=self.username,
            email='test@example.com',
            password=self.password
        )
        
        # Utwórz tło
        self.background = BackgroundImage.objects.create(
            name='Test Background',
            image=SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        )
        
        # Utwórz trasę dla użytkownika
        self.route = Route.objects.create(
            name='Test Route',
            background=self.background,
            user=self.user
        )
        
        # Uzyskaj token API dla użytkownika
        from rest_framework.authtoken.models import Token
        self.token = Token.objects.create(user=self.user)
        self.auth_header = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}
    
    def test_api_get_routes(self):
        """Test pobierania tras przez API."""
        # Wywołaj endpoint API
        response = self.client.get(
            reverse('route-list'),
            **self.auth_header
        )
        
        # Sprawdź, czy odpowiedź jest poprawna
        self.assertEqual(response.status_code, 200)
        
        # Sprawdź, czy trasa jest w odpowiedzi
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Test Route')
    
    def test_api_create_route(self):
        """Test tworzenia trasy przez API."""
        # Przygotuj dane dla nowej trasy
        route_data = {
            'name': 'API Test Route',
            'background': self.background.id
        }
        
        # Wywołaj endpoint API
        response = self.client.post(
            reverse('route-list'),
            data=json.dumps(route_data),
            content_type='application/json',
            **self.auth_header
        )
        
        # Sprawdź, czy odpowiedź jest poprawna
        self.assertEqual(response.status_code, 201)
        
        # Sprawdź, czy trasa została utworzona
        data = json.loads(response.content)
        self.assertEqual(data['name'], 'API Test Route')
        self.assertTrue(Route.objects.filter(name='API Test Route').exists())
    
    def test_api_bulk_update_points(self):
        """Test masowej aktualizacji punktów trasy przez API."""
        # Przygotuj dane dla aktualizacji punktów
        points_data = {
            'points': [
                {'x': 150, 'y': 150, 'color': '#FF00FF', 'order': 0},
                {'x': 250, 'y': 250, 'color': '#00FFFF', 'order': 1}
            ]
        }
        
        # Wywołaj endpoint API (używając bezpośredniego URL)
        response = self.client.post(
            f'/api/routes/{self.route.id}/bulk-update-points/',
            data=json.dumps(points_data),
            content_type='application/json',
            **self.auth_header
        )
        
        # Sprawdź, czy odpowiedź jest poprawna
        self.assertEqual(response.status_code, 200)
    
        # Sprawdź, czy punkty zostały zaktualizowane
        updated_points = RoutePoint.objects.filter(route=self.route).order_by('order')
        self.assertEqual(len(updated_points), 2)
        self.assertEqual(updated_points[0].x, 150)
        self.assertEqual(updated_points[1].x, 250)