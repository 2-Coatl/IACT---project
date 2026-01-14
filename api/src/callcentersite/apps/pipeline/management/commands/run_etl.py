"""Comando para ejecutar el ETL manualmente."""

from __future__ import annotations

from django.core.management.base import BaseCommand

from ...jobs import run_etl


class Command(BaseCommand):
    help = "Ejecuta el proceso ETL completo"

    def handle(self, *args, **options):  # type: ignore[override]
        run_etl()
        self.stdout.write(self.style.SUCCESS("Proceso ETL ejecutado correctamente"))
