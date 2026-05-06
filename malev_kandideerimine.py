"""
Tallinna Õpilasmalev — Automaatne kandideerimise skript
=======================================================
Käivita see skript umbes kell 15:55.
Skript ootab täpselt kell 16:00:00 ning esitab ankeedi automaatselt.

Paigaldamine (üks kord):
    pip install playwright python-dotenv
    playwright install chromium

Seadistamine:
    cp .env.example .env
    Ava .env ja täida oma andmetega

Käivitamine:
    python malev_kandideerimine.py
"""

import asyncio
import os
from datetime import datetime, time
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Lae isikuandmed .env failist (mitte koodist!)
load_dotenv()

# ─────────────────────────────────────────────
#  LOGIMINE
# ─────────────────────────────────────────────
LOG_FAIL = "tulemus.log"
_log_read = []

def log(sõnum: str, tase: str = "INFO"):
    """Kirjutab sõnumi nii terminali kui tulemus.log faili."""
    ajatempel = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rida = f"[{ajatempel}] [{tase}] {sõnum}"
    print(rida)
    _log_read.append(rida)
    with open(LOG_FAIL, "a", encoding="utf-8") as f:
        f.write(rida + "\n")

def kirjuta_kokkuvõte(olek: str, üksikasjad: list[str]):
    """Kirjutab struktureeritud kokkuvõtte logi lõppu."""
    piir = "=" * 55
    with open(LOG_FAIL, "a", encoding="utf-8") as f:
        f.write(f"\n{piir}\n")
        f.write(f"  KOKKUVÕTE — {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"  Olek: {olek}\n")
        f.write(f"{piir}\n")
        for rida in üksikasjad:
            f.write(f"  • {rida}\n")
        f.write(f"{piir}\n\n")

# ─────────────────────────────────────────────
#  KANDIDAADI ANDMED (.env failist)
# ─────────────────────────────────────────────
ANDMED = {
    "nimi":                 os.getenv("NIMI", "[NIMI puudub]"),
    "isikukood":            os.getenv("ISIKUKOOD", "[ISIKUKOOD puudub]"),
    "aadress":              os.getenv("AADRESS", "[AADRESS puudub]"),
    "telefon":              os.getenv("TELEFON", "[TELEFON puudub]"),
    "email":                os.getenv("EMAIL", "[EMAIL puudub]"),
    "lapsevanema_telefon":  os.getenv("LAPSEVANEMA_TELEFON", "[LP_TELEFON puudub]"),
    "lapsevanema_email":    os.getenv("LAPSEVANEMA_EMAIL", "[LP_EMAIL puudub]"),
    "kool":                 os.getenv("KOOL", "[KOOL puudub]"),
    "pangakonto":           os.getenv("PANGAKONTO", "[PANGAKONTO puudub]"),
    "pangakonto_omanik":    os.getenv("PANGAKONTO_OMANIK", "[OMANIK puudub]"),
    "sargi_suurus":         os.getenv("SARGI_SUURUS", "M"),
    "huvialad":             os.getenv("HUVIALAD", "[HUVIALAD puuduvad]"),
    "malevakogemus":        os.getenv("MALEVAKOGEMUS", "[KOGEMUS puudub]"),
    "motivatsioon":         os.getenv("MOTIVATSIOON", "[MOTIVATSIOON puudub]"),
    "ryhm_1":               os.getenv("RYHM_1", "[RÜHM 1 puudub]"),
    "ryhm_2":               os.getenv("RYHM_2", "[RÜHM 2 puudub]"),
}

# ─────────────────────────────────────────────
#  AJASTUS
# ─────────────────────────────────────────────
KANDIDEERIMISE_ALGUS = time(16, 0, 0)   # 16:00:00
MALEV_URL = "https://malev.ee/"


# ─────────────────────────────────────────────
#  ABI­FUNKTSIOONID
# ─────────────────────────────────────────────
async def oota_kuni_16(page):
    """Uuendab malev.ee iga 5 sekundi tagant kuni kandideerimislink ilmub."""
    log("⏳  Ootan kandideerimislingi ilmumist...")
    while True:
        now = datetime.now().time()
        if now >= KANDIDEERIMISE_ALGUS:
            await page.goto(MALEV_URL, wait_until="domcontentloaded")
            # Otsi kandideerimisnuppu / linki
            link = await leia_kandideerimislink(page)
            if link:
                log(f"✅  Kandideerimislink leitud: {link}")
                return link
            else:
                log(f"🔄  {datetime.now().strftime('%H:%M:%S')} — linki pole veel, proovin uuesti...")
                await asyncio.sleep(3)
        else:
            jarg = datetime.now().replace(
                hour=16, minute=0, second=0, microsecond=0
            )
            delta = (jarg - datetime.now()).total_seconds()
            if delta > 60:
                log(f"⏰  {datetime.now().strftime('%H:%M:%S')} — kandideerimine algab {delta/60:.1f} minuti pärast")
                await asyncio.sleep(30)
            elif delta > 5:
                log(f"⏰  {datetime.now().strftime('%H:%M:%S')} — {delta:.0f} sekundit jäänud...")
                await asyncio.sleep(2)
            else:
                await asyncio.sleep(0.5)


async def leia_kandideerimislink(page):
    """Otsib lehelt kandideerimislinki mitme strateegiaga."""
    # 1) Otsi teksti järgi
    for tekst in ["Kandideeri", "kandideeri", "Kandideerimise link", "Täida ankeet"]:
        try:
            el = page.get_by_text(tekst, exact=False).first
            href = await el.get_attribute("href")
            if href:
                return href
        except Exception:
            pass

    # 2) Otsi linke mis sisaldavad kandideerimisele viitavaid sõnu
    links = await page.query_selector_all("a[href]")
    for link in links:
        href = await link.get_attribute("href")
        if href and any(k in href.lower() for k in [
            "kandideeri", "forms.gle", "typeform", "ankeet", "apply", "register"
        ]):
            return href

    return None


async def taida_google_form(page):
    """Täidab Google Formsi ankeedi."""
    log("📝  Täidan Google Forms ankeeti...")

    async def taida_valja(label_tekst, vastus):
        try:
            # Leia label ja sealt input
            label = page.get_by_text(label_tekst, exact=False).first
            input_el = page.locator("input[type='text'], textarea").nth(0)
            # Proovi leida input sama grupist
            await input_el.fill(vastus)
            print(f"   ✓ {label_tekst}")
        except Exception as e:
            log(f"   ⚠️  {label_tekst}: {e}", "WARN")

    # Oota et leht laeb
    await page.wait_for_load_state("networkidle")
    await asyncio.sleep(1)

    # Täida kõik tekstiväljad järjest
    inputs = await page.query_selector_all("input[type='text'], textarea")
    vastused = [
        ANDMED["nimi"],
        ANDMED["isikukood"],
        ANDMED["aadress"],
        ANDMED["telefon"],
        ANDMED["email"],
        ANDMED["lapsevanema_telefon"],
        ANDMED["lapsevanema_email"],
        ANDMED["kool"],
        ANDMED["pangakonto"],
        ANDMED["pangakonto_omanik"],
        ANDMED["sargi_suurus"],
        ANDMED["huvialad"],
        ANDMED["malevakogemus"],
        ANDMED["motivatsioon"],
    ]

    for i, (inp, vastus) in enumerate(zip(inputs, vastused)):
        await inp.click()
        await inp.fill(vastus)
        log(f"   ✓ Väli {i+1} täidetud")
        await asyncio.sleep(0.2)

    # Rühma valik (dropdown või raadionupp)
    try:
        dropdowns = await page.query_selector_all("select, [role='listbox']")
        if dropdowns:
            await dropdowns[0].select_option(label=ANDMED["ryhm_1"])
            log(f"   ✓ Rühm 1: {ANDMED['ryhm_1']}")
        # Proovi ka teksti järgi klikkida
        else:
            await page.get_by_text(ANDMED["ryhm_1"], exact=False).first.click()
    except Exception as e:
        log(f"   ⚠️  Rühma valimine: {e}", "WARN")

    log("✅  Ankeet täidetud! Vaatan üle enne esitamist...")


async def taida_kohandatud_vorm(page):
    """Täidab kohandatud PHP/WP vormi."""
    log("📝  Täidan kohandatud vormi...")
    await page.wait_for_load_state("networkidle")

    # Kaardista väljad nime või placeholder järgi
    valja_kaart = {
        "nimi":                ["nimi", "name", "eesnimi"],
        "isikukood":           ["isikukood", "id", "personal"],
        "aadress":             ["aadress", "address"],
        "telefon":             ["telefon", "phone", "tel"],
        "email":               ["email", "e-mail", "meil"],
        "lapsevanema_telefon": ["lapsevanema", "parent", "vanem"],
        "lapsevanema_email":   ["lapsevanema_email", "parent_email"],
        "kool":                ["kool", "school"],
        "pangakonto":          ["pangakonto", "iban", "konto"],
        "pangakonto_omanik":   ["omanik", "owner"],
        "sargi_suurus":        ["sark", "shirt", "suurus", "size"],
        "huvialad":            ["huvialad", "hobby", "huvi"],
        "malevakogemus":       ["kogemus", "experience"],
        "motivatsioon":        ["motivat", "põhjend", "reason"],
    }

    for andme_key, otsisõnad in valja_kaart.items():
        for sona in otsisõnad:
            try:
                sel = f"input[name*='{sona}' i], textarea[name*='{sona}' i], input[placeholder*='{sona}' i]"
                el = page.locator(sel).first
                if await el.count() > 0:
                    await el.fill(ANDMED[andme_key])
                    log(f"   ✓ {andme_key}")
                    break
            except Exception:
                continue


async def esita_ankeet(page):
    """Leiab ja klikib esitamise nupu."""
    log("🚀  Esitan ankeedi...")
    for tekst in ["Esita", "Submit", "Saada", "Kandideeri", "Kinnita"]:
        try:
            nupp = page.get_by_role("button", name=tekst, exact=False).first
            if await nupp.count() > 0:
                await nupp.click()
                log(f"✅  Ankeet esitatud! ({tekst})")
                await asyncio.sleep(3)
                # Tee ekraanitõmmis kinnituseks
                await page.screenshot(path="kinnituskuva.png")
                log("📸  Ekraanitõmmis salvestatud: kinnituskuva.png")
                return True
        except Exception:
            continue
    log("⚠️  Esitamisnuppu ei leitud — kontrolli brauser akent käsitsi!", "WARN")
    return False


# ─────────────────────────────────────────────
#  PEAMINE
# ─────────────────────────────────────────────
async def main():
    # Alusta uut logi sessiooni
    with open(LOG_FAIL, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*55}\n  SESSIOON ALGAB — {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n{'='*55}\n")

    log("=" * 55)
    log("  Tallinna Õpilasmalev — Automaatne kandideerimine")
    log("=" * 55)
    log(f"  Kandidaat : {ANDMED['nimi']}")
    log(f"  Rühm 1    : {ANDMED['ryhm_1']}")
    log(f"  Rühm 2    : {ANDMED['ryhm_2']}")
    log(f"  Algusaeg  : {KANDIDEERIMISE_ALGUS.strftime('%H:%M:%S')}")
    log("=" * 55)

    esitatud = False
    kandideerimis_url = None
    vormi_tüüp = "teadmata"

    async with async_playwright() as p:
        # headless=True — serveris pole X-serverit
        browser = await p.chromium.launch(headless=True, slow_mo=50)
        context = await browser.new_context()
        page = await context.new_page()

        # Ava malev.ee juba ette
        await page.goto(MALEV_URL, wait_until="domcontentloaded")
        log(f"\n🌐  malev.ee avatud. Ootan kuni 16:00...\n")

        # Oota kandideerimislinki
        kandideerimis_url = await oota_kuni_16(page)

        if not kandideerimis_url:
            log("❌  Linki ei leitud. Kontrolli käsitsi!", "ERROR")
            kirjuta_kokkuvõte("EBAÕNNESTUS", [
                "Kandideerimislinki ei leitud malev.ee lehelt",
                "Kontrolli käsitsi brauserist",
            ])
            input("Vajuta Enter sulgemiseks...")
            return

        # Ava kandideerimisvorm
        log(f"\n➡️   Avan vormi: {kandideerimis_url}")
        await page.goto(kandideerimis_url, wait_until="domcontentloaded")
        await asyncio.sleep(1)

        # Tuvasta vormi tüüp
        url = page.url
        if "forms.gle" in url or "docs.google.com/forms" in url:
            vormi_tüüp = "Google Forms"
            await taida_google_form(page)
        else:
            vormi_tüüp = "Kohandatud vorm"
            await taida_kohandatud_vorm(page)

        # Küsi kasutajalt kinnitust enne esitamist
        log("\n" + "=" * 55)
        log("⚠️   PALUN KONTROLLI BRAUSER AKNAS KÕIK VÄLJAD ÜLE!")
        log("=" * 55)
        kinnitus = input("\nKas esitan ankeedi? (jah/ei): ").strip().lower()

        if kinnitus in ["jah", "j", "yes", "y"]:
            esitatud = await esita_ankeet(page)
        else:
            log("❌  Esitamine tühistatud kasutaja poolt.", "WARN")

        # ── Kokkuvõte ──────────────────────────────────
        if esitatud:
            kirjuta_kokkuvõte("EDUKAS", [
                f"Kandidaat: {ANDMED['nimi']}",
                f"Rühm 1: {ANDMED['ryhm_1']}",
                f"Rühm 2: {ANDMED['ryhm_2']}",
                f"Vorm: {vormi_tüüp}",
                f"URL: {kandideerimis_url}",
                "Ekraanitõmmis: kinnituskuva.png",
            ])
            log(f"\n📄  Täielik logi salvestatud: {LOG_FAIL}")
        elif kinnitus not in ["jah", "j", "yes", "y"]:
            kirjuta_kokkuvõte("TÜHISTATUD", [
                "Kasutaja loobus esitamisest",
                f"Vorm täidetud: {vormi_tüüp}",
                f"URL: {kandideerimis_url or 'ei leitud'}",
            ])
        else:
            kirjuta_kokkuvõte("EBAÕNNESTUS", [
                "Esitamisnuppu ei leitud",
                f"Vorm: {vormi_tüüp}",
                f"URL: {kandideerimis_url}",
                "Kontrolli käsitsi kinnituskuva.png",
            ])

        input("\nVajuta Enter brauseri sulgemiseks...")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
