from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from routes.models import Route, RoutePoint, BackgroundImage
from django.db.models import Max

User = get_user_model()

class RouteModelTests(TestCase):
    """Tests for the Route model."""
    
    @classmethod
    def setUpTestData(cls):
        # Create test user
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create background
        cls.background = BackgroundImage.objects.create(
            name='Test Background',
            image=SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        )
    
    def test_route_creation(self):
        """Test creating a new route."""
        route = Route.objects.create(
            name='Test Route',
            background=self.background,
            user=self.user
        )
        
        # Get route from database
        saved_route = Route.objects.get(id=route.id)
        
        # Check if route was correctly saved
        self.assertEqual(saved_route.name, 'Test Route')
        self.assertEqual(saved_route.background, self.background)
        self.assertEqual(saved_route.user, self.user)
        self.assertFalse(saved_route.is_temporary)
    
    def test_temporary_route_creation(self):
        """Test creating a temporary route."""
        route = Route.objects.create(
            name='Temporary Route',
            background=self.background,
            is_temporary=True
        )
        
        # Get route from database
        saved_route = Route.objects.get(id=route.id)
        
        # Check if route was correctly saved
        self.assertEqual(saved_route.name, 'Temporary Route')
        self.assertEqual(saved_route.background, self.background)
        self.assertIsNone(saved_route.user)
        self.assertTrue(saved_route.is_temporary)


class RoutePointModelTests(TestCase):
    """Tests for the RoutePoint model."""
    
    @classmethod
    def setUpTestData(cls):
        # Create test user
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create background
        cls.background = BackgroundImage.objects.create(
            name='Test Background',
            image=SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        )
        
        # Create route
        cls.route = Route.objects.create(
            name='Test Route',
            background=cls.background,
            user=cls.user
        )
    
    def test_route_point_creation(self):
        """Test creating a new route point."""
        point = RoutePoint.objects.create(
            route=self.route,
            x=100.5,
            y=200.5,
            color='#FF0000',
            order=0
        )
        
        # Get point from database
        saved_point = RoutePoint.objects.get(id=point.id)
        
        # Check if point was correctly saved
        self.assertEqual(saved_point.route, self.route)
        self.assertEqual(saved_point.x, 100.5)
        self.assertEqual(saved_point.y, 200.5)
        self.assertEqual(saved_point.color, '#FF0000')
        self.assertEqual(saved_point.order, 0)
    
    def test_route_point_ordering(self):
        """Test ordering of route points."""
        # Create several points with different orders
        RoutePoint.objects.create(route=self.route, x=100, y=100, color='#FF0000', order=2)
        RoutePoint.objects.create(route=self.route, x=200, y=200, color='#00FF00', order=0)
        RoutePoint.objects.create(route=self.route, x=300, y=300, color='#0000FF', order=1)
        
        # Get points sorted by order
        points = RoutePoint.objects.filter(route=self.route).order_by('order')
        
        # Check if points are in the correct order
        self.assertEqual(points[0].x, 200)
        self.assertEqual(points[1].x, 300)
        self.assertEqual(points[2].x, 100)