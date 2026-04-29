from django.db import models # type: ignore
from django.contrib.auth.models import User # type: ignore
import qrcode # type: ignore
from io import BytesIO
from django.core.files import File # type: ignore
from PIL import Image, ImageDraw # type: ignore
from decimal import Decimal
from django.conf import settings # type: ignore
from django.core.validators import MinValueValidator, MaxValueValidator # type: ignore
from django.utils import timezone # type: ignore

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
    INVENTORY_CHOICES = (
        ("in_stock", "In Stock"),
        ("low_stock", "Low Stock"),
        ("out_of_stock", "Out of Stock"),
        ("seasonal_unavailable", "Seasonal / Unavailable"),
    )

    PRODUCT_TYPE_CHOICES = (
        ("produce", "Produce"),
        ("fruit", "Fruit"),
        ("vegetable", "Vegetable"),
        ("herb_spice", "Herbs / Spices"),
        ("plant", "Plant"),
        ("preserved_good", "Preserved Good"),
        ("merch", "Merchandise"),
        ("digital", "Digital"),
        ("other", "Other"),
    )

    UNIT_TYPE_CHOICES = (
        ("each", "Each"),
        ("lb", "Pound"),
        ("oz", "Ounce"),
        ("quart", "Quart"),
        ("pint", "Pint"),
        ("half_pint", "Half Pint"),
        ("bushel", "Bushel"),
        ("bunch", "Bunch"),
        ("bag", "Bag"),
        ("box", "Box"),
        ("jar", "Jar"),
        ("bundle", "Bundle"),
        ("custom", "Custom"),
    )

    FULFILLMENT_CHOICES = (
        ("pickup_only", "Pickup Only"),
        ("shipping_only", "Shipping Only"),
        ("pickup_or_shipping", "Pickup or Shipping"),
        ("local_delivery", "Local Delivery"),
    )

    product_name = models.CharField(max_length=120)

    sku = models.CharField(
        max_length=60,
        null=True,
        blank=True,
        unique=True
    )

    product_type = models.CharField(
        max_length=30,
        choices=PRODUCT_TYPE_CHOICES,
        default="produce"
    )

    ribbon = models.CharField(
        max_length=60,
        null=True,
        blank=True,
        help_text="Example: Fresh Picked, New, Best Seller, Limited Batch"
    )

    short_description = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    description = models.TextField(
        max_length=3000,
        null=True,
        blank=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))]
    )

    unit_type = models.CharField(
        max_length=30,
        choices=UNIT_TYPE_CHOICES,
        default="each",
        help_text="How this item is sold, like each, pound, quart, bunch, jar, etc."
    )

    unit_label = models.CharField(
        max_length=60,
        null=True,
        blank=True,
        help_text="Optional display label like 'per quart', 'per lb', 'per bunch'"
    )

    on_sale = models.BooleanField(default=False)

    sale_percentage = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )

    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))]
    )

    track_inventory = models.BooleanField(default=False)

    inventory_status = models.CharField(
        max_length=75,
        choices=INVENTORY_CHOICES,
        default="in_stock"
    )

    inventory_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Can support counts or weight-based inventory, like 25 quarts or 40.5 lbs."
    )

    allow_backorder = models.BooleanField(default=False)

    pre_order = models.BooleanField(default=False)

    pre_order_message = models.CharField(
        max_length=180,
        null=True,
        blank=True,
        help_text="Example: Available for pickup Saturday morning."
    )

    harvest_date = models.DateField(
        null=True,
        blank=True,
        help_text="Useful for fresh-picked produce."
    )

    season_start = models.DateField(
        null=True,
        blank=True
    )

    season_end = models.DateField(
        null=True,
        blank=True
    )

    is_seasonal = models.BooleanField(default=False)

    limit_per_order = models.BooleanField(default=False)

    limit_number = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    fulfillment_type = models.CharField(
        max_length=30,
        choices=FULFILLMENT_CHOICES,
        default="pickup_only"
    )

    shipping_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Weight in pounds for shipping calculations."
    )

    taxable = models.BooleanField(
        default=True,
        help_text="Some food/produce may be taxed differently depending on rules."
    )

    show_in_store = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)
    is_active_online = models.BooleanField(default=True)
    is_active_offline = models.BooleanField(default=True)

    allow_custom_price = models.BooleanField(
        default=False,
        help_text="Useful for POS/manual farm stand pricing."
    )

    pos_display_order = models.PositiveIntegerField(default=0)
    store_display_order = models.PositiveIntegerField(default=0)

    mainImage = models.ImageField(
        upload_to="product_images/",
        null=True,
        blank=True
    )

    alt_text = models.CharField(
        max_length=160,
        null=True,
        blank=True
    )

    meta_title = models.CharField(
        max_length=160,
        null=True,
        blank=True
    )

    meta_description = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["store_display_order", "product_name"]
        verbose_name = "Store Product"
        verbose_name_plural = "Store Products"

    def get_active_price(self):
        if self.on_sale and self.sale_price is not None:
            return self.sale_price
        return self.price

    def get_unit_display_label(self):
        if self.unit_label:
            return self.unit_label

        unit_labels = {
            "each": "each",
            "lb": "per lb",
            "oz": "per oz",
            "quart": "per quart",
            "pint": "per pint",
            "half_pint": "per half pint",
            "bushel": "per bushel",
            "bunch": "per bunch",
            "bag": "per bag",
            "box": "per box",
            "jar": "per jar",
            "bundle": "per bundle",
            "custom": "",
        }

        return unit_labels.get(self.unit_type, "")

    def is_available_for_online_store(self):
        if not self.is_active or not self.is_active_online or not self.show_in_store:
            return False

        if self.inventory_status == "out_of_stock" and not self.allow_backorder:
            return False

        return True
    
    def has_variants(self):
        return self.variants.filter(
            is_active=True,
            is_active_online=True
        ).exists()
    
    def get_available_variants(self):
        return self.variants.filter(
            is_active=True,
            is_active_online=True
        ).order_by("display_order", "id")

    def __str__(self):
        return f"{self.id} - {self.product_name}"
          
class cart_items(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_index=True
    )

    product = models.ForeignKey(
        mainStore_products,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    variant = models.ForeignKey(
        'mainStore_product_variants',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    quantity = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_item_name(self):
        if self.variant:
            return f"{self.product.product_name} - {self.variant.get_variant_label()}"
        return self.product.product_name

    def get_price(self):
        if self.variant:
            return self.variant.get_active_price()
        return self.product.get_active_price()

    def get_total(self):
        return self.get_price() * self.quantity

    def __str__(self):
        owner = self.user if self.user else f"Guest {self.session_key}"
        return f"{owner} - {self.get_item_name()} x {self.quantity}"
    
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

class POSSession(models.Model):
    sessionStatusChoices = (
        ('open', 'Open'),
        ('closed', 'Closed'),
    )

    status = models.CharField(
        max_length=20,
        choices=sessionStatusChoices,
        default='open'
    )

    opened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='opened_pos_sessions'
    )

    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='closed_pos_sessions'
    )

    opening_cash = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )

    closing_cash = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    expected_cash = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    notes = models.TextField(
        null=True,
        blank=True
    )

    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"POS Session {self.id} - {self.status}"

class POSSale(models.Model):
    saleStatusChoices = (
        ('open', 'Open'),
        ('completed', 'Completed'),
        ('voided', 'Voided'),
        ('refunded', 'Refunded'),
    )

    paymentMethodChoices = (
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('tap_to_pay', 'Tap to Pay'),
        ('manual_card', 'Manual Card'),
        ('other', 'Other'),
    )

    paymentStatusChoices = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
    )

    payment_status = models.CharField(
        max_length=20,
        choices=paymentStatusChoices,
        default='pending'
    )

    stripe_terminal_reader_id = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    stripe_terminal_location_id = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    stripe_payment_status = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    sale_number = models.CharField(
        max_length=30,
        unique=True
    )

    session = models.ForeignKey(
        POSSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales'
    )

    status = models.CharField(
        max_length=20,
        choices=saleStatusChoices,
        default='open'
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )

    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )

    payment_method = models.CharField(
        max_length=20,
        choices=paymentMethodChoices,
        null=True,
        blank=True
    )

    stripe_payment_intent_id = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    stripe_charge_id = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    stripe_receipt_url = models.URLField(
        null=True,
        blank=True
    )

    cash_received = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    cash_change = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    customer_name = models.CharField(
        max_length=120,
        null=True,
        blank=True
    )

    customer_email = models.EmailField(
        null=True,
        blank=True
    )

    notes = models.TextField(
        null=True,
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_pos_sales'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.sale_number} - {self.status}"

class POSSaleItem(models.Model):
    sale = models.ForeignKey(
        POSSale,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        mainStore_products,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pos_sale_items'
    )

    product_name_snapshot = models.CharField(max_length=255)
    sku_snapshot = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('1.00')
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )

    line_subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )

    sold_by_weight = models.BooleanField(default=False)

    weight_amount = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sale.sale_number} - {self.product_name_snapshot}"

class POSPaymentEvent(models.Model):
    sale = models.ForeignKey(
        POSSale,
        on_delete=models.CASCADE,
        related_name='payment_events'
    )

    provider = models.CharField(
        max_length=50,
        default='stripe'
    )

    event_type = models.CharField(max_length=100)

    external_id = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    payload_json = models.JSONField(
        default=dict,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sale.sale_number} - {self.event_type}"

class mainStore_product_variants(models.Model):
    SIZE_CHOICES = (
        ("xs", "XS"),
        ("s", "Small"),
        ("m", "Medium"),
        ("l", "Large"),
        ("xl", "XL"),
        ("2xl", "2XL"),
        ("3xl", "3XL"),
        ("4xl", "4XL"),
        ("youth_s", "Youth Small"),
        ("youth_m", "Youth Medium"),
        ("youth_l", "Youth Large"),
        ("custom", "Custom"),
    )

    product = models.ForeignKey(
        mainStore_products,
        on_delete=models.CASCADE,
        related_name="variants"
    )

    variant_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Example: Small, Large, Quart, Pint, 2XL, Red XL"
    )

    size = models.CharField(
        max_length=30,
        choices=SIZE_CHOICES,
        null=True,
        blank=True
    )

    sku = models.CharField(
        max_length=80,
        null=True,
        blank=True,
        unique=True
    )

    price_override = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Leave blank to use the parent product price."
    )

    sale_price_override = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Optional sale price for this specific variant."
    )

    track_inventory = models.BooleanField(default=True)

    inventory_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Inventory for this specific size/variant."
    )

    is_active = models.BooleanField(default=True)
    is_active_online = models.BooleanField(default=True)
    is_active_offline = models.BooleanField(default=True)

    display_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "id"]
        verbose_name = "Store Product Variant"
        verbose_name_plural = "Store Product Variants"

    def get_variant_label(self):
        if self.variant_name:
            return self.variant_name

        if self.size:
            return self.get_size_display()

        return "Default"

    def get_active_price(self):
        if self.sale_price_override is not None:
            return self.sale_price_override

        if self.price_override is not None:
            return self.price_override

        return self.product.get_active_price()

    def is_available(self):
        if not self.is_active or not self.is_active_online:
            return False

        if self.track_inventory and self.inventory_total is not None and self.inventory_total <= 0:
            return False

        return True

    def __str__(self):
        return f"{self.product.product_name} - {self.get_variant_label()}"
    
class UPickEvent(models.Model):
    crop_name = models.CharField(max_length=100, default="Strawberries")

    title = models.CharField(
        max_length=150,
        default="U-Pick Strawberries"
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    date = models.DateField()

    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)

    default_slot_capacity = models.PositiveIntegerField(default=10)
    default_slot_minutes = models.PositiveIntegerField(default=60)
    grace_period_minutes = models.PositiveIntegerField(default=15)

    weather_note = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    field_note = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    rules_text = models.TextField(
        blank=True,
        null=True,
        default=(
            "Your reservation time is your scheduled arrival/check-in time. "
            "Please arrive within 15 minutes of your scheduled time. "
            "Reservations not checked in within 15 minutes may be released for walk-ins. "
            "Picking time is expected to last up to 60–90 minutes depending on field conditions and crop availability. "
            "All guests must check in before entering the field. "
            "Children must stay with an adult. "
            "No pets in the picking field. "
            "Please only pick what you plan to purchase."
        )
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date", "title"]
        verbose_name = "U-Pick Event"
        verbose_name_plural = "U-Pick Events"

    def __str__(self):
        return f"{self.title} - {self.date}"

class UPickTimeSlot(models.Model):
    event = models.ForeignKey(
        UPickEvent,
        on_delete=models.CASCADE,
        related_name="time_slots"
    )

    start_time = models.TimeField()
    end_time = models.TimeField()

    capacity = models.PositiveIntegerField(default=10)

    is_active = models.BooleanField(default=True)
    is_walk_in_available = models.BooleanField(default=True)

    notes = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["event__date", "start_time"]
        verbose_name = "U-Pick Time Slot"
        verbose_name_plural = "U-Pick Time Slots"

    def reserved_count(self):
        return sum(
            reservation.party_size
            for reservation in self.reservations.filter(
                status__in=["confirmed", "checked_in"]
            )
        )

    def spots_remaining(self):
        remaining = self.capacity - self.reserved_count()
        return max(remaining, 0)

    def is_full(self):
        return self.spots_remaining() <= 0

    def get_slot_label(self):
        return f"{self.start_time.strftime('%-I:%M %p')} - {self.end_time.strftime('%-I:%M %p')}"

    def __str__(self):
        return f"{self.event.date} | {self.get_slot_label()} | {self.spots_remaining()} spots left"

class UPickReservation(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("checked_in", "Checked In"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("no_show", "No Show"),
        ("released", "Released to Walk-ins"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    time_slot = models.ForeignKey(
        UPickTimeSlot,
        on_delete=models.CASCADE,
        related_name="reservations"
    )

    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField()
    phone = models.CharField(max_length=30)

    party_size = models.PositiveIntegerField(default=1)

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="confirmed"
    )

    agreed_to_rules = models.BooleanField(default=False)

    customer_note = models.TextField(
        blank=True,
        null=True
    )

    internal_note = models.TextField(
        blank=True,
        null=True
    )

    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True
    )

    check_in_time = models.DateTimeField(
        blank=True,
        null=True
    )

    completed_time = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["time_slot__event__date", "time_slot__start_time", "last_name"]
        verbose_name = "U-Pick Reservation"
        verbose_name_plural = "U-Pick Reservations"

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def check_in(self):
        self.status = "checked_in"
        self.check_in_time = timezone.now()
        self.save(update_fields=["status", "check_in_time"])

    def mark_completed(self):
        self.status = "completed"
        self.completed_time = timezone.now()
        self.save(update_fields=["status", "completed_time"])

    def mark_no_show(self):
        self.status = "no_show"
        self.save(update_fields=["status"])

    def cancel(self):
        self.status = "cancelled"
        self.save(update_fields=["status"])

    def release_to_walkins(self):
        self.status = "released"
        self.save(update_fields=["status"])

    def can_check_in(self):
        return self.status == "confirmed"

    def can_complete(self):
        return self.status == "checked_in"

    def __str__(self):
        return f"{self.full_name()} | {self.party_size} people | {self.time_slot}"
    
class StoreOrder(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
        ("fulfilled", "Fulfilled"),
        ("refunded", "Refunded"),
    )

    FULFILLMENT_CHOICES = (
        ("pickup", "Farm Pickup"),
        ("shipping", "Shipping"),
        ("local_delivery", "Local Delivery"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_index=True
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="pending"
    )

    fulfillment_type = models.CharField(
        max_length=30,
        choices=FULFILLMENT_CHOICES,
        default="pickup"
    )

    customer_email = models.EmailField(null=True, blank=True)
    customer_name = models.CharField(max_length=180, null=True, blank=True)

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )

    tax_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )

    delivery_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )

    stripe_checkout_session_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True
    )

    stripe_payment_intent_id = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    paid_at = models.DateTimeField(null=True, blank=True)

    customer_note = models.TextField(null=True, blank=True)
    internal_note = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def recalculate_totals(self):
        subtotal = Decimal("0.00")

        for item in self.items.all():
            subtotal += item.line_total

        self.subtotal = subtotal
        self.total = self.subtotal + self.tax_total + self.delivery_total
        self.save(update_fields=["subtotal", "total"])

    def __str__(self):
        return f"Order #{self.id} - {self.status} - ${self.total}"

class StoreOrderItem(models.Model):
    order = models.ForeignKey(
        'StoreOrder',
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        'mainStore_products',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    variant = models.ForeignKey(
        'mainStore_product_variants',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    product_name = models.CharField(max_length=180)
    variant_name = models.CharField(max_length=120, null=True, blank=True)

    sku = models.CharField(max_length=100, null=True, blank=True)

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantity = models.PositiveIntegerField(default=1)

    line_total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    unit_label = models.CharField(
        max_length=80,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"



