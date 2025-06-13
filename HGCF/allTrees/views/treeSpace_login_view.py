from django.shortcuts import render, redirect
from ..forms import CreateUserForm
from ..models import locationTree_model
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout

def login_view(request):
    login_error = {"error":False, "message":''}
    locationData = locationTree_model.objects.all()
    if locationData.exists():
        goLocation = locationData[0].locationID
    else:
        goLocation = 'addLocation'
        
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username.lower(), password=password)

        if user is not None:
            login(request, user)
            
            return redirect('dashboard')
        else:
            login_error["error"] = True
            login_error["message"] = 'Incorrect username or password'

    return render(request, 'treeSpace/treeSpace_login.html', {

    })

def logout_view(request):
    logout(request)

    return redirect('login')

def profile_redirect(request, facility):
    return redirect('../' + facility + '/profile/main')

    return render(request, 'profile.hmtl', {

    })