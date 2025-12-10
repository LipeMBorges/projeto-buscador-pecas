import asyncio
from browser_use_sdk import AsyncBrowserUse

from .browser_client import get_client
from .config import HARDWARE_SITES
from .models import SearchResult


def build_hardware_task_prompt(search_query: str) -> str:
    """
    Monta o prompt que será enviado para o Browser Use.

    IMPORTANTE:
    - 'search_query' aqui já é uma versão simplificada da frase do usuário,
      pensada só para ser usada no campo de busca dos sites (ex: 'Ryzen 7').
    - Filtros de preço / marca (ex: 'até 1500', 'ROG', 'TUF') serão aplicados
      localmente em Python, NÃO pelo agente no navegador.
    """
    sites_str = ", ".join(HARDWARE_SITES)

    prompt = f"""
Você é um agente especializado em pesquisar peças de hardware para computadores.

Seu objetivo é navegar em alguns sites de lojas brasileiras e retornar uma LISTA
ESTRUTURADA de produtos de hardware relacionados à consulta de busca.

IMPORTANTE:
- Use o texto da consulta de busca exatamente como fornecido abaixo ao usar a busca dos sites.
- NÃO aplique filtros de preço ou marca por conta própria.
- Apenas busque e colete os produtos relevantes à consulta.
- O sistema Python fará filtros adicionais (preço, marca, etc.) depois.
- Se algum site tiver desafio de segurança (como Cloudflare) ou não carregar,
  ignore esse site e continue com os outros.

SITES QUE VOCÊ PODE USAR (ACESSAR APENAS ESTES):
{sites_str}

CONSULTA DE BUSCA (COLE EXATAMENTE NO CAMPO DE BUSCA DO SITE):
\"\"\"{search_query}\"\"\"

PARA CADA SITE:
1. Abra o site.
2. Encontre o campo de busca.
3. Cole a consulta exatamente como escrita acima.
4. Pressione Enter ou clique no botão de buscar.
5. Na página de resultados, identifique produtos de hardware relevantes para a consulta.
   - Exemplos de itens válidos: placas de vídeo, processadores, memórias, SSDs, placas-mãe etc.
   - Evite acessórios irrelevantes como cabo HDMI, capinhas, adaptadores simples, etc.
6. Coleta de dados:
   Para cada produto relevante (até 10 por site), extraia:
   - store: nome da loja (ex: "Kabum", "TerabyteShop", "Pichau")
   - name: nome completo do produto, conforme aparece no site
   - price_brl: preço em reais como NÚMERO (float). Converta de texto como
     "R$ 1.999,90" para 1999.90 (sem "R$", sem ponto de milhar, use PONTO como separador decimal).
   - availability: texto simples como "Em estoque", "Esgotado", "Pré-venda" ou similar, se disponível.
   - url: link direto para a página do produto.

SOBRE SITES COM PROBLEMA:
- Se um site mostrar desafios de segurança (como Cloudflare), ficar travado, ou não carregar resultados,
  você pode pular esse site e continuar com os demais.
- Ainda assim, retorne os dados dos sites que funcionarem normalmente.

FORMATO DE RETORNO:
- Você DEVE retornar os dados exatamente no formato do schema Pydantic chamado SearchResult, que contém:
  - items: lista de objetos HardwareItem, cada um com {{ "store", "name", "price_brl", "availability", "url" }}.

- NÃO invente produtos.
- Se não encontrar nada em nenhum site, retorne SearchResult com items como lista vazia.
"""
    return prompt


async def search_hardware_async(search_query: str, show_steps: bool = True) -> SearchResult:
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
        task=build_hardware_task_prompt(search_query),
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
        print("\n[DEBUG] Saída bruta do LLM:")
        print(result.output)
        return SearchResult(items=[])

    return result.parsed_output


def search_hardware(search_query: str, show_steps: bool = True) -> SearchResult:
    """
    Versão síncrona (para ser chamada do main).
    """
    return asyncio.run(search_hardware_async(search_query, show_steps=show_steps))
