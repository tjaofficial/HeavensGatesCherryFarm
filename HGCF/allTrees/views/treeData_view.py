from django.shortcuts import render # type: ignore
from ..models import individualTrees_model, areaTree_model, locationTree_model, treeLogs_model, tree_qr
from django.contrib.auth.decorators import login_required # type: ignore

lock = login_required(login_url='login')

@lock
def treeData_view(request, locationID, areaID, treeID):
    noFooter = True
    smallHeader = True
    sideBar = True
    fullTreeID = f"{locationID}-{areaID}-{treeID}"
    treeData = individualTrees_model.objects.get(areaID__areaID=areaID, treeID=treeID)
    treeLogs = treeLogs_model.objects.filter(treeID=treeData).order_by('-timestamp')
    treeQrCode = tree_qr.objects.filter(treeID__id=treeData.id)
    if treeQrCode.exists():
        treeQrCode = treeQrCode[0]
    else:
        treeQrCode = False
    

    print(treeLogs)
    return render(request, 'tree_grid/select_pages/tree_data.html',{
        'treeQrCode': treeQrCode, 
        'treeLogs': treeLogs, 
        'locationID': locationID, 
        'areaID': areaID, 
        'treeID': treeID, 
        'treeData': treeData,
        'smallHeader': smallHeader,
        'noFooter': noFooter,
        'sideBar': sideBar,
        'fullTreeID': fullTreeID
    })
    
@lock
def treeLog_view(request, locationID, areaID, treeID, selector):
    noFooter = True
    smallHeader = True
    sideBar = True
    treeData = individualTrees_model.objects.get(areaID__areaID=areaID, treeID=treeID)
    if selector == 'all':
        treeLogData = treeLogs_model.objects.filter(treeID=treeData).order_by('-timestamp')
        variables = {
            'locationID': locationID, 
            'areaID': areaID, 
            'treeID': treeID, 
            'selector': selector,
            'treeLogData': treeLogData,
            'smallHeader': smallHeader,
            'noFooter': noFooter,
            'sideBar': sideBar
        }
    else:
        treeLog = treeLogs_model.objects.get(id=int(selector))
        variables = {
            'locationID': locationID, 
            'areaID': areaID, 
            'treeID': treeID, 
            'treeLog': treeLog,
            'selector': selector,
            'smallHeader': smallHeader,
            'noFooter': noFooter,
            'sideBar': sideBar
        }
    print(selector)
    return render(request, 'tree_grid/select_pages/tree_log.html', variables)

@lock
def location_list_view(request):
    noFooter = True
    smallHeader = True
    sideBar = True

    locations = locationTree_model.objects.all()
    print(locations)
    return render(request, 'tree_grid/select_pages/tree_locations.html', {
        'locations': locations,
        'smallHeader': smallHeader,
        'noFooter': noFooter,
        'sideBar': sideBar
    })

@lock
def area_list_view(request, location_id):
    noFooter = True
    smallHeader = True
    sideBar = True

    location = locationTree_model.objects.get(id=location_id)
    areas = areaTree_model.objects.filter(locationID=location)
    return render(request, 'tree_grid/select_pages/tree_areas.html', {
        'location': location, 
        'areas': areas,
        'smallHeader': smallHeader,
        'noFooter': noFooter,
        'sideBar': sideBar
    })

@lock
def area_tree_grid_view(request, area_id):
    noFooter = True
    smallHeader = True
    sideBar = True
    area = areaTree_model.objects.get(id=area_id)
    trees = individualTrees_model.objects.filter(areaID=area)
    tree_map = {}

    for tree in trees:
        tree_map[tree.treeID] = {
            "rootStock": tree.rootStock,
            "zionType": tree.zionType,
            "datePlanted": tree.datePlanted.strftime('%Y-%m-%d'),
            "status": getattr(tree, 'status', 'healthy'),  # optional field
        }

    return render(request, 'tree_grid/select_pages/tree_grid.html', {
        'area': area,
        'range_area': range(1, area.lengthByTree + 1),
        'range_width': range(1, area.widthByTree + 1),
        'tree_map': tree_map,
        'smallHeader': smallHeader,
        'noFooter': noFooter,
        'sideBar': sideBar
    })



