from rest_framework import serializers
from .models import Route, RoutePoint, BackgroundImage
from users.serializers import UserSerializer

class BackgroundImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackgroundImage
        fields = ['id', 'name', 'image']

class RoutePointSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutePoint
        fields = ['id', 'x', 'y', 'color', 'order']
        read_only_fields = ['id']

class RoutePointDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutePoint
        fields = ['id', 'x', 'y', 'color', 'order', 'route']
        read_only_fields = ['id', 'route']

class RouteSerializer(serializers.ModelSerializer):
    points = RoutePointSerializer(many=True, read_only=True)

    class Meta:
        model = Route
        fields = ['id', 'name', 'background', 'points', 'is_temporary']
        read_only_fields = ['id', 'is_temporary']

class RouteDetailSerializer(serializers.ModelSerializer):
    points = RoutePointSerializer(many=True, read_only=True)
    background = BackgroundImageSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Route
        fields = ['id', 'name', 'background', 'user', 'points', 'is_temporary']
        read_only_fields = ['id']

class RouteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ['id', 'name', 'background']
        read_only_fields = ['id']