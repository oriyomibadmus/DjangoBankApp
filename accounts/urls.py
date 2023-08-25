from django.urls import path
from accounts import views

app_name = "accounts"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("", views.account, name="account"),
    path("kyc-reg/", views.kyc_registration, name="kyc-reg"),
]
