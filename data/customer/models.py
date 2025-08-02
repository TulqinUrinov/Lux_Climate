from decimal import Decimal
from typing import TYPE_CHECKING

from data.common.models import BaseModel
from django.db import models

from data.order.models import Order

from django.db import transaction

from django.db.models import Sum

from data.balance.models import Balance

if TYPE_CHECKING:
    from data.payment.models import Payment


class Customer(BaseModel):
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, unique=True)
    get_order = models.BooleanField(default=False)

    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))

    def __str__(self):
        return self.full_name

    payments: "models.QuerySet[Payment]"
    balances: "models.QuerySet[Balance]"
    orders: "models.QuerySet[Order]"

    def recalculate_balance(self):

        with transaction.atomic():
            self.balances.all().delete()
            balance_entries = []

            # 1. Add balances from orders
            for order in self.orders.all():
                direction = (
                    order.order_type
                )  # "CUSTOMER_TO_COMPANY" or "COMPANY_TO_CUSTOMER"
                amount = order.price
                sign = (
                    Decimal("1")
                    if direction == "CUSTOMER_TO_COMPANY"
                    else Decimal("-1")
                )
                transaction_type = "INCOME" if sign > 0 else "OUTCOME"

                balance_entries.append(
                    Balance(
                        customer=self,
                        user=order.created_by,
                        reason="ORDER",
                        change=amount * sign,
                        amount=amount,
                        type=transaction_type,
                        created_at=order.created_at,
                        comment=f"Order #{order.id}",
                    )
                )

            # 2. Add balances from payments
            for payment in self.payments.filter(is_deleted=False):
                p_type = payment.payment_type
                sign = (
                    Decimal("1") if p_type == "CUSTOMER_TO_COMPANY" else Decimal("-1")
                )
                transaction_type = "INCOME" if sign > 0 else "OUTCOME"

                balance_entries.append(
                    Balance(
                        customer=self,
                        user=payment.created_by,
                        payment=payment,
                        reason="PAYMENT_INCOME" if sign > 0 else "PAYMENT_OUTCOME",
                        change=payment.amount * sign,
                        amount=payment.amount,
                        type=transaction_type,
                        created_at=payment.created_at,
                        comment=payment.comment or f"Payment #{payment.id}",
                    )
                )

            Balance.objects.bulk_create(balance_entries)

            # 3. Recalculate OrderSplits (for BOTH order types separately)

            # 🟢 CUSTOMER_TO_COMPANY: customer owes us → reduce with positive payments
            total_received = self.balances.aggregate(total=Sum("change"))[
                "total"
            ] or Decimal("0")
            available_received = total_received

            for order in self.orders.filter(
                order_type="CUSTOMER_TO_COMPANY"
            ).prefetch_related("order_splits"):
                for split in order.order_splits.all().order_by("payment_date"):
                    planned = split.amount

                    if available_received >= planned:
                        split.left = Decimal("0")
                        available_received -= planned
                    elif available_received > 0:
                        split.left = planned - available_received
                        available_received = Decimal("0")
                    else:
                        split.left = planned

                    split.save(update_fields=["left"])

            # 🔴 COMPANY_TO_CUSTOMER: we owe customer → reduce with negative pool
            total_paid = self.balances.aggregate(total=Sum("change"))[
                "total"
            ] or Decimal("0")
            available_paid = abs(total_paid) if total_paid < 0 else Decimal("0")

            for order in self.orders.filter(
                order_type="COMPANY_TO_CUSTOMER"
            ).prefetch_related("order_splits"):
                for split in order.order_splits.all().order_by("payment_date"):
                    planned = split.amount

                    if available_paid >= planned:
                        split.left = Decimal("0")
                        available_paid -= planned
                    elif available_paid > 0:
                        split.left = planned - available_paid
                        available_paid = Decimal("0")
                    else:
                        split.left = planned

                    split.save(update_fields=["left"])

            # 4. Save actual balance snapshot to customer
            self.balance = self.balances.aggregate(total=Sum("change"))[
                "total"
            ] or Decimal("0")

            self.save(update_fields=["balance"])
