from django.shortcuts import render, redirect # type: ignore
from ..forms import locationTree_form, areaTree_form, individualTrees_form
from ..models import locationTree_model, areaTree_model, individualTrees_model, tree_qr
from..utils import selectNextID
from django.contrib.auth.decorators import login_required # type: ignore
from django.conf import settings # type: ignore
import json
from datetime import datetime

lock = login_required(login_url='login')

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
            return redirect('location_list')
        
    return render(request, 'tree_grid/add_pages/add_location.html', {
        'addForm': addForm, 
        'locationsData': locationsData, 
        'newID': newID, 
        'smallHeader': smallHeader,
        'noFooter': noFooter,
        'addForm': addForm,
        'sideBar': sideBar
    })

@lock
def addArea_view(request, location_id):
    noFooter = True
    smallHeader = True
    sideBar = True
    today = datetime.now().date()
    addForm = areaTree_form
    location = locationTree_model.objects.get(id=location_id)
    areasData = areaTree_model.objects.filter(locationID=location)
    newID = selectNextID(areasData.order_by('-areaID'), 'area')
    if request.method == 'POST':
        print(request.POST)
        newLocationID = locationTree_model.objects.get(locationID=request.POST['locationID'])
        dataCopy = request.POST.copy()
        dataCopy['locationID'] = newLocationID
        formData = areaTree_form(dataCopy)
        print(formData.errors)
        if formData.is_valid():
            A = formData.save()

            areaWidth = int(A.widthByTree)
            areaLength = int(A.lengthByTree)
            
            for x in range(areaWidth):
                column = x+1
                for y in range(areaLength):
                    row = y+1
                    treeID = f"{column}-{row}"
                    newTree = individualTrees_model(
                        treeID=treeID,
                        areaID=A,
                        rootStock="none",
                        zionType="none",
                        datePlanted=today,
                        status='healthy'
                    )
                    newTree.save()
                    print(newTree)
                    starting_url = 'https://www.heavensgatescherryfarm.com/treespace/tree-data' if settings.USE_S3 == 'TRUE' else 'http://127.0.0.1:8000/treespace/tree-data'
                    QRs = tree_qr(treeID=newTree, url=f"{starting_url}/{newTree.areaID.locationID.locationID}/{newTree.areaID.areaID}/{newTree.treeID}")
                    QRs.save()

            return redirect('area_list', location_id)
    return render(request, 'tree_grid/add_pages/add_area.html', {
        'newID': newID, 
        'location': location, 
        'areasData': areasData, 
        'locationID': location_id,
        'smallHeader': smallHeader,
        'noFooter': noFooter,
        'addForm': addForm,
        'sideBar': sideBar
    })

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



