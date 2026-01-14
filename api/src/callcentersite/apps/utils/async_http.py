"""
Cliente HTTP asíncrono basado en HTTPX.
Migración de requests síncronos a HTTPX asíncrono para mejorar rendimiento.
"""

import asyncio
import logging
from typing import Any, Dict, Optional
from contextlib import asynccontextmanager

import httpx

logger = logging.getLogger(__name__)


class AsyncHTTPClient:
    """
    Cliente HTTP asíncrono para realizar peticiones I/O sin bloqueo.

    Ejemplo:
        client = AsyncHTTPClient()
        response = await client.get("https://api.example.com/data")

        # O usando context manager
        async with AsyncHTTPClient() as client:
            response = await client.get("https://api.example.com/data")
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        follow_redirects: bool = True,
        verify_ssl: bool = True,
        default_headers: Optional[Dict[str, str]] = None,
    ):
        """
        Inicializa el cliente HTTP asíncrono.

        Args:
            base_url: URL base para todas las peticiones
            timeout: Timeout en segundos para las peticiones
            follow_redirects: Seguir redirecciones automáticamente
            verify_ssl: Verificar certificados SSL
            default_headers: Headers por defecto para todas las peticiones
        """
        self.base_url = base_url
        self.timeout = timeout
        self.follow_redirects = follow_redirects
        self.verify_ssl = verify_ssl
        self.default_headers = default_headers or {}

        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()

    async def connect(self):
        """Establece la conexión del cliente."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout),
                follow_redirects=self.follow_redirects,
                verify=self.verify_ssl,
                headers=self.default_headers,
            )

    async def close(self):
        """Cierra la conexión del cliente."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """
        Realiza una petición GET asíncrona.

        Args:
            url: URL de la petición
            params: Parámetros de query string
            headers: Headers adicionales

        Returns:
            Response de HTTPX
        """
        if self._client is None:
            await self.connect()

        try:
            logger.debug(f"GET request to {url}")
            response = await self._client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise

    async def post(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """
        Realiza una petición POST asíncrona.

        Args:
            url: URL de la petición
            json: Datos JSON para el body
            data: Datos form para el body
            headers: Headers adicionales

        Returns:
            Response de HTTPX
        """
        if self._client is None:
            await self.connect()

        try:
            logger.debug(f"POST request to {url}")
            response = await self._client.post(
                url, json=json, data=data, headers=headers
            )
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise

    async def put(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """Realiza una petición PUT asíncrona."""
        if self._client is None:
            await self.connect()

        try:
            logger.debug(f"PUT request to {url}")
            response = await self._client.put(
                url, json=json, data=data, headers=headers
            )
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise

    async def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """Realiza una petición DELETE asíncrona."""
        if self._client is None:
            await self.connect()

        try:
            logger.debug(f"DELETE request to {url}")
            response = await self._client.delete(url, headers=headers)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise

    async def parallel_get(
        self,
        urls: list[str],
        params: Optional[Dict[str, Any]] = None,
    ) -> list[httpx.Response]:
        """
        Realiza múltiples peticiones GET en paralelo.

        Args:
            urls: Lista de URLs para solicitar
            params: Parámetros comunes para todas las peticiones

        Returns:
            Lista de respuestas en el mismo orden que las URLs

        Ejemplo:
            urls = ["https://api.example.com/1", "https://api.example.com/2"]
            responses = await client.parallel_get(urls)
        """
        if self._client is None:
            await self.connect()

        tasks = [self.get(url, params=params) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=False)


@asynccontextmanager
async def async_http_client(
    base_url: Optional[str] = None,
    timeout: float = 30.0,
) -> AsyncHTTPClient:
    """
    Context manager para crear y gestionar un cliente HTTP asíncrono.

    Ejemplo:
        async with async_http_client("https://api.example.com") as client:
            response = await client.get("/endpoint")
            data = response.json()
    """
    client = AsyncHTTPClient(base_url=base_url, timeout=timeout)
    await client.connect()
    try:
        yield client
    finally:
        await client.close()


async def fetch_url(
    url: str,
    method: str = "GET",
    **kwargs: Any,
) -> httpx.Response:
    """
    Función helper para realizar una petición HTTP asíncrona simple.

    Args:
        url: URL de la petición
        method: Método HTTP (GET, POST, PUT, DELETE)
        **kwargs: Argumentos adicionales para la petición

    Returns:
        Response de HTTPX

    Ejemplo:
        response = await fetch_url("https://api.example.com/data")
        data = response.json()
    """
    async with httpx.AsyncClient() as client:
        response = await client.request(method, url, **kwargs)
        response.raise_for_status()
        return response


async def fetch_multiple(
    urls: list[str],
    method: str = "GET",
    max_concurrent: int = 10,
) -> list[httpx.Response]:
    """
    Obtiene múltiples URLs en paralelo con límite de concurrencia.

    Args:
        urls: Lista de URLs para solicitar
        method: Método HTTP para todas las peticiones
        max_concurrent: Número máximo de peticiones concurrentes

    Returns:
        Lista de respuestas

    Ejemplo:
        urls = ["https://api.example.com/1", "https://api.example.com/2"]
        responses = await fetch_multiple(urls, max_concurrent=5)
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_with_semaphore(url: str) -> httpx.Response:
        async with semaphore:
            return await fetch_url(url, method=method)

    tasks = [fetch_with_semaphore(url) for url in urls]
    return await asyncio.gather(*tasks)


# Ejemplo de migración de código síncrono a asíncrono
class ExampleMigration:
    """
    Ejemplos de cómo migrar código de requests síncrono a HTTPX asíncrono.
    """

    # ANTES (síncrono con requests)
    # import requests
    #
    # def fetch_data(url):
    #     response = requests.get(url)
    #     return response.json()

    # DESPUÉS (asíncrono con HTTPX)
    @staticmethod
    async def fetch_data(url: str) -> dict:
        """Versión asíncrona de fetch_data."""
        response = await fetch_url(url)
        return response.json()

    # ANTES (múltiples peticiones síncronas)
    # def fetch_all(urls):
    #     results = []
    #     for url in urls:
    #         response = requests.get(url)
    #         results.append(response.json())
    #     return results

    # DESPUÉS (múltiples peticiones asíncronas en paralelo)
    @staticmethod
    async def fetch_all(urls: list[str]) -> list[dict]:
        """Versión asíncrona de fetch_all con ejecución paralela."""
        responses = await fetch_multiple(urls)
        return [response.json() for response in responses]
