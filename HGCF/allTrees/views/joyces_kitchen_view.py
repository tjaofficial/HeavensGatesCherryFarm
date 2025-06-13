from django.shortcuts import render, redirect
from ..models import recipeModel
from ..forms import recipeForm
from django.contrib.auth.decorators import login_required

lock = login_required(login_url='Login')

@lock
def recipeForm_view(request):
    noFooter = True
    smallHeader = True
    sideBar = True
    form = recipeForm
    modelData = recipeModel.objects.all()
    if request.method == "POST":
        totalElements = int(request.POST['numberOfElements'])
        dataCopy = request.POST.copy()
        print(dataCopy)
        iList = {}
        for element in range(1,totalElements+1):
            elementDict = {}
            totalIngredients = int(request.POST['totalIngredients'+str(element)])
            if 'elementName' + str(element) in dataCopy:
                for ingredient in range(1,totalIngredients+1):
                    if 'iName-El'+str(element)+'-i'+str(ingredient) in dataCopy:
                        elementDict[ingredient] = {
                            'name': dataCopy['iName-El'+str(element)+'-i'+str(ingredient)],
                            'quantity': dataCopy['iQty-El'+str(element)+'-i'+str(ingredient)],
                            'measurement': dataCopy['iMeasurement-El'+str(element)+'-i'+str(ingredient)],
                            'notes': dataCopy['iNotes-El'+str(element)+'-i'+str(ingredient)]
                        }
                iList[element] = {
                    'name': dataCopy['elementName' + str(element)],
                    'eIngredients': elementDict
                }
        dataCopy['ingredients'] = iList
        
        eList = {}
        for x in range(1,16):
            if 'eName'+ str(x) in dataCopy:
                eList[str(x)] = {
                    'name': dataCopy['eName'+ str(x)],
                    'qty': dataCopy['eQty'+ str(x)],
                    'notes': dataCopy['eNotes'+ str(x)]
                }
        dataCopy['equipment'] = eList
        
        tPrep = dataCopy['prep-time']
        tCook = dataCopy['cook-time']
        tTotal = dataCopy['total-time']
        dataCopy['time'] = {
            'prep_time': tPrep,
            'cook_time': tCook,
            'total_time': tTotal
        }
        
        data = recipeForm(dataCopy, request.FILES)
        if data.is_valid():
            print('saved')
            data.save()
        else:
            print(data.errors)
    return render(request, "recipes/recipeForm.html", {
        'smallHeader': smallHeader,
        'noFooter': noFooter,
        'sideBar': sideBar,
        'form': form,
        'modelData': modelData
    })
    
def recipeInfo_view(request, recipe):
    noFooter = True
    smallHeader = True
    sideBar = True
    modelData = recipeModel.objects.all()
    recipeData = modelData.filter(name=recipe)
    if recipeData.exists():
        recipeData = recipeData[0]
    directionSplit = recipeData.directions.split("\r\n\r\n")
    key = 1
    elementLines = []
    newDirectionList = []
    count = 1
    for direct in directionSplit:
        if direct[0] == "@":
            count = 1
            elementLines.append(key)
            newDirectionList.append(direct[1:])
        else:
            newDirectionList.append(str(count) + ") " + direct)
        key += 1
        count += 1
            
    return render(request, "recipes/recipeInfo.html", {
        'smallHeader': smallHeader,
        'noFooter': noFooter,
        'sideBar': sideBar,
        'modelData': modelData,
        'recipeData': recipeData,
        'directionSplit': newDirectionList,
        'elementLines': elementLines
})