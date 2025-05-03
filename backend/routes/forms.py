from django import forms
from .models import Route, RoutePoint

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['background', 'name']

class RoutePointForm(forms.ModelForm):
    class Meta:
        model = RoutePoint
        fields = ['x', 'y', 'order', 'color']
