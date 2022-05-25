# from tkinter import FLAT
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from doneez_app.models import Business, BusinessType, Item, ItemCategory
from django.utils.safestring import mark_safe
from doneez_app.models import CustomUser


#--- Signup Form ---#

class UserSignupForm(UserCreationForm):

    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username','class': 'form-control', 'autofocus': True})
    )

    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'First Name','class': 'form-control'})
    )

    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Last Name','class': 'form-control',})
    )

    email = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': 'Email','class': 'form-control',})
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password','class': 'form-control','data-toggle': 'password',})
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password','class': 'form-control','data-toggle': 'password','id': 'password','name': 'password',})
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        # fields = UserCreationForm.Meta.fields + ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']



#--- Custom Choice Field ---#

class CustomChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return mark_safe("<span class='selector-title'> %s </span><br><span class='selector-description'> %s </span><br><br>" % (obj.business_type,obj.business_type_description))



#--- Signup Type Form ---#

class SignupTypeForm(forms.ModelForm):

    business_type = CustomChoiceField(widget=forms.RadioSelect(attrs={'class': "custom-radio-list"}), queryset=BusinessType.objects.all())

    class Meta:
        model = Business
        fields = ['business_type',]



#--- Login Form ---#

class LoginForm(AuthenticationForm):

    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Username', 'autofocus': True})
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'Password','data-toggle': 'password','id': 'password','name': 'password',})
    )

    # remember_me = forms.BooleanField(required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'password']



#--- Change Password Form ---#

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].widget = forms.PasswordInput(attrs={"class": "form-control",'data-toggle': 'password', 'placeholder':'Old Password','id': 'old_password', 'autofocus': True})
        self.fields["new_password1"].widget = forms.PasswordInput(attrs={"class": "form-control",'data-toggle': 'password', 'placeholder':'New Password','id': 'new_password1'})
        self.fields["new_password2"].widget = forms.PasswordInput(attrs={"class": "form-control",'data-toggle': 'password', 'placeholder':'Confirm New Password','id': 'new_password2'})



#--- Account Details Form ---#

class UpdateAccountDetailsForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': True})
    )

    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'First Name','class': 'form-control'})
    )

    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Last Name','class': 'form-control',})
    )

    email = forms.EmailField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email']



#--- Business Profile Form ---#

class UpdateBusinessProfileForm(forms.ModelForm):

    class Meta:
        model = Business
        fields = [
            'business_name', 
            'business_tagline', 
            'business_email', 
            'business_website', 
            'business_phone1', 
            'business_locations', 
            'business_hours_mon_fm', 
            'business_hours_mon_to', 
            'business_hours_tue_fm', 
            'business_hours_tue_to', 
            'business_hours_wed_fm', 
            'business_hours_wed_to', 
            'business_hours_thu_fm', 
            'business_hours_thu_to', 
            'business_hours_fri_fm', 
            'business_hours_fri_to', 
            'business_hours_sat_fm', 
            'business_hours_sat_to', 
            'business_hours_sun_fm', 
            'business_hours_sun_to', 
            'business_hours_note', 
            'business_description', 
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Business Name', 'autofocus': True}),
            'business_tagline': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Business Tagline'}),
            'business_email': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Business Email'}),
            'business_website': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Website Address'}),
            'business_phone1': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Primary Phone'}),
            'business_locations': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Location Count'}),
            'business_hours_mon_fm': forms.Select(attrs={'class': 'select-muted'}),
            'business_hours_mon_to': forms.Select(attrs={'class': 'select-muted'}),
            'business_hours_tue_fm': forms.Select(attrs={'class': 'select-muted'}),
            'business_hours_tue_to': forms.Select(attrs={'class': 'select-muted'}),
            'business_hours_wed_fm': forms.Select(attrs={'class': 'select-muted'}),
            'business_hours_wed_to': forms.Select(attrs={'class': 'select-muted'}),
            'business_hours_thu_fm': forms.Select(attrs={'class': 'select-muted'}),
            'business_hours_thu_to': forms.Select(attrs={'class': 'select-muted'}),
            'business_hours_fri_fm': forms.Select(attrs={'class': 'select-muted'}),
            'business_hours_fri_to': forms.Select(attrs={'class': 'select-muted'}),
            'business_hours_sat_fm': forms.Select(attrs={'class': 'select-muted'}),
            'business_hours_sat_to': forms.Select(attrs={'class': 'select-muted'}),
            'business_hours_sun_fm': forms.Select(attrs={'class': 'select-muted'}),
            'business_hours_sun_to': forms.Select(attrs={'class': 'select-muted'}),
            'business_hours_note': forms.Textarea(attrs={'class': 'form-control', 'placeholder':'Special Hours', 'style': 'height:6rem;'}),
            'business_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder':'Business Description', 'style': 'height:8rem;'}),
        }



#--- Business Map Address Form ---#

class UpdateBusinessMapAddressForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = [
            'business_address_street1', 
            'business_address_street2', 
            'business_address_city', 
            'business_address_state', 
            'business_address_zip', 
        ]
        widgets = {
            'business_address_street1': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Address Line 1'}),
            'business_address_street2': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Address Line 2'}),
            'business_address_city': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'City'}),
            'business_address_state': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'State'}),
            'business_address_zip': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Zip'}),
        }
    def clean_business_address_state(self):
        return self.cleaned_data['business_address_state'].upper()


#--- Business Settings Form ---#

class UpdateBusinessSettingsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(UpdateBusinessSettingsForm, self).__init__(*args, **kwargs)
        self.fields["items_offered"].widget = forms.CheckboxSelectMultiple({'class': 'custom-radio-list-wrap'})

        # The following complex query returns a list of Items from which a business can select to determine
        # the types of products and services they want to offer. The list of Items to choose from is determined by
        # which BusinessType is selected for the Business.
        self.fields["items_offered"].queryset = Item.objects.filter(item_category__in=ItemCategory.objects.filter(business_type__in=BusinessType.objects.filter(id=self.request.user.business.business_type.id)))

    class Meta:
        model = Business
        fields = ('items_offered',)


