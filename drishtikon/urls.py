from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="HomePage"),
    path("loginpage/", views.login_page, name="LoginPage"),
    path("login/", views.login, name="Login"),
    path("logout/", views.logout, name="Logout"),
    path("registerpage/", views.register_page, name="RegisterPage"),
    path("register/", views.register, name="Register"),
    path("contactpage/", views.contact_us_page, name="ContactUsPage"),
    path("sendquery/", views.send_query, name="SendQuery"),
    path("faq/", views.faq, name="FAQPage"),
    path("verifyemailpage/", views.verify_email_page, name="VerifyEmailPage"),
    path("verifyemail/", views.verify_email, name="VerifyEmail"),
    path("studentindex/", views.student_index, name="StudentIndexPage"),
    path("professorindex/", views.professor_index, name="ProfessorIndexPage"),
    path("createtestpage/", views.create_test_page, name="CreateTestPage"),
    path("createtest/", views.create_test, name="CreateTest"),
    path("givetestpage/", views.give_test_page, name="GiveTestPage"),
    path("givetest/", views.give_test, name="GiveTest"),
    path("test/<str:testid>/", views.test, name="Test"),
    ]