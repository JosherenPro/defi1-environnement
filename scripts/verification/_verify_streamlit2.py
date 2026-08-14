from playwright.sync_api import sync_playwright
import pathlib, time
URL="http://127.0.0.1:8502/"
shots=pathlib.Path("/home/eren/Documents/env_challenge_datalab/qa/screenshots/streamlit_folium")
shots.mkdir(exist_ok=True)
errors=[]
with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox"])
    pg=b.new_page(viewport={"width":1280,"height":1000})
    pg.on("console", lambda m: errors.append(f"{m.type}: {m.text}") if m.type=="error" else None)
    pg.on("pageerror", lambda e: errors.append(f"PAGEERROR: {e}"))
    pg.goto(URL, wait_until="networkidle", timeout=45000)
    pg.wait_for_timeout(4000)
    pg.wait_for_selector("text=Accès à l'Eau Potable au Togo", timeout=20000)
    pg.screenshot(path=str(shots/"overview.png"))
    # Cartographie tab
    pg.click("button:has-text('Cartographie')", timeout=8000); pg.wait_for_timeout(3500)
    pg.screenshot(path=str(shots/"carto_points.png"))
    # switch to FRI mode
    pg.click("text=Risque d'inondation (FRI cantons)", timeout=8000); pg.wait_for_timeout(3500)
    pg.screenshot(path=str(shots/"carto_fri.png"))
    b.close()
print("ERRORS:")
for e in errors[:30]: print("  ",e)
print("TOTAL:",len(errors))
