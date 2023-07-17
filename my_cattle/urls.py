
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, PasswordResetView
from my_cattle.views import main
from user.views import profile, register, password
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', main, name='main'),
    path('', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('my_farm/', include("my_farm.urls")),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('register/', register, name='register'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('profile/', profile, name='profile'),
    path('profile/password_change/', password, name='password_change'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

