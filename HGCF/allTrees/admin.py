from django.contrib import admin # type: ignore
from .models import *

# Register your models here.
admin.site.register(individualTrees_model)
admin.site.register(locationTree_model)
admin.site.register(areaTree_model)
admin.site.register(logCategory_model)
admin.site.register(treeLogs_model)
admin.site.register(tree_qr)
admin.site.register(recipeModel)
admin.site.register(mainStore_products)
admin.site.register(cart_items)
admin.site.register(valve_registration)
admin.site.register(valve_schedule)