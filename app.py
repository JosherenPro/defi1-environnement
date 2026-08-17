"""Point d'entrée Streamlit Cloud vers l'application principale."""
import os
import runpy
import sys

# Définir le chemin absolu vers dashboard
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.join(ROOT_DIR, "dashboard")
DASHBOARD_APP = os.path.join(DASHBOARD_DIR, "app.py")

if DASHBOARD_DIR not in sys.path:
    sys.path.insert(0, DASHBOARD_DIR)

# Exécute toujours la même application que le lancement local.
runpy.run_path(DASHBOARD_APP, run_name="__main__")
