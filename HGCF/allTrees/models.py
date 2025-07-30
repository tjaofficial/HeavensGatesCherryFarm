from django.db import models # type: ignore
from django.contrib.auth.models import User # type: ignore
import qrcode # type: ignore
from io import BytesIO
from django.core.files import File # type: ignore
from PIL import Image, ImageDraw # type: ignore
# Create your models here.

meal_type_choices = (
    ('dessert', 'Dessert'),
    ('dinner-main', 'Dinner - Main'),
    ('dinner-side', 'Dinner - Side'),
    ('breakfast', 'Breakfast'),
    ('lunch', 'Lunch'),
    ('brunch', 'Brunch'),
    ('quick snack', 'Quick Snack'),
)    
yes_no_choice = (
    ("yes","Yes"),
    ("no","No"),
)
DAYS_OF_WEEK = [
    ('sun', 'Sunday'),
    ('mon', 'Monday'),
    ('tue', 'Tuesday'),
    ('wed', 'Wednesday'),
    ('thu', 'Thursday'),
    ('fri', 'Friday'),
    ('sat', 'Saturday'),
]
STATUS_CHOICES = [
    ('healthy', 'Healthy'),
    ('missing', 'Missing'),
    ('dead', 'Dead'),
]

class locationTree_model(models.Model):
    locationID = models.CharField(max_length=10)
    name = models.CharField(max_length=45, blank=True, null=True)
    address = models.CharField(max_length=40)
    city = models.CharField(max_length=15)
    state = models.CharField(max_length=15)
    dateEst = models.DateField(auto_now=False, auto_now_add=False)
    def __str__(self):
        return self.locationID
    
class areaTree_model(models.Model):
    areaID = models.CharField(max_length=10)
    locationID = models.ForeignKey(
        'locationTree_model', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True
    )
    name = models.CharField(max_length=45, blank=True, null=True)
    widthByTree = models.IntegerField()
    lengthByTree = models.IntegerField()
    dateEst = models.DateField(auto_now=False, auto_now_add=False)
    def __str__(self):
        return str(self.locationID) + " - " + str(self.areaID)

class individualTrees_model(models.Model):
    treeID = models.CharField(max_length=20)
    areaID = models.ForeignKey(
        'areaTree_model', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True
    )
    rootStock = models.CharField(
        max_length=10,
        default='none'
    )
    zionType = models.CharField(
        max_length=10,
        default='none'
    )
    datePlanted = models.DateField(auto_now=False, auto_now_add=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='healthy')
    def __str__(self):
        return str(self.areaID.areaID) + " - " + str(self.treeID)

class logCategory_model(models.Model):
    name = models.CharField(max_length=25)
    description = models.CharField(max_length=300, blank=True, null=True)
    def __str__(self):
        return self.name
    
class treeLogs_model(models.Model):
    treeID = models.ForeignKey(
        'individualTrees_model', 
        on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(auto_now_add=False)
    note = models.CharField(max_length=10000)
    category = models.ForeignKey(
        'logCategory_model', 
        on_delete=models.CASCADE
    )
    def __str__(self):
        return f"[ {self.timestamp} ] {self.category.name} - {self.note}"
    
    class Meta:
        indexes = [
            models.Index(fields=['treeID']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']
    
class tree_qr(models.Model):
    treeID = models.OneToOneField(
        individualTrees_model,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    url = models.CharField(max_length=300)
    qr_code = models.ImageField(upload_to='qr_codes', blank=True)

    def __str__(self):
        return str(self.treeID)
    
    def save(self, *args, **kwargs):
        qrcode_img = qrcode.make(self.url)
        canvas = Image.new('RGB', (400,400), 'white')
        draw = ImageDraw.Draw(canvas)
        canvas.paste(qrcode_img)
        fname = f'qr_code-{self.treeID}'+'.png'
        buffer = BytesIO()
        canvas.save(buffer, 'PNG')
        self.qr_code.save(fname, File(buffer), save=False)
        canvas.close()
        super().save(*args,**kwargs)

class recipeModel(models.Model):
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=200)
    cuisine = models.CharField(max_length=70)
    freezer_friendly = models.CharField(max_length=80)
    ingredients = models.JSONField()
    equipment = models.JSONField()
    serving_size = models.IntegerField(
        null=True,
        blank=True
    )
    time = models.JSONField(
        null=True,
        blank=True
    )
    meal_type = models.CharField(
        max_length=60,
        choices=meal_type_choices
    )
    directions = models.TextField(max_length=20000)
    special_notes = models.CharField(
        max_length=2000,
        null=True,
        blank=True
    )
    image1 = models.ImageField(
        upload_to='media/recipe_images/',
        null = True,
        blank = True
    )
    image2 = models.ImageField(
        upload_to='media/recipe_images/',
        null = True,
        blank = True
    )
    image3 = models.ImageField(
        upload_to='media/recipe_images/',
        null = True,
        blank = True
    )
    image4 = models.ImageField(
        upload_to='media/recipe_images/',
        null = True,
        blank = True
    )
    
    def __str__(self):
        return str(self.id) + " - " + str(self.name)
    
class mainStore_products(models.Model):
    inventoryChoices = (
        ('in_stock', 'In stock'),
        ('out_of_stock', 'Out of stock')
    )
    product_name = models.CharField(max_length=60)
    ribbon = models.CharField(
        max_length=60,
        null = True,
        blank = True
    )
    description = models.TextField(max_length=2000)
    price = models.FloatField()
    on_sale = models.BooleanField(
        default=False
    )
    sale_percentage = models.IntegerField(
        null = True,
        blank = True
    )
    sale_price = models.FloatField(
        null = True,
        blank = True
    )
    track_inventory = models.BooleanField(
        default=False
    )
    inventory_status = models.CharField(
        max_length=75,
        choices=inventoryChoices,
        null = True,
        blank = True
    )
    shipping_weight = models.FloatField()
    inventory_total = models.IntegerField(
        null = True,
        blank = True
    )
    pre_order = models.BooleanField(
        default=False
    )
    pre_order_message = models.CharField(
        max_length=150,
        null = True,
        blank = True
    )
    limit = models.BooleanField(
        default=False,
        null = True,
        blank = True
    )
    limit_number = models.IntegerField(
        null = True,
        blank = True
    )
    show_in_store = models.BooleanField(
        default=True
    )
    mainImage = models.ImageField(
        upload_to='media/product_images/',
        null = True,
        blank = True
    )
    def __str__(self):
        return str(self.id) + " - " + str(self.product_name)
    
        
class cart_items(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null = True,
        blank = True
    )
    product = models.ForeignKey(
        mainStore_products, 
        on_delete=models.CASCADE, 
        null = True,
        blank = True
    )
    quantity = models.PositiveIntegerField(default=1)
    def __str__(self):
        return f"Cart for {self.user.username} - {self.product.product_name}"
    

class valve_registration(models.Model):
    name = models.CharField(
        max_length=30
    )
    valveIP = models.CharField(
        max_length=17
    )
    areaID = models.ForeignKey(
        'areaTree_model', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True
    )
    sub_area = models.CharField(
        max_length=17,
        blank=True, 
        null=True
    )
    manual_override = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.name}"
    
class valve_schedule(models.Model):
    valve = models.ForeignKey(
        'valve_registration', 
        on_delete=models.CASCADE
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    days = models.CharField(
        max_length=100
    ) # Comma-separated values like "mon,wed,fri"

    def get_day_list(self):
        return self.days.split(',')