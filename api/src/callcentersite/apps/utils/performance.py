"""
Utilidades para medición de rendimiento en Python.
Incluye decoradores y funciones para medir tiempo de ejecución y uso de memoria.
"""

import cProfile
import functools
import io
import logging
import pstats
import time
from contextlib import contextmanager
from typing import Any, Callable, TypeVar
from memory_profiler import profile as memory_profile

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def timeit(func: F) -> F:
    """
    Decorador para medir el tiempo de ejecución de una función.

    Ejemplo:
        @timeit
        def mi_funcion():
            time.sleep(1)
            return "hola"

        resultado = mi_funcion()  # Logs: "mi_funcion took 1.00 seconds"
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time

        logger.info(
            f"{func.__name__} took {execution_time:.4f} seconds",
            extra={
                "function": func.__name__,
                "execution_time": execution_time,
                "args": str(args)[:100],  # Primeros 100 chars
                "kwargs": str(kwargs)[:100],
            }
        )
        return result

    return wrapper  # type: ignore


def timeit_verbose(iterations: int = 1) -> Callable[[F], F]:
    """
    Decorador para medir el tiempo de ejecución con múltiples iteraciones.

    Args:
        iterations: Número de veces que se ejecutará la función

    Ejemplo:
        @timeit_verbose(iterations=100)
        def mi_funcion():
            return sum(range(1000))

        resultado = mi_funcion()
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            times = []
            result = None

            for i in range(iterations):
                start_time = time.perf_counter()
                result = func(*args, **kwargs)
                end_time = time.perf_counter()
                times.append(end_time - start_time)

            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)

            logger.info(
                f"{func.__name__} statistics over {iterations} iterations:\n"
                f"  Average: {avg_time:.6f}s\n"
                f"  Min: {min_time:.6f}s\n"
                f"  Max: {max_time:.6f}s",
                extra={
                    "function": func.__name__,
                    "iterations": iterations,
                    "avg_time": avg_time,
                    "min_time": min_time,
                    "max_time": max_time,
                }
            )

            return result

        return wrapper  # type: ignore

    return decorator


def profile_performance(output_file: str | None = None) -> Callable[[F], F]:
    """
    Decorador para perfilar el rendimiento de una función con cProfile.

    Args:
        output_file: Archivo donde guardar los resultados (opcional)

    Ejemplo:
        @profile_performance(output_file="profile_results.txt")
        def mi_funcion_compleja():
            # código complejo
            pass

        mi_funcion_compleja()
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            profiler = cProfile.Profile()
            profiler.enable()

            result = func(*args, **kwargs)

            profiler.disable()

            # Crear un stream para los resultados
            s = io.StringIO()
            stats = pstats.Stats(profiler, stream=s)
            stats.strip_dirs()
            stats.sort_stats("cumulative")
            stats.print_stats(20)  # Top 20 funciones

            profile_output = s.getvalue()

            # Guardar en archivo si se especifica
            if output_file:
                with open(output_file, "w") as f:
                    f.write(profile_output)
                logger.info(f"Profile results saved to {output_file}")

            # Log los resultados
            logger.info(
                f"Profile results for {func.__name__}:\n{profile_output}",
                extra={"function": func.__name__, "profile_type": "cProfile"}
            )

            return result

        return wrapper  # type: ignore

    return decorator


@contextmanager
def measure_time(operation_name: str):
    """
    Context manager para medir el tiempo de un bloque de código.

    Ejemplo:
        with measure_time("Database query"):
            User.objects.all()[:100]  # Logs: "Database query took 0.05 seconds"
    """
    start_time = time.perf_counter()
    try:
        yield
    finally:
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        logger.info(
            f"{operation_name} took {execution_time:.4f} seconds",
            extra={"operation": operation_name, "execution_time": execution_time}
        )


@contextmanager
def profile_block(output_file: str | None = None):
    """
    Context manager para perfilar un bloque de código.

    Ejemplo:
        with profile_block("complex_operation_profile.txt"):
            # código complejo
            for i in range(1000):
                complex_calculation()
    """
    profiler = cProfile.Profile()
    profiler.enable()

    try:
        yield profiler
    finally:
        profiler.disable()

        s = io.StringIO()
        stats = pstats.Stats(profiler, stream=s)
        stats.strip_dirs()
        stats.sort_stats("cumulative")
        stats.print_stats(30)

        profile_output = s.getvalue()

        if output_file:
            with open(output_file, "w") as f:
                f.write(profile_output)
            logger.info(f"Profile results saved to {output_file}")

        logger.info(f"Profile results:\n{profile_output}")


class PerformanceMonitor:
    """
    Clase para monitorear el rendimiento de múltiples operaciones.

    Ejemplo:
        monitor = PerformanceMonitor()

        with monitor.measure("operation1"):
            # código

        with monitor.measure("operation2"):
            # código

        monitor.report()  # Imprime reporte de todas las operaciones
    """

    def __init__(self):
        self.measurements: dict[str, list[float]] = {}

    @contextmanager
    def measure(self, operation_name: str):
        """Mide y registra una operación."""
        start_time = time.perf_counter()
        try:
            yield
        finally:
            end_time = time.perf_counter()
            execution_time = end_time - start_time

            if operation_name not in self.measurements:
                self.measurements[operation_name] = []

            self.measurements[operation_name].append(execution_time)

    def report(self):
        """Genera un reporte de todas las mediciones."""
        if not self.measurements:
            logger.info("No measurements recorded")
            return

        report_lines = ["Performance Report:", "=" * 60]

        for operation, times in self.measurements.items():
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            total_time = sum(times)

            report_lines.extend([
                f"\n{operation}:",
                f"  Executions: {len(times)}",
                f"  Total time: {total_time:.4f}s",
                f"  Average: {avg_time:.4f}s",
                f"  Min: {min_time:.4f}s",
                f"  Max: {max_time:.4f}s",
            ])

        report = "\n".join(report_lines)
        logger.info(report)

        return report

    def clear(self):
        """Limpia todas las mediciones."""
        self.measurements.clear()


# Decorator alias para compatibilidad
time_it = timeit
profile_it = profile_performance
