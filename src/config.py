from pathlib import Path
from dotenv import load_dotenv
import os

# Diretório raiz do projeto (onde está o .env)
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# Carrega variáveis do arquivo .env, se existir
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    print("[AVISO] Arquivo .env não encontrado na raiz do projeto.")

# Lê a chave da Browser Use Cloud
BROWSER_USE_API_KEY = os.getenv("BROWSER_USE_API_KEY")

if not BROWSER_USE_API_KEY:
    raise RuntimeError(
        "Variável BROWSER_USE_API_KEY não encontrada.\n"
        "Crie o arquivo .env na raiz do projeto com:\n"
        "BROWSER_USE_API_KEY=bu_sua_chave_aqui"
    )

# *** AQUI A MUDANÇA: apenas Kabum por enquanto ***
HARDWARE_SITES = [
    "https://www.kabum.com.br",
]
