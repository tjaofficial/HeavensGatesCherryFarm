from django import forms # type: ignore
from django.forms import ModelForm # type: ignore
from .models import * # type: ignore
from django.contrib.auth.forms import UserCreationForm # type: ignore
from django.contrib.auth.models import User # type: ignore
from django.forms import inlineformset_factory # type: ignore

class individualTrees_form(ModelForm):
    class Meta:
        model = individualTrees_model
        fields = ("__all__")
        widgets = {
            'treeID': forms.TextInput(),
            'rootStock': forms.TextInput(),
            'zionType': forms.TextInput(),
            'datePlanted': forms.DateInput(attrs={'type':'date'}),
        }
        
class locationTree_form(ModelForm):
    class Meta:
        model = locationTree_model
        fields = ("__all__")
        widgets = {
            'locationID':forms.TextInput(attrs={}),
            'name':forms.TextInput(),
            'address':forms.TextInput(),
            'city':forms.TextInput(),
            'state':forms.TextInput(),
            'dateEst':forms.DateInput(attrs={'type':'date'}),
        }
        
class areaTree_form(ModelForm):
    class Meta:
        model = areaTree_model
        fields = ("__all__")
        widgets = {
            'areaID': forms.TextInput(),
            'name': forms.TextInput(),
            'dateEst': forms.DateInput(attrs={'type':'date'}),
            'widthByTree': forms.NumberInput(),
            'lengthByTree': forms.NumberInput(),
        }
        
class logCategory_form(ModelForm):
    class Meta:
        model = logCategory_model
        fields = ("__all__")
        widgets = {
            'name': forms.TextInput(),
            'description': forms.TextInput(),
        }
              
class treeLogs_form(ModelForm):
    class Meta:
        model = treeLogs_model
        fields = ("__all__")
        widgets = {
            'treeID': forms.TextInput(),
            'date': forms.DateInput(attrs={'type':'date'}),
            'time': forms.TimeInput(attrs={'type':'time'}),
            'note': forms.TextInput(),
            'category': forms.Select(),
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
    days = forms.MultipleChoiceField(
        choices=DAYS_OF_WEEK,
        widget=forms.CheckboxSelectMultiple,
        label="Days to Run"
    )

    class Meta:
        model = valve_schedule
        fields = ['valve', 'start_time', 'end_time', 'days']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time', 'style': 'width: 130px;'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'style': 'width: 130px;'}),
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
            "customer_note",
            "agreed_to_rules",
        ]

        widgets = {
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

    def clean_agreed_to_rules(self):
        agreed = self.cleaned_data.get("agreed_to_rules")

        if not agreed:
            raise forms.ValidationError("You must agree to the U-Pick rules before reserving.")

        return agreed
    


    

