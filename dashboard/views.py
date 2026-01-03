from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
import logging

from django.db.models import Count, Sum
from django.db.models.functions import Coalesce, TruncDate
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import TicketSettlement
from printer.service import PrintService


logger = logging.getLogger(__name__)


class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        self._ensure_superuser(request)

        start_date, end_date = self._resolve_period(
            request.query_params.get("date"),
            request.query_params.get("start_date"),
            request.query_params.get("end_date"),
        )
        summary = self._build_summary(start_date, end_date)
        return Response(summary, status=status.HTTP_200_OK)

    def _ensure_superuser(self, request: Request) -> None:
        if not request.user.is_superuser:
            raise PermissionDenied("Apenas superusuários podem acessar o dashboard.")

    def _build_summary(self, start_date: date, end_date: date) -> dict:
        start, end = self._range_boundaries(start_date, end_date)
        settlements_qs = self._get_settlements_queryset(start, end)
        aggregates = self._aggregate_metrics(settlements_qs)

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

        return {
            "date": start_date.isoformat(),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_sales": float(aggregates["total_sales"]),
            "total_additions": float(aggregates["total_additions"]),
            "total_tables": int(aggregates["tables_served"]),
            "daily_breakdown": self._daily_breakdown(settlements_qs),
            "settlements": settlements,
        }

    def _get_settlements_queryset(
        self, start: datetime, end: datetime
    ):
        return (
            TicketSettlement.objects.select_related("ticket")
            .filter(created_at__gte=start, created_at__lte=end, canceled=False)
            .order_by("-created_at")
        )

    def _resolve_target_date(self, date_param: str | None) -> date:
        if not date_param:
            return timezone.localdate()
        return self._parse_date(date_param, "data")

    def _resolve_period(
        self,
        date_param: str | None,
        start_param: str | None,
        end_param: str | None,
    ) -> tuple[date, date]:
        if start_param or end_param:
            if not start_param or not end_param:
                raise ValidationError(
                    "Informe as datas inicial e final para consultar o período."
                )
            start_date = self._parse_date(start_param, "data inicial")
            end_date = self._parse_date(end_param, "data final")
            if start_date > end_date:
                raise ValidationError(
                    "A data inicial deve ser menor ou igual à data final."
                )
            return start_date, end_date

        target_date = self._resolve_target_date(date_param)
        return target_date, target_date

    def _parse_date(self, date_str: str, field_label: str) -> date:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValidationError(
                f"Formato de data inválido para {field_label}. Use AAAA-MM-DD."
            ) from exc

    def _range_boundaries(self, start_date: date, end_date: date) -> tuple[datetime, datetime]:
        start = datetime.combine(start_date, time.min)
        end = datetime.combine(end_date, time.max)
        if timezone.is_naive(start):
            start = timezone.make_aware(start)
            end = timezone.make_aware(end)
        return start, end

    def _aggregate_metrics(self, queryset):
        return queryset.aggregate(
            total_sales=Coalesce(Sum("final_value"), Decimal("0")),
            total_additions=Coalesce(Sum("additions_value"), Decimal("0")),
            tables_served=Count("id"),
        )

    def _daily_breakdown(self, queryset):
        daily_stats = (
            queryset.annotate(day=TruncDate("created_at"))
            .values("day")
            .order_by("day")
            .annotate(
                total_additions=Coalesce(Sum("additions_value"), Decimal("0")),
                tables_served=Count("id"),
            )
        )
        return [
            {
                "date": day_stats["day"].isoformat() if day_stats["day"] else None,
                "total_additions": float(day_stats["total_additions"]),
                "total_tables": int(day_stats["tables_served"]),
            }
            for day_stats in daily_stats
        ]


class DashboardAdditionsPrintView(DashboardSummaryView):
    def post(self, request: Request) -> Response:
        self._ensure_superuser(request)

        payload = request.data if hasattr(request, "data") else {}
        if not hasattr(payload, "get"):
            payload = {}

        date_param = payload.get("date") or request.query_params.get("date")
        start_param = payload.get("start_date") or request.query_params.get("start_date")
        end_param = payload.get("end_date") or request.query_params.get("end_date")

        start_date, end_date = self._resolve_period(date_param, start_param, end_param)
        start_dt, end_dt = self._range_boundaries(start_date, end_date)
        settlements_qs = self._get_settlements_queryset(start_dt, end_dt)
        aggregates = self._aggregate_metrics(settlements_qs)

        printer_service = PrintService()
        try:
            success, printer_status, printer_response = (
                printer_service.print_dashboard_summary(
                    start_date=start_date,
                    end_date=end_date,
                    total_additions=aggregates["total_additions"],
                    total_tables=int(aggregates["tables_served"]),
                )
            )
        except Exception as exc:  # pragma: no cover
            logger.exception("Erro ao imprimir resumo dos 10%%: %s", exc)
            raise ValidationError("Erro ao enviar a impressão.")

        if not success:
            logger.error(
                "Falha ao imprimir resumo dos 10%% (status=%s, response=%s)",
                printer_status,
                printer_response,
            )
            raise ValidationError(
                "Não foi possível enviar a impressão. Tente novamente em instantes."
            )

        return Response(status=status.HTTP_202_ACCEPTED)
