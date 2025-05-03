from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from routes.forms import RouteForm, RoutePointForm
from routes.models import BackgroundImage

class RouteFormTests(TestCase):
    """Tests for the Route form."""
    
    @classmethod
    def setUpTestData(cls):
        # Create background for tests
        cls.background = BackgroundImage.objects.create(
            name='Test Background',
            image=SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        )
    
    def test_valid_route_form(self):
        """Test for a valid route form."""
        form_data = {
            'name': 'Test Route',
            'background': self.background.id
        }
        form = RouteForm(data=form_data)
        
        # Check if the form is valid
        self.assertTrue(form.is_valid())
    
    def test_invalid_route_form(self):
        """Test for an invalid route form."""
        # Missing name
        form_data = {
            'background': self.background.id
        }
        form = RouteForm(data=form_data)
        
        # Check if the form is invalid
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)


class RoutePointFormTests(TestCase):
    """Tests for the RoutePoint form."""
    
    def test_valid_route_point_form(self):
        """Test for a valid route point form."""
        # Adjust the data to match the actual form definition in your application
        form_data = {
            'x': '100.5',
            'y': '200.5',
            'color': '#FF0000',
            'order': 1
        }
        form = RoutePointForm(data=form_data)
        
        # Check the form and display errors in case of failure
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        
        # Check if the form is valid
        self.assertTrue(form.is_valid())
    
    def test_invalid_route_point_form(self):
        """Test for an invalid route point form."""
        # Missing coordinates
        form_data = {
            'color': '#FF0000'
        }
        form = RoutePointForm(data=form_data)
        
        # Check if the form is invalid
        self.assertFalse(form.is_valid())
        self.assertIn('x', form.errors)
        self.assertIn('y', form.errors)