from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .models import User  # Add this import for the custom User model
import logging

logger = logging.getLogger(__name__)

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Successfully signed up!')
            logger.info(f'User {user.email} signed up.')
            return redirect('dashboard')
        else:
            logger.error('Signup form invalid: ' + str(form.errors))
            messages.error(request, 'There was an error signing up. Please check your details.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # Use email as username
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Successfully logged in!')
                logger.info(f'User {email} logged in.')
                return redirect('dashboard')
            else:
                logger.error(f'Authentication failed for email: {email}')
                messages.error(request, 'Invalid email or password.')
        else:
            logger.error('Login form invalid: ' + str(form.errors))
            messages.error(request, 'Invalid email or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Successfully logged out!')
    logger.info('User logged out.')
    return redirect('login')