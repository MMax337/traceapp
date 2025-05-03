import json
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from routes.models import Route, RoutePoint

def register(request):
    """Rejestracja nowego użytkownika."""

    if request.method != 'POST':
        form = UserCreationForm()
        return render(request, 'register.html', {'form': form})

    form = UserCreationForm(request.POST)
    if not form.is_valid():
        return render(request, 'register.html', {'form': form})

    # Create and login user
    user = form.save()
    login(request, user)

    # Process routes from localStorage
    process_localStorage_routes(request, user)

    if 'route_id' in request.session:
        del request.session['route_id']
    if 'temp_points' in request.session:
        del request.session['temp_points']

    messages.success(request, 'Account created successfully!')
    return redirect(reverse('route_create'))

def process_localStorage_routes(request, user):
    """Process routes from localStorage."""
    points_data = request.POST.get('points_data')
    if not points_data:
        return

    try:
        routes_json = json.loads(points_data)
        for route_id, route_data in routes_json.items():
            try:
                # Get the route if it exists
                route = Route.objects.get(id=route_id, is_temporary=True)
                
                # Update the route to belong to the user
                route.user = user
                route.is_temporary = False
                route.save()
                
                # Clear existing points
                route.points.all().delete()

                # Create points from saved data
                for idx, point_data in enumerate(route_data.get('points', [])):
                    print("creating point, ", point_data)
                    RoutePoint.objects.create(
                        route=route,
                        x=point_data['x'],
                        y=point_data['y'],
                        color=point_data.get('color', '#ef4444'),
                        order=point_data.get('order', idx)
                    )
            except Route.DoesNotExist:
                print("not exist why????")
            except Exception as e:
                print("err here ", e)
                print("user ", user)
    except Exception:
        pass
