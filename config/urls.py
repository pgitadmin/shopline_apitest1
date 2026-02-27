"""
Main URL configuration.
"""
from django.contrib import admin
from django.contrib.admin.sites import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect
from django.urls import path, include

# After admin login, redirect to /portal/ instead of admin index
_original_admin_login = admin.site.login


def _admin_login_redirect_to_portal(request, extra_context=None):
    if request.method == "GET" and admin.site.has_permission(request):
        return HttpResponseRedirect("/portal/")
    if REDIRECT_FIELD_NAME not in request.GET and REDIRECT_FIELD_NAME not in request.POST:
        extra_context = dict(extra_context or {})
        extra_context[REDIRECT_FIELD_NAME] = "/portal/"
    return _original_admin_login(request, extra_context)


admin.site.login = _admin_login_redirect_to_portal

urlpatterns = [
    path("admin/", admin.site.urls),
    path("portal/", include("shopline_customers.urls")),
]
