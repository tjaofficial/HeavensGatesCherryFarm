from django.shortcuts import render, redirect
from ..forms import treeLogs_form
from ..models import individualTrees_model
from django.contrib.auth.decorators import login_required

lock = login_required(login_url='Login')

@lock
def addLog2_view(request, locationID2, areaID2, treeID2):
    noFooter = True
    smallHeader = True
    sideBar = True
    treeData = individualTrees_model.objects.get(locationID__locationID=locationID2, areaID__areaID=areaID2, treeID=treeID2)
    initial_data = {
        'treeID': treeData
    }
    logForm = treeLogs_form(initial=initial_data)
    
    if request.method == 'POST':
        formData = treeLogs_form(request.POST)
        print(formData.errors)
        if formData.is_valid():
            formData.save()
            
            return redirect('treeData', locationID2, areaID2, treeID2)
    return render(request, 'addLog.html',{
        'locationID': locationID2, 
        'areaID': areaID2, 
        'treeID': treeID2, 
        'logForm': logForm,
        'smallHeader': smallHeader,
        'noFooter': noFooter,
        'sideBar': sideBar
    })