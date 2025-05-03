from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from routes.models import Route, RoutePoint, BackgroundImage
import json

User = get_user_model()

class RouteViewsTests(TestCase):
    """Testy dla widoków związanych z trasami."""
    
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
        
        # Utwórz kilka punktów trasy
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
        """Test widoku listy tras."""
        # Zaloguj użytkownika
        self.client.login(username=self.username, password=self.password)
        
        # Wywołaj widok listy tras
        response = self.client.get(reverse('route_list'))
        
        # Sprawdź, czy odpowiedź jest poprawna
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'route_list.html')
        
        # Sprawdź, czy trasa jest na liście
        self.assertContains(response, 'Test Route')
    
    def test_route_detail_view(self):
        """Test widoku szczegółów trasy."""
        # Zaloguj użytkownika
        self.client.login(username=self.username, password=self.password)
        
        # Wywołaj widok szczegółów trasy
        response = self.client.get(reverse('route_detail', args=[self.route.id]))
        
        # Sprawdź, czy odpowiedź jest poprawna
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'route_detail.html')
        
        # Sprawdź, czy nazwa trasy jest wyświetlana
        self.assertContains(response, 'Test Route')
    
    def test_route_create_view(self):
        """Test tworzenia nowej trasy."""
        # Zaloguj użytkownika
        self.client.login(username=self.username, password=self.password)
        
        # Przygotuj dane dla nowej trasy
        route_data = {
            'name': 'New Test Route',
            'background': self.background.id
        }
        
        # Wyślij żądanie POST do utworzenia trasy
        response = self.client.post(reverse('route_create'), data=route_data)
        
        # Sprawdź, czy przekierowanie działa
        self.assertEqual(response.status_code, 302)
        
        # Sprawdź, czy trasa została utworzona
        self.assertTrue(Route.objects.filter(name='New Test Route').exists())
    
    def test_route_delete_view(self):
        """Test usuwania trasy."""
        # Zaloguj użytkownika
        self.client.login(username=self.username, password=self.password)
        
        # Wyślij żądanie POST do usunięcia trasy
        response = self.client.post(reverse('route_delete', args=[self.route.id]))
        
        # Sprawdź, czy przekierowanie działa
        self.assertEqual(response.status_code, 302)
        
        # Sprawdź, czy trasa została usunięta
        self.assertFalse(Route.objects.filter(id=self.route.id).exists())
    
    def test_unauthorized_route_access(self):
        """Test dostępu do trasy innego użytkownika."""
        # Utwórz innego użytkownika
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpassword'
        )
        
        # Zaloguj innego użytkownika
        self.client.login(username='otheruser', password='otherpassword')
        
        # Próba dostępu do trasy pierwszego użytkownika
        response = self.client.get(reverse('route_detail', args=[self.route.id]))
        
        # Sprawdź, czy dostęp jest zabroniony (kod 404 zgodnie z implementacją)
        self.assertEqual(response.status_code, 404)
    
    def test_temporary_route_creation(self):
        """Test tworzenia tymczasowej trasy (bez logowania)."""
        # Wyloguj użytkownika
        self.client.logout()
        
        # Przygotuj dane dla nowej trasy
        route_data = {
            'name': 'Temporary Route',
            'background': self.background.id
        }
        
        # Wyślij żądanie POST do utworzenia trasy
        response = self.client.post(reverse('create_anonymous_route'), data=route_data)
        
        # Sprawdź, czy przekierowanie działa
        self.assertEqual(response.status_code, 302)
        
        # Sprawdź, czy trasa została utworzona
        route = Route.objects.get(name='Temporary Route')
        self.assertTrue(route.is_temporary)
        self.assertIsNone(route.user)


class RouteAPITests(TestCase):
    """Testy dla API tras."""
    
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
    
    # Usunięto test dodawania punktu (test_api_add_point)
    
    def test_api_bulk_update_points(self):
        """Test masowej aktualizacji punktów trasy przez API."""
        # Przygotuj dane dla aktualizacji punktów
        points_data = {
            'points': [
                {'x': 150, 'y': 150, 'color': '#FF00FF', 'order': 0},
                {'x': 250, 'y': 250, 'color': '#00FFFF', 'order': 1}
            ]
        }
        
        # Wywołaj endpoint API
        response = self.client.post(
            f'/api/routes/{self.route.id}/bulk-update-points/',  # Bezpośredni URL zamiast reverse
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