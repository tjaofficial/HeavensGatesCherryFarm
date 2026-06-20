from django.shortcuts import render, get_object_or_404 # type: ignore
from ..models import individualTrees_model, areaTree_model, locationTree_model, treeLogs_model, tree_qr
from django.contrib.auth.decorators import login_required # type: ignore

lock = login_required(login_url='login')

@lock
def treeData_view(request, locationID, areaID, treeID):
    noFooter = True
    smallHeader = True
    sideBar = True

    treeData = get_object_or_404(
        individualTrees_model.objects.select_related(
            'areaID',
            'areaID__locationID'
        ),
        areaID__locationID__locationID=locationID,
        areaID__areaID=areaID,
        treeID=treeID
    )

    treeLogs = treeLogs_model.objects.filter(
        treeID=treeData
    ).select_related('category').order_by('-timestamp')

    treeQrCode = tree_qr.objects.filter(treeID=treeData).first()

    fullTreeID = f"{locationID}-{areaID}-{treeID}"

    displayName = getattr(treeData, 'name', None) or f"Tree {treeID}"
    notes = getattr(treeData, 'notes', '') or ''

    try:
        column, row = treeID.split('-', 1)
        positionLabel = f"Column {column}, Row {row}"
    except Exception:
        column = None
        row = None
        positionLabel = "Position Unknown"

    return render(request, 'tree_grid/select_pages/tree_data.html', {
        'treeQrCode': treeQrCode,
        'treeLogs': treeLogs,
        'recentTreeLogs': treeLogs[:5],
        'logCount': treeLogs.count(),

        'locationID': locationID,
        'areaID': areaID,
        'treeID': treeID,
        'treeData': treeData,

        'displayName': displayName,
        'notes': notes,
        'fullTreeID': fullTreeID,
        'positionLabel': positionLabel,
        'column': column,
        'row': row,

        'smallHeader': smallHeader,
        'noFooter': noFooter,
        'sideBar': sideBar,
    })
    
@lock
def treeLog_view(request, locationID, areaID, treeID, selector):
    noFooter = True
    smallHeader = True
    sideBar = True

    treeData = get_object_or_404(
        individualTrees_model.objects.select_related(
            'areaID',
            'areaID__locationID'
        ),
        areaID__locationID__locationID=locationID,
        areaID__areaID=areaID,
        treeID=treeID
    )

    displayName = getattr(treeData, 'name', None) or f"Tree {treeID}"
    fullTreeID = f"{locationID}-{areaID}-{treeID}"

    baseVariables = {
        'locationID': locationID,
        'areaID': areaID,
        'treeID': treeID,
        'selector': selector,
        'treeData': treeData,
        'displayName': displayName,
        'fullTreeID': fullTreeID,
        'smallHeader': smallHeader,
        'noFooter': noFooter,
        'sideBar': sideBar,
    }

    if selector == 'all':
        treeLogData = treeLogs_model.objects.filter(
            treeID=treeData
        ).select_related('category').order_by('-timestamp')

        baseVariables['treeLogData'] = treeLogData
        baseVariables['logCount'] = treeLogData.count()

    else:
        treeLog = get_object_or_404(
            treeLogs_model.objects.select_related('category'),
            id=int(selector),
            treeID=treeData
        )

        baseVariables['treeLog'] = treeLog

    return render(request, 'tree_grid/select_pages/tree_log.html', baseVariables)


