from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from . import api_views
from . import views

# Create a router for our API
router = DefaultRouter()
router.register(r'backgrounds', api_views.BackgroundImageViewSet, basename='background')
router.register(r'routes', api_views.RouteViewSet, basename='route')

# Create a nested router for route points
route_router = NestedDefaultRouter(router, r'routes', lookup='route')
route_router.register(r'points', api_views.RoutePointViewSet, basename='route-point')

# The API URLs are now automatically determined by the router
urlpatterns = [
    # Web Views
    path('', views.index, name='index'),
    path('routes/', views.route_list, name='route_list'),
    path('routes/create/', views.route_create, name='route_create'),
    path('routes/<int:route_id>/delete/', views.route_delete, name='route_delete'),
    path('routes/create/anonymous', views.create_anonymous_route, name='create_anonymous_route'),
    path('routes/<int:route_id>/', views.route_detail, name='route_detail'),
    path('points/<int:point_id>/delete/', views.delete_point, name='delete_point'),
    
    # API URLs
    path('api/', include(router.urls)),
    path('api/', include(route_router.urls)),
    path('api/routes/<int:route_pk>/bulk-update-points/', api_views.BulkRoutePointUpdateView.as_view(), name='bulk-update-points'),
    
    # Authentication for API
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]