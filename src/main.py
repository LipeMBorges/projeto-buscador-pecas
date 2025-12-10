import re
from typing import List, Optional

import pandas as pd

from .models import SearchResult
from .tasks import search_hardware


# Palavras que vamos tentar detectar como "marca/linha"
BRAND_KEYWORDS = ["rog", "tuf", "asus", "strix"]


def result_to_dataframe(result: SearchResult) -> pd.DataFrame:
    """
    Converte SearchResult (Pydantic) em um DataFrame do pandas.
    """
    if not result.items:
        return pd.DataFrame(columns=["store", "name", "price_brl", "availability", "url"])

    data = [item.model_dump() for item in result.items]
    df = pd.DataFrame(data)
    return df


def extract_max_price_from_query(query: str) -> Optional[float]:
    """
    Tenta encontrar um valor numérico na frase e usar como "preço máximo".

    Exemplo:
    - "até 5000 mil reais" -> 5000.0
    - "abaixo de 2500" -> 2500.0

    Estratégia:
    - Procurar números na string.
    - Pegar o ÚLTIMO número encontrado (normalmente é o preço).
    """
    numbers = re.findall(r"\d+(?:[.,]\d+)?", query)

    if not numbers:
        return None

    value_str = numbers[-1]
    value_str = value_str.replace(".", "").replace(",", ".")

    try:
        value = float(value_str)
        return value
    except ValueError:
        return None


def extract_brand_keywords_from_query(query: str) -> List[str]:
    """
    Procura por palavras como 'rog', 'tuf', 'asus', 'strix' na query.

    Retorna a lista de palavras encontradas.
    """
    q = query.lower()
    found = [kw for kw in BRAND_KEYWORDS if kw in q]
    return found


def build_search_terms(query: str) -> str:
    """
    Gera a string que será usada no campo de busca dos sites.

    Estratégia simples:
    - Divide a frase em tokens.
    - Vai pegando os tokens até encontrar uma palavra que sugira início de condição de preço,
      como 'até', 'ate', 'abaixo', 'menos', 'baixo'.
    - Exemplo:
      - 'RTX ROG ou TUF até 5000 mil reais' -> 'RTX ROG ou TUF'
      - 'Ryzen 7 até 1500' -> 'Ryzen 7'
      - 'SSD 1TB abaixo de 600' -> 'SSD 1TB'
    - Se não encontrar nenhuma dessas palavras, devolve a frase inteira.
    """
    tokens = query.split()
    cut_words = {"até", "ate", "abaixo", "menos", "baixo"}

    kept_tokens: List[str] = []
    for tok in tokens:
        if tok.lower() in cut_words:
            break
        kept_tokens.append(tok)

    if not kept_tokens:
        return query.strip()

    return " ".join(kept_tokens).strip()


def filter_dataframe(
    df: pd.DataFrame,
    max_price: Optional[float] = None,
    brand_keywords: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Aplica filtros de preço e marca no DataFrame.

    - max_price: se fornecido, mantém apenas itens com price_brl <= max_price.
    - brand_keywords: se fornecido, mantém apenas itens cujo 'name' contenha
      pelo menos uma dessas palavras (ignorando maiúsculas/minúsculas).
    """
    if df.empty:
        return df

    filtered = df.copy()

    # Filtro de preço
    if max_price is not None and "price_brl" in filtered.columns:
        before_count = len(filtered)
        filtered = filtered[filtered["price_brl"] <= max_price]
        after_count = len(filtered)
        print(f"[INFO] Filtro de preço: {before_count} -> {after_count} itens (<= {max_price:.2f})")

    # Filtro de marca/linha
    if brand_keywords:
        name_lower = filtered["name"].astype(str).str.lower()
        mask = False

        for kw in brand_keywords:
            mask = mask | name_lower.str.contains(kw, na=False)

        before_count = len(filtered)
        filtered = filtered[mask]
        after_count = len(filtered)
        print(f"[INFO] Filtro de marca/linha ({', '.join(brand_keywords)}): {before_count} -> {after_count} itens")

    # Ordena por preço (se disponível)
    if "price_brl" in filtered.columns:
        filtered = filtered.sort_values(by="price_brl", ascending=True)

    return filtered


def main():
    print("=" * 60)
    print(" BUSCADOR DE PEÇAS (Browser Use + Python) ")
    print("=" * 60)

    query = input("Digite o que você quer buscar (ex: 'RTX ROG ou TUF até 5000 mil reais'): ").strip()

    if not query:
        print("Você não digitou nada. Encerrando.")
        return

    # Extrai filtros da query ORIGINAL
    max_price = extract_max_price_from_query(query)
    brand_keywords = extract_brand_keywords_from_query(query)

    # Gera a string que será usada na busca dos sites
    search_terms = build_search_terms(query)
    print(f"\n[DEBUG] Termos de busca usados nos sites: {search_terms!r}")
    if max_price is not None:
        print(f"[DEBUG] Preço máximo detectado: {max_price:.2f}")
    if brand_keywords:
        print(f"[DEBUG] Palavras de marca/linha detectadas: {', '.join(brand_keywords)}")

    print("\n[INFO] Buscando peças, isso pode levar alguns segundos...\n")

    # Busca usando Browser Use (navegação na nuvem)
    result: SearchResult = search_hardware(search_terms, show_steps=True)

    # Converte para DataFrame
    df = result_to_dataframe(result)

    if df.empty:
        print("Nenhum resultado retornado pela Browser Use. Tente outra busca ou verifique os sites.")
        return

    print(f"\n[INFO] Itens retornados pela Browser Use (sem filtros locais): {len(df)}")

    # Aplica filtros locais
    df_filtered = filter_dataframe(df, max_price=max_price, brand_keywords=brand_keywords)

    # Se filtros ficaram muito restritivos, mostramos um fallback
    if df_filtered.empty:
        print("\n[AVISO] Nenhum item bateu com os filtros de preço/marca.")
        print("Mostrando todos os itens brutos retornados pela Browser Use:\n")
        df_to_show = df.sort_values(by="price_brl") if "price_brl" in df.columns else df
    else:
        df_to_show = df_filtered

    print("RESULTADOS ENCONTRADOS:\n")
    print(df_to_show.to_string(index=False))

    # Salva em CSV
    csv_path = "resultado_busca_pecas.csv"
    df_to_show.to_csv(csv_path, index=False)
    print(f"\n[OK] Resultado salvo em: {csv_path}")


if __name__ == "__main__":
    main()
