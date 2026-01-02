from __future__ import annotations

import re
from datetime import date, datetime, time
from pathlib import Path
from typing import Iterable
from zipfile import ZIP_DEFLATED, ZipFile

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q, QuerySet
from django.utils import timezone

from orders.models import TicketSettlement


class Command(BaseCommand):
    help = (
        "Exporta os XML das NFC-e não canceladas entre duas datas para um arquivo .zip."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "start_date",
            help="Data inicial (AAAA-MM-DD) usada para filtrar pela autorização da NFC-e.",
        )
        parser.add_argument(
            "end_date",
            help="Data final (AAAA-MM-DD) usada para filtrar pela autorização da NFC-e.",
        )
        parser.add_argument(
            "--output",
            dest="output_path",
            help=(
                "Caminho completo para o arquivo .zip de saída "
                "(padrão: nfce_xml_<inicio>_<fim>.zip no diretório atual)."
            ),
        )

    def handle(self, *args, **options):
        start_date = self._parse_date(options["start_date"])
        end_date = self._parse_date(options["end_date"])

        if start_date > end_date:
            raise CommandError("A data inicial não pode ser maior do que a data final.")

        start_datetime, end_datetime = self._build_datetime_range(start_date, end_date)
        queryset = self._build_queryset(start_datetime, end_datetime)
        total = queryset.count()

        if total == 0:
            self.stdout.write(
                self.style.WARNING(
                    "Nenhuma NFC-e com XML encontrada para o intervalo informado."
                )
            )
            return

        output_path = self._resolve_output_path(
            options.get("output_path"), start_date, end_date
        )
        saved = self._write_zip(output_path, queryset.iterator())

        self.stdout.write(
            self.style.SUCCESS(
                f"{saved} arquivos XML exportados para '{output_path.resolve()}'."
            )
        )

    def _parse_date(self, value: str) -> date:
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError as exc:
            raise CommandError(
                f"Data inválida '{value}'. Utilize o formato AAAA-MM-DD."
            ) from exc

    def _build_datetime_range(self, start: date, end: date) -> tuple[datetime, datetime]:
        start_dt = datetime.combine(start, time.min)
        end_dt = datetime.combine(end, time.max)
        return (self._make_aware(start_dt), self._make_aware(end_dt))

    def _make_aware(self, dt: datetime) -> datetime:
        if timezone.is_naive(dt):
            return timezone.make_aware(dt, timezone.get_current_timezone())
        return dt

    def _build_queryset(
        self, start_datetime: datetime, end_datetime: datetime
    ) -> QuerySet[TicketSettlement]:
        """
        Limita os resultados para NFC-e autorizadas (ou emitidas) no intervalo informado.
        """
        auth_range = Q(nfce_authorization_datetime__range=(start_datetime, end_datetime))
        emission_range = Q(nfce_emission_datetime__range=(start_datetime, end_datetime))

        return (
            TicketSettlement.objects.filter(canceled=False, nfce_xml__isnull=False)
            .filter(auth_range | (Q(nfce_authorization_datetime__isnull=True) & emission_range))
            .order_by("nfce_authorization_datetime", "nfce_emission_datetime", "created_at")
        )

    def _resolve_output_path(
        self, user_defined_path: str | None, start_date: date, end_date: date
    ) -> Path:
        if user_defined_path:
            path = Path(user_defined_path)
        else:
            filename = f"nfce_xml_{start_date.isoformat()}_{end_date.isoformat()}.zip"
            path = Path.cwd() / filename

        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def _write_zip(
        self, output_path: Path, settlements: Iterable[TicketSettlement]
    ) -> int:
        """
        Persist the XMLs while ensuring unique filenames inside the archive.
        """
        used_names: dict[str, int] = {}
        saved = 0
        with ZipFile(output_path, "w", compression=ZIP_DEFLATED) as zip_file:
            for settlement in settlements:
                xml_content = (settlement.nfce_xml or "").strip()
                if not xml_content:
                    continue
                filename = self._build_unique_filename(settlement, used_names)
                zip_file.writestr(filename, xml_content)
                saved += 1
        return saved

    def _build_unique_filename(
        self, settlement: TicketSettlement, used_names: dict[str, int]
    ) -> str:
        candidate = (
            settlement.nfce_access_key
            or settlement.nfce_number
            or settlement.nfce_series
            or str(settlement.id)
        )
        sanitized = self._sanitize_file_stem(candidate)
        counter = used_names.get(sanitized, 0)
        used_names[sanitized] = counter + 1

        suffix = "" if counter == 0 else f"_{counter}"
        return f"{sanitized}{suffix}.xml"

    def _sanitize_file_stem(self, value: str) -> str:
        sanitized = re.sub(r"[^0-9A-Za-z_-]", "_", value.strip())
        return sanitized or "nfce"
