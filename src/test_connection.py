# src/test_connection.py

import asyncio
from browser_use_sdk import AsyncBrowserUse
from .config import BROWSER_USE_API_KEY


async def main():
    client = AsyncBrowserUse(api_key=BROWSER_USE_API_KEY)

    # Task simples só para testar
    task = await client.tasks.create_task(
        task="Open https://news.ycombinator.com and return the title of the page.",
    )

    print("[INFO] Task criada. Acompanhando passos em tempo real...\n")

    # STREAMING: mostra cada passo que o agente dá no navegador
    async for step in task.stream():
        print(
            f"[PASSO {step.number}] "
            f"URL atual: {step.url or '-'} | Próximo objetivo: {step.next_goal}"
        )

    print("\n[INFO] Task finalizada. Buscando resultado final...\n")

    result = await task.complete()

    print("=== RESULTADO BRUTO ===")
    print(result.output)


if __name__ == "__main__":
    asyncio.run(main())
