# src/browser_client.py

from browser_use_sdk import AsyncBrowserUse
from .config import BROWSER_USE_API_KEY


def get_client() -> AsyncBrowserUse:
    """
    Cria e retorna uma instância do cliente AsyncBrowserUse.

    Boas práticas:
    - Centralizar a criação do client em um único lugar
    - Facilitar testes (mockar esse client no futuro)
    """
    client = AsyncBrowserUse(
        api_key=BROWSER_USE_API_KEY  # também poderia vir do env
    )
    return client
