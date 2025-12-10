import asyncio
from browser_use_sdk import AsyncBrowserUse

from .browser_client import get_client
from .config import HARDWARE_SITES
from .models import SearchResult


def build_hardware_task_prompt(query: str) -> str:
    """
    Monta o prompt que será enviado para o Browser Use.

    Explicando para júnior:
    - Aqui você descreve, em linguagem natural, o que quer que o
      agente faça dentro do navegador.
    - Seja específico com os sites e com o formato dos dados.
    """
    sites_str = ", ".join(HARDWARE_SITES)

    prompt = f"""
Você é um agente especializado em pesquisar peças de hardware para computadores.

1. Acesse APENAS os seguintes sites de lojas de hardware brasileiras:
   {sites_str}

2. Em cada um desses sites, pesquise pela seguinte peça (use o campo de busca do site):
   "{query}"

3. Para cada site, pegue até os 5 primeiros resultados que realmente correspondam à peça
   (por exemplo, mesma GPU/CPU, mesma geração ou muito próxima).

4. Para cada produto encontrado, extraia:
   - store: nome da loja (ex: Kabum, Terabyte, Pichau)
   - name: nome completo do produto
   - price_brl: preço em reais como número (sem R$, sem ponto de milhar, use ponto como separador decimal)
   - availability: texto simples como "Em estoque", "Esgotado", "Pré-venda" ou similar
   - url: link direto para a página do produto

5. Não inclua itens que sejam acessórios irrelevantes (ex: cabo HDMI, capinha, etc.)
   se a busca for por uma peça principal (GPU, CPU, memória, SSD...).

6. Retorne os dados EXATAMENTE no formato do schema Pydantic que o sistema espera.
"""
    return prompt


async def search_hardware_async(query: str, show_steps: bool = True) -> SearchResult:
    """
    Função assíncrona que:
    - Cria o client do Browser Use
    - Cria uma task pedindo para buscar a peça em vários sites
    - (Opcional) Mostra passos em tempo real
    - Aguarda a conclusão e retorna um SearchResult (Pydantic)
    """
    client: AsyncBrowserUse = get_client()

    print("[INFO] Criando task na Browser Use Cloud...")
    task = await client.tasks.create_task(
        task=build_hardware_task_prompt(query),
        schema=SearchResult,
    )

    if show_steps:
        print("\n[INFO] Acompanhando passos em tempo real:\n")
        async for step in task.stream():
            print(
                f"[PASSO {step.number}] "
                f"URL atual: {step.url or '-'} | Próximo objetivo: {step.next_goal}"
            )

    print("\n[INFO] Task finalizada. Buscando resultado estruturado...\n")

    result = await task.complete()

    if result.parsed_output is None:
        print("[AVISO] Não foi possível converter a saída para SearchResult. Verifique o prompt.")
        return SearchResult(items=[])

    return result.parsed_output


def search_hardware(query: str, show_steps: bool = True) -> SearchResult:
    """
    Versão síncrona (para ser chamada do main).

    Explicação para júnior:
    - Asyncio é como "modo turbo" para I/O.
    - Mas às vezes queremos só chamar uma função normal.
    - Aqui, usamos asyncio.run() para rodar a função async.
    """
    return asyncio.run(search_hardware_async(query, show_steps=show_steps))
