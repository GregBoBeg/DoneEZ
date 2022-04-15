from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('about/', views.about, name="about"),
    path('faq/', views.faq, name="faq"),
    path('terms/', views.terms, name="terms"),
    path('how/', views.how, name="how"),
    path('contact/', views.contact, name="contact"),
    path('testmap/', views.testmap, name="testmap"),
    path('partner-selector/', views.partner_selector, name="partner-selector"),
] 


