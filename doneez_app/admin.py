from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.forms import CheckboxSelectMultiple

from doneez_app.forms import CustomUserCreationForm

from .models import BusinessType, Business, ItemCategory, Item, CustomUser
from doneez_app.forms import BusinessForm
from django.forms import Textarea
from django.db import models
from django.shortcuts import redirect
from django.urls import reverse, path
from django.utils.html import format_html, strip_tags
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.admin import UserAdmin




# CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    verbose_name = "User"
    verbose_name_plural = "Users"




# Item

class ItemInline(admin.TabularInline):
    model = Item
    extra = 3
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':1, 'cols':100})},
    }
    verbose_name = "Product or Service Item"
    verbose_name_plural = "List of Items for this Category"



# Category

class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ['business_type','item_category']
    list_display_links = ['item_category']
    list_filter = ['business_type']
    fields = ['business_type','item_category']
    inlines = [ItemInline]
    verbose_name = "Category Name"
    verbose_name_plural = "Categories"

# Business Type

class BusinessTypeAdmin(admin.ModelAdmin):
    list_display = ['business_type','b2b']
    list_display_links = ['business_type']
    list_filter = ['business_type']
    verbose_name = "Business Type"
    verbose_name_plural = "Business Types"


# Business

class BusinessAdmin(admin.ModelAdmin):
    form = BusinessForm
    #filter_horizontal = ('business_type',)

    def approve(self, obj):
        url = reverse('admin:approve_url', kwargs={'id': obj.id})
        if obj.signup_stage == "PENDING":
            return format_html('<a class="button" href="{}">Approve</a>', url)
        else:
            return ('')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('approve/<int:id>', self.approve_business, name='approve_url'),
        ]
        return custom_urls + urls

    def approve_business(self, request, id):

        business = Business.objects.get(pk=id)
        business.signup_stage='DONE'
        business.save()

        subject = 'DoneEZ - Your Account is Approved!'
        html_message = render_to_string('doneez_app/email-account-approved.html', {'username': business.user.username})
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        to = business.user.email

        send_mail(subject, plain_message, from_email, [to], html_message=html_message, fail_silently=False)

        redirect_url = "admin:{}_{}_changelist".format(self.opts.app_label, self.opts.model_name)
        return redirect(reverse(redirect_url))


    list_display = ('business_name','user','business_type','business_address_city','business_address_state','business_address_zip','signup_stage','business_address_map_status','approve' )
    list_filter = ['business_type', 'signup_stage', 'business_address_map_status']
    list_display_links = ['business_name',]

    fieldsets = [
        ('Business Details', {
            'fields': [
                'user',
                'business_name',
                'business_tagline',
                'business_type',
                'signup_stage',
                'business_featured',
                'business_description',
            ]}),

        ('Contact Information', {
            'fields': [
                'business_phone1',
                'business_email',
                'business_website',
                'business_locations',
                'business_address_street1',
                'business_address_street2',
                ('business_address_city','business_address_state','business_address_zip'),
                ('business_address_latitude','business_address_longitude'),
                'business_address_map_status',
            ],
            'classes': [
                'collapse'
            ]
        }),

        ('Business Hours', {
            'fields': [
                ('business_hours_mon_fm','business_hours_mon_to'),
                ('business_hours_tue_fm','business_hours_tue_to'),
                ('business_hours_wed_fm','business_hours_wed_to'),
                ('business_hours_thu_fm','business_hours_thu_to'),
                ('business_hours_fri_fm','business_hours_fri_to'),
                ('business_hours_sat_fm','business_hours_sat_to'),
                ('business_hours_sun_fm','business_hours_sun_to'),
                'business_hours_note',
            ],
            'classes': [
                'collapse'
            ]
        }),
        ('Products/Services', {
            'fields': [
                'items_offered',
            ],
            'classes': [
                'collapse'
            ]
        }),
    ]


    readonly_fields = ['user']
    filter_horizontal = ('items_offered',)

    # Disable widget buttons
    def get_form(self, request, obj=None, **kwargs):
        form = super(BusinessAdmin, self).get_form(request, obj, **kwargs)
        field = form.base_fields["business_type"]
        field.widget.can_add_related = False
        field.widget.can_change_related = False
        field.widget.can_delete_related = False
        return form



admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(BusinessType, BusinessTypeAdmin)
admin.site.register(ItemCategory, ItemCategoryAdmin)
admin.site.register(Business, BusinessAdmin)
admin.site.unregister(Group)

