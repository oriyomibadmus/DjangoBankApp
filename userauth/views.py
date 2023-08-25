from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

#Custom Import
from userauth.forms import UserRegisterForm
from userauth.models import User

# Registration View
def RegisterView(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'User Registered Successfully')
            return redirect('core:index')
    else:
        form = UserRegisterForm()

    context = {
        'form': form
    }
    return render(request, 'userauth/register.html', context)

# Login View
def LoginView(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'You have been logged in successfully')
                return redirect('core:index')
            else:
                messages.warning(request, 'The email or password does not match a user')
                return redirect('userauth:login')
        except:
            messages.warning(request, 'User does not exiist')

    return render(request, 'userauth/login.html')

# Logout View
def LogoutView(request):
    logout(request)
    messages.success(request,'You have been logged out successfully')
    return redirect('userauth:login')