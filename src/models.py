# src/models.py

from pydantic import BaseModel, Field
from typing import List, Optional


class HardwareItem(BaseModel):
    """
    Representa uma peça de hardware encontrada em um site.

    Essa estrutura será usada como "schema" para o Browser Use
    retornar dados já organizados.
    """
    store: str = Field(..., description="Nome da loja (ex: Kabum, Terabyte)")
    name: str = Field(..., description="Nome do produto")
    price_brl: float = Field(..., description="Preço em reais (somente número)")
    availability: Optional[str] = Field(
        None, description="Disponibilidade (ex: 'Em estoque', 'Esgotado')"
    )
    url: str = Field(..., description="URL do produto na loja")


class SearchResult(BaseModel):
    """
    Resultado de uma busca de peças em vários sites.
    """
    items: List[HardwareItem] = Field(
        default_factory=list,
        description="Lista de itens encontrados"
    )
