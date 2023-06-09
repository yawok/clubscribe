from uuid import uuid4
import logging

from square.client import Client
from django.conf import settings

logger = logging.getLogger(__name__)


class Square:
    __access_token = settings.SQUARE.get("ACCESS_TOKEN")

    def __init__(self, access_token=__access_token):
        self.__application_id = settings.SQUARE.get("APPLICATION_ID")
        self.__application_secret = settings.SQUARE.get("APPLICATION_SECRET")
        environment = "sandbox" if settings.DEBUG else "production"
        self.client = Client(access_token=access_token, environment=environment)

    def get_authorization_url(self):
        if settings.DEBUG:
            base_url = "https://connect.squareupsandbox.com"
        else:
            base_url = "https://connect.squareup.com"
        application_id = settings.SQUARE.get("APPLICATION_ID")
        permission_scope = "CUSTOMERS_READ+PAYMENTS_WRITE+SUBSCRIPTIONS_WRITE+ITEMS_READ+ORDERS_WRITE+INVOICES_WRITE+ITEMS_READ+ITEMS_WRITE+MERCHANT_PROFILE_READ"
        authorization_redirect_url = f"{base_url}/oauth2/authorize?client_id={application_id}&scope={permission_scope}"

        logger.info(f"Sent auth url: {authorization_redirect_url}")
        return authorization_redirect_url

    def get_merchant_currency(self):
        merchant_info_result = self.client.merchants.retrieve_merchant(merchant_id="me")
        currency = merchant_info_result.body["merchant"]["currency"]
        return currency

    def obtain_merchant_token(self, merchant_code):
        result = self.client.o_auth.obtain_token(
            body={
                "client_id": self.__application_id,
                "client_secret": self.__application_secret,
                "code": merchant_code,
                "grant_type": "authorization_code",
            }
        )
        if result.is_success():
            merchant_token_info = {
                "access_token": result.body["access_token"],
                "refresh_token": result.body["refresh_token"],
                "expiry_date": result.body["expires_at"],
            }
            logger.info("Merchant token obtained")
            return merchant_token_info
        else:
            logger.info("Error while obtaining merchant token")
            logger.error(result.error)
            return None

    def create_subscription_catalog_item(self, **kwargs):
        name = kwargs.get("name")
        period = kwargs.get("period")
        converted_price = kwargs.get("converted_price")
        currency = kwargs.get("currency")

        result = self.client.catalog.upsert_catalog_object(
            body={
                "idempotency_key": f"{uuid4()}",
                "object": {
                    "type": "SUBSCRIPTION_PLAN",
                    "id": "#1",
                    "subscription_plan_data": {
                        "name": name,
                        "phases": [
                            {
                                "cadence": period,
                                "periods": 1,
                                "recurring_price_money": {
                                    "amount": converted_price,
                                    "currency": currency,
                                },
                                "ordinal": 1,
                            }
                        ],
                    },
                },
            }
        )

        if result.is_success():
            print(result.body)
            id = result.body["catalog_object"]["id"]
            name = result.body["catalog_object"]["subscription_plan_data"]["name"]
            description = kwargs.get("description")
            price = kwargs.get("price")
            club = kwargs.get("club")
            data = {
                "catalog_item_id": id,
                "name": name,
                "description": description,
                "price": price,
                "club": club,
            }
            logger.info("Subscription catalog item created")
            return data
        else:
            logger.info("An error occurred while creating subscription catalog item")
            logger.error(result.errers)
            return None

    def create_payment_link(self, **kwargs):
        plan_name = kwargs.get("plan_name")
        price = kwargs.get("price")
        currency = kwargs.get("currency")
        plan_id = kwargs.get("plan_id")

        result = self.client.checkout.create_payment_link(
            body={
                "idempotency_key": f"{uuid4()}",
                "quick_pay": {
                    "name": plan_name,
                    "price_money": {"amount": price, "currency": currency},
                    "location_id": "LNVBKM1QE64DV",
                },
                "checkout_options": {"subscription_plan_id": f"{plan_id}"},
            }
        )
        print(result.body)
        payment_url = result.body["payment_link"]["url"]
        return payment_url
