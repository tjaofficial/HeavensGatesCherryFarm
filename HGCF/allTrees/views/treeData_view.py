from django.shortcuts import render
from ..models import individualTrees_model, areaTree_model, locationTree_model, treeLogs_model, tree_qr
from django.contrib.auth.decorators import login_required

lock = login_required(login_url='Login')

@lock
def treeData2_view(request, locationID2, areaID2, treeID2):
    noFooter = True
    smallHeader = True
    sideBar = True
    treeData = individualTrees_model.objects.get(locationID__locationID=locationID2, areaID__areaID=areaID2, treeID=treeID2)
    treeLogs = treeLogs_model.objects.filter(treeID__locationID__locationID=locationID2, treeID__areaID__areaID=areaID2, treeID__treeID=treeID2).order_by('-date')
    treeQrCode = tree_qr.objects.filter(treeID__id=treeData.id)
    if treeQrCode.exists():
        treeQrCode = treeQrCode[0]
    else:
        treeQrCode = False
    

    print(treeLogs)
    return render(request, 'treeData.html',{
        'treeQrCode': treeQrCode, 
        'treeLogs': treeLogs, 
        'locationID': locationID2, 
        'areaID': areaID2, 
        'treeID': treeID2, 
        'treeData': treeData,
        'smallHeader': smallHeader,
        'noFooter': noFooter,
        'sideBar': sideBar
    })
    
@lock
def treeLog_view(request, locationID2, areaID2, treeID2, selector):
    noFooter = True
    smallHeader = True
    sideBar = True
    if selector == 'all':
        treeLogData = treeLogs_model.objects.all().filter(treeID__locationID__locationID=locationID2, treeID__areaID__areaID=areaID2, treeID__treeID=treeID2).order_by('-date')
        variables = {
            'locationID': locationID2, 
            'areaID': areaID2, 
            'treeID': treeID2, 
            'selector': selector,
            'treeLogData': treeLogData,
            'smallHeader': smallHeader,
            'noFooter': noFooter,
            'sideBar': sideBar
        }
    else:
        treeLog = treeLogs_model.objects.get(id=int(selector))
        variables = {
            'locationID': locationID2, 
            'areaID': areaID2, 
            'treeID': treeID2, 
            'treeLog': treeLog,
            'selector': selector,
            'smallHeader': smallHeader,
            'noFooter': noFooter,
            'sideBar': sideBar
        }
    print(selector)
    return render(request, 'treeLog.html', variables)