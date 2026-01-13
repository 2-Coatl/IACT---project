"""
Comando de Django para ejecutar profiling de código con cProfile y generar visualizaciones.

Uso:
    python manage.py profile_code --function=my_function --output=profile.prof
    python manage.py profile_code --snakeviz  # Abre visualización con SnakeViz
"""

import cProfile
import pstats
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Profile code execution with cProfile and optionally visualize with SnakeViz"

    def add_arguments(self, parser):
        parser.add_argument(
            "--code",
            type=str,
            help="Python code to profile (as string)",
        )
        parser.add_argument(
            "--file",
            type=str,
            help="Python file to profile",
        )
        parser.add_argument(
            "--output",
            type=str,
            default="profile.prof",
            help="Output file for profile data",
        )
        parser.add_argument(
            "--snakeviz",
            action="store_true",
            help="Open SnakeViz visualization after profiling",
        )
        parser.add_argument(
            "--top",
            type=int,
            default=20,
            help="Number of top functions to display",
        )
        parser.add_argument(
            "--sort",
            type=str,
            default="cumulative",
            choices=["cumulative", "time", "calls"],
            help="Sort order for profile results",
        )

    def handle(self, *args, **options):
        code = options.get("code")
        file_path = options.get("file")
        output = options["output"]
        snakeviz = options["snakeviz"]
        top = options["top"]
        sort_by = options["sort"]

        if not code and not file_path:
            raise CommandError("Either --code or --file must be specified")

        # Ejecutar profiling
        profiler = cProfile.Profile()

        self.stdout.write(self.style.SUCCESS("Starting profiling..."))

        if code:
            profiler.runctx(code, globals(), locals())
        elif file_path:
            with open(file_path) as f:
                code_content = f.read()
            profiler.runctx(code_content, globals(), locals())

        # Guardar resultados
        profiler.dump_stats(output)
        self.stdout.write(
            self.style.SUCCESS(f"Profile data saved to {output}")
        )

        # Mostrar estadísticas
        stats = pstats.Stats(profiler)
        stats.strip_dirs()
        stats.sort_stats(sort_by)

        self.stdout.write(self.style.WARNING(f"\nTop {top} functions by {sort_by}:"))
        stats.print_stats(top)

        # Abrir SnakeViz si se solicita
        if snakeviz:
            try:
                import subprocess
                self.stdout.write(
                    self.style.SUCCESS("\nOpening SnakeViz visualization...")
                )
                subprocess.run(["snakeviz", output])
            except FileNotFoundError:
                self.stdout.write(
                    self.style.ERROR(
                        "SnakeViz not found. Install it with: pip install snakeviz"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error opening SnakeViz: {e}")
                )

        self.stdout.write(
            self.style.SUCCESS("\nProfiling completed successfully!")
        )
        self.stdout.write(
            f"\nTo visualize results, run: snakeviz {output}"
        )
