from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from user.forms import RegisterForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import PasswordChangeForm


@csrf_protect
def register(request):
    """
    View function to handle user registration.

    :param request: The HTTP request object.
    :return: Rendered registration form or redirect to the login page on successful registration.
    """
    if request.method == "POST":
        f = RegisterForm(request.POST)
        if f.is_valid():
            username = f.cleaned_data.get('username')
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username is already taken')
                return redirect('register')
            email = f.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'User with the provided email already exists')
                return redirect('register')
            password1 = f.cleaned_data.get('password1')
            password2 = f.cleaned_data.get('password2')
            if password1 == password2:
                f.save()
                messages.add_message(request, messages.INFO,
                                     'Registration successful! Please login with your credentials.')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match')
                return redirect('register')
    else:
        f = RegisterForm()

    return render(request, 'user/register.html', {'form': f})


@login_required
def profile(request):
    """
    View function to display the user's profile.

    :param request: The HTTP request object.
    :return: Rendered profile template with the user's username and email.
    """
    user = request.user
    context = {
        'username': user.username,
        'email': user.email
    }
    return render(request, 'registration/profile.html', context)


@csrf_protect
def password(request):
    """
    View function to handle password change.

    :param request: The HTTP request object.
    :return: Rendered password change form or redirect to the password change page on successful update.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully changed.')
            return redirect('password')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)

    context = {
        'form': form
    }
    return render(request, 'registration/password_change.html', context)
