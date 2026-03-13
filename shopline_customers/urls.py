from django.urls import path

from . import views

app_name = "shopline_customers"

urlpatterns = [
    path("", views.portal_home),
    path("customers/", views.customer_list, name="customer_list"),
    path("customers/<str:customer_id>/", views.customer_detail, name="customer_detail"),
    path("customers/<str:customer_id>/points/", views.customer_points_summary, name="customer_points_summary"),
    path("customers/<str:customer_id>/store-credits/", views.customer_store_credit_summary, name="customer_store_credit_summary"),
    path("customers/<str:customer_id>/quick-view/", views.customer_quick_view, name="customer_quick_view"),
]
