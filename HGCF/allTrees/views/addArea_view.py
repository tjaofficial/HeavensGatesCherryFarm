from django.shortcuts import render, redirect
from ..forms import areaTree_form
from ..models import areaTree_model, locationTree_model
from ..utils import selectNextID
from django.contrib.auth.decorators import login_required

lock = login_required(login_url='Login')

@lock
def addArea_view(request, locationID2):
    noFooter = True
    smallHeader = True
    sideBar = True
    addForm = areaTree_form
    location = locationTree_model.objects.get(locationID=locationID2)
    areasData = areaTree_model.objects.filter(locationID=location)
    newID = selectNextID(areasData.order_by('-areaID'), 'area')
    print(locationID2)
    if request.method == 'POST':
        print(request.POST)
        newLocationID = locationTree_model.objects.get(locationID=request.POST['locationID'])
        dataCopy = request.POST.copy()
        dataCopy['locationID'] = newLocationID
        formData = areaTree_form(dataCopy)
        print(formData.errors)
        if formData.is_valid():
            print('Hello')
            formData.save()
            return redirect('addArea', locationID2)
    return render(request, 'addArea.html', {
        'newID': newID, 
        'location': location, 
        'areasData': areasData, 
        'locationID': locationID2,
        'smallHeader': smallHeader,
        'noFooter': noFooter,
        'addForm': addForm,
        'sideBar': sideBar
    })