import cx_Freeze
import sys
import os

# 1. Configuração de Base (GUI vs Console)
base = None
if sys.platform == 'win32':
    base = "Win32GUI"

# 2. Tratamento seguro de arquivos e pastas inclusos
include_files = []
items_to_include = ["icons", "Docs", "imgs", "config.ini", "sqlite.db"]

for item in items_to_include:
    if os.path.exists(item):
        include_files.append(item)
    else:
        print(f"Aviso: '{item}' não foi encontrado na raiz e não será incluído.")

# 3. Configuração do Executável
executables = [cx_Freeze.Executable("main.py", base=base, target_name="ASW")]

# 4. Setup do cx_Freeze
try:
    cx_Freeze.setup(
        name="ASW",
        version="2608.19",
        description="Auto Simulate Whatsapp",
        options={
            "build_exe": {
                "packages": ["tkinter"], 
                "include_files": include_files,
                "build_exe": "build/ASW_Build" # Caminho relativo e limpo
            }
        },
        executables=executables
    )
    print("Build configurado com sucesso!")
except Exception as e:
    print(f'Erro ao configurar o build: {e}')