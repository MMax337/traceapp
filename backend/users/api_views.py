from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user and return an authentication token.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    
    if not username or not password:
        return Response(
            {'error': 'Please provide both username and password'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if username already exists
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create user
    user = User.objects.create_user(
        username=username,
        password=password,
        email=email
    )

    # Create token
    token, created = Token.objects.get_or_create(user=user)

    # Check for temporary routes in session if a session ID is provided
    session_key = request.data.get('session_key')
    route_id = None

    if session_key:
        from django.contrib.sessions.models import Session
        from routes.models import Route  # Adjust import based on your app name

        try:
            session = Session.objects.get(session_key=session_key)
            session_data = session.get_decoded()
            route_id = session_data.get('route_id')

            if route_id:
                # Claim the temporary route
                route = get_object_or_404(Route, id=route_id, is_temporary=True)
                route.user = user
                route.is_temporary = False
                route.save()

                # Clear the session
                session_data.pop('route_id')
                session.session_data = session_data
                session.save()
        except (Session.DoesNotExist, Route.DoesNotExist):
            pass
    
    return Response(
        {
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'claimed_route_id': route_id
        },
        status=status.HTTP_201_CREATED
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Authenticate a user and return a token.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Please provide both username and password'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if not user:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    token, created = Token.objects.get_or_create(user=user)
    
    return Response(
        {
            'token': token.key,
            'user_id': user.id,
            'username': user.username
        },
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
def logout_user(request):
    """
    Logout a user by deleting their token.
    """
    # Delete the user's token to logout
    request.user.auth_token.delete()
    
    return Response(
        {'message': 'Successfully logged out'},
        status=status.HTTP_200_OK
    )