from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
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

    today = datetime.now().date()

    locationsData = locationTree_model.objects.all()
    newID = selectNextID(locationsData.order_by('-locationID'), 'location')

    if request.method == 'POST':
        dataCopy = request.POST.copy()

        if not dataCopy.get('locationID'):
            dataCopy['locationID'] = newID

        formData = locationTree_form(dataCopy, request.FILES)

        if formData.is_valid():
            location = formData.save()
            return redirect('farm_map_location', location_id=location.id)

    else:
        formData = locationTree_form(initial={
            'locationID': newID,
            'dateEst': today,
        })

    return render(request, 'tree_grid/add_pages/add_location.html', {
        'form': formData,
        'newID': newID,
        'smallHeader': smallHeader,
        'noFooter': noFooter,
        'sideBar': sideBar,
    })

@lock
def addArea_view(request, location_id):
    noFooter = True
    smallHeader = True
    sideBar = True

    today = datetime.now().date()

    location = locationTree_model.objects.get(id=location_id)

    areasData = areaTree_model.objects.filter(locationID=location)
    newID = selectNextID(areasData.order_by('-areaID'), 'area')

    if request.method == 'POST':
        dataCopy = request.POST.copy()

        if not dataCopy.get('areaID'):
            dataCopy['areaID'] = newID

        formData = areaTree_form(dataCopy, request.FILES)

        if formData.is_valid():
            area = formData.save(commit=False)
            area.locationID = location
            area.save()

            return redirect('farm_map_area', location_id=location.id, area_id=area.id)

    else:
        formData = areaTree_form(initial={
            'areaID': newID,
            'dateEst': today,
        })

    return render(request, 'tree_grid/add_pages/add_area.html', {
        'form': formData,
        'newID': newID,
        'location': location,
        'smallHeader': smallHeader,
        'noFooter': noFooter,
        'sideBar': sideBar,
    })

@lock
def addTree_view(request, locationID2, areaID2):
    noFooter = True
    smallHeader = True
    sideBar = True

    today = datetime.now().date()

    location = get_object_or_404(locationTree_model, locationID=locationID2)

    areaData = get_object_or_404(
        areaTree_model,
        areaID=areaID2,
        locationID=location
    )

    selected_column = request.GET.get("column")
    selected_row = request.GET.get("row")

    initial_tree_id = None

    if selected_column and selected_row:
        initial_tree_id = f"{selected_column}-{selected_row}"

    if request.method == "POST":
        formData = individualTrees_form(request.POST, request.FILES)

        if formData.is_valid():
            newTree = formData.save(commit=False)
            newTree.areaID = areaData

            column = request.POST.get("column")
            row = request.POST.get("row")

            if column and row:
                newTree.treeID = f"{column}-{row}"
            elif initial_tree_id:
                newTree.treeID = initial_tree_id
            else:
                formData.add_error(None, "Column and row are required.")
                return render(request, 'tree_grid/add_tree.html', {
                    'form': formData,
                    'location': location,
                    'area': areaData,
                    'selected_column': selected_column,
                    'selected_row': selected_row,
                    'smallHeader': smallHeader,
                    'noFooter': noFooter,
                    'sideBar': sideBar,
                })

            existing_tree = individualTrees_model.objects.filter(
                areaID=areaData,
                treeID=newTree.treeID
            ).first()

            if existing_tree:
                formData.add_error(None, f"A tree already exists at position {newTree.treeID}.")
                return render(request, 'tree_grid/add_tree.html', {
                    'form': formData,
                    'location': location,
                    'area': areaData,
                    'selected_column': selected_column,
                    'selected_row': selected_row,
                    'smallHeader': smallHeader,
                    'noFooter': noFooter,
                    'sideBar': sideBar,
                })

            newTree.save()

            starting_url = (
                'https://www.heavensgatescherryfarm.com/treespace/tree-data'
                if getattr(settings, "USE_S3", "FALSE") == 'TRUE'
                else 'http://127.0.0.1:8000/treespace/tree-data'
            )

            tree_qr.objects.get_or_create(
                treeID=newTree,
                defaults={
                    'url': f"{starting_url}/{newTree.areaID.locationID.locationID}/{newTree.areaID.areaID}/{newTree.treeID}/"
                }
            )

            return redirect('farm_map_area', location_id=location.id, area_id=areaData.id)

    else:
        formData = individualTrees_form(initial={
            'datePlanted': today,
            'status': 'healthy',
        })

    return render(request, 'tree_grid/add_tree.html', {
        'form': formData,
        'location': location,
        'area': areaData,
        'selected_column': selected_column,
        'selected_row': selected_row,
        'smallHeader': smallHeader,
        'noFooter': noFooter,
        'sideBar': sideBar,
    })






