from django.db import models
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import Route, RoutePoint, BackgroundImage
from .forms import RouteForm, RoutePointForm

User = get_user_model()

def index(request):
    return render(request, 'index.html')


@login_required
def route_list(request):
    """Lista tras użytkownika."""
    routes = Route.objects.filter(user=request.user)
    return render(request, 'route_list.html', {'routes': routes})

@login_required
def route_create(request):
    """Tworzenie nowej trasy dla zalogowanego użytkownika."""
    user = request.user

    if request.method == 'POST':
        form = RouteForm(request.POST)

        if 'add_background' in request.POST and request.FILES.get('background_image'):
            # Handle background upload
            background_name = request.POST.get('background_name', 'Własne tło')
            background_image = request.FILES['background_image']

            # Create new background
            BackgroundImage.objects.create(
                name=background_name,
                image=background_image,
                user=user
            )

            messages.success(request, f"Dodano nowe tło: {background_name}")

            # Just create a new empty form - no need to set queryset yet
            form = RouteForm()
            return redirect('route_create')
        elif 'delete_background' in request.POST:
            # Handle background deletion
            background_id = request.POST.get('background_id')
            try:
                background = BackgroundImage.objects.get(id=background_id, user=user)
                background_name = background.name
                background.delete()
                messages.success(request, f"Usunięto tło: {background_name}")
            except BackgroundImage.DoesNotExist:
                messages.error(request, "Nie znaleziono tła lub nie masz uprawnień do jego usunięcia")
            
            return redirect('route_create')
        elif form.is_valid():
            # Create route if form is valid
            route = form.save(commit=False)
            route.user = user
            route.save()
            return redirect('route_detail', route_id=route.id)
    else:
        # For GET requests, just create an empty form
        form = RouteForm()

    standard_backgrounds = BackgroundImage.objects.filter(user=None)
    user_backgrounds = BackgroundImage.objects.filter(user=user)

    form.fields['background'].queryset = standard_backgrounds | user_backgrounds

    # Get recent routes - just once for all paths
    recent_routes = Route.objects.filter(user=user).order_by('-id')[:4]

    # Render the template with all context data
    return render(request, 'route_create.html', {
        'form': form,
        'backgrounds': standard_backgrounds,
        'user_backgrounds': user_backgrounds,
        'routes': recent_routes,
    })

def create_anonymous_route(request):
    """Tworzenie tymczasowej trasy dla niezalogowanego użytkownika."""
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            background = form.cleaned_data['background']
            if background.user is not None:
                return Http404("Nie możesz użyć tego tła. Wybierz tło publiczne.")

            route = form.save(commit=False)
            route.is_temporary = True
            route.save()

            request.session['route_id'] = route.id

            messages.success(request, "Trasa została utworzona. Możesz teraz dodać punkty.")
            return redirect('route_detail', route_id=route.id)

    backgrounds = BackgroundImage.objects.filter(user=None)
    form = RouteForm()
    return render(request, 'route_create.html', {
        'form': form,
        'backgrounds': backgrounds,
    })

def route_detail(request, route_id):
    if request.user.is_authenticated:
        route = get_object_or_404(
            Route,
            id=route_id,
            user=request.user
        )
    else:
        route = get_object_or_404(
            Route,
            id=route_id,
            is_temporary=True
        )

        if request.session.get('route_id') != route_id:
            messages.error(request, "You don't have permission to view this route.")
            return redirect('index')

    if request.method == 'POST':
        if 'save_name' in request.POST:
            new_name = request.POST.get('name')
            if new_name:
                route.name = new_name
                route.save()
                messages.success(request, "Route name updated successfully!")
                return redirect('route_detail', route_id=route.id)
        else:
            point_form = RoutePointForm(request.POST)
            if point_form.is_valid():
                point = point_form.save(commit=False)
                point.route = route

                max_order = route.points.aggregate(models.Max('order'))['order__max']
                point.order = 0 if max_order is None else max_order + 1

                point.save()
                return redirect('route_detail', route_id=route.id)

    points = route.points.all().order_by('order')
    point_form = RoutePointForm()
    context = {
        'route': route,
        'points': points,
        'point_form': point_form,
        'preset_colors': ['#ef4444', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#000000'],
        'is_temporary': route.is_temporary,
        'session_key': request.session.session_key,
    }
    
    return render(request, 'route_detail.html', context)

@login_required
def delete_point(request, point_id):
    point = get_object_or_404(RoutePoint, id=point_id)
    
    if point.route.user != request.user:
        messages.error(request, "You don't have permission to delete this point.")
        return redirect('route_list')


@login_required
def route_delete(request, route_id):
    route = get_object_or_404(Route, id=route_id, user=request.user)
    
    if request.method == 'POST':
        route_name = route.name
        
        route.delete()
        
        messages.success(request, f"Trasa '{route_name}' została usunięta.")
        return redirect('route_list')
    
    return render(request, 'route_confirm_delete.html', {'route': route})