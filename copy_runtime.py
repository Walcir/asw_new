import os
import shutil


def copy_tree_if_exists(src, dst):
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)


# Quando PyInstaller gera --onedir para Windows/Linux, normalmente cria dist/ASW
if os.path.isdir(os.path.join("dist", "ASW")):
    target = os.path.join("dist", "ASW")

    os.makedirs(os.path.join(target, "Docs"), exist_ok=True)

    if os.path.exists("config.ini"):
        shutil.copy2("config.ini", os.path.join(target, "config.ini"))

    copy_tree_if_exists("icons", os.path.join(target, "icons"))


# Quando PyInstaller gera --onedir --windowed no macOS, normalmente cria dist/ASW.app
if os.path.isdir(os.path.join("dist", "ASW.app")):
    os.makedirs(os.path.join("dist", "Docs"), exist_ok=True)

    if os.path.exists("config.ini"):
        shutil.copy2("config.ini", os.path.join("dist", "config.ini"))

    copy_tree_if_exists("icons", os.path.join("dist", "icons"))

print("Arquivos de runtime copiados para dist.")
