from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Max

from .models import Route, RoutePoint, BackgroundImage
from .serializers import (
    RouteSerializer,
    RouteDetailSerializer,
    RoutePointSerializer,
    RoutePointDetailSerializer,
    BackgroundImageSerializer,
    RouteCreateSerializer
)

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        return obj.user == request.user

class BackgroundImageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows background images to be viewed.
    """
    queryset = BackgroundImage.objects.all()
    serializer_class = BackgroundImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class RouteViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows routes to be viewed or edited.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        This view should return a list of all routes for the currently authenticated user,
        and any temporary routes in the session.
        """
        user = self.request.user
        if user.is_authenticated:
            # Return user's routes and any temporary routes in session
            route_id = self.request.session.get('route_id')
            if route_id:
                return Route.objects.filter(user=user) | Route.objects.filter(id=route_id, is_temporary=True)
            return Route.objects.filter(user=user)
        else:
            # For anonymous users, only return temporary routes in session
            route_id = self.request.session.get('route_id')
            if route_id:
                return Route.objects.filter(id=route_id, is_temporary=True)
            return Route.objects.none()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RouteDetailSerializer
        elif self.action == 'create':
            return RouteCreateSerializer
        return RouteSerializer

    def perform_create(self, serializer):
        """Save the route owner if user is authenticated."""
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user, is_temporary=False)
        else:
            # For anonymous users, create a temporary route
            instance = serializer.save(is_temporary=True)
            self.request.session['route_id'] = instance.id

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def claim(self, request, pk=None):
        """
        Claim a temporary route by assigning the current user and marking it as permanent.
        """
        route = self.get_object()

        if not route.is_temporary:
            return Response(
                {"detail": "This route is already claimed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        route.user = request.user
        route.is_temporary = False
        route.save()

        # Clear the session if this was the temporary route stored there
        if request.session.get('route_id') == route.id:
            del request.session['route_id']

        return Response(
            {"detail": "Route claimed successfully."},
            status=status.HTTP_200_OK
        )

class RoutePointViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows route points to be viewed or edited.
    """
    serializer_class = RoutePointSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        This view should return a list of all points for the specified route.
        """
        route_id = self.kwargs.get('route_pk')
        if route_id:
            return RoutePoint.objects.filter(route_id=route_id).order_by('order')
        return RoutePoint.objects.none()

    def get_serializer_class(self):
        if self.action in ['retrieve', 'create', 'update', 'partial_update']:
            return RoutePointDetailSerializer
        return RoutePointSerializer

    def perform_create(self, serializer):
        """
        Create a new point and automatically set the route and order.
        """
        route_id = self.kwargs.get('route_pk')
        route = get_object_or_404(Route, id=route_id)

        # Check if user is owner of route or if route is temporary and in session
        if route.user and route.user != self.request.user:
            self.permission_denied(self.request, message="You do not have permission to add points to this route.")

        # Get the highest order value and add 1
        max_order = RoutePoint.objects.filter(route=route).aggregate(Max('order'))['order__max']
        next_order = 0 if max_order is None else max_order + 1

        serializer.save(route=route, order=next_order)

    def perform_update(self, serializer):
        """
        Check if user has permission to update this point.
        """
        point = self.get_object()
        route = point.route

        if route.user and route.user != self.request.user:
            self.permission_denied(self.request, message="You do not have permission to update points on this route.")

        serializer.save()

    def perform_destroy(self, instance):
        """
        Check if user has permission to delete this point.
        """
        route = instance.route

        if route.user and route.user != self.request.user:
            self.permission_denied(self.request, message="You do not have permission to delete points from this route.")

        instance.delete()

        # Reorder remaining points to ensure consistent ordering
        points = RoutePoint.objects.filter(route=route).order_by('order')
        for index, point in enumerate(points):
            if point.order != index:
                point.order = index
                point.save()

class BulkRoutePointUpdateView(APIView):
    """
    API endpoint to update multiple route points at once.
    """
    permission_classes = [permissions.AllowAny]


    def post(self, request, route_pk):
        route = get_object_or_404(Route, pk=route_pk)

        # Check if user is owner of route or if route is temporary and in session
        if route.user and route.user != request.user and not (route.is_temporary and request.session.get('route_id') == route.id):
            return Response(
                {"detail": "You do not have permission to update points on this route."},
                status=status.HTTP_403_FORBIDDEN
            )
        points_data = request.data.get('points', [])

        # Get existing points ordered by order
        existing_points = list(RoutePoint.objects.filter(route=route).order_by('order'))

        for i, point_data in enumerate(points_data):
            if i < len(existing_points):
                # Update existing point
                point = existing_points[i]
                point.x = point_data['x']
                point.y = point_data['y']
                point.color = point_data.get('color', point.color)
                point.order = i
                point.save()
            else:
                # Create new point
                RoutePoint.objects.create(
                    route=route,
                    x=point_data['x'],
                    y=point_data['y'],
                    color=point_data.get('color', '#FF0000'),
                    order=i
                )

        # Delete extra points that were not updated
        if len(existing_points) > len(points_data):
            for point in existing_points[len(points_data):]:
                point.delete()

        return Response({"status": "success"})