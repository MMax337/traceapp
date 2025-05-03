from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from routes.forms import RouteForm, RoutePointForm
from routes.models import BackgroundImage

class RouteFormTests(TestCase):
    """Testy dla formularza Route."""
    
    @classmethod
    def setUpTestData(cls):
        # Utwórz tło do testów
        cls.background = BackgroundImage.objects.create(
            name='Test Background',
            image=SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        )
    
    def test_valid_route_form(self):
        """Test poprawnego formularza trasy."""
        form_data = {
            'name': 'Test Route',
            'background': self.background.id
        }
        form = RouteForm(data=form_data)
        
        # Sprawdź, czy formularz jest ważny
        self.assertTrue(form.is_valid())
    
    def test_invalid_route_form(self):
        """Test niepoprawnego formularza trasy."""
        # Brak nazwy
        form_data = {
            'background': self.background.id
        }
        form = RouteForm(data=form_data)
        
        # Sprawdź, czy formularz jest nieważny
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)


class RoutePointFormTests(TestCase):
    """Testy dla formularza RoutePoint."""
    
    def test_valid_route_point_form(self):
        """Test poprawnego formularza punktu trasy."""
        # Dostosuj dane do faktycznej definicji formularza w twojej aplikacji
        form_data = {
            'x': '100.5',
            'y': '200.5',
            'color': '#FF0000',
            'order': 1
        }
        form = RoutePointForm(data=form_data)
        
        # Sprawdź formularz i wyświetl błędy w przypadku niepowodzenia
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        
        # Sprawdź, czy formularz jest ważny
        self.assertTrue(form.is_valid())
    
    def test_invalid_route_point_form(self):
        """Test niepoprawnego formularza punktu trasy."""
        # Brak współrzędnych
        form_data = {
            'color': '#FF0000'
        }
        form = RoutePointForm(data=form_data)
        
        # Sprawdź, czy formularz jest nieważny
        self.assertFalse(form.is_valid())
        self.assertIn('x', form.errors)
        self.assertIn('y', form.errors)