from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from ..forms import individualTrees_form

from ..models import (
    locationTree_model,
    areaTree_model,
    individualTrees_model,
    treeLogs_model,
    tree_qr,
)

lock = login_required(login_url='login')


@lock
def farm_map_view(request, location_id=None, area_id=None):
    noFooter = True
    smallHeader = True
    sideBar = True

    locations = locationTree_model.objects.all().order_by('locationID')

    selected_location = None
    selected_area = None
    areas = areaTree_model.objects.none()

    tree_grid = []
    flat_cells = []
    columns = []

    plant_capacity = 0
    existing_tree_count = 0

    if location_id:
        selected_location = get_object_or_404(locationTree_model, id=location_id)

        areas = areaTree_model.objects.filter(
            locationID=selected_location
        ).order_by('areaID')

    if area_id:
        selected_area = get_object_or_404(
            areaTree_model.objects.select_related('locationID'),
            id=area_id
        )

        selected_location = selected_area.locationID

        areas = areaTree_model.objects.filter(
            locationID=selected_location
        ).order_by('areaID')

        trees = individualTrees_model.objects.filter(
            areaID=selected_area
        ).order_by('treeID')

        existing_tree_count = trees.count()
        plant_capacity = selected_area.widthByTree * selected_area.lengthByTree

        tree_map = {}

        for tree in trees:
            try:
                column, row = tree.treeID.split('-', 1)
                tree_map[(int(column), int(row))] = tree
            except Exception:
                continue

        columns = range(1, selected_area.widthByTree + 1)

        for row in range(1, selected_area.lengthByTree + 1):
            row_cells = []

            for column in columns:
                tree = tree_map.get((column, row))

                full_id = (
                    f"{selected_location.locationID}-"
                    f"{selected_area.areaID}-"
                    f"{column}-{row}"
                )

                cell_data = {
                    'row': row,
                    'column': column,
                    'tree': tree,
                    'full_id': full_id,
                    'tree_position': f"{column}-{row}",
                    'status_label': tree.status if tree else 'open',
                }

                row_cells.append(cell_data)
                flat_cells.append(cell_data)

            tree_grid.append({
                'row_number': row,
                'cells': row_cells,
            })

    return render(request, 'tree_grid/farm_map.html', {
        'locations': locations,
        'selected_location': selected_location,
        'selected_area': selected_area,
        'areas': areas,
        'columns': columns,
        'tree_grid': tree_grid,
        'plant_capacity': plant_capacity,
        'existing_tree_count': existing_tree_count,
        'flat_cells': flat_cells,
        'smallHeader': smallHeader,
        'noFooter': noFooter,
        'sideBar': sideBar,
    })

@lock
def tree_quick_view_api(request, tree_pk):
    tree = get_object_or_404(
        individualTrees_model.objects.select_related(
            'areaID',
            'areaID__locationID',
        ),
        id=tree_pk
    )

    latest_log = treeLogs_model.objects.filter(
        treeID=tree
    ).select_related('category').order_by('-timestamp').first()

    qr = tree_qr.objects.filter(treeID=tree).first()

    location = tree.areaID.locationID
    area = tree.areaID

    full_tree_id = f"{location.locationID}-{area.areaID}-{tree.treeID}"

    display_name = getattr(tree, 'name', None) or f"Tree {tree.treeID}"
    notes = getattr(tree, 'notes', '') or ''

    image_url = ''
    if hasattr(tree, 'image') and tree.image:
        image_url = tree.image.url

    qr_url = ''
    if qr and qr.qr_code:
        qr_url = qr.qr_code.url

    full_page_url = reverse(
        'treeData',
        args=[
            location.locationID,
            area.areaID,
            tree.treeID,
        ]
    )

    edit_url = reverse(
        'editTree',
        args=[
            location.locationID,
            area.areaID,
            tree.treeID,
        ]
    )

    try:
        column, row = tree.treeID.split('-', 1)
        position_label = f"Row {row} • Column {column}"
    except Exception:
        position_label = "Position Unknown"

    add_log_url = reverse(
        'addLog',
        args=[
            location.locationID,
            area.areaID,
            tree.treeID,
        ]
    )

    data = {
        'tree_pk': tree.id,
        'display_name': display_name,
        'treeID': tree.treeID,
        'full_tree_id': full_tree_id,
        'rootStock': tree.rootStock,
        'zionType': tree.zionType,
        'datePlanted': tree.datePlanted.strftime('%Y-%m-%d'),
        'status': tree.status,
        'notes': notes,
        'image_url': image_url,
        'qr_url': qr_url,
        'full_page_url': full_page_url,
        'add_log_url': add_log_url,
        'edit_url': edit_url,
        'position_label': position_label,
        'latest_log': {
            'timestamp': latest_log.timestamp.strftime('%Y-%m-%d %I:%M %p'),
            'category': latest_log.category.name,
            'note': latest_log.note,
        } if latest_log else None,
    }

    return JsonResponse(data)

@lock
def legacy_location_list_redirect(request):
    return redirect('farm_map')

@lock
def legacy_area_list_redirect(request, location_id):
    return redirect('farm_map_location', location_id=location_id)

@lock
def legacy_tree_grid_redirect(request, area_id):
    area = get_object_or_404(areaTree_model.objects.select_related('locationID'), id=area_id)

    return redirect(
        'farm_map_area',
        location_id=area.locationID.id,
        area_id=area.id
    )

@lock
def editTree_view(request, locationID, areaID, treeID):
    noFooter = True
    smallHeader = True
    sideBar = True

    tree = get_object_or_404(
        individualTrees_model.objects.select_related(
            'areaID',
            'areaID__locationID'
        ),
        areaID__locationID__locationID=locationID,
        areaID__areaID=areaID,
        treeID=treeID
    )

    location = tree.areaID.locationID
    area = tree.areaID

    if request.method == "POST":
        form = individualTrees_form(request.POST, request.FILES, instance=tree)

        if form.is_valid():
            form.save()
            return redirect('farm_map_area', location_id=location.id, area_id=area.id)
    else:
        form = individualTrees_form(instance=tree)

    return render(request, 'tree_grid/edit_tree.html', {
        'form': form,
        'tree': tree,
        'location': location,
        'area': area,
        'smallHeader': smallHeader,
        'noFooter': noFooter,
        'sideBar': sideBar,
    })



