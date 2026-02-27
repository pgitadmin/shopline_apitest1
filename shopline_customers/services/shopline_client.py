"""
Shopline Open API client for customers and membership.
Base: https://open.shopline.io/v1
Auth: Bearer access_token (from Staff Settings > API Auth).
"""
import logging
from typing import Any, Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class ShoplineAPIError(Exception):
    """Raised when Shopline API returns an error."""

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[dict] = None):
        self.status_code = status_code
        self.response = response
        super().__init__(message)


class ShoplineAPIClient:
    """Client for Shopline Open API (customers, etc.)."""

    def __init__(
        self,
        access_token: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.access_token = access_token or getattr(settings, "SHOPLINE_ACCESS_TOKEN", "") or ""
        self.base_url = (base_url or getattr(settings, "SHOPLINE_API_BASE_URL", "https://open.shopline.io/v1")).rstrip("/")

    def _headers(self) -> dict:
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": "shopline-admin-portal",
        }

    def _request(self, method: str, path: str, params: Optional[dict] = None, timeout: int = 30) -> dict:
        url = f"{self.base_url}{path}"
        try:
            resp = requests.request(
                method,
                url,
                headers=self._headers(),
                params=params,
                timeout=timeout,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            try:
                body = e.response.json()
            except Exception:
                body = e.response.text
            logger.warning("Shopline API error: %s %s -> %s %s", method, path, e.response.status_code, body)
            raise ShoplineAPIError(
                message=str(e) or f"API error {e.response.status_code}",
                status_code=e.response.status_code,
                response=body if isinstance(body, dict) else None,
            )
        except requests.exceptions.RequestException as e:
            logger.exception("Shopline API request failed: %s", e)
            raise ShoplineAPIError(message=str(e))

    def get_customers(
        self,
        page: int = 1,
        per_page: int = 24,
        sort_by: str = "desc",
        updated_after: Optional[str] = None,
        updated_before: Optional[str] = None,
        previous_id: Optional[str] = None,
    ) -> dict:
        """
        GET /v1/customers — list customers with pagination.
        Use either page or previous_id (cursor-based).
        """
        params: dict[str, Any] = {
            "page": page,
            "per_page": per_page,
            "sort_by": sort_by,
        }
        if updated_after:
            params["updated_after"] = updated_after
        if updated_before:
            params["updated_before"] = updated_before
        if previous_id:
            params["previous_id"] = previous_id
            params.pop("page", None)
        return self._request("GET", "/customers", params=params)

    def get_customer(
        self,
        customer_id: str,
        excludes: Optional[list[str]] = None,
        fields: Optional[list[str]] = None,
        include_fields: Optional[list[str]] = None,
    ) -> dict:
        """GET /v1/customers/:id — single customer details."""
        params = {}
        if excludes:
            for ex in excludes:
                params.setdefault("excludes[]", []).append(ex)
        if fields:
            for f in fields:
                params.setdefault("fields[]", []).append(f)
        if include_fields:
            for f in include_fields:
                params.setdefault("include_fields[]", []).append(f)
        return self._request("GET", f"/customers/{customer_id}", params=params or None)

    def search_customers(
        self,
        page: int = 1,
        per_page: int = 30,
        query: Optional[str] = None,
        is_member: Optional[bool] = None,
        membership_tier_id: Optional[str] = None,
        **kwargs: Any,
    ) -> dict:
        """
        GET /v1/customers/search — search customers.
        query searches name, email, phones, mobile_phone.
        """
        params: dict[str, Any] = {"page": page, "per_page": min(per_page, 999)}
        if query:
            params["query"] = query
        if is_member is not None:
            params["is_member"] = str(is_member).lower()
        if membership_tier_id is not None:
            params["membership_tier_id"] = membership_tier_id
        for key, value in kwargs.items():
            if value is not None:
                params[key] = value
        return self._request("GET", "/customers/search", params=params)

    def get_customer_promotions(
        self,
        customer_id: str,
        status: Optional[str] = None,
        platform: Optional[str] = None,
        **kwargs: Any,
    ) -> dict:
        """
        GET /v1/customers/:customer_id/promotions — promotions/coupons for a customer.

        The official docs call this "Get Customer Promotions".
        """
        params: dict[str, Any] = {}
        if status:
            params["status"] = status
        if platform:
            params["platform"] = platform
        for key, value in kwargs.items():
            if value is not None:
                params[key] = value
        return self._request("GET", f"/customers/{customer_id}/promotions", params=params or None)
