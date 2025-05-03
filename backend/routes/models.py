from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

class BackgroundImage(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='backgrounds/')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                            on_delete=models.CASCADE,
                            null=True, blank=True)

    def __str__(self):
        return self.name

class Route(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             null=True, blank=True)

    background = models.ForeignKey(BackgroundImage, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_temporary = models.BooleanField(default=False)

def __str__(self):
    if self.user:
        return f"{self.name} ({self.user.username})"
    else:
        return f"{self.name} (Anonymous)"

class RoutePoint(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='points')
    x = models.FloatField()
    y = models.FloatField()
    color = models.CharField(max_length=7, default='#FF0000')  # Default to red
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"({self.x}, {self.y})"
