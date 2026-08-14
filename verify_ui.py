"""
Script Playwright de vérification visuelle du dashboard Streamlit avec la bannière Togo AI Lab et logo DataLab.
"""
import os, time, subprocess
from playwright.sync_api import sync_playwright

PORT = 8504
URL = f"http://localhost:{PORT}"

print("==> Démarrage du serveur Streamlit...")
proc = subprocess.Popen(
    ["streamlit", "run", "dashboard/app.py", "--server.port", str(PORT), "--server.headless", "true"],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
)

time.sleep(4)

SHOTS_DIR = "/tmp/datalab_banner_shots"
os.makedirs(SHOTS_DIR, exist_ok=True)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 950})
        print(f"==> Navigation vers {URL}...")
        page.goto(URL, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2500)

        # 1. Capture Vue d'ensemble (Hero banner, Logo Datalab, Metrics, Charts)
        shot1 = f"{SHOTS_DIR}/01_vue_ensemble.png"
        page.screenshot(path=shot1, full_page=False)
        print("Capture 1 enregistrée :", shot1)

        # 2. Onglet Cartographie
        page.get_by_role("tab", name="Cartographie SIG").click()
        page.wait_for_timeout(2000)
        shot2 = f"{SHOTS_DIR}/02_cartographie.png"
        page.screenshot(path=shot2, full_page=False)
        print("Capture 2 enregistrée :", shot2)

        # 3. Onglet État & Maintenance
        page.get_by_role("tab", name="État & Maintenance").click()
        page.wait_for_timeout(1500)
        shot3 = f"{SHOTS_DIR}/03_maintenance.png"
        page.screenshot(path=shot3, full_page=False)
        print("Capture 3 enregistrée :", shot3)

        # 4. Onglet Risque d'inondation
        page.get_by_role("tab", name="Risque d'inondation").click()
        page.wait_for_timeout(1500)
        shot4 = f"{SHOTS_DIR}/04_inondation_fri.png"
        page.screenshot(path=shot4, full_page=False)
        print("Capture 4 enregistrée :", shot4)

        # 5. Onglet Recommandations
        page.get_by_role("tab", name="Recommandations").click()
        page.wait_for_timeout(1500)
        shot5 = f"{SHOTS_DIR}/05_recommandations.png"
        page.screenshot(path=shot5, full_page=False)
        print("Capture 5 enregistrée :", shot5)

        browser.close()
        print("Vérification Playwright terminée avec succès !")

finally:
    proc.terminate()
    proc.wait()
