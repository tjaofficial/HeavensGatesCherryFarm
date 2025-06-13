from django.shortcuts import render, redirect 
from ..models import mainStore_products, cart_items
from ..forms import mainStore_products_form
from django.http import JsonResponse
import json

def store_view(request):
    noFooter = False
    smallHeader = False
    sideBar = False
    allProducts = mainStore_products.objects.all()
    
    if request.method == "POST":
        print('added to cart')
        request_body_data_bytes = request.body
        request_body_data_str = request_body_data_bytes.decode('utf-8')

        try:
            json_data = json.loads(request_body_data_str)
        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        product_id = json_data.get('product_id', None)
        
        print(product_id)
        # Get the user (assuming user is authenticated)
        user = request.user
        
        # Get the product based on the product_id
        product = mainStore_products.objects.get(pk=product_id)
        
        # Check if the product is already in the cart
        cart_item, item_created = cart_items.objects.get_or_create(user=user, product=product)
        
        # If the product is already in the cart, increase the quantity
        if not item_created:
            cart_item.quantity += 1
            cart_item.save()
        
        response_data = {
            'success': True,
            'message': 'Item added to the cart successfully',
            'redirectUrl': '/store'
        }
        return JsonResponse(response_data)
        
    return render(request, "store/store.html", {
        'smallHeader': smallHeader,
        'noFooter': noFooter,
        'sideBar': sideBar,
        'allProducts': allProducts
    })

def addProduct_view(request):
    noFooter = True
    smallHeader = True
    sideBar = True
    productForm = mainStore_products_form
    
    if request.method == 'POST':
        formData = request.POST
        data = mainStore_products_form(formData, request.FILES)
        print(formData)
        
        print(data.errors)
        if data.is_valid():
            data.save()
            return redirect('store')
    
    return render(request, "store/addProduct.html", {
        'smallHeader': smallHeader,
        'noFooter': noFooter,
        'sideBar': sideBar,
        'productForm': productForm
    })