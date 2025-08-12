from decimal import Decimal
from typing import TYPE_CHECKING

from rest_framework.exceptions import ValidationError

from data.common.models import BaseModel
from django.db import models

from data.order.models import Order

from django.db import transaction

from django.db.models import Sum

from data.balance.models import Balance
from data.payment.models import InstallmentPayment

if TYPE_CHECKING:
    from data.payment.models import Payment


class Customer(BaseModel):
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, unique=True)
    get_order = models.BooleanField(default=False)

    is_archived = models.BooleanField(default=False)

    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))

    def clean(self):
        super().clean()

        cleaned_phone = self.phone_number.lstrip('+') if self.phone_number else None

        from data.user.models import User

        if cleaned_phone and User.objects.filter(phone_number=cleaned_phone).exists():
            raise ValidationError("Bu telefon raqami allaqachon User sifatida mavjud.")

        # Modelga + belgisisiz telefon raqamni yozamiz
        self.phone_number = cleaned_phone

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name

    payments: "models.QuerySet[Payment]"
    balances: "models.QuerySet[Balance]"
    orders: "models.QuerySet[Order]"

    order_splits: "models.QuerySet[InstallmentPayment]"

    def recalculate_balance(self):
        with transaction.atomic():
            # 1. Delete old balances
            self.balances.all().delete()
            balance_entries = []

            # 2. Create balances from orders
            # for order in self.orders.all():
            #     direction = (
            #         order.order_type
            #     )  # "CUSTOMER_TO_COMPANY" or "COMPANY_TO_CUSTOMER"
            #     amount = order.price
            #     sign = (
            #         Decimal("-1")
            #         if direction == "CUSTOMER_TO_COMPANY"
            #         else Decimal("1")
            #     )
            #     transaction_type = "INCOME" if sign > 0 else "OUTCOME"
            #
            #     balance_entries.append(
            #         Balance(
            #             customer=self,
            #             user=order.created_by,
            #             reason="ORDER",
            #             change=amount * sign,
            #             amount=amount,
            #             type=transaction_type,
            #             created_at=order.created_at,
            #             comment=f"Order #{order.id}",
            #         )
            #     )

            # PRODUCT orders
            for order in self.orders.filter(product="PRODUCT"):
                direction = order.order_type  # "CUSTOMER_TO_COMPANY" yoki "COMPANY_TO_CUSTOMER"
                amount = order.price
                sign = Decimal("-1") if direction == "CUSTOMER_TO_COMPANY" else Decimal("1")
                transaction_type = "INCOME" if sign > 0 else "OUTCOME"

                balance_entries.append(
                    Balance(
                        customer=self,
                        user=order.created_by,
                        reason="ORDER",
                        payment_choice="PRODUCT",
                        change=amount * sign,
                        amount=amount,
                        type=transaction_type,
                        created_at=order.created_at,
                        comment=f"Order #{order.id}",
                    )
                )

            # SERVICE orders
            for order in self.orders.filter(product="SERVICE"):
                direction = order.order_type
                amount = order.price
                sign = Decimal("-1") if direction == "CUSTOMER_TO_COMPANY" else Decimal("1")
                transaction_type = "INCOME" if sign > 0 else "OUTCOME"

                balance_entries.append(
                    Balance(
                        customer=self,
                        user=order.created_by,
                        reason="ORDER",
                        payment_choice="SERVICE",
                        change=amount * sign,
                        amount=amount,
                        type=transaction_type,
                        created_at=order.created_at,
                        comment=f"Order #{order.id}",
                    )
                )

            # # 3. Create balances from payments
            # for payment in self.payments.filter(is_deleted=False):
            #     p_type = (
            #         payment.payment_type
            #     )  # "CUSTOMER_TO_COMPANY" or "COMPANY_TO_CUSTOMER"
            #     sign = (
            #         Decimal("1") if p_type == "CUSTOMER_TO_COMPANY" else Decimal("-1")
            #     )
            #     transaction_type = "INCOME" if sign > 0 else "OUTCOME"
            #
            #     balance_entries.append(
            #         Balance(
            #             customer=self,
            #             user=payment.created_by,
            #             payment=payment,
            #             reason="PAYMENT_INCOME" if sign > 0 else "PAYMENT_OUTCOME",
            #             change=payment.amount * sign,
            #             amount=payment.amount,
            #             type=transaction_type,
            #             created_at=payment.created_at,
            #             comment=payment.comment or f"Payment #{payment.id}",
            #         )
            #     )

            # PRODUCT payments
            for payment in self.payments.filter(is_deleted=False, payment_choice="PRODUCT"):
                p_type = (
                    payment.payment_type
                )  # "CUSTOMER_TO_COMPANY" or "COMPANY_TO_CUSTOMER"
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
                        payment_choice=payment.payment_choice,
                        change=payment.amount * sign,
                        amount=payment.amount,
                        type=transaction_type,
                        created_at=payment.created_at,
                        comment=payment.comment or f"Payment #{payment.id}",
                    )
                )

            # SERVICE payments
            for payment in self.payments.filter(is_deleted=False, payment_choice="SERVICE"):
                p_type = (
                    payment.payment_type
                )  # "CUSTOMER_TO_COMPANY" or "COMPANY_TO_CUSTOMER"
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
                        payment_choice=payment.payment_choice,
                        change=payment.amount * sign,
                        amount=payment.amount,
                        type=transaction_type,
                        created_at=payment.created_at,
                        comment=payment.comment or f"Payment #{payment.id}",
                    )
                )

            # 4. Bulk insert balances
            Balance.objects.bulk_create(balance_entries)

            # 5. Recalculate OrderSplit.left for CUSTOMER_TO_COMPANY
            total_received = self.balances.filter(
                type="INCOME",
            ).aggregate(
                total=Sum("change")
            )["total"] or Decimal("0")
            available_received = total_received

            splits = (
                InstallmentPayment.objects.filter(
                    order__customer=self, order__order_type="CUSTOMER_TO_COMPANY"
                )
                .select_related("order")
                .order_by("payment_date")
            )

            for split in splits:
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

            # 6. Recalculate OrderSplit.left for COMPANY_TO_CUSTOMER
            total_paid = self.balances.filter(type="OUTCOME").aggregate(
                total=Sum("change")
            )["total"] or Decimal("0")
            available_paid = abs(total_paid) if total_paid < 0 else Decimal("0")

            splits = (
                InstallmentPayment.objects.filter(
                    order__customer=self, order__order_type="COMPANY_TO_CUSTOMER"
                )
                .select_related("order")
                .order_by("payment_date")
            )

            for split in splits:
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

            # 7. Save snapshot balance to Customer
            self.balance = self.balances.aggregate(total=Sum("change"))[
                               "total"
                           ] or Decimal("0")
            self.save(update_fields=["balance"])
