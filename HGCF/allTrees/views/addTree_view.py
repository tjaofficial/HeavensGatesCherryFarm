from django.shortcuts import render, redirect
from ..models import individualTrees_model, areaTree_model, tree_qr, locationTree_model
from ..forms import individualTrees_form
from ..utils import alphabetKey, selectNextID
import json
from django.contrib.auth.decorators import login_required

lock = login_required(login_url='Login')

@lock
def addTree_view(request, locationID2, areaID2):
    noFooter = True
    smallHeader = True
    sideBar = True
    addForm = individualTrees_form
    location = locationTree_model.objects.get(locationID=locationID2)
    areaData = areaTree_model.objects.get(areaID=areaID2, locationID=location)
    treeData = individualTrees_model.objects.filter(locationID=location, areaID=areaData)
    print(treeData)
    
    treeList = []
    if treeData.exists():
        for tree in treeData:
            treeList.append(tree.treeID)
    treeList = json.dumps(treeList)
    gridWidth = areaData.widthByTree
    indexWidth = gridWidth + 1
    
    def letterNumber(number):
        charNumber = 64 + number
        print(chr(charNumber))

    letterNumber(gridWidth)
    columnList = []
    for x in range(65, (65+gridWidth)):
        columnList.append(chr(x))
    columnList.insert(0, "-")
    print(columnList)


    gridlength = areaData.lengthByTree
    rowRange = range(1, int(gridlength) + 1)
    print(gridlength)
    print(treeList)

    if request.method == "POST":
        print(request.POST)
        copyRequest = request.POST.copy()
        copyRequest['locationID'] = location
        copyRequest['areaID'] = areaData
        copyRequest['treeID'] = str(request.POST['row']) + '-' + str(request.POST['column'])
        
        formData = individualTrees_form(copyRequest)
        print(formData.errors)
        if formData.is_valid():
            A = formData.save()
            QRs = tree_qr(treeID=A, url="http://127.0.0.1:8000/treeData/"+A.locationID.locationID+"/"+ A.areaID.areaID +"/"+ A.treeID)
            QRs.save()
            
            return redirect('addTree', locationID2, areaID2)
    return render(request, 'addTree.html', {
        'rowRange': rowRange, 
        'columnList': columnList, 
        'addForm': addForm, 
        'treeData': treeData, 
        'locationID': locationID2, 
        'areaID': areaID2, 
        'gridWidth': gridWidth, 
        'gridlength': gridlength, 
        'treeList': treeList, 
        'gridRange': range(1,((gridlength*gridWidth)+1)),
        'smallHeader': smallHeader,
        'noFooter': noFooter,
        'indexWidth': indexWidth,
        'sideBar': sideBar
    })