"""
Point d'entrée racine pour le déploiement Streamlit Cloud.
Redirige l'exécution vers dashboard/app.py tout en conservant les chemins d'accès relatifs.
"""
import os
import runpy
import sys

# Définir le chemin absolu vers dashboard
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.join(ROOT_DIR, "dashboard")
DASHBOARD_APP = os.path.join(DASHBOARD_DIR, "app.py")

if DASHBOARD_DIR not in sys.path:
    sys.path.insert(0, DASHBOARD_DIR)

if __name__ == "__main__" or "streamlit" in sys.modules:
    # Exécute dashboard/app.py dans son propre contexte
    runpy.run_path(DASHBOARD_APP, run_name="__main__")
