function showInputsI() {
    const iAmount = document.getElementById('iAmount').value;
    const ingredientCont = document.getElementById('ingredientCont');
    let ingredients = ingredientCont.children
    for (let x=0; x<ingredients.length; x++) {
        var iSingle = ingredients[x];
        if (parseInt(iSingle.id.slice(1,)) <= parseInt(iAmount)){
            iSingle.style.display = 'block';
            let inputChildren = iSingle.children;
            inputChildren[0].disabled = false;
            inputChildren[1].disabled = false;
            inputChildren[2].disabled = false;
        } else {
            iSingle.style.display = 'none';
            let inputChildren = iSingle.children;
            inputChildren[0].disabled = true;
            inputChildren[1].disabled = true;
            inputChildren[2].disabled = true;
        }
    }
}
function showInputsE() {
    const iAmount = document.getElementById('eAmount').value;
    const ingredientCont = document.getElementById('equipmentCont');
    let ingredients = ingredientCont.children
    for (let x=0; x<ingredients.length; x++) {
        var iSingle = ingredients[x];
        if (parseInt(iSingle.id.slice(1,)) <= parseInt(iAmount)){
            iSingle.style.display = 'block';
            let inputChildren = iSingle.children;
            inputChildren[0].disabled = false;
            inputChildren[1].disabled = false;
            inputChildren[2].disabled = false;
        } else {
            iSingle.style.display = 'none';
            let inputChildren = iSingle.children;
            inputChildren[0].disabled = true;
            inputChildren[1].disabled = true;
            inputChildren[2].disabled = true;
        }
    }
}

const elementCont = document.getElementById('elementsCont');

addElement = (elem) => {
    var totalElements = elem.value;
    let addHTML = ``
    if (!totalElements){
        console.log('nothing')
    } else if (elementCont.children.length > totalElements && totalElements){
        var elemDifference = elementCont.children.length - totalElements
        var getBackTo = elementCont.children.length - elemDifference;
        console.log((elementCont.children.length - elemDifference))
        for (var i=elementCont.children.length; i>getBackTo; i--){
            console.log(String(i)+' is the number we are at')
            console.log('compared to number '+ String(elementCont.children.length - elemDifference))
            elementCont.removeChild(elementCont.lastChild);
        }
    } else {
        console.log('Add More')
        var elemDifference = totalElements - elementCont.children.length;

        for(let x=(elementCont.children.length)+1; x<parseInt(totalElements)+1; x++){
            console.log(x)
            let newChild = document.createElement('div');
            newChild.id = `element${x}`
            newChild.innerHTML = `<input id="elementName${x}" type="text" name="elementName${x}" style="width:100px;" placeholder="Element Name"> - <input type="number" oninput="addIngredients(this)" id="totalIngredients${x}" name="totalIngredients${x}" style="width:35px;"><br><div id="ingredientsCont${x}"></div>`;
            elementCont.appendChild(newChild);
            //also append a <br>
        }
    }
}

addIngredients = (ingredient) => {
    const mainHolder = ingredient.parentNode;
    var totalIngredients = ingredient.value;
    let addHTML = ``
    var elementID = ingredient.name.substr(-1)
    var ingredientCont = document.getElementById(`ingredientsCont${elementID}`);
    if (!totalIngredients){
        console.log('nothing')
    } else if (ingredientCont.children.length>totalIngredients){
        var elemDifference = ingredientCont.children.length - totalIngredients
        var getBackTo = ingredientCont.children.length - elemDifference;
        for(let i=ingredientCont.children.length; i>getBackTo; i--){
            ingredientCont.removeChild(ingredientCont.lastChild);
        }
    } else {
        console.log('Add More')
        var elemDifference = totalIngredients - ingredientCont.children.length;
        for(let x=parseInt(ingredientCont.children.length)+1; x<parseInt(totalIngredients)+1; x++){
            console.log('ingredients')
            let newChild = document.createElement('div');
            newChild.id = `el${elementID}i${x}`
            newChild.style = `padding-left: 30px;`
            newChild.innerHTML = `${x}) <input id="iName-El${elementID}-i${x}" type="text" name="iName-El${elementID}-i${x}" placeholder="ingredient" style="width:170px;">
            <input id="iQty-El${elementID}-i${x}" type="text" name="iQty-El${elementID}-i${x}" placeholder="qty" style="width:55px;">
            <input id="iMeasurement-El${elementID}-i${x}" type="text" name="iMeasurement-El${elementID}-i${x}" placeholder="measurement" style="width:65px;">
            <input id="iNotes-El${elementID}-i${x}" type="text" name="iNotes-El${elementID}-i${x}" placeholder="notes" style="width:150px;">`

            console.log(newChild)
            ingredientCont.appendChild(newChild);
        }
    }
}