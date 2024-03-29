from django import forms
from django.db import models
from django.utils import timezone
from django.core.validators import URLValidator
from django.conf import settings

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.contrib.postgres.fields import CICharField
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _



class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    This model replaces the Django default User model
    to allow current and future customizations.
    It is nearly an exact copy of the default User model,
    with a few customizations indicated in the comments throughout.
        
    """

    # Customize the validator to use Ascii instead of Unicode
    username_validator = ASCIIUsernameValidator()

    # Customize the username field to be case-insensitive, using the Postgres CITextExtension implementation
    username = CICharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)



class BusinessType(models.Model):
    B2B_CHOICES = (
        ('RETAIL', 'Retail'),
        ('SUPPLIER', 'Supplier'),
        ('SOLUTION', 'Solution')
    )
    business_type = models.CharField(max_length=50, verbose_name="Type of Business", help_text='Give a title to this new type of business.')
    business_type_tagline = models.CharField(max_length=100, null=True, blank=True, verbose_name="Business Type Tagline", help_text='Provide a short tagline to describe the Business Type.')
    business_type_description = models.CharField(max_length=250, verbose_name="Business Type Description", help_text='Provide the text that will describe this Business Type to Partners during the Signup process.<br> Ex:  We provide automotive services on retail consumer vehicles.')
    b2b = models.CharField(max_length=10, default="RETAIL", verbose_name="B2B", choices=B2B_CHOICES, help_text='Indicates the type of business and where the business will show up.  "Retail" businesses are displayed in end-consumer searches. "Supplier" businesses are displayed in Supplier Searches.  "Solution" businesses are displayed on the Solutions page.')
    pending_default = models.BooleanField(default=False, verbose_name="Requires Account Approval",help_text='Indicates whether this Business-Type will require the Site Admin to approve the account.')
    class Meta:
        verbose_name = "Business Type"
        verbose_name_plural = "Business Types"

    def __str__(self):
        return self.business_type


class ItemCategory(models.Model):
    business_type = models.ForeignKey(BusinessType, verbose_name="Business Type",on_delete=models.CASCADE)
    item_category = models.CharField(max_length=50, verbose_name="Item Category", help_text='Item Category')

    class Meta:
        verbose_name = "Item Category"
        verbose_name_plural = "Item Categories"
        ordering = ['item_category']

    def __str__(self):
        return self.item_category


class Item(models.Model):
    item_category = models.ForeignKey(ItemCategory, verbose_name="Category",on_delete=models.CASCADE)
    item_title = models.CharField(max_length=50, verbose_name="Item (Product or Service)", help_text='Enter a name or title of your item/product/service.)')
    search_terms = models.TextField(max_length=500, blank=True, verbose_name="Search Terms", help_text='Enter Search Terms that customers will type to find this item.')
    list_filter = ('item_category__business_type',)

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"
        ordering = ['item_category','item_title']

    def item_category_name(self):
        return self.item_category.item_category
    item_category_name.short_description = 'Category'

    def __str__(self):
        return f'{self.item_category} || {self.item_title}'


class Business(models.Model):
    PARTNER_SIGNUP_STAGES = (
        ('TYPE', 'Waiting on Business Type'),
        ('PROFILE', 'Waiting on Business Profile'),
        ('MAP', 'Waiting on Map Address Verification'),
        ('SETTINGS', 'Waiting on Items Offered'),
        ('PENDING', 'Needs Approval'),
        ('DONE', 'Signup Complete'),
    )
    MAP_STATUS_CHOICES = (
        ('Map Unverified', 'Map Unverified'),
        ('Map Verified', 'Map Verified'),
        ('Map Error', 'Map Error'),
    )
    BUSINESS_HOURS_FM = (
        ("Leave Blank", "Leave Blank"),
        ("Closed", "Closed"),
        ("24 Hours", "24 Hours"),
        ("12:30 am", "12:30 am"),
        ("1:00 am", "1:00 am"),
        ("1:30 am", "1:30 am"),
        ("2:00 am", "2:00 am"),
        ("2:30 am", "2:30 am"),
        ("3:00 am", "3:00 am"),
        ("3:30 am", "3:30 am"),
        ("4:00 am", "4:00 am"),
        ("4:30 am", "4:30 am"),
        ("5:00 am", "5:00 am"),
        ("5:30 am", "5:30 am"),
        ("6:00 am", "6:00 am"),
        ("6:30 am", "6:30 am"),
        ("7:00 am", "7:00 am"),
        ("7:30 am", "7:30 am"),
        ("8:00 am", "8:00 am"),
        ("8:30 am", "8:30 am"),
        ("9:00 am", "9:00 am"),
        ("9:30 am", "9:30 am"),
        ("10:00 am", "10:00 am"),
        ("10:30 am", "10:30 am"),
        ("11:00 am", "11:00 am"),
        ("11:30 am", "11:30 am"),
        ("Noon", "Noon"),
        ("12:30 pm", "12:30 pm"),
        ("1:00 pm", "1:00 pm"),
        ("1:30 pm", "1:30 pm"),
        ("2:00 pm", "2:00 pm"),
        ("2:30 pm", "2:30 pm"),
        ("3:00 pm", "3:00 pm"),
        ("3:30 pm", "3:30 pm"),
        ("4:00 pm", "4:00 pm"),
        ("4:30 pm", "4:30 pm"),
        ("5:00 pm", "5:00 pm"),
        ("5:30 pm", "5:30 pm"),
        ("6:00 pm", "6:00 pm"),
        ("6:30 pm", "6:30 pm"),
        ("7:00 pm", "7:00 pm"),
        ("7:30 pm", "7:30 pm"),
        ("8:00 pm", "8:00 pm"),
        ("8:30 pm", "8:30 pm"),
        ("9:00 pm", "9:00 pm"),
        ("9:30 pm", "9:30 pm"),
        ("10:00 pm", "10:00 pm"),
        ("10:30 pm", "10:30 pm"),
        ("11:00 pm", "11:00 pm"),
        ("11:30 pm", "11:30 pm"),
        ("Midnight", "Midnight"),
    )
    BUSINESS_HOURS_TO = (
        ("Leave Blank", "Leave Blank"),
        ("12:30 am", "12:30 am"),
        ("1:00 am", "1:00 am"),
        ("1:30 am", "1:30 am"),
        ("2:00 am", "2:00 am"),
        ("2:30 am", "2:30 am"),
        ("3:00 am", "3:00 am"),
        ("3:30 am", "3:30 am"),
        ("4:00 am", "4:00 am"),
        ("4:30 am", "4:30 am"),
        ("5:00 am", "5:00 am"),
        ("5:30 am", "5:30 am"),
        ("6:00 am", "6:00 am"),
        ("6:30 am", "6:30 am"),
        ("7:00 am", "7:00 am"),
        ("7:30 am", "7:30 am"),
        ("8:00 am", "8:00 am"),
        ("8:30 am", "8:30 am"),
        ("9:00 am", "9:00 am"),
        ("9:30 am", "9:30 am"),
        ("10:00 am", "10:00 am"),
        ("10:30 am", "10:30 am"),
        ("11:00 am", "11:00 am"),
        ("11:30 am", "11:30 am"),
        ("Noon", "Noon"),
        ("12:30 pm", "12:30 pm"),
        ("1:00 pm", "1:00 pm"),
        ("1:30 pm", "1:30 pm"),
        ("2:00 pm", "2:00 pm"),
        ("2:30 pm", "2:30 pm"),
        ("3:00 pm", "3:00 pm"),
        ("3:30 pm", "3:30 pm"),
        ("4:00 pm", "4:00 pm"),
        ("4:30 pm", "4:30 pm"),
        ("5:00 pm", "5:00 pm"),
        ("5:30 pm", "5:30 pm"),
        ("6:00 pm", "6:00 pm"),
        ("6:30 pm", "6:30 pm"),
        ("7:00 pm", "7:00 pm"),
        ("7:30 pm", "7:30 pm"),
        ("8:00 pm", "8:00 pm"),
        ("8:30 pm", "8:30 pm"),
        ("9:00 pm", "9:00 pm"),
        ("9:30 pm", "9:30 pm"),
        ("10:00 pm", "10:00 pm"),
        ("10:30 pm", "10:30 pm"),
        ("11:00 pm", "11:00 pm"),
        ("11:30 pm", "11:30 pm"),
        ("Midnight", "Midnight"),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL,null=True, blank=True, on_delete=models.CASCADE)
    business_type = models.ForeignKey(BusinessType, null=True, verbose_name="Business Type", help_text="Select which type of business this is.", on_delete=models.CASCADE)
    signup_stage = models.CharField(max_length=10, choices=PARTNER_SIGNUP_STAGES, default='TYPE', help_text='Indicates where a new partner is in the signup process.')
    items_offered = models.ManyToManyField(Item, verbose_name="Items Offered", help_text="Select all corresponding items your business offers, so that your business can be found when customers search for these products/services.")
    business_tagline = models.TextField(max_length=70, blank=True, verbose_name="Business Tagline", help_text="Provide a concise tagline to appear in customer's search results.")
    business_featured = models.BooleanField(default=False, verbose_name="Featured?", help_text='Determines whether a business is to be featured at the top of search results.')
    business_name = models.CharField(max_length=100, verbose_name="Business Name")
    business_phone1 = models.CharField(blank=True, max_length=20, verbose_name="Primary Phone", help_text="Enter your business' primary phone number to be displayed publicly online.")
    business_email = models.EmailField(max_length=100, verbose_name="Business Email", help_text="Enter the business email address where customers can send emails.")
    business_website = models.URLField(max_length=100, verbose_name="Website Address or Referral Link", help_text="Enter your business web address.  If you have a referral link, please supply it here, instead of your web address.")
    business_address_street1 = models.CharField(max_length=100, verbose_name="Street Address Line 1")
    business_address_street2 = models.CharField(max_length=100, blank=True, verbose_name="Street Address Line 2")
    business_address_city = models.CharField(max_length=50, verbose_name="City")
    business_address_state = models.CharField(max_length=2, verbose_name="State")
    business_address_zip = models.CharField(max_length=10, verbose_name="Zip")
    business_address_latitude = models.DecimalField(max_digits=20, decimal_places=16, default=0, blank=True, verbose_name="Latitude")
    business_address_longitude = models.DecimalField(max_digits=20, decimal_places=16, default=0, blank=True, verbose_name="Longitude")
    business_address_map_status = models.CharField(max_length=14, default="Map Unverified", choices=MAP_STATUS_CHOICES, blank=True, verbose_name="Map Status")
    business_hours_mon_fm = models.CharField(max_length=20, default="Leave Blank", choices=BUSINESS_HOURS_FM, verbose_name="Mon From")
    business_hours_mon_to = models.CharField(max_length=20, default="8:00 pm", choices=BUSINESS_HOURS_TO, verbose_name="Mon To")
    business_hours_tue_fm = models.CharField(max_length=20, default="Leave Blank", choices=BUSINESS_HOURS_FM, verbose_name="Tue From")
    business_hours_tue_to = models.CharField(max_length=20, default="8:00 pm", choices=BUSINESS_HOURS_TO, verbose_name="Tue To")
    business_hours_wed_fm = models.CharField(max_length=20, default="Leave Blank", choices=BUSINESS_HOURS_FM, verbose_name="Wed From")
    business_hours_wed_to = models.CharField(max_length=20, default="8:00 pm", choices=BUSINESS_HOURS_TO, verbose_name="Wed To")
    business_hours_thu_fm = models.CharField(max_length=20, default="Leave Blank", choices=BUSINESS_HOURS_FM, verbose_name="Thu From")
    business_hours_thu_to = models.CharField(max_length=20, default="8:00 pm", choices=BUSINESS_HOURS_TO, verbose_name="Thu To")
    business_hours_fri_fm = models.CharField(max_length=20, default="Leave Blank", choices=BUSINESS_HOURS_FM, verbose_name="Fri From")
    business_hours_fri_to = models.CharField(max_length=20, default="8:00 pm", choices=BUSINESS_HOURS_TO, verbose_name="Fri To")
    business_hours_sat_fm = models.CharField(max_length=20, default="Leave Blank", choices=BUSINESS_HOURS_FM, verbose_name="Sat From")
    business_hours_sat_to = models.CharField(max_length=20, default="8:00 pm", choices=BUSINESS_HOURS_TO, verbose_name="Sat To")
    business_hours_sun_fm = models.CharField(max_length=20, default="Leave Blank", choices=BUSINESS_HOURS_FM, verbose_name="Sun From")
    business_hours_sun_to = models.CharField(max_length=20, default="8:00 pm", choices=BUSINESS_HOURS_TO, verbose_name="Sun To")
    business_hours_note = models.TextField(max_length=300, blank=True, verbose_name="Special Hours", help_text='Type in any special notes regarding business hours.<br>Ex: holidays, appointments, and delivery hours.')
    business_locations = models.SmallIntegerField(blank=True, null=True, verbose_name="Location Count", help_text='How many total business locations are there?')
    business_description = models.TextField(max_length=2000, blank=True, verbose_name="Business Description", help_text='Give us a detailed description of your business for customers to see on your Business Profile page.  If you need more space to write, expand the text box by pulling down on the bottom-right corner.')

    class Meta:
        verbose_name = "Business"
        verbose_name_plural = "Businesses"

    def __str__(self):
        return self.business_name

