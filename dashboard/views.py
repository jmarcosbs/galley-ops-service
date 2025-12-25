from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import TicketSettlement


class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        if not request.user.is_superuser:
            raise PermissionDenied("Apenas superusuários podem acessar o dashboard.")

        target_date = self._resolve_target_date(request.query_params.get("date"))
        start, end = self._date_boundaries(target_date)

        settlements_qs = (
            TicketSettlement.objects.select_related("ticket")
            .filter(created_at__gte=start, created_at__lte=end, canceled=False)
            .order_by("-created_at")
        )

        aggregates = settlements_qs.aggregate(
            total_sales=Coalesce(Sum("final_value"), Decimal("0")),
            total_additions=Coalesce(Sum("additions_value"), Decimal("0")),
        )

        settlements = [
            {
                "uuid": str(settlement.uuid),
                "ticket_number": settlement.ticket.number,
                "ticket_label": settlement.ticket.table_label,
                "is_outside": settlement.ticket.is_outside,
                "final_value": float(settlement.final_value),
                "additions_value": float(settlement.additions_value),
                "created_at": settlement.created_at.isoformat(),
            }
            for settlement in settlements_qs
        ]

        data = {
            "date": target_date.isoformat(),
            "total_sales": float(aggregates["total_sales"]),
            "total_additions": float(aggregates["total_additions"]),
            "settlements": settlements,
        }

        return Response(data, status=status.HTTP_200_OK)

    def _resolve_target_date(self, date_param: str | None) -> date:
        if not date_param:
            return timezone.localdate()
        try:
            return datetime.strptime(date_param, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValidationError("Formato de data inválido. Use AAAA-MM-DD.") from exc

    def _date_boundaries(self, target: date) -> tuple[datetime, datetime]:
        start = datetime.combine(target, time.min)
        end = datetime.combine(target, time.max)
        if timezone.is_naive(start):
            start = timezone.make_aware(start)
            end = timezone.make_aware(end)
        return start, end
