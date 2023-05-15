# from asyncio.windows_events import NULL
from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth import update_session_auth_hash, login, logout, authenticate
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.postgres.search import SearchVector
from django.contrib.postgres.search import SearchQuery
from django.urls import reverse_lazy
from doneez_app.models import Business, Item, BusinessType, ItemCategory
from .forms import SignupTypeForm, UserSignupForm, LoginForm, CustomPasswordChangeForm, UpdateAccountDetailsForm, UpdateBusinessProfileForm, UpdateBusinessMapAddressForm, UpdateBusinessSettingsForm
from django.views.generic import ListView
from django.db.models import Q
from geopy import distance
from geopy.geocoders import Nominatim
import folium
from decimal import Decimal
from django.utils.html import format_html, strip_tags
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


# Authentication Section
# -------------------------------------------------------------------
# The following views handle user login and authentication functions. 



# Account Login

# Django's Login - Customized to accommodate "pending_approval" logic.
def account_login(request):
    # Do not allow access if already logged in
    if request.user.is_authenticated:
        return redirect(to='dashboard-home')
    else:

        if request.method == 'POST':
            form = LoginForm(data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    if request.user.business.signup_stage == "PENDING":
                        logout(request)
                        return redirect(to='partner-signup-pending')
                    else:
                        return redirect(to='dashboard-home')
        else:
            form = LoginForm(request)
        return render(request, 'dashboard/account-login.html', {'form': form})



# Password Reset

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'dashboard/password-reset.html'
    email_template_name = 'dashboard/email-password-reset.html'
    subject_template_name = 'dashboard/password-reset-subject.txt'
    success_message = "Password-reset instructions have been sent to the email address on file.  Check your spam/junk folder if not received within a few minutes."
    success_url = reverse_lazy('login')


# Partner Signup Section
# -----------------------------------------------------------------------------------------------------------------------------------
# IMPORTANT DEVELOPER NOTES: 
# Each User (aka: Partner) has to go through a "Signup Process", before they can access their account "Dashboard".
# The Signup Process follows a sequence of stages that must be completed; therefore, we use a "signup_stage" attribute
# to track user progress, and we use the "dashboard_home" view to provide appropriate routing to corresponding "signup_stage" templates.
# Each of the following views handle logic that is unique to this Signup Process.



# Home

@login_required
def dashboard_home(request):

    # Only allow access to the Dashboard if signup is "DONE"; otherwise, route to the appropriate signup page.
    if request.user.business.signup_stage == "ACCOUNT":
        return redirect(to='partner-signup-account')

    elif request.user.business.signup_stage == "TYPE":
        return redirect(to='partner-signup-type')

    elif request.user.business.signup_stage == "PROFILE":
        return redirect(to='business-profile')

    elif request.user.business.signup_stage == "MAP":
        return redirect(to='business-map-address')

    elif request.user.business.signup_stage == "SETTINGS":
        return redirect(to='partner-signup-settings')

    elif request.user.business.signup_stage == "PENDING":
        logout(request)
        return redirect(to='partner-signup-pending')
    else:
        business_type_list = BusinessType.objects.filter(b2b="SUPPLIER").order_by('business_type',)
        context = {
            'business_type_list': business_type_list,
        }
        return render(request, 'dashboard/business-home.html', context)



# Partner Signup - Create Account  (ACCOUNT Stage)

# Start the Signup Process by creating a User Account
def partner_signup_account(request):
    
    # Do not allow access if already logged in
    if request.user.is_authenticated:
        return redirect(to='dashboard-home')
    else:
        if request.method == 'POST':
            form = UserSignupForm(request.POST)

            if form.is_valid():
                # Save the clean form data.
                form.save()

                #Login the user for the remainder of the signup process
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)
                login(request, user)

                messages.success(request, f'Your "{username}" administrator account has been created.  Please continue through the signup process for your business.')
                return redirect(to='partner-signup-type')
        else:
            form = UserSignupForm()
        return render(request, 'dashboard/partner-signup-account.html', {'form': form})



# Partner Signup - Business Type  (TYPE Stage)

# Before we can create a Business Profile, we need to know what type of business it will be.
@login_required
def partner_signup_type(request):
    # Only allow access if we are on the correct signup step
    if request.user.business.signup_stage != "TYPE":
        return redirect(to='dashboard-home')
    else:

        if request.method == 'POST':
            form = SignupTypeForm(request.POST, instance=request.user.business)

            if form.is_valid():

                # Save the clean form data.
                form.save()
                # This signup stage is complete.  Specify the next signup stage.
                Business.objects.filter(pk=request.user.business.id).update(signup_stage='PROFILE')
                messages.success(request, f'Your "Business Type" selection has been noted. Please continue through the signup process.')
                return redirect(to='business-profile')
        else:
            form = SignupTypeForm(instance=request.user.business)
        return render(request, 'dashboard/partner-signup-type.html', {'form': form})



# Partner Signup - Settings  (SETTINGS Stage)

# Allow the business to adjust account settings, such as the products and services they offer their customers.
@login_required
def partner_signup_settings(request):
    # Only allow access if we are on the correct signup step
    if request.user.business.signup_stage != "SETTINGS":
        return redirect(to='dashboard-home')
    else:

        if request.method == 'POST':

            form = UpdateBusinessSettingsForm(request.POST, instance=request.user.business, request=request)

            if form.is_valid():
                
                # IMPORTANT DEVELOPER NOTES: 
                # Certain types of business accounts will need to be approved by the Website Admin, before allowing anyone to login and use that account.
                # Therefore, when a new business is created, it will either require approval or not, which is determined by the BusinessType selected (via an attributed called "pending_default").
                # If the pending_default = True, then the business account will need to be approved by the Website Admin; therefore, we
                # logout of the account and prevent further use of the Dashboard app until approval has been granted. 


                # Get the pending_default for this Business Type
                requires_approval = request.user.business.business_type.pending_default

                # Save the form and retreive the business record
                form.save()
                business = Business.objects.get(pk=request.user.business.id)

                if requires_approval:
                    business.signup_stage='PENDING'
                    business.save()
                    messages.success(request, 'Congratulations!  You have completed the Partner Signup!  We are now reviewing your account for approval.')

                    # Send a Confirmation Email
                    subject = 'DoneEZ - Your Signup is Complete (but Pending Approval)'
                    html_message = render_to_string('dashboard/email-account-completed.html', {'username': business.user.username})
                    plain_message = strip_tags(html_message)
                    from_email = settings.DEFAULT_FROM_EMAIL
                    to = business.user.email
                    send_mail(subject, plain_message, from_email, [to], html_message=html_message, fail_silently=False)

                    logout(request)
                    return redirect(to='partner-signup-pending')
                else:
                    business.signup_stage='DONE'
                    business.save()
                    messages.success(request, 'Congratulations!  You have completed the Partner Signup!  You are now a valuable member of the DoneEZ network!')

                    # Send a Confirmation Email
                    subject = 'DoneEZ - Your Account Was Created Successfully!'
                    html_message = render_to_string('dashboard/email-account-created.html', {'username': business.user.username})
                    plain_message = strip_tags(html_message)
                    from_email = settings.DEFAULT_FROM_EMAIL
                    to = business.user.email
                    send_mail(subject, plain_message, from_email, [to], html_message=html_message, fail_silently=False)

                    return redirect(to='dashboard-home')

        else:
            
            form = UpdateBusinessSettingsForm(instance=request.user.business, request=request)

        return render(request, 'dashboard/partner-signup-settings.html', {'form': form})



# Partner Signup - Pending  (PENDING Stage)

def partner_signup_pending(request):
    # Do not allow access if already logged in
    if request.user.is_authenticated:
        return redirect(to='dashboard-home')
    else:
        return render(request, 'dashboard/partner-signup-pending.html')




# Signup and Dashboard Common Section
# -----------------------------------------------------------------------------------------------------------------------------------
# IMPORTANT DEVELOPER NOTES: 
# Each User (aka: Partner) has to go through a "Signup Process", before they can access their account "Dashboard".
# Each of the following views handle common logic between the Dashboard functions and the Signup Process.
# For example, we collect Business Profile data during the Signup Process AND allow that data to be modified from the Dashboard.
# Therefore, we use 1 view to handle both the Dashboard functions and the Signup Process, due to their shared similarities.
# However, they do have some differences:
#   - The Dashboard and Signup Process each have their own menus and footers that need to be rendered.
#   - Additionally, the Signup Process follows a sequence of stages that must be completed in sequential order.
# To accomodate the menu and footer differences, we use separate templates for the Dashboard and Signup Process.
# To accomodate the sequential Signup Process, we use a "signup_stage" to track user progress,
# and the "dashboard_home" view provides the appropriate routing to their corresponding "signup_stage" page.



# Business Profile  (PROFILE Stage)

@login_required
def business_profile(request):
    # Only allow access for the appropriate signup stages.
    if request.user.business.signup_stage == "PROFILE" or request.user.business.signup_stage == "DONE":

        if request.method == 'POST':

            form = UpdateBusinessProfileForm(request.POST, instance=request.user.business)

            if form.is_valid():
                form.save()
                messages.success(request, 'Your profile has been updated successfully.  Please continue.')

                # This signup stage is complete.  Specify the next signup stage.
                if request.user.business.signup_stage == "PROFILE":
                    Business.objects.filter(pk=request.user.business.id).update(signup_stage='MAP')

                return redirect(to='dashboard-home')
        else:
            
            form = UpdateBusinessProfileForm(instance=request.user.business)

        # Render appropriate Signup or Non-Signup Template
        if request.user.business.signup_stage == "DONE":
            return render(request, 'dashboard/business-profile.html', {'form': form})
        else:
            return render(request, 'dashboard/partner-signup-profile.html', {'form': form})
    else:
        return redirect(to='dashboard-home')



# Business Map Address  (MAP Stage)

@login_required
def business_map_address(request):
    # Only allow access for the appropriate signup stages.
    if request.user.business.signup_stage == "MAP" or request.user.business.signup_stage == "DONE":

        if request.method == 'POST':

            form = UpdateBusinessMapAddressForm(request.POST, instance=request.user.business)
            print(form.is_valid())
            if form.is_valid():
                form.save()

                # Get and Save Latitude and Longitude of Address
                    
                try:
                    loc =  (form.cleaned_data.get('business_address_street1') + "," + 
                            form.cleaned_data.get('business_address_city') + "," + 
                            form.cleaned_data.get('business_address_state') + "," + 
                            form.cleaned_data.get('business_address_zip'))

                    nomAgent = Nominatim(user_agent = 'DoneEZ')
                    myaddr = nomAgent.geocode(loc, timeout = 3)
                    Business.objects.filter(pk=request.user.business.id).update(**{
                        'business_address_longitude':myaddr.longitude,
                        'business_address_latitude':myaddr.latitude                    
                        })
                    
                except:
                    messages.error(request, 'We are unable to locate your business on our map.  Please check the business address for accuracy.')

                # Map is Unverified
                if request.POST.get("map_unverified"):
                    Business.objects.filter(pk=request.user.business.id).update(**{
                        'business_address_map_status':'Map Unverified',
                    })
                    messages.warning(request, 'Is the map showing the correct location?')
                    # Redirect to same page
                    return redirect(to='business-map-address')

                # Map is Verified
                elif request.POST.get("map_verified"):
                    Business.objects.filter(pk=request.user.business.id).update(**{
                        'business_address_map_status':'Map Verified',
                    })
                    messages.success(request, 'Your address and map location have been verified successfully.')

                # Map has Error
                elif request.POST.get("map_error"):
                    Business.objects.filter(pk=request.user.business.id).update(**{
                        'business_address_map_status':'Map Error',
                    })
                    messages.error(request, 'The map error has been reported to our Website Administrator.')

                # This signup stage is complete.  Specify the next signup stage.
                if request.user.business.signup_stage == "MAP":
                    Business.objects.filter(pk=request.user.business.id).update(signup_stage='SETTINGS')

                return redirect(to='dashboard-home')

        else:
            
            form = UpdateBusinessMapAddressForm(instance=request.user.business)
        

        # Get the business record
        business_object = Business.objects.get(pk=request.user.business.id)
        
        # Plot business on map
        b2b_map = ''
        b2b_map = folium.Map(location=[37.0902, -95.7129], zoom_start=5)
        if business_object.business_address_latitude and business_object.business_address_longitude:
            folium.Marker([business_object.business_address_latitude, business_object.business_address_longitude], popup=business_object.business_name).add_to(b2b_map)
        b2b_map.fit_bounds(b2b_map.get_bounds(), padding=(50, 50))
        b2b_map = b2b_map._repr_html_()

        # Prepare the context to be passed to the form
        context = {
            'form': form,
            'b2b_map': b2b_map,
            'map_status': business_object.business_address_map_status
        }

        # Render appropriate Signup or Non-Signup Template
        if request.user.business.signup_stage == "DONE":
            return render(request, 'dashboard/business-map-address.html', context)
        else:
            return render(request, 'dashboard/partner-signup-map-address.html', context)

    # Do not allow access
    else:
        return redirect(to='dashboard-home')




# Dashboard Section
#-----------------------------------------------------------------------
# The following views handle functions that are unique to the Dashboard.



# Account Details

@login_required
def account_details(request):
    # Only allow access if signup is "DONE".
    if request.user.business.signup_stage != "DONE":
        return redirect(to='dashboard-home')
    else:

        if request.method == 'POST':
            form = UpdateAccountDetailsForm(request.POST, instance=request.user)

            if form.is_valid():
                form.save()
                messages.success(request, 'Your account has been successfully updated.')
                return redirect(to='dashboard-home')
        else:
            
            form = UpdateAccountDetailsForm(instance=request.user)

        return render(request, 'dashboard/account-details.html', {'form': form})



# Business Settings

@login_required
def business_settings(request):
    # Only allow access if signup is "DONE".
    if request.user.business.signup_stage != "DONE":
        return redirect(to='dashboard-home')
    else:
        if request.method == 'POST':

            form = UpdateBusinessSettingsForm(request.POST, instance=request.user.business, request=request)

            if form.is_valid():
                form.save()
                messages.success(request, 'Your settings have been updated successfully.')
                return redirect(to='dashboard-home')
        else:
            
            form = UpdateBusinessSettingsForm(instance=request.user.business, request=request)

        return render(request, 'dashboard/business-settings.html', {'form': form})



# B2B Search

@login_required
def b2b_search(request):
    # Only allow access if signup is "DONE".
    if request.user.business.signup_stage != "DONE":
        return redirect(to='dashboard-home')
    else:

        # Get the current business' coordinates
        latitude_from = request.user.business.business_address_latitude
        longitude_from = request.user.business.business_address_longitude

        # Grab all of the form's filter and search parameters
        form_items_filter = request.GET.getlist('FormItemCheckbox')
        if request.GET.get('FormItemSearch'):
            form_items_search = request.GET.get('FormItemSearch')
        else:
            form_items_search = 'XXXXX'
        if request.GET.get('FormDistanceRadio'):
            form_distance_selected = Decimal(request.GET.get('FormDistanceRadio'))
        else:
            form_distance_selected = 9999

        # Return all records matching the filter & search provided on the form

        search_vector_phrase = SearchQuery(form_items_search, search_type='phrase')

        object_list = Business.objects.filter(
            Q(items_offered__in=form_items_filter) |
            Q(items_offered__item_title__icontains=form_items_search) |
            Q(items_offered__search_terms__icontains=form_items_search) |
            Q(items_offered__item_title__search=search_vector_phrase) |
            Q(items_offered__search_terms__search=search_vector_phrase)

            ).filter(business_type__b2b="SUPPLIER").filter(signup_stage="DONE").distinct().order_by('-business_featured',)
        # object_list = Business.objects.annotate(search=SearchVector('items_offered__item_title', 'items_offered__search_terms')).filter(search=search_vector_phrase).filter(
        #     Q(items_offered__in=form_items_filter)).filter(business_type__b2b=True).filter(signup_stage="DONE").distinct().order_by('-business_featured',)

        # Calculate the distance between the the two businesses and add the result to the query
        for business_object in object_list:
            coords_from = (latitude_from, longitude_from)
            coords_to = (business_object.business_address_latitude, business_object.business_address_longitude)
            business_object.distance_between = distance.distance(coords_from, coords_to).mi

        # Plot the matching businesses on the map
        b2b_map = ''
        if object_list:

            b2b_map = folium.Map(location=[37.0902, -95.7129], zoom_start=5)
            for business_location in object_list:
                # Developer Note:  The "distance_between" value that we added to the object_list queryset can only be accessed within a loop (as done here),
                # and cannot be used to "filter" the query (a Django limitation); therefore, we have to reference it from within a loop, each time we need it.
                popupDtls=folium.Popup(business_location.business_name, max_width=len(business_location.business_name)*20)
                if business_location.business_address_latitude and business_location.business_address_longitude and business_location.distance_between < form_distance_selected:
                    folium.Marker([business_location.business_address_latitude, business_location.business_address_longitude], popup=popupDtls).add_to(b2b_map)
            b2b_map.fit_bounds(b2b_map.get_bounds(), padding=(30, 30))
            b2b_map = b2b_map._repr_html_()

        # Prepare the context values to be sent to the form
        business_type_list = BusinessType.objects.filter(b2b="SUPPLIER").order_by('business_type',)

        if request.GET.get('BusinessTypeSelected'):
            context_business_type_selected = int(request.GET.get('BusinessTypeSelected'))
        else:
            # context_business_type_selected = int(business_type_list[0].id)
            context_business_type_selected = int(0)

        if request.GET.get('BusinessTypeSelected'):
            context_form_items_search = request.GET.get('FormItemSearch')
        else:
            context_form_items_search = ''

        context = {
            'object_list': object_list,
            'page_get_request': request.GET.copy(),
            'form_items_selected': list(map(int, request.GET.getlist('FormItemCheckbox'))),
            'form_distance_selected': form_distance_selected,
            'items_list': Item.objects.all(),
            'categories_list': ItemCategory.objects.all(),
            'business_type_list': business_type_list,
            'business_type_selected': context_business_type_selected,
            'form_items_search': context_form_items_search,
            'b2b_map': b2b_map,
            'latitude_from': latitude_from,
            'longitude_from': longitude_from
        }


        return render(request, 'dashboard/b2b_search.html', context)



# Solutions

@login_required
def solutions(request, business_type_selected=None):
    # Only allow access if signup is "DONE".
    if request.user.business.signup_stage != "DONE":
        return redirect(to='dashboard-home')
    else:
        if business_type_selected:
            object_list = Business.objects.filter(business_type__b2b="SOLUTION").filter(signup_stage="DONE").filter(business_type=business_type_selected)
        else:
            object_list = Business.objects.filter(business_type__b2b="SOLUTION").filter(signup_stage="DONE")

        object_list = object_list.distinct().order_by('business_type','-business_featured',)

        # Prepare the context values to be sent to the form
        business_type_list = BusinessType.objects.filter(b2b="SOLUTION")


        context = {
            'object_list': object_list,
            'page_get_request': request.GET.copy(),
            'items_list': Item.objects.all(),
            'categories_list': ItemCategory.objects.all(),
            'business_type_list': business_type_list,
        }


        return render(request, 'dashboard/solutions.html', context)



# Vendor Profile (aka "Supplier")

@login_required
def vendor_profile(request,vendor_business_id):

    business_object = Business.objects.get(id = vendor_business_id)

    # Plot business on map
    b2b_map = ''
    b2b_map = folium.Map(location=[37.0902, -95.7129], zoom_start=5)
    if business_object.business_address_latitude and business_object.business_address_longitude:
        folium.Marker([business_object.business_address_latitude, business_object.business_address_longitude], popup=folium.Popup(business_object.business_name, max_width=200, min_width=200)).add_to(b2b_map)
    b2b_map.fit_bounds(b2b_map.get_bounds(), padding=(50, 50))
    b2b_map = b2b_map._repr_html_()

    # Format Hours of Operation
    #Monday
    if business_object.business_hours_mon_fm != "Leave Blank":
        hours_mon = business_object.business_hours_mon_fm
        if business_object.business_hours_mon_to != "Leave Blank" and business_object.business_hours_mon_fm != "Closed" and business_object.business_hours_mon_fm != "24 Hours":
            hours_mon += " - " + business_object.business_hours_mon_to
    else:
        hours_mon = ""
    
    #Tuesday
    if business_object.business_hours_tue_fm != "Leave Blank":
        hours_tue = business_object.business_hours_tue_fm
        if business_object.business_hours_tue_to != "Leave Blank" and business_object.business_hours_tue_fm != "Closed" and business_object.business_hours_tue_fm != "24 Hours":
            hours_tue += " - " + business_object.business_hours_tue_to
    else:
        hours_tue = ""
    
    #Wednesday
    if business_object.business_hours_wed_fm != "Leave Blank":
        hours_wed = business_object.business_hours_wed_fm
        if business_object.business_hours_wed_to != "Leave Blank" and business_object.business_hours_wed_fm != "Closed" and business_object.business_hours_wed_fm != "24 Hours":
            hours_wed += " - " + business_object.business_hours_wed_to
    else:
        hours_wed = ""
    
    #Thursday
    if business_object.business_hours_thu_fm != "Leave Blank":
        hours_thu = business_object.business_hours_thu_fm
        if business_object.business_hours_thu_to != "Leave Blank" and business_object.business_hours_thu_fm != "Closed" and business_object.business_hours_thu_fm != "24 Hours":
            hours_thu += " - " + business_object.business_hours_thu_to
    else:
        hours_thu = ""
    
    #Friday
    if business_object.business_hours_fri_fm != "Leave Blank":
        hours_fri = business_object.business_hours_fri_fm
        if business_object.business_hours_fri_to != "Leave Blank" and business_object.business_hours_fri_fm != "Closed" and business_object.business_hours_fri_fm != "24 Hours":
            hours_fri += " - " + business_object.business_hours_fri_to
    else:
        hours_fri = ""
    
    #Saturday
    if business_object.business_hours_sat_fm != "Leave Blank":
        hours_sat = business_object.business_hours_sat_fm
        if business_object.business_hours_sat_to != "Leave Blank" and business_object.business_hours_sat_fm != "Closed" and business_object.business_hours_sat_fm != "24 Hours":
            hours_sat += " - " + business_object.business_hours_sat_to
    else:
        hours_sat = ""
    
    #Sunday
    if business_object.business_hours_sun_fm != "Leave Blank":
        hours_sun = business_object.business_hours_sun_fm
        if business_object.business_hours_sun_to != "Leave Blank" and business_object.business_hours_sun_fm != "Closed" and business_object.business_hours_sun_fm != "24 Hours":
            hours_sun += " - " + business_object.business_hours_sun_to
    else:
        hours_sun = ""


    # Prepare the context to be passed to the form
    context = {
        'business': business_object,
        'b2b_map': b2b_map,
        'hours_mon': hours_mon,
        'hours_tue': hours_tue,
        'hours_wed': hours_wed,
        'hours_thu': hours_thu,
        'hours_fri': hours_fri,
        'hours_sat': hours_sat,
        'hours_sun': hours_sun,
    }


    return render(request, 'dashboard/vendor-profile.html', context)



# Change Password

@login_required
def change_password(request):
    # Only allow access if signup is "DONE".
    if request.user.business.signup_stage != "DONE":
        return redirect(to='dashboard-home')
    else:

        if request.method == 'POST':
            form = CustomPasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)  # Important!
                messages.success(request, 'Your password has been updated successfully.')

                # Send a Confirmation Email
                subject = 'DoneEZ - Password Changed'
                html_message = render_to_string('dashboard/email-password-changed.html', {'username': request.user.username})
                plain_message = strip_tags(html_message)
                from_email = settings.DEFAULT_FROM_EMAIL
                to = request.user.email
                send_mail(subject, plain_message, from_email, [to], html_message=html_message, fail_silently=False)

                return redirect(to='dashboard-home')
            else:
                messages.error(request, 'Please correct the error below.')
        else:
            form = CustomPasswordChangeForm(request.user)
        return render(request, 'dashboard/password-change.html', {'form': form,})



# Close Account

@login_required
def account_close(request):
    # Only allow access if signup is "DONE".
    if request.user.business.signup_stage != "DONE":
        return redirect(to='dashboard-home')
    else:

        if request.method == 'POST':
            if 'close_account_confirmed' in request.POST:
                user = request.user
                user.is_active = False
                user.save()
                messages.success(request, 'Your account has been closed and customers will no longer be able to reach you on our platform.')

                # Send a Confirmation Email
                subject = 'DoneEZ - Account Closed'
                html_message = render_to_string('dashboard/email-account-closed.html', {'username': user.username})
                plain_message = strip_tags(html_message)
                from_email = settings.DEFAULT_FROM_EMAIL
                to = user.email
                send_mail(subject, plain_message, from_email, [to], html_message=html_message, fail_silently=False)

                return redirect(to='account-closed')
            else:
                return redirect(to='dashboard-home')
            
        return render(request, 'dashboard/account-close.html')



# Account Closed

def account_closed(request):
    return render(request, 'dashboard/account-closed.html')



# Contact Admin

@login_required
def contact_admin(request):
    # Only allow access if signup is "DONE".
    if request.user.business.signup_stage != "DONE":
        return redirect(to='dashboard-home')
    else:
        return render(request, 'dashboard/contact-admin.html')




# DO NOT DELETE - FUTURE CODE SAMPLES
# -------------------------------------
# Flex Box Wrapping and Such

# https://stackoverflow.com/questions/39457010/why-do-flex-items-wrap-instead-of-shrink