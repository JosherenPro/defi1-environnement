from playwright.sync_api import sync_playwright
import pathlib
URL="http://127.0.0.1:8502/"
shots=pathlib.Path("/home/eren/Documents/env_challenge_datalab/qa/screenshots/streamlit")
shots.mkdir(exist_ok=True)
errors=[]
with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox"])
    pg=b.new_page(viewport={"width":1280,"height":1000})
    pg.on("console", lambda m: errors.append(f"{m.type}: {m.text}") if m.type in ("error","warning") else None)
    pg.on("pageerror", lambda e: errors.append(f"PAGEERROR: {e}"))
    pg.goto(URL, wait_until="networkidle", timeout=45000)
    pg.wait_for_timeout(4000)
    # wait for streamlit to finish booting (look for the banniere text)
    pg.wait_for_selector("text=Accès à l'Eau Potable au Togo", timeout=20000)
    pg.screenshot(path=str(shots/"overview.png"), full_page=False)
    # click each tab by text using locator
    for label in ["Vue d'ensemble", "Cartographie", "État & Maintenance", "Pression démographique", "Risque d'inondation", "Consommation", "Recommandations"]:
        try:
            pg.get_by_role("tab", name=label).click(timeout=8000)
            pg.wait_for_timeout(2500)
            safe_name = label.replace("'", "_").replace(" ", "_")
            pg.screenshot(path=str(shots/f"{safe_name}.png"))
        except Exception as e:
            errors.append(f"TAB FAIL {label}: {e}")
    b.close()
print("ERRORS:")
for e in errors[:40]: print("  ",e)
print("TOTAL:",len(errors))
