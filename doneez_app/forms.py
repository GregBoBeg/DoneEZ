from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Business, CustomUser
from django.forms.widgets import CheckboxSelectMultiple
from django.forms.models import ModelMultipleChoiceField

class CustomUserCreationForm(UserCreationForm):
  class Meta:
    model = CustomUser
    fields = "__all__"

class CustomSelectMultiple(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "%s: %s %s" %(obj.name, obj.short_description, obj.price)

class BusinessForm(forms.ModelForm):

    class Meta:
        model = Business
        fields = '__all__'
        widgets = {
          'business_description': forms.Textarea(attrs={'rows':9, 'cols':90}),
          'business_hours': forms.Textarea(attrs={'rows':4, 'cols':60}),
          'business_hours_note': forms.Textarea(attrs={'rows':4, 'cols':60}),
        }


