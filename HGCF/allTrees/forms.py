from django import forms # type: ignore
from django.forms import ModelForm # type: ignore
from .models import * # type: ignore
from django.contrib.auth.forms import UserCreationForm # type: ignore
from django.contrib.auth.models import User # type: ignore

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
        
class mainStore_products_form(ModelForm):
    class Meta:
        model = mainStore_products
        fields = ("__all__")
        widgets = {
            'product_name': forms.TextInput(attrs={'class':'input', 'style':'width: 92%;', 'placeholder':'Add a product name'}),
            'ribbon': forms.TextInput(attrs={'class':'input', 'placeholder':'e.g., New Arrival'}),
            'description': forms.Textarea(attrs={'class':'input', 'style':'width:100%; height:unset; padding-top: 12px;overflow: scroll;padding-right: 12px;'}),
            'price': forms.NumberInput(attrs={'min':'0', 'step':'0.01', 'class':'input', 'style':'padding-left: 22px; text-align:left; width: 5rem;'}),
            'on_sale': forms.CheckboxInput(attrs={'required':False, 'class':'input'}),
            'sale_percentage': forms.NumberInput(attrs={'class':'input'}),
            'sale_price': forms.NumberInput(attrs={'class':'input'}),
            'inventory_status': forms.Select(attrs={'required':False, 'class':'input'}),
            'shipping_weight': forms.NumberInput(attrs={'class':'input'}),
            'inventory_total': forms.NumberInput(attrs={'class':'input'}),
            'pre_order': forms.CheckboxInput(attrs={'required':False, 'class':'input'}),
            'pre_order_message': forms.TextInput(attrs={'class':'input'}),
            'limit': forms.CheckboxInput(attrs={'required':False, 'class':'input'}),
            'limit_number': forms.NumberInput(attrs={'class':'input'}),
            'show_in_store': forms.CheckboxInput(attrs={'required':False, 'class':'input'}),
            'mainImage': forms.ClearableFileInput,
            'track_inventory': forms.CheckboxInput(attrs={'required':False, 'class':'input'}),
        }

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