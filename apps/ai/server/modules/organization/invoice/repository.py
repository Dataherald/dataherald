from datetime import datetime, timedelta

from bson import ObjectId

from config import CREDIT_COL, ORGANIZATION_COL, USAGE_COL
from database.mongo import MongoDB
from modules.organization.invoice.models.entities import (
    Credit,
    PaymentPlan,
    RecordStatus,
    Usage,
)


class InvoiceRepository:
    def get_daily_usages(self, org_id: str, date: datetime) -> list[Usage]:
        # Create a range for the date to cover the entire day
        start_date = datetime(date.year, date.month, date.day, 0, 0, 0)
        end_date = start_date + timedelta(days=1) - timedelta(microseconds=1)
        return [
            Usage(id=str(usage["_id"]), **usage)
            for usage in MongoDB.find(
                USAGE_COL,
                {
                    "organization_id": org_id,
                    "created_at": {"$gte": start_date, "$lte": end_date},
                },
            )
        ]

    def get_usages(
        self,
        org_id: str,
        start_date: datetime,
        end_date: datetime,
        record_status: RecordStatus = None,
    ) -> list[Usage]:
        start_date = datetime(
            start_date.year, start_date.month, start_date.day, 0, 0, 0
        )
        end_date = (
            datetime(end_date.year, end_date.month, end_date.day, 0, 0, 0)
            + timedelta(days=1)
            - timedelta(microseconds=1)
        )

        query = {
            "organization_id": org_id,
            "created_at": {"$gte": start_date, "$lte": end_date},
        }

        if record_status:
            query["status"] = record_status

        return [
            Usage(id=str(usage["_id"]), **usage)
            for usage in MongoDB.find(
                USAGE_COL,
                query,
            )
        ]

    def get_credits(self, org_id: str, record_status: str) -> list[Credit]:
        return [
            Credit(id=str(credit["_id"]), **credit)
            for credit in MongoDB.find(
                CREDIT_COL,
                {
                    "organization_id": org_id,
                    "status": record_status,
                },
            )
        ]

    def get_credit(self, credit_id: str) -> Credit:
        credit = MongoDB.find_one(CREDIT_COL, {"_id": ObjectId(credit_id)})
        return Credit(id=str(credit["_id"]), **credit) if credit else None

    def get_positive_credits(self, org_id: str) -> list[Credit]:
        return [
            Credit(id=str(credit["_id"]), **credit)
            for credit in MongoDB.find(
                CREDIT_COL,
                {
                    "organization_id": org_id,
                    "amount": {"$gt": 0},
                },
            )
        ]

    def create_usage(self, usage: Usage) -> str:
        return str(MongoDB.insert_one(USAGE_COL, usage.dict(exclude={"id"})))

    def update_spending_limit(self, org_id: str, spending_limit: int) -> int:
        return MongoDB.update_one(
            ORGANIZATION_COL,
            {"_id": ObjectId(org_id)},
            {"invoice_details.spending_limit": spending_limit},
        )

    def update_payment_plan(self, org_id: str, plan: PaymentPlan) -> int:
        return MongoDB.update_one(
            ORGANIZATION_COL,
            {"_id": ObjectId(org_id)},
            {"invoice_details.plan": plan},
        )

    def update_stripe_subcription_status(self, org_id: str, status: str) -> int:
        return MongoDB.update_one(
            ORGANIZATION_COL,
            {"_id": ObjectId(org_id)},
            {"invoice_details.stripe_subscription_status": status},
        )

    def update_billing_cyce_anchor(self, org_id: str, billing_cycle_anchor: int) -> int:
        return MongoDB.update_one(
            ORGANIZATION_COL,
            {"_id": ObjectId(org_id)},
            {"invoice_details.billing_cycle_anchor": billing_cycle_anchor},
        )

    def create_credit(self, credit: Credit) -> str:
        return str(MongoDB.insert_one(CREDIT_COL, credit.dict(exclude={"id"})))

    def update_available_credits(self, org_id: str, credit: int) -> int:
        return MongoDB.update_one(
            ORGANIZATION_COL,
            {"_id": ObjectId(org_id)},
            {"invoice_details.available_credits": credit},
        )
