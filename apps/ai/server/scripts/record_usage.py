import json
import os
import uuid

import pymongo
import stripe

MONGODB_URI = os.environ.get("MONGODB_URI")
MONGODB_DB_NAME = os.environ.get("MONGODB_DB_NAME")
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY")

data_store = pymongo.MongoClient(MONGODB_URI)[MONGODB_DB_NAME]
stripe.api_key = STRIPE_API_KEY
stripe.max_network_retries = 2


def lambda_handler(event, context):  # noqa: ARG001
    print("Start Recording Usage")
    org_cursor = data_store["organizations"].find(
        {"invoice_details.plan": {"$in": ["USAGE_BASED", "CREDIT_ONLY"]}}
    )
    for org in org_cursor:
        print(f"Processing usage for organization: {str(org['_id'])}")
        try:
            subscription = stripe.Subscription.retrieve(
                org["invoice_details"]["stripe_subscription_id"]
            )

            # this is a safe guard in case webhook listener doesn't update the status
            data_store["organizations"].update_one(
                {"_id": org["_id"]},
                {
                    "$set": {
                        "invoice_details.stripe_subscription_status": subscription.status
                    }
                },
            )
            if subscription.status != "active":
                print(f"Subscription status is not active: {subscription.status}")
                data_store["organizations"].update_one(
                    {"_id": org["_id"]},
                    {
                        "$set": {
                            "invoice_details.plan": "CREDIT_ONLY",
                        }
                    },
                )
            usages = data_store["usages"].find(
                {
                    "organization_id": str(org["_id"]),
                    "status": "UNRECORDED",
                }
            )

            credits = data_store["credits"].find(
                {"organization_id": str(org["_id"]), "status": "UNRECORDED"}
            )

            # everything is in cents
            usage_cost_in_cents = 0
            credit_in_cents = 0
            usage_dict = {
                "SQL_GENERATION": 0,
                "FINETUNING_GPT_35": 0,
                "FINETUNING_GPT_4": 0,
            }
            for usage in usages:
                usage_dict[usage["type"]] += usage["quantity"]
            for credit in credits:
                credit_in_cents += credit["amount"]
            # credits applied should be negative, but might have positive credit in the future
            if credit_in_cents < 0:
                stripe.Customer.create_balance_transaction(
                    org["invoice_details"]["stripe_customer_id"],
                    amount=credit_in_cents,
                    currency="usd",
                    description="add credit balance",
                )

            for item in subscription["items"]:
                if not item.price.lookup_key:
                    print(f"Item without lookup key: {item.id}")
                quantity = usage_dict[item.price.lookup_key]
                # record usage
                stripe.SubscriptionItem.create_usage_record(
                    item.id, quantity=quantity, idempotency_key=str(uuid.uuid4())
                )
                usage_cost_in_cents += quantity * item.price.unit_amount

            # update usages status to invoiced
            data_store["usages"].update_many(
                {
                    "organization_id": str(org["_id"]),
                    "status": "UNRECORDED",
                },
                {"$set": {"status": "RECORDED"}},
            )
            data_store["credits"].update_many(
                {"organization_id": str(org["_id"]), "status": "UNRECORDED"},
                {"$set": {"status": "RECORDED"}},
            )

            print(f"Total usage: {usage_dict}")
            print(f"Total usage cost: {usage_cost_in_cents} cents")
            print(f"Total credit applied: {credit_in_cents} cents")
            print(f"Total balance: {usage_cost_in_cents + credit_in_cents} cents")

        except Exception as e:
            print(f"Error processing organization: {str(org['_id'])}")
            print(e)

    return {"statusCode": 200, "body": json.dumps("Record usage completed!")}
