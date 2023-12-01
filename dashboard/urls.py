from django.urls import path
from dashboard import views
from django.contrib.auth import views as auth_views


urlpatterns = [


     # Root Path to Dashboard Home

     path('', views.dashboard_home, name='dashboard-home'),


     # Partner Signup

     path('partner-signup-account/', views.partner_signup_account, name="partner-signup-account"),
     path('partner-signup-type/', views.partner_signup_type, name='partner-signup-type'),
     path('partner-signup-settings/', views.partner_signup_settings, name='partner-signup-settings'),
     path('partner-signup-pending/', views.partner_signup_pending, name='partner-signup-pending'),


     # Authentication

     path('login/', views.account_login, name='login'),
     path('logout/', auth_views.LogoutView.as_view(template_name='dashboard/account-logout.html'), name='logout'),
     path('password-reset/', views.ResetPasswordView.as_view(), name='password-reset'),
     path('password-reset-confirm/<uidb64>/<token>/',
          auth_views.PasswordResetConfirmView.as_view(template_name='dashboard/password-reset-confirm.html'),
          name='password_reset_confirm'),
     path('password-reset-complete/',
          auth_views.PasswordResetCompleteView.as_view(template_name='dashboard/password-reset-complete.html'),
          name='password_reset_complete'),


     # Dashboard

     path('business-profile/', views.business_profile, name='business-profile'),
     path('business-map-address/', views.business_map_address, name='business-map-address'),
     path('account-details/', views.account_details, name='account-details'),
     path('change-password/', views.change_password, name='change-password'),
     path('contact-admin/', views.contact_admin, name='contact-admin'),
     path('business-settings/', views.business_settings, name='business-settings'),
     path('account-close/', views.account_close, name='account-close'),
     path('account-closed/', views.account_closed, name='account-closed'),
     path('b2b-search/', views.b2b_search, name='b2b-search'),
     path('supplies/', views.supplies, name='supplies'),
     path('solutions/', views.solutions, name='solutions'),
     path('solutions/<str:solutions_menu_selection>', views.solutions, name='solutions'),
     path('vendor-profile/<str:vendor_business_id>', views.vendor_profile, name='vendor-profile'),

]
