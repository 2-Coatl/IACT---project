"""
Helpers y utilidades para programación asíncrona con AsyncIO.
Incluye decoradores, context managers y funciones útiles para async/await.
"""

import asyncio
import functools
import logging
from typing import Any, Callable, Coroutine, TypeVar
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

T = TypeVar("T")


def run_async(coro: Coroutine[Any, Any, T]) -> T:
    """
    Ejecuta una coroutine en un event loop nuevo.
    Útil para ejecutar código async desde código síncrono.

    Args:
        coro: Coroutine a ejecutar

    Returns:
        Resultado de la coroutine

    Ejemplo:
        async def async_function():
            await asyncio.sleep(1)
            return "done"

        result = run_async(async_function())  # "done"
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Si hay un loop corriendo, crear uno nuevo en un thread
            with ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        # No hay event loop, crear uno nuevo
        return asyncio.run(coro)


def async_to_sync(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., T]:
    """
    Decorador para convertir una función asíncrona en síncrona.

    Ejemplo:
        @async_to_sync
        async def fetch_data():
            await asyncio.sleep(1)
            return "data"

        result = fetch_data()  # Se puede llamar de forma síncrona
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        coro = func(*args, **kwargs)
        return run_async(coro)

    return wrapper


def sync_to_async(func: Callable[..., T]) -> Callable[..., Coroutine[Any, Any, T]]:
    """
    Decorador para convertir una función síncrona bloqueante en asíncrona.
    Ejecuta la función en un ThreadPoolExecutor para no bloquear el event loop.

    Ejemplo:
        @sync_to_async
        def blocking_io():
            time.sleep(5)
            return "done"

        result = await blocking_io()  # No bloquea el event loop
    """
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,  # Usa el executor por defecto
            functools.partial(func, *args, **kwargs)
        )

    return wrapper


async def gather_with_concurrency(
    n: int,
    *tasks: Coroutine[Any, Any, T],
) -> list[T]:
    """
    Similar a asyncio.gather pero con límite de concurrencia.

    Args:
        n: Número máximo de tareas concurrentes
        *tasks: Tareas a ejecutar

    Returns:
        Lista de resultados

    Ejemplo:
        tasks = [fetch_url(url) for url in urls]
        results = await gather_with_concurrency(5, *tasks)
    """
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task: Coroutine[Any, Any, T]) -> T:
        async with semaphore:
            return await task

    return await asyncio.gather(*(sem_task(task) for task in tasks))


async def retry_async(
    func: Callable[..., Coroutine[Any, Any, T]],
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
) -> T:
    """
    Reintenta una función asíncrona con backoff exponencial.

    Args:
        func: Función asíncrona a ejecutar
        max_retries: Número máximo de reintentos
        delay: Delay inicial entre reintentos en segundos
        backoff: Factor de multiplicación del delay
        exceptions: Tupla de excepciones a capturar

    Returns:
        Resultado de la función

    Ejemplo:
        result = await retry_async(
            lambda: fetch_url("https://api.example.com"),
            max_retries=5,
            delay=1.0,
        )
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await func()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries:
                wait_time = delay * (backoff ** attempt)
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                    f"Retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"All {max_retries + 1} attempts failed")

    raise last_exception


def retry_async_decorator(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """
    Decorador para reintentar funciones asíncronas.

    Ejemplo:
        @retry_async_decorator(max_retries=5, delay=1.0)
        async def fetch_data():
            async with httpx.AsyncClient() as client:
                response = await client.get("https://api.example.com")
                return response.json()

        data = await fetch_data()
    """
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]):
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            return await retry_async(
                lambda: func(*args, **kwargs),
                max_retries=max_retries,
                delay=delay,
                backoff=backoff,
                exceptions=exceptions,
            )
        return wrapper
    return decorator


async def timeout_async(
    coro: Coroutine[Any, Any, T],
    timeout_seconds: float,
) -> T:
    """
    Ejecuta una coroutine con timeout.

    Args:
        coro: Coroutine a ejecutar
        timeout_seconds: Timeout en segundos

    Returns:
        Resultado de la coroutine

    Raises:
        asyncio.TimeoutError: Si se excede el timeout

    Ejemplo:
        try:
            result = await timeout_async(fetch_data(), timeout_seconds=5.0)
        except asyncio.TimeoutError:
            print("Operation timed out")
    """
    return await asyncio.wait_for(coro, timeout=timeout_seconds)


class AsyncEventLoopManager:
    """
    Gestor de event loop para debugging y monitoreo.

    Ejemplo:
        manager = AsyncEventLoopManager()
        manager.start()

        # Tu código asíncrono
        await manager.run(my_async_function())

        manager.stop()
        manager.print_stats()
    """

    def __init__(self):
        self.loop: asyncio.AbstractEventLoop | None = None
        self.tasks: list[asyncio.Task] = []
        self.start_time: float = 0.0

    def start(self):
        """Inicia el event loop."""
        try:
            self.loop = asyncio.get_running_loop()
            logger.info("Using existing event loop")
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            logger.info("Created new event loop")

        self.start_time = self.loop.time()

        # Habilitar debug mode si es necesario
        self.loop.set_debug(True)

    def stop(self):
        """Detiene el event loop."""
        if self.loop and not self.loop.is_closed():
            pending = asyncio.all_tasks(self.loop)
            for task in pending:
                task.cancel()

            self.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            self.loop.close()
            logger.info("Event loop stopped")

    async def run(self, coro: Coroutine[Any, Any, T]) -> T:
        """Ejecuta una coroutine en el event loop."""
        if not self.loop:
            self.start()

        task = asyncio.create_task(coro)
        self.tasks.append(task)
        return await task

    def print_stats(self):
        """Imprime estadísticas del event loop."""
        if not self.loop:
            logger.info("No event loop running")
            return

        elapsed = self.loop.time() - self.start_time
        logger.info(f"Event loop stats:")
        logger.info(f"  Running time: {elapsed:.2f}s")
        logger.info(f"  Tasks created: {len(self.tasks)}")
        logger.info(f"  Tasks completed: {sum(1 for t in self.tasks if t.done())}")
        logger.info(f"  Tasks pending: {sum(1 for t in self.tasks if not t.done())}")


# Ejemplo de uso del event loop debugging
async def debug_slow_task():
    """Ejemplo de debugging de tareas lentas."""
    import sys

    # Habilitar debug warnings para coroutines que tardan mucho
    asyncio.get_event_loop().slow_callback_duration = 0.1

    # Tu código aquí
    await asyncio.sleep(0.2)  # Esto generará un warning

    # Para ver todas las tareas en ejecución
    for task in asyncio.all_tasks():
        print(f"Task: {task.get_name()}, Done: {task.done()}")
