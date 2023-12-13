from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="HomePage"),
    path("login/", views.login, name="LoginPage"),
    path("registerpage/", views.register_page, name="RegisterPage"),
    path("register/", views.register, name="Register"),
    path("contactpage/", views.contact_us_page, name="ContactUsPage"),
    path("sendquery/", views.send_query, name="SendQuery"),
    path("faq/", views.faq, name="FAQPage"),
    ]