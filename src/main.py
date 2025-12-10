import pandas as pd

from .models import SearchResult
from .tasks import search_hardware


def result_to_dataframe(result: SearchResult) -> pd.DataFrame:
    """
    Converte SearchResult (Pydantic) em um DataFrame do pandas.
    """
    if not result.items:
        return pd.DataFrame(columns=["store", "name", "price_brl", "availability", "url"])

    data = [item.model_dump() for item in result.items]
    df = pd.DataFrame(data)
    return df


def main():
    print("=" * 60)
    print(" BUSCADOR DE PEÇAS (Browser Use + Python) ")
    print("=" * 60)

    query = input("Digite o nome da peça que você deseja buscar (ex: 'RTX 4060 8GB'): ").strip()

    if not query:
        print("Você não digitou nada. Encerrando.")
        return

    print("\n[INFO] Buscando peças, isso pode levar alguns segundos...\n")

    # Agora com streaming de passos
    result: SearchResult = search_hardware(query, show_steps=True)

    df = result_to_dataframe(result)

    if df.empty:
        print("Nenhum resultado encontrado. Tente outra busca ou verifique os sites.")
        return

    print("RESULTADOS ENCONTRADOS:\n")
    print(df.to_string(index=False))

    csv_path = "resultado_busca_pecas.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n[OK] Resultado salvo em: {csv_path}")


if __name__ == "__main__":
    main()
