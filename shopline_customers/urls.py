from django.urls import path

from . import views

app_name = "shopline_customers"

urlpatterns = [
    path("", views.portal_home),
    path("customers/", views.customer_list, name="customer_list"),
    path("customers/<str:customer_id>/", views.customer_detail, name="customer_detail"),
]
