"""
Admin portal views for Shopline customers and membership.
Staff-only; data is fetched from Shopline API.
"""
import logging
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_GET
from .services import ShoplineAPIClient
from .services.shopline_client import ShoplineAPIError

logger = logging.getLogger(__name__)


def _get_client() -> ShoplineAPIClient:
    return ShoplineAPIClient()


@staff_member_required
@require_GET
def customer_list(request: HttpRequest) -> HttpResponse:
    """List customers from Shopline API with pagination and optional search."""
    if not getattr(settings, "SHOPLINE_ACCESS_TOKEN", ""):
        return render(request, "shopline_customers/portal_error.html", {
            "error_title": "Configuration missing",
            "error_message": "SHOPLINE_ACCESS_TOKEN is not set. Add it in .env or environment.",
        })

    client = _get_client()
    page_num = request.GET.get("page", "1")
    per_page = request.GET.get("per_page", "24")
    query = request.GET.get("query", "").strip()
    is_member = request.GET.get("is_member", "").strip().lower()
    sort_by = request.GET.get("sort_by", "desc")

    try:
        page_num = max(1, int(page_num))
        per_page = min(999, max(1, int(per_page)))
    except ValueError:
        page_num = 1
        per_page = 24

    is_member_filter = None
    if is_member in ("true", "false"):
        is_member_filter = is_member == "true"

    try:
        if query or is_member_filter is not None:
            data = client.search_customers(
                page=page_num,
                per_page=per_page,
                query=query or None,
                is_member=is_member_filter,
            )
        else:
            data = client.get_customers(page=page_num, per_page=per_page, sort_by=sort_by)
    except ShoplineAPIError as e:
        logger.exception("Shopline API error in customer_list")
        return render(request, "shopline_customers/portal_error.html", {
            "error_title": "Shopline API error",
            "error_message": str(e),
            "status_code": getattr(e, "status_code", None),
        })

    items = data.get("items") or []
    pagination = data.get("pagination") or {}
    total_count = pagination.get("total_count", len(items))
    total_pages = pagination.get("total_pages", 1)
    current_page = pagination.get("current_page", page_num)

    return render(request, "shopline_customers/customer_list.html", {
        "customers": items,
        "pagination": pagination,
        "total_count": total_count,
        "total_pages": total_pages,
        "current_page": current_page,
        "per_page": per_page,
        "query": query,
        "is_member_filter": is_member,
        "sort_by": sort_by,
    })


@staff_member_required
@require_GET
def customer_detail(request: HttpRequest, customer_id: str) -> HttpResponse:
    """Single customer detail from Shopline API (membership, orders, etc.)."""
    if not getattr(settings, "SHOPLINE_ACCESS_TOKEN", ""):
        return render(request, "shopline_customers/portal_error.html", {
            "error_title": "Configuration missing",
            "error_message": "SHOPLINE_ACCESS_TOKEN is not set.",
        })

    client = _get_client()
    try:
        customer = client.get_customer(
            customer_id,
            include_fields=["subscription", "referrer_data"],
        )
    except ShoplineAPIError as e:
        if getattr(e, "status_code", None) == 404:
            return render(request, "shopline_customers/portal_error.html", {
                "error_title": "Customer not found",
                "error_message": f"No customer with ID {customer_id}.",
            }, status=404)
        logger.exception("Shopline API error in customer_detail")
        return render(request, "shopline_customers/portal_error.html", {
            "error_title": "Shopline API error",
            "error_message": str(e),
            "status_code": getattr(e, "status_code", None),
        })

    # Resolve membership tier display name (name_translations is a dict)
    tier = customer.get("membership_tier")
    if tier and isinstance(tier.get("name_translations"), dict):
        names = tier["name_translations"]
        customer["membership_tier_display"] = next(iter(names.values()), None) or tier.get("id", "")
    else:
        customer["membership_tier_display"] = tier.get("id", "") if tier else ""

    return render(request, "shopline_customers/customer_detail.html", {
        "customer": customer,
    })


@staff_member_required
@require_GET
def portal_home(request: HttpRequest) -> HttpResponse:
    """Redirect to customer list."""
    return redirect("shopline_customers:customer_list")
