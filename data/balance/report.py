import io
import os

import requests
import xlsxwriter
from datetime import datetime, time

from django.db.models import Sum, Q
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from xlsxwriter import worksheet

from data.balance.models import Balance
from data.balance.services import mutual_settlements
from data.bot.permission import IsBotAuthenticated
from data.customer.models import Customer


class BalanceReportExportView(APIView):
    permission_classes = [IsBotAuthenticated]

    def get(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        customer_id = request.query_params.get("customer_id")

        chat_id = self.request.bot_user.chat_id

        if not start_date or not end_date or not customer_id:
            return Response(
                {"error": "start_date, end_date va customer_id kerak"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            start = datetime.combine(
                datetime.strptime(start_date, "%Y-%m-%d"), time.min
            )
            end = datetime.combine(datetime.strptime(end_date, "%Y-%m-%d"), time.max)
            customer_id = int(customer_id)
        except ValueError:
            return Response(
                {"error": "Sana yoki customer_id noto'g'ri. Sana formati: YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # balances = (
        #     Balance.objects.filter(
        #         created_at__range=(start, end), customer_id=customer_id
        #     )
        #     .select_related("user", "customer")
        #     .order_by("-created_at", "-id")
        # )
        #
        # # Balanslar xaritasi
        # balances_map = {}
        # records = mutual_settlements(self, customer_id=customer_id)
        # for record in records:
        #     balances_map[record["id"]] = {
        #         "start_balance": record["start_balance"],
        #         "final_balance": record["final_balance"],
        #     }
        #
        # output = io.BytesIO()
        # workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        # worksheet = workbook.add_worksheet("Hisobot")
        #
        # # Header
        # headers = [
        #     "Sana",
        #     "Turi",
        #     "Sabab",
        #     "Boshlang'ich summa",
        #     "O‘zgarish",
        #     "Oxirgi summa",
        #     "Izoh",
        # ]
        # for col_num, header in enumerate(headers):
        #     worksheet.write(0, col_num, header)
        #
        # type_display = {"income": "Kirim", "outcome": "Chiqim"}
        #
        # reason_display = {"payment": "To‘lov", "order": "Buyurtma"}
        #
        # # Ma’lumotlar
        # for row_num, balance in enumerate(balances, start=1):
        #     bal_data = balances_map.get(balance.id, {})
        #     worksheet.write(row_num, 0, balance.created_at.strftime("%d-%m-%Y"))
        #     worksheet.write(row_num, 1, type_display.get(balance.type, balance.type))
        #     worksheet.write(
        #         row_num, 2, reason_display.get(balance.reason, balance.reason)
        #     )
        #     worksheet.write(row_num, 3, bal_data.get("start_balance", "-"))
        #     worksheet.write(row_num, 4, balance.change)
        #     worksheet.write(row_num, 5, bal_data.get("final_balance", "-"))
        #     worksheet.write(row_num, 6, balance.comment or "")

        balances = (
            Balance.objects.filter(
                created_at__range=(start, end), customer_id=customer_id
            )
            .select_related("user", "customer")
            .order_by("-created_at", "-id")
        )

        # Balanslar xaritasi
        balances_map = {}
        records = mutual_settlements(self, customer_id=customer_id)
        for record in records:
            balances_map[record["id"]] = {
                "start_balance": record["start_balance"],
                "final_balance": record["final_balance"],
            }

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        worksheet = workbook.add_worksheet("Hisobot")

        # Header
        headers = [
            "Sana",
            "Turi",
            "Sabab",
            "Boshlang'ich summa",
            "O‘zgarish",
            "Oxirgi summa",
            "Izoh",
        ]
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header)

        type_display = {"income": "Kirim", "outcome": "Chiqim"}
        reason_display = {"payment": "To‘lov", "order": "Buyurtma"}

        # Ma’lumotlar
        for row_num, balance in enumerate(balances, start=1):
            bal_data = balances_map.get(balance.id, {})
            worksheet.write(row_num, 0, balance.created_at.strftime("%d-%m-%Y"))
            worksheet.write(row_num, 1, type_display.get(balance.type, balance.type))
            worksheet.write(
                row_num, 2, reason_display.get(balance.reason, balance.reason)
            )
            worksheet.write(row_num, 3, bal_data.get("start_balance", "-"))
            worksheet.write(row_num, 4, balance.change)
            worksheet.write(row_num, 5, bal_data.get("final_balance", "-"))
            worksheet.write(row_num, 6, balance.comment or "")

        # ======== Statistika qo‘shish ========
        stats_all = balances.aggregate(
            total_income=Sum("change", filter=Q(type="INCOME")),
            total_outcome=Sum("change", filter=Q(type="OUTCOME")),
        )

        stats_product = balances.filter(payment_choice="PRODUCT").aggregate(
            total_income=Sum("change", filter=Q(type="INCOME")),
            total_outcome=Sum("change", filter=Q(type="OUTCOME")),
        )

        stats_service = balances.filter(payment_choice="SERVICE").aggregate(
            total_income=Sum("change", filter=Q(type="INCOME")),
            total_outcome=Sum("change", filter=Q(type="OUTCOME")),
        )

        row_offset = len(balances) + 2
        worksheet.write(row_offset, 0, "Statistika")
        worksheet.write(row_offset + 1, 0, "Turi")
        worksheet.write(row_offset + 1, 1, "Kirim")
        worksheet.write(row_offset + 1, 2, "Chiqim")
        worksheet.write(row_offset + 1, 3, "Yakuniy balans")

        worksheet.write(row_offset + 2, 0, "Umumiy")
        worksheet.write(row_offset + 2, 1, stats_all["total_income"] or 0)
        worksheet.write(row_offset + 2, 2, stats_all["total_outcome"] or 0)
        worksheet.write(row_offset + 2, 3, (stats_all["total_income"] or 0) - (stats_all["total_outcome"] or 0))

        worksheet.write(row_offset + 3, 0, "PRODUCT")
        worksheet.write(row_offset + 3, 1, stats_product["total_income"] or 0)
        worksheet.write(row_offset + 3, 2, stats_product["total_outcome"] or 0)
        worksheet.write(row_offset + 3, 3, (stats_product["total_income"] or 0) - (stats_product["total_outcome"] or 0))

        worksheet.write(row_offset + 4, 0, "SERVICE")
        worksheet.write(row_offset + 4, 1, stats_service["total_income"] or 0)
        worksheet.write(row_offset + 4, 2, stats_service["total_outcome"] or 0)
        worksheet.write(row_offset + 4, 3, (stats_service["total_income"] or 0) - (stats_service["total_outcome"] or 0))

        workbook.close()
        output.seek(0)

        filename = f"hisobot_{start_date}_dan_{end_date}_gacha.xlsx"

        files = {'document': (filename, output.getvalue())}
        data = {'chat_id': chat_id}

        BOT_TOKEN = os.environ.get("BOT_TOKEN")

        if not BOT_TOKEN:
            return Response(
                {"error": "Telegram bot tokeni sozlanmagan"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response = requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendDocument',
            files=files,
            data=data
        )

        if response.status_code != 200:
            return Response(
                {"error": "Telegramga fayl yuborishda xatolik", "details": response.json()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"success": "Hisobot fayli muvaffaqiyatli yuborildi"},
            status=status.HTTP_200_OK,
        )

        # response = HttpResponse(
        #     output,
        #     content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        # )
        # response["Content-Disposition"] = f"attachment; filename={filename}"
        # return response
