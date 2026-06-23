from django import forms # type: ignore
from django.forms import ModelForm # type: ignore
from .models import * # type: ignore
from django.contrib.auth.forms import UserCreationForm # type: ignore
from django.contrib.auth.models import User # type: ignore
from django.forms import inlineformset_factory # type: ignore

class individualTrees_form(forms.ModelForm):
    class Meta:
        model = individualTrees_model
        fields = [
            'name',
            'image',
            'notes',
            'rootStock',
            'zionType',
            'datePlanted',
            'status',
        ]

        labels = {
            'name': 'Plant Name',
            'image': 'Plant Image',
            'notes': 'Notes',
            'rootStock': 'Rootstock',
            'zionType': 'Zion Type',
            'datePlanted': 'Date Planted',
            'status': 'Status',
        }

        widgets = {
            'datePlanted': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }
        
class locationTree_form(forms.ModelForm):
    class Meta:
        model = locationTree_model
        fields = [
            'locationID',
            'name',
            'address',
            'city',
            'state',
            'dateEst',
            'image',
        ]

        labels = {
            'locationID': 'Location ID',
            'name': 'Location Name',
            'address': 'Address',
            'city': 'City',
            'state': 'State',
            'dateEst': 'Date Established',
        }

        widgets = {
            'locationID': forms.HiddenInput(),
            'dateEst': forms.DateInput(attrs={'type': 'date'}),
        }
        
class areaTree_form(forms.ModelForm):
    class Meta:
        model = areaTree_model
        fields = [
            'areaID',
            'name',
            'widthByTree',
            'lengthByTree',
            'dateEst',
            'image',
            'description',
        ]

        labels = {
            'areaID': 'Section ID',
            'name': 'Section Name',
            'widthByTree': 'Columns',
            'lengthByTree': 'Rows',
            'dateEst': 'Date Established',
        }

        widgets = {
            'areaID': forms.HiddenInput(),
            'dateEst': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        
class logCategory_form(ModelForm):
    class Meta:
        model = logCategory_model
        fields = ("__all__")
        widgets = {
            'name': forms.TextInput(),
            'description': forms.TextInput(),
        }
              
class treeLogs_form(forms.ModelForm):
    timestamp = forms.DateTimeField(
        label="Date / Time",
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        ),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = treeLogs_model
        fields = [
            'timestamp',
            'category',
            'note',
        ]

        labels = {
            'timestamp': 'Date / Time',
            'category': 'Category',
            'note': 'Log Note',
        }

        widgets = {
            'note': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Write the log details here...'
            }),
        }

class CreateUserForm(UserCreationForm):
    password1 = forms.CharField(max_length=16, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(max_length=16, widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']
        
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'E-mail'}),
            'password1': forms.TextInput(attrs={'type': 'password', 'placeholder': 'Password'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
        }
        
class recipeForm(ModelForm):
    class Meta:
        model = recipeModel
        fields = ("__all__")
        widgets = {
            'name': forms.TextInput(attrs={'placeholder':'recipe name'}),
            'ingredients': forms.TextInput(),
            'equipment': forms.TextInput(),
            'serving_size': forms.NumberInput(attrs={'placeholder':'serving #'}),
            'time': forms.TextInput(attrs={'placeholder':'HH:MM'}),
            'meal_type': forms.Select(),
            'directions': forms.Textarea(),
            'special_notes': forms.TextInput(),
            'healthy_choice': forms.Select(),
            'description': forms.TextInput(),
            'cuisine': forms.TextInput(),
            'freezer_friendly': forms.TextInput(),
        }
        
class mainStore_products_form(forms.ModelForm):
    class Meta:
        model = mainStore_products
        fields = [
            "mainImage",
            "product_name",
            "sku",
            "product_type",
            "ribbon",
            "short_description",
            "description",

            "price",
            "unit_type",
            "unit_label",
            "on_sale",
            "sale_percentage",
            "sale_price",

            "track_inventory",
            "inventory_status",
            "inventory_total",
            "allow_backorder",

            "pre_order",
            "pre_order_message",
            "is_seasonal",
            "harvest_date",
            "season_start",
            "season_end",

            "limit_per_order",
            "limit_number",

            "fulfillment_type",
            "shipping_weight",
            "taxable",

            "show_in_store",
            "is_active",
            "is_active_online",
            "is_active_offline",
            "allow_custom_price",
            "store_display_order",
            "pos_display_order",

            "alt_text",
            "meta_title",
            "meta_description",
        ]

        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "short_description": forms.TextInput(attrs={"maxlength": 255}),
            "pre_order_message": forms.TextInput(attrs={"maxlength": 180}),
            "harvest_date": forms.DateInput(attrs={"type": "date"}),
            "season_start": forms.DateInput(attrs={"type": "date"}),
            "season_end": forms.DateInput(attrs={"type": "date"}),
        }

class mainStore_product_variant_form(forms.ModelForm):
    class Meta:
        model = mainStore_product_variants
        fields = [
            "variant_name",
            "size",
            "sku",
            "price_override",
            "sale_price_override",
            "track_inventory",
            "inventory_total",
            "is_active",
            "is_active_online",
            "is_active_offline",
            "display_order",
        ]

ProductVariantFormSet = inlineformset_factory(
    mainStore_products,
    mainStore_product_variants,
    form=mainStore_product_variant_form,
    extra=0,
    can_delete=True
)

class valve_schedule_form(forms.ModelForm):
    DAY_CHOICES = [
        ('sun', 'Sunday'),
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
    ]

    days = forms.MultipleChoiceField(
        choices=DAY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Days"
    )

    start_time = forms.TimeField(
        label="Start Time",
        widget=forms.TimeInput(
            format='%H:%M',
            attrs={
                'type': 'time',
                'class': 'clean-time-input'
            }
        ),
        input_formats=['%H:%M', '%H:%M:%S']
    )

    end_time = forms.TimeField(
        label="End Time",
        widget=forms.TimeInput(
            format='%H:%M',
            attrs={
                'type': 'time',
                'class': 'clean-time-input'
            }
        ),
        input_formats=['%H:%M', '%H:%M:%S']
    )

    class Meta:
        model = valve_schedule
        fields = [
            'valve',
            'start_time',
            'end_time',
            'days',
        ]

        labels = {
            'valve': 'Select Valve',
            'start_time': 'Start Time',
            'end_time': 'End Time',
            'days': 'Days',
        }

class ValveRegistrationForm(forms.ModelForm):
    class Meta:
        model = valve_registration
        fields = ['name', 'valveIP', 'areaID', 'sub_area']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Valve Name'}),
            'valveIP': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Valve IP Address'}),
            'areaID': forms.Select(attrs={'class': 'form-control'}),
            'sub_area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sub Area'}),
        }

class UPickReservationForm(forms.ModelForm):
    honey_pot = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "hp-field",
            "autocomplete": "off",
            "tabindex": "-1"
        })
    )

    class Meta:
        model = UPickReservation
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "party_size",
            "estimated_quarts",
            "customer_note",
            "agreed_to_rules",
        ]

        widgets = {
            "party_size": forms.NumberInput(attrs={
                "min": 1,
            }),
            "estimated_quarts": forms.NumberInput(attrs={
                "min": 0,
                "placeholder": "Example: 4",
            }),
            "customer_note": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Anything we should know? Optional."
            }),
            "agreed_to_rules": forms.CheckboxInput(),
        }

    def clean_honey_pot(self):
        honey_pot = self.cleaned_data.get("honey_pot")

        if honey_pot:
            raise forms.ValidationError("Spam detected.")

        return honey_pot

    def clean_party_size(self):
        party_size = self.cleaned_data.get("party_size")

        if party_size < 1:
            raise forms.ValidationError("Party size must be at least 1.")

        if party_size > 10:
            raise forms.ValidationError("For groups larger than 10, please contact us directly.")

        return party_size

    def clean_estimated_quarts(self):
        estimated_quarts = self.cleaned_data.get("estimated_quarts")

        if estimated_quarts is not None and estimated_quarts < 0:
            raise forms.ValidationError("Estimated quarts cannot be negative.")

        return estimated_quarts

    def clean_agreed_to_rules(self):
        agreed = self.cleaned_data.get("agreed_to_rules")

        if not agreed:
            raise forms.ValidationError("You must agree to the U-Pick rules before reserving.")

        return agreed
    
class POSProductEditForm(forms.ModelForm):
    class Meta:
        model = mainStore_products

        fields = [
            "product_name",
            "sku",
            "product_type",
            "ribbon",
            "short_description",
            "description",

            "price",
            "unit_type",
            "unit_label",

            "on_sale",
            "sale_percentage",
            "sale_price",

            "track_inventory",
            "inventory_status",
            "inventory_total",
            "allow_backorder",

            "pre_order",
            "pre_order_message",

            "harvest_date",
            "season_start",
            "season_end",
            "is_seasonal",

            "limit_per_order",
            "limit_number",

            "fulfillment_type",
            "shipping_weight",
            "taxable",

            "show_in_store",
            "is_active",
            "is_active_online",
            "is_active_offline",
            "allow_custom_price",

            "pos_display_order",
            "store_display_order",

            "mainImage",
            "alt_text",
            "meta_title",
            "meta_description",
        ]

        widgets = {
            "product_name": forms.TextInput(attrs={"class": "formInput"}),
            "sku": forms.TextInput(attrs={"class": "formInput"}),
            "product_type": forms.Select(attrs={"class": "formInput"}),
            "ribbon": forms.TextInput(attrs={"class": "formInput"}),
            "short_description": forms.TextInput(attrs={"class": "formInput"}),
            "description": forms.Textarea(attrs={"class": "formInput", "rows": 5}),

            "price": forms.NumberInput(attrs={"class": "formInput", "step": "0.01"}),
            "unit_type": forms.Select(attrs={"class": "formInput"}),
            "unit_label": forms.TextInput(attrs={"class": "formInput"}),

            "sale_percentage": forms.NumberInput(attrs={"class": "formInput", "min": "1", "max": "100"}),
            "sale_price": forms.NumberInput(attrs={"class": "formInput", "step": "0.01"}),

            "inventory_status": forms.Select(attrs={"class": "formInput"}),
            "inventory_total": forms.NumberInput(attrs={"class": "formInput", "step": "0.01"}),

            "pre_order_message": forms.TextInput(attrs={"class": "formInput"}),

            "harvest_date": forms.DateInput(attrs={"class": "formInput", "type": "date"}),
            "season_start": forms.DateInput(attrs={"class": "formInput", "type": "date"}),
            "season_end": forms.DateInput(attrs={"class": "formInput", "type": "date"}),

            "limit_number": forms.NumberInput(attrs={"class": "formInput", "min": "1"}),

            "fulfillment_type": forms.Select(attrs={"class": "formInput"}),
            "shipping_weight": forms.NumberInput(attrs={"class": "formInput", "step": "0.01"}),

            "pos_display_order": forms.NumberInput(attrs={"class": "formInput", "min": "0"}),
            "store_display_order": forms.NumberInput(attrs={"class": "formInput", "min": "0"}),

            "mainImage": forms.ClearableFileInput(attrs={"class": "formInput"}),
            "alt_text": forms.TextInput(attrs={"class": "formInput"}),
            "meta_title": forms.TextInput(attrs={"class": "formInput"}),
            "meta_description": forms.TextInput(attrs={"class": "formInput"}),
        }

class FarmAnnouncementForm(forms.ModelForm):
    publish_date = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
                "class": "formInput",
            },
            format="%Y-%m-%dT%H:%M"
        )
    )

    class Meta:
        model = FarmAnnouncement

        fields = [
            "title",
            "announcement_type",
            "summary",
            "body",
            "featured_image",
            "image_alt_text",
            "is_pinned",
            "status",
            "publish_date",
            "meta_title",
            "meta_description",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "formInput",
                "placeholder": "Example: Strawberries Are Almost Ready"
            }),

            "announcement_type": forms.Select(attrs={
                "class": "formInput"
            }),

            "summary": forms.TextInput(attrs={
                "class": "formInput",
                "placeholder": "Short preview shown on announcement cards."
            }),

            "body": forms.Textarea(attrs={
                "class": "formInput",
                "rows": 8,
                "placeholder": "Write the full announcement here..."
            }),

            "featured_image": forms.ClearableFileInput(attrs={
                "class": "formInput"
            }),

            "image_alt_text": forms.TextInput(attrs={
                "class": "formInput",
                "placeholder": "Describe the image for accessibility."
            }),

            "status": forms.Select(attrs={
                "class": "formInput"
            }),

            "meta_title": forms.TextInput(attrs={
                "class": "formInput",
                "placeholder": "Optional SEO title"
            }),

            "meta_description": forms.TextInput(attrs={
                "class": "formInput",
                "placeholder": "Optional SEO description"
            }),
        }

class UPickWaitlistForm(forms.ModelForm):
    class Meta:
        model = UPickWaitlistEntry
        fields = [
            "preferred_type",
            "preferred_date",
            "first_name",
            "last_name",
            "email",
            "phone",
            "people_count",
            "estimated_quarts",
            "notes",
        ]

        widgets = {
            "preferred_type": forms.RadioSelect,
            "preferred_date": forms.DateInput(attrs={
                "type": "date",
            }),
            "people_count": forms.NumberInput(attrs={
                "min": 1,
            }),
            "estimated_quarts": forms.NumberInput(attrs={
                "min": 0,
                "placeholder": "Example: 4",
            }),
            "notes": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Anything we should know?",
            }),
        }

        labels = {
            "preferred_type": "Availability Preference",
            "preferred_date": "Preferred Day",
            "people_count": "Number of People",
            "estimated_quarts": "Estimated Quarts",
            "notes": "Note",
        }