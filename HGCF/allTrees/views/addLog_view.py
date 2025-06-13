from django.shortcuts import render, redirect # type: ignore
from ..forms import treeLogs_form
from ..models import individualTrees_model
from django.contrib.auth.decorators import login_required # type: ignore

lock = login_required(login_url='login')

@lock
def addLog_view(request, locationID, areaID, treeID):
    noFooter = True
    smallHeader = True
    sideBar = True
    treeData = individualTrees_model.objects.get(areaID__areaID=areaID, treeID=treeID)
    initial_data = {
        'treeID': treeData
    }
    logForm = treeLogs_form(initial=initial_data)
    
    if request.method == 'POST':
        formData = treeLogs_form(request.POST)
        print(formData.errors)
        if formData.is_valid():
            formData.save()
            
            return redirect('treeData', locationID, areaID, treeID)
    return render(request, 'addLog.html',{
        'locationID': locationID, 
        'areaID': areaID, 
        'treeID': treeID, 
        'logForm': logForm,
        'smallHeader': smallHeader,
        'noFooter': noFooter,
        'sideBar': sideBar
    })