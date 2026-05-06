# 🛠️ Juhend: malev2026 seadistamine terminalis

## OSA 1 — GitHub repo loomine ja GitHub Pages käivitamine

### Eeldused
- GitHub konto: https://github.com/signup (tasuta)
- Git paigaldatud: https://git-scm.com/downloads

---

### Samm 1: Loo uus repo GitHubis (veebis)

1. Mine: https://github.com/new
2. Repository name: `malev2026`
3. Vali: **Public**
4. Lisa linnuke: **Add a README file**
5. Kliki: **Create repository**

---

### Samm 2: Seadista Git oma arvutis (üks kord)

Ava terminal (Windows: PowerShell, Mac/Linux: Terminal):

```bash
git config --global user.name "Sinu Nimi"
git config --global user.email "sinu@email.ee"
```

---

### Samm 3: Kloni repo oma arvutisse

```bash
git clone https://github.com/[SINU-KASUTAJANIMI]/malev2026.git
cd malev2026
```

---

### Samm 4: Lisa failid kausta

Kopeeri järgmised failid `malev2026/` kausta:
- `index.html` (õppematerjal)
- `malev_kandideerimine.py` (Python skript)

---

### Samm 5: Lükka failid GitHubi

```bash
git add .
git commit -m "Lisa koolitusmaterjal ja kandideerimise skript"
git push origin main
```

---

### Samm 6: Lülita sisse GitHub Pages

1. Mine: https://github.com/[KASUTAJANIMI]/malev2026/settings/pages
2. Source: **Deploy from a branch**
3. Branch: **main** → **/ (root)**
4. Kliki **Save**
5. Oota ~2 minutit

✅ **Sinu leht on nüüd avalik:**
`https://[KASUTAJANIMI].github.io/malev2026/`

---

### Kuidas materjali uuendada tulevikus?

```bash
cd malev2026
# Muuda faile
git add .
git commit -m "Uuendus: [kirjelda mida muutsid]"
git push origin main
```
GitHub Pages uuendub automaatselt ~1-2 minutiga.

---

## OSA 2 — Claude Code paigaldamine ja Pythoni skripti käivitamine

### Eeldused
- Node.js paigaldatud: https://nodejs.org (vali LTS versioon)
- Python paigaldatud: https://python.org/downloads

---

### Samm 1: Paigalda Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

Kontrolli:
```bash
claude --version
```

---

### Samm 2: Käivita Claude Code malev2026 kaustas

```bash
cd malev2026
claude
```

Claude Code avaneb interaktiivse terminali sessioonina. Saad anda käske eesti keeles.

---

### Samm 3: Paigalda Playwright (üks kord)

Kas Claude Code terminalis või tavaterminalis:

```bash
pip install playwright
playwright install chromium
```

---

### Samm 4: Käivita kandideerimise skript

**NB! Käivita kell ~15:55 — skript ootab automaatselt kuni 16:00**

```bash
python malev_kandideerimine.py
```

Skript:
- Avab brauseri aknana (näed mis toimub)
- Ootab täpselt kell 16:00:00
- Täidab ankeedi automaatselt
- Küsib sinu kinnitust enne esitamist
- Teeb ekraanitõmmise kinnituseks (`kinnituskuva.png`)

---

### Ühe käsuga: repo + GitHub Pages + skript

```bash
# 1. Kloni repo
git clone https://github.com/[KASUTAJANIMI]/malev2026.git && cd malev2026

# 2. Paigalda sõltuvused
pip install playwright && playwright install chromium

# 3. Käivita Claude Code
claude

# 4. Käivita skript (Claude Code terminalis)
python malev_kandideerimine.py
```

---

## 🔒 Turvalisuse märkused

| Teema | Soovitus |
|-------|----------|
| Isikuandmed | Ära lae GitHubi faile, mis sisaldavad päris isikuandmeid |
| Skript | malev_kandideerimine.py sisaldab eeltäidetud andmeid — hoia privaatsena |
| Repo | Hoia repo Public ainult index.html jaoks; skripti võid hoida Private repos |
| GDPR | Veendu et index.html ei sisalda isikuandmeid enne avalikustamist |

---

*Koostatud Claude AI abil · malev2026 · 2026*
