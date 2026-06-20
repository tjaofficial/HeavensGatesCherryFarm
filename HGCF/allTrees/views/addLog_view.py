from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from ..forms import treeLogs_form
from ..models import individualTrees_model

lock = login_required(login_url='login')


@lock
def addLog_view(request, locationID, areaID, treeID):
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

    if request.method == 'POST':
        formData = treeLogs_form(request.POST)

        if formData.is_valid():
            log = formData.save(commit=False)
            log.treeID = treeData
            log.save()

            return redirect('treeData', locationID, areaID, treeID)

    else:
        now = timezone.localtime()
        formData = treeLogs_form(initial={
            'timestamp': now.strftime('%Y-%m-%dT%H:%M'),
        })

    return render(request, 'tree_grid/add_pages/add_log.html', {
        'logForm': formData,
        'treeData': treeData,
        'displayName': displayName,
        'fullTreeID': fullTreeID,
        'locationID': locationID,
        'areaID': areaID,
        'treeID': treeID,
        'smallHeader': smallHeader,
        'noFooter': noFooter,
        'sideBar': sideBar,
    })