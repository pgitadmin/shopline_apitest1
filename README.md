# Shopline Customers Admin Portal

Django admin portal to view **Shopline customer and membership** data via the [Shopline Open API](https://open-api.docs.shoplineapp.com/docs/getting-started).

## Features

- **Customer list** – Paginated list with search (name, email, phone) and member filter
- **Customer detail** – Full profile, membership tier, orders total, credit balance, subscriptions, delivery addresses
- **Staff-only** – Uses Django admin login; only staff users can access the portal

## Setup

### 1. Get Shopline access token

1. In SHOPLINE admin: **Settings → Staff Settings**
2. Create or edit a staff account for API use
3. Open **API Auth**, select the APIs you need, then **Generate** to get an `access_token`
4. (Optional) Set **Expired At** and IP whitelist for security

See [How to get access_token](https://open-api.docs.shoplineapp.com/docs/getting-started).

### 2. Install and run

```bash
cd shopline_apitest1
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
cp .env.example .env
# Edit .env and set SHOPLINE_ACCESS_TOKEN=your_token

python manage.py migrate
python manage.py createsuperuser   # for admin login
python manage.py runserver
```

### 3. Use the portal

1. Open **http://127.0.0.1:8000/admin/** and log in with your superuser (staff) account.
2. Open **http://127.0.0.1:8000/portal/** to see the customer list.
3. Use search/filters and click **View** on a customer for full membership and order info.

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SHOPLINE_ACCESS_TOKEN` | Yes | Bearer token from SHOPLINE API Auth |
| `SHOPLINE_API_BASE_URL` | No | Default: `https://open.shopline.io/v1` |
| `SECRET_KEY` | Yes (prod) | Django secret key |
| `DEBUG` | No | Set to `False` in production |

## API used

- **GET /v1/customers** – List customers (pagination, sort, updated_after/before)
- **GET /v1/customers/:id** – Single customer (membership, orders, subscriptions)
- **GET /v1/customers/search** – Search by query and filters (e.g. `is_member`)

All requests use `Authorization: Bearer {access_token}`.
