from django.shortcuts import render, redirect
from ..forms import locationTree_form
from ..models import locationTree_model
from..utils import selectNextID
from django.contrib.auth.decorators import login_required

lock = login_required(login_url='Login')

@lock
def addLocation_view(request):
    noFooter = True
    smallHeader = True
    sideBar = True
    addForm = locationTree_form
    locationsData = locationTree_model.objects.all()
    newID = selectNextID(locationsData.order_by('-locationID'), 'location')
    
    if request.method == 'POST':
        print(request.POST)
        formData = locationTree_form(request.POST)
        if formData.is_valid():
            formData.save()
            return redirect('addLocation')
        
    return render(request, 'addLocation.html', {
        'addForm': addForm, 
        'locationsData': locationsData, 
        'newID': newID, 
        'smallHeader': smallHeader,
        'noFooter': noFooter,
        'addForm': addForm,
        'sideBar': sideBar
    })