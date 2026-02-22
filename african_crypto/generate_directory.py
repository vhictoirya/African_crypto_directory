import pandas as pd
import json

# Pull from Google Sheet
sheet_id = "1-Sj9cqZa_E7DLnsCuDDljgJnzpcvJ3XmYeDcVD4XZFM"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

df = pd.read_csv(url)

# Remove blank rows and section header rows
df = df[df["Name"].notna()]
df = df[~df["Name"].str.contains("Projects|African founders|Global/international", na=False)]
df = df[df["Name"].str.strip() != ""]

# Map columns to frontend fields
projects = []
for _, row in df.iterrows():
    name = str(row.get("Name", "")).strip()
    if not name or name == "nan":
        continue

    cats = str(row.get("Category ", "")).strip()
    cat_list = [c.strip() for c in cats.split(",") if c.strip() and c.strip() != "nan"]

    def clean(val):
        v = str(row.get(val, "")).strip()
        return "" if v in ["nan", "N/A", "n/a"] else v

    projects.append({
        "name":        name,
        "website":     clean("Website URL"),
        "categories":  cat_list,
        "shortDesc":   clean("Short description "),
        "longDesc":    clean("Long description "),
        "funding":     clean("Funding"),
        "latestRound": clean("Latest round"),
        "employees":   clean("Employees"),
        "hq":          clean("HQ"),
        "ceo":         clean("CEO Name"),
        "ceoTwitter":  clean("CEO X URL"),         
        "ceoLinkedin": clean("CEO LinkedIn URL"),   
        "linkedin":    clean("LinkedIn URL"),
        "twitter":     clean("XURL"),
        "investors":   clean("Investors / Partners"),
        "section":     clean("Section"),
    })

print(f"✅ Loaded {len(projects)} companies")
for s in ["Core African Projects", "African-Focused Projects", "Africa-Serving Projects"]:
    cnt = sum(1 for p in projects if p["section"] == s)
    print(f"   {s}: {cnt}")

# ── 4. Build the full HTML ──
json_data = json.dumps(projects, indent=2)

html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Africa Crypto Directory</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0a0a0f; --bg2: #0f0f1a; --surface: #13131f; --surface2: #1a1a2e; --surface3: #1f1f35;
    --accent: #f97316; --accent2: #fb923c; --accent-dim: rgba(249,115,22,0.12); --accent-border: rgba(249,115,22,0.25);
    --text: #f1f0ee; --text2: #a8a3b0; --muted: #5a5468;
    --border: rgba(255,255,255,0.06); --border2: rgba(255,255,255,0.1); --white: #ffffff; --radius: 12px;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; font-size: 15px; line-height: 1.6; overflow-x: hidden; }
  .orb { position: fixed; border-radius: 50%; filter: blur(120px); pointer-events: none; z-index: 0; }
  .orb-1 { width: 600px; height: 600px; background: rgba(249,115,22,0.07); top: -200px; left: -200px; }
  .orb-2 { width: 500px; height: 500px; background: rgba(99,102,241,0.06); bottom: -100px; right: -100px; }
  .topbar { position: fixed; top: 0; left: 0; right: 0; z-index: 200; background: rgba(10,10,15,0.88); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border); padding: 0 40px; height: 64px; display: flex; align-items: center; justify-content: space-between; gap: 24px; }
  .logo { display: flex; align-items: center; gap: 10px; text-decoration: none; flex-shrink: 0; }
  .logo-mark { width: 34px; height: 34px; background: var(--accent); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-family: 'Outfit', sans-serif; font-weight: 900; font-size: 16px; color: #000; }
  .logo-text { font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 16px; color: var(--white); }
  .logo-text span { color: var(--accent); }
  .topbar-search { position: relative; flex: 1; max-width: 420px; }
  .topbar-search svg { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--muted); pointer-events: none; }
  .topbar-search input { width: 100%; height: 40px; background: var(--surface); border: 1px solid var(--border2); border-radius: 8px; padding: 0 16px 0 42px; color: var(--text); font-family: 'Inter', sans-serif; font-size: 13.5px; outline: none; transition: border-color 0.2s, box-shadow 0.2s; }
  .topbar-search input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(249,115,22,0.1); }
  .topbar-search input::placeholder { color: var(--muted); }
  .count-badge { padding: 5px 12px; background: var(--accent-dim); border: 1px solid var(--accent-border); border-radius: 100px; font-size: 12px; font-weight: 600; color: var(--accent); white-space: nowrap; }
  .layout { display: flex; padding-top: 64px; min-height: 100vh; position: relative; z-index: 1; }
  .sidebar { width: 240px; flex-shrink: 0; position: sticky; top: 64px; height: calc(100vh - 64px); overflow-y: auto; padding: 28px 0; border-right: 1px solid var(--border); background: rgba(13,13,26,0.4); }
  .sidebar::-webkit-scrollbar { width: 4px; }
  .sidebar::-webkit-scrollbar-thumb { background: var(--surface3); border-radius: 2px; }
  .sidebar-section { padding: 0 16px; margin-bottom: 28px; }
  .sidebar-label { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.14em; color: var(--muted); padding: 0 8px; margin-bottom: 8px; }
  .sidebar-item { display: flex; align-items: center; padding: 8px 10px; border-radius: 8px; cursor: pointer; font-size: 13.5px; color: var(--text2); font-weight: 400; transition: all 0.15s; border: 1px solid transparent; gap: 8px; width: 100%; background: none; text-align: left; }
  .sidebar-item:hover { background: var(--surface); color: var(--text); }
  .sidebar-item.active { background: var(--accent-dim); border-color: var(--accent-border); color: var(--accent); font-weight: 500; }
  .sidebar-item-icon { width: 20px; text-align: center; flex-shrink: 0; font-size: 13px; }
  .sidebar-item-count { font-size: 11px; font-weight: 600; padding: 2px 7px; border-radius: 100px; background: var(--surface3); color: var(--muted); margin-left: auto; }
  .sidebar-item.active .sidebar-item-count { background: var(--accent-border); color: var(--accent); }
  .sidebar-divider { height: 1px; background: var(--border); margin: 8px 16px 20px; }
  .content { flex: 1; min-width: 0; padding: 32px 36px; }
  .hero { background: linear-gradient(135deg, var(--surface2) 0%, var(--surface) 100%); border: 1px solid var(--border2); border-radius: 16px; padding: 32px 36px; margin-bottom: 32px; position: relative; overflow: hidden; }
  .hero::before { content: ''; position: absolute; top: -40px; right: -40px; width: 200px; height: 200px; background: radial-gradient(circle, rgba(249,115,22,0.15), transparent 70%); border-radius: 50%; }
  .hero-tag { display: inline-flex; align-items: center; gap: 6px; padding: 5px 12px; background: var(--accent-dim); border: 1px solid var(--accent-border); border-radius: 100px; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: var(--accent); margin-bottom: 14px; }
  .hero-tag::before { content: ''; width: 6px; height: 6px; background: var(--accent); border-radius: 50%; animation: pulse 2s infinite; }
  @keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.4; } }
  .hero h1 { font-family: 'Outfit', sans-serif; font-size: clamp(28px, 3.5vw, 44px); font-weight: 800; line-height: 1.1; letter-spacing: -0.03em; color: var(--white); margin-bottom: 10px; }
  .hero h1 em { font-style: normal; color: var(--accent); }
  .hero p { font-size: 14px; color: var(--text2); max-width: 520px; margin-bottom: 24px; line-height: 1.6; }
  .hero-stats { display: flex; gap: 28px; flex-wrap: wrap; align-items: center; }
  .hero-stat { display: flex; flex-direction: column; gap: 2px; }
  .hero-stat-num { font-family: 'Outfit', sans-serif; font-size: 24px; font-weight: 800; color: var(--accent); line-height: 1; }
  .hero-stat-label { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em; }
  .hero-stat-sep { width: 1px; height: 36px; background: var(--border2); }
  .section-header { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 18px; margin-top: 36px; }
  .section-header:first-of-type { margin-top: 0; }
  .section-dot { width: 8px; height: 8px; background: var(--accent); border-radius: 50%; box-shadow: 0 0 12px rgba(249,115,22,0.6); flex-shrink: 0; margin-top: 4px; }
  .section-title-group { display: flex; flex-direction: column; gap: 3px; flex: 1; }
  .section-title { font-family: 'Outfit', sans-serif; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em; color: var(--text2); }
  .section-subtitle { font-size: 11.5px; color: var(--muted); font-weight: 400; line-height: 1.4; }
  .section-line { width: 40px; height: 1px; background: var(--border); margin-top: 8px; flex-shrink: 0; }
  .section-cnt { font-size: 12px; font-weight: 600; color: var(--muted); padding: 3px 10px; background: var(--surface); border: 1px solid var(--border); border-radius: 100px; white-space: nowrap; margin-top: 2px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(310px, 1fr)); gap: 12px; margin-bottom: 12px; }
  .card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 22px; cursor: pointer; transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s; position: relative; overflow: hidden; display: flex; flex-direction: column; }
  .card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, var(--accent), transparent); opacity: 0; transition: opacity 0.2s; }
  .card:hover { border-color: rgba(249,115,22,0.3); transform: translateY(-2px); box-shadow: 0 8px 32px rgba(0,0,0,0.4); }
  .card:hover::before { opacity: 1; }
  .card:hover .card-links { opacity: 1; }
  .card-top { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 14px; gap: 10px; }
  .card-avatar { width: 42px; height: 42px; border-radius: 10px; background: linear-gradient(135deg, var(--surface3), var(--surface2)); border: 1px solid var(--border2); display: flex; align-items: center; justify-content: center; font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 15px; color: var(--accent); flex-shrink: 0; }
  .card-links { display: flex; gap: 6px; opacity: 0; transition: opacity 0.2s; }
  .card-link { width: 28px; height: 28px; border-radius: 6px; background: var(--surface2); border: 1px solid var(--border2); display: flex; align-items: center; justify-content: center; color: var(--muted); text-decoration: none; font-size: 11px; font-weight: 700; transition: all 0.15s; }
  .card-link:hover { background: var(--accent-dim); border-color: var(--accent-border); color: var(--accent); }
  .card-name { font-family: 'Outfit', sans-serif; font-size: 17px; font-weight: 700; color: var(--white); letter-spacing: -0.01em; margin-bottom: 3px; line-height: 1.2; }
  .card-hq { font-size: 12px; color: var(--muted); margin-bottom: 10px; }
  .card-desc { font-size: 13px; color: var(--text2); line-height: 1.55; margin-bottom: 14px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; flex: 1; }
  .card-tags { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 14px; }
  .tag { padding: 2px 9px; border-radius: 100px; font-size: 11px; font-weight: 500; border: 1px solid; }
  .tag-exchange       { background: rgba(249,115,22,0.1);  border-color: rgba(249,115,22,0.3);  color: #fb923c; }
  .tag-payments       { background: rgba(251,191,36,0.08); border-color: rgba(251,191,36,0.25); color: #fbbf24; }
  .tag-infrastructure { background: rgba(99,102,241,0.1);  border-color: rgba(99,102,241,0.3);  color: #818cf8; }
  .tag-defi           { background: rgba(52,211,153,0.08); border-color: rgba(52,211,153,0.25); color: #34d399; }
  .tag-ramp           { background: rgba(232,121,249,0.08);border-color: rgba(232,121,249,0.25);color: #e879f9; }
  .tag-blockchain     { background: rgba(56,189,248,0.08); border-color: rgba(56,189,248,0.25); color: #38bdf8; }
  .tag-stablecoin     { background: rgba(249,115,22,0.08); border-color: rgba(249,115,22,0.2);  color: #fdba74; }
  .tag-remittance     { background: rgba(74,222,128,0.08); border-color: rgba(74,222,128,0.2);  color: #4ade80; }
  .tag-wallet         { background: rgba(148,163,184,0.08);border-color: rgba(148,163,184,0.2); color: #94a3b8; }
  .tag-baas           { background: rgba(168,85,247,0.08); border-color: rgba(168,85,247,0.25); color: #c084fc; }
  .tag-savings        { background: rgba(251,146,60,0.08); border-color: rgba(251,146,60,0.2);  color: #fb923c; }
  .tag-default        { background: rgba(90,84,104,0.15);  border-color: rgba(90,84,104,0.35);  color: var(--muted); }
  .card-bottom { display: flex; justify-content: space-between; align-items: center; padding-top: 12px; border-top: 1px solid var(--border); margin-top: auto; }
  .card-funding { font-family: 'Outfit', sans-serif; font-size: 14px; font-weight: 700; color: var(--accent); }
  .card-employees { font-size: 11px; color: var(--muted); }
  .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.75); backdrop-filter: blur(12px); z-index: 1000; display: none; align-items: center; justify-content: center; padding: 20px; }
  .modal-overlay.open { display: flex; }
  .modal { background: var(--surface); border: 1px solid var(--border2); border-radius: 18px; max-width: 640px; width: 100%; max-height: 88vh; overflow-y: auto; position: relative; animation: fadeUp 0.22s cubic-bezier(0.16,1,0.3,1); box-shadow: 0 24px 80px rgba(0,0,0,0.6); }
  @keyframes fadeUp { from { opacity:0; transform:translateY(24px) scale(0.96); } to { opacity:1; transform:translateY(0) scale(1); } }
  .modal::-webkit-scrollbar { width: 4px; }
  .modal::-webkit-scrollbar-thumb { background: var(--surface3); border-radius: 2px; }
  .modal-close { position: absolute; top: 18px; right: 18px; width: 30px; height: 30px; border-radius: 8px; background: var(--surface2); border: 1px solid var(--border2); color: var(--muted); cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 16px; transition: all 0.15s; z-index: 10; }
  .modal-close:hover { color: var(--text); background: var(--surface3); }
  .modal-hero { padding: 28px 28px 22px; border-bottom: 1px solid var(--border); background: linear-gradient(160deg, var(--surface2), var(--surface)); border-radius: 18px 18px 0 0; position: relative; overflow: hidden; }
  .modal-hero::before { content: ''; position: absolute; top: -60px; right: -60px; width: 200px; height: 200px; background: radial-gradient(circle, rgba(249,115,22,0.12), transparent 70%); }
  .modal-header-row { display: flex; align-items: center; gap: 14px; margin-bottom: 14px; }
  .modal-avatar { width: 54px; height: 54px; border-radius: 13px; background: var(--surface3); border: 1px solid var(--border2); display: flex; align-items: center; justify-content: center; font-family: 'Outfit', sans-serif; font-weight: 900; font-size: 20px; color: var(--accent); flex-shrink: 0; }
  .modal-name { font-family: 'Outfit', sans-serif; font-size: 24px; font-weight: 800; color: var(--white); letter-spacing: -0.02em; line-height: 1.15; }
  .modal-hq { font-size: 13px; color: var(--muted); margin-top: 2px; }
  .modal-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 14px; }
  .modal-desc { font-size: 14px; color: var(--text2); line-height: 1.65; }
  .modal-body { padding: 24px 28px; }
  .modal-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 22px; }
  .modal-field { background: var(--bg2); border: 1px solid var(--border); border-radius: 10px; padding: 12px 14px; }
  .modal-field label { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.13em; color: var(--muted); display: block; margin-bottom: 4px; }
  .modal-field p { font-size: 14px; color: var(--text); font-weight: 500; }
  .modal-field p.hi { color: var(--accent); font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 15px; }
  .modal-field a { color: var(--accent); text-decoration: none; }
  .modal-field a:hover { text-decoration: underline; }
  .modal-sub { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em; color: var(--muted); margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }
  .modal-investors { font-size: 13.5px; color: var(--text2); line-height: 1.65; margin-bottom: 22px; background: var(--bg2); border: 1px solid var(--border); border-radius: 10px; padding: 14px; }
  .modal-actions { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
  .modal-divider { width: 1px; background: var(--border2); align-self: stretch; margin: 0 4px; min-height: 32px; }
  .btn { padding: 9px 16px; border-radius: 8px; font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; transition: all 0.15s; cursor: pointer; border: none; white-space: nowrap; }
  .btn-primary { background: var(--accent); color: #000; }
  .btn-primary:hover { background: var(--accent2); box-shadow: 0 4px 16px rgba(249,115,22,0.35); }
  .btn-secondary { background: var(--surface2); border: 1px solid var(--border2); color: var(--text2); }
  .btn-secondary:hover { border-color: rgba(249,115,22,0.4); color: var(--accent); background: var(--accent-dim); }
  .empty { text-align: center; padding: 80px 20px; color: var(--muted); }
  .empty .e-icon { font-size: 48px; margin-bottom: 16px; }
  .empty h3 { font-family: 'Outfit', sans-serif; font-size: 20px; color: var(--text2); margin-bottom: 8px; font-weight: 700; }
  ::-webkit-scrollbar { width: 5px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: var(--surface3); border-radius: 3px; }
  @media (max-width: 900px) { .sidebar { display: none; } .topbar { padding: 0 20px; } .content { padding: 20px; } .hero { padding: 24px 20px; } .grid { grid-template-columns: 1fr; } }
@media (max-width: 600px) { .modal-grid { grid-template-columns: 1fr; } .modal-hero, .modal-body { padding: 20px; } }

  html.light {
    --bg: #f8f8f5;
    --bg2: #f0f0ec;
    --surface: #ffffff;
    --surface2: #f5f5f0;
    --surface3: #ebebE6;
    --text: #1a1a2e;
    --text2: #4a4a6a;
    --muted: #8a8aaa;
    --border: rgba(0,0,0,0.08);
    --border2: rgba(0,0,0,0.12);
    --white: #1a1a2e;
  }
</style>
</head>
<body>
<div class="orb orb-1"></div>
<div class="orb orb-2"></div>
<nav class="topbar">
  <a href="#" class="logo">
    <div class="logo-mark">I</div>
    <span class="logo-text">Intelli<span>Sages</span></span>
  </a>
  <div class="topbar-search">
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
    <input type="text" id="search" placeholder="Search companies, locations, categories…" oninput="applyFilters()">
  </div>
  <div style="display:flex;align-items:center;gap:12px;flex-shrink:0;">
    <span class="count-badge" id="count-badge">Loading…</span>
    <button onclick="toggleTheme()" id="theme-btn" style="background:var(--surface);border:1px solid var(--border2);color:var(--text2);border-radius:8px;padding:6px 12px;cursor:pointer;font-size:13px;">🌙 Dark</button>
  </div>
</nav>
<div class="layout">
  <aside class="sidebar">
    <div class="sidebar-section">
      <div class="sidebar-label">Category</div>
      <button class="sidebar-item active" data-cat="all" onclick="filterCat(this)">
        <span class="sidebar-item-icon">⊞</span><span style="flex:1">All Categories</span>
        <span class="sidebar-item-count" id="cnt-all">—</span>
      </button>
    </div>
    <div class="sidebar-divider"></div>
    <div class="sidebar-section">
      <div class="sidebar-label">Tier</div>
      <button class="sidebar-item active" data-section="all" onclick="filterSection(this)">
        <span class="sidebar-item-icon">🌍</span><span style="flex:1">All Tiers</span>
      </button>
      <button class="sidebar-item" data-section="Core African Projects" onclick="filterSection(this)">
        <span class="sidebar-item-icon">⭐</span><span style="flex:1">Core African</span>
      </button>
      <button class="sidebar-item" data-section="African-Focused Projects" onclick="filterSection(this)">
        <span class="sidebar-item-icon">🎯</span><span style="flex:1">Africa-Focused</span>
      </button>
      <button class="sidebar-item" data-section="Africa-Serving Projects" onclick="filterSection(this)">
        <span class="sidebar-item-icon">🌐</span><span style="flex:1">Africa-Serving</span>
      </button>
    </div>
    <div class="sidebar-divider"></div>
    <div class="sidebar-section" id="cat-sidebar">
      <div class="sidebar-label">Browse by Type</div>
    </div>
  </aside>
  <main class="content">
    <div class="hero">
      <div class="hero-tag">Live Directory</div>
      <h1>The <em>African</em> Crypto<br>Ecosystem Map</h1>
      <p>Discover exchanges, payment infrastructure, DeFi protocols, and on/off-ramp providers shaping the future of African crypto and finance.</p>
      <div class="hero-stats">
        <div class="hero-stat"><span class="hero-stat-num" id="vis-count">—</span><span class="hero-stat-label">Companies</span></div>
        <div class="hero-stat-sep"></div>
        <div class="hero-stat"><span class="hero-stat-num">3</span><span class="hero-stat-label">Tiers</span></div>
        <div class="hero-stat-sep"></div>
        <div class="hero-stat"><span class="hero-stat-num">15+</span><span class="hero-stat-label">Countries</span></div>
        <div class="hero-stat-sep"></div>
        <div class="hero-stat"><span class="hero-stat-num">$2B+</span><span class="hero-stat-label">Raised</span></div>
      </div>
    </div>
    <div id="directory"></div>
  </main>
</div>
<div class="modal-overlay" id="modal-overlay" onclick="if(event.target===this)closeModal()">
  <div class="modal">
    <button class="modal-close" onclick="closeModal()">✕</button>
    <div id="modal-content"></div>
  </div>
</div>
<script>
const DATA = """ + json_data + """;

const SECTION_META = {
  'Core African Projects': {
    title: 'Core African Projects',
    subtitle: 'HQ in Africa · African founders · Majority African users · Africa-licensed · Solving Africa-specific problems'
  },
  'African-Focused Projects': {
    title: 'African-Focused Projects',
    subtitle: 'African founders OR significant African operations (20%+ of business) OR Africa as strategic priority OR partnerships with African institutions'
  },
  'Africa-Serving Projects': {
    title: 'Africa-Serving Projects',
    subtitle: 'Global/international companies with African operations where Africa is one of several markets but providing infrastructure to African companies'
  }
};

const CAT_META = {
  'Exchange':       { icon:'💱', cls:'tag-exchange' },
  'Payments':       { icon:'💳', cls:'tag-payments' },
  'Infrastructure': { icon:'🏗️', cls:'tag-infrastructure' },
  'DeFi':           { icon:'⚡', cls:'tag-defi' },
  'On/Off-Ramp':    { icon:'🔄', cls:'tag-ramp' },
  'On/off ramp':    { icon:'🔄', cls:'tag-ramp' },
  'Blockchain':     { icon:'⛓️', cls:'tag-blockchain' },
  'Stablecoin':     { icon:'🪙', cls:'tag-stablecoin' },
  'Remittance':     { icon:'✈️', cls:'tag-remittance' },
  'Wallet':         { icon:'👛', cls:'tag-wallet' },
  'BaaS':           { icon:'🏦', cls:'tag-baas' },
  'Savings':        { icon:'💰', cls:'tag-savings' },
};

function tagCls(cat) {
  for (const [k,v] of Object.entries(CAT_META)) {
    if (cat.toLowerCase().includes(k.toLowerCase())) return v.cls;
  }
  return 'tag-default';
}

function initials(name) {
  return name.split(/[\\s\\/]+/).slice(0,2).map(w=>w[0]?.toUpperCase()||'').join('');
}

const catCounts = {};
DATA.forEach(d => d.categories.forEach(c => { catCounts[c] = (catCounts[c]||0)+1; }));
const SHOW_CATS = ['Exchange','Payments','Infrastructure','DeFi','On/Off-Ramp','Blockchain','Stablecoin','Remittance','Wallet','BaaS','Savings'];
const catSidebar = document.getElementById('cat-sidebar');
SHOW_CATS.forEach(cat => {
  const cnt = Object.entries(catCounts).reduce((a,[k,v]) => k.toLowerCase().includes(cat.toLowerCase()) ? a+v : a, 0);
  if (!cnt) return;
  const meta = CAT_META[cat] || { icon:'▸' };
  const btn = document.createElement('button');
  btn.className = 'sidebar-item';
  btn.dataset.cat = cat;
  btn.innerHTML = `<span class="sidebar-item-icon">${meta.icon}</span><span style="flex:1">${cat}</span><span class="sidebar-item-count">${cnt}</span>`;
  btn.onclick = function() { filterCat(this); };
  catSidebar.appendChild(btn);
});

let currentCat = 'all', currentSection = 'all';

function filterCat(el) {
  document.querySelectorAll('[data-cat]').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  currentCat = el.dataset.cat;
  applyFilters();
}

function filterSection(el) {
  document.querySelectorAll('[data-section]').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  currentSection = el.dataset.section;
  applyFilters();
}

function applyFilters() {
  const q = document.getElementById('search').value.toLowerCase().trim();
  const sections = {};
  const ORDER = ['Core African Projects','African-Focused Projects','Africa-Serving Projects'];
  let vis = 0;

  DATA.forEach(d => {
    const matchCat = currentCat === 'all' || d.categories.some(c => c.toLowerCase().includes(currentCat.toLowerCase()));
    const matchSec = currentSection === 'all' || d.section === currentSection;
    const matchQ = !q
      || d.name.toLowerCase().includes(q)
      || d.shortDesc.toLowerCase().includes(q)
      || d.hq.toLowerCase().includes(q)
      || d.categories.some(c => c.toLowerCase().includes(q))
      || (d.investors||'').toLowerCase().includes(q)
      || (d.ceo||'').toLowerCase().includes(q);
    if (matchCat && matchSec && matchQ) {
      if (!sections[d.section]) sections[d.section] = [];
      sections[d.section].push(d);
      vis++;
    }
  });

  document.getElementById('vis-count').textContent = vis;
  document.getElementById('count-badge').textContent = vis + ' Compan' + (vis===1?'y':'ies');
  document.getElementById('cnt-all').textContent = vis;

  const dir = document.getElementById('directory');
  dir.innerHTML = '';

  if (!vis) {
    dir.innerHTML = '<div class="empty"><div class="e-icon">🌍</div><h3>No results found</h3><p>Try different filters or clear your search</p></div>';
    return;
  }

  ORDER.forEach(sec => {
    if (!sections[sec]) return;
    const meta = SECTION_META[sec] || { title: sec, subtitle: '' };
    const label = document.createElement('div');
    label.className = 'section-header';
    label.innerHTML = `
      <div class="section-dot"></div>
      <div class="section-title-group">
        <span class="section-title">${meta.title}</span>
        <span class="section-subtitle">${meta.subtitle}</span>
      </div>
      <div class="section-line"></div>
      <span class="section-cnt">${sections[sec].length}</span>`;
    dir.appendChild(label);
    const grid = document.createElement('div');
    grid.className = 'grid';
    sections[sec].forEach(d => grid.appendChild(buildCard(d)));
    dir.appendChild(grid);
  });
}

function buildCard(d) {
  const el = document.createElement('div');
  el.className = 'card';
  el.onclick = () => openModal(d);
  const tags = d.categories.slice(0,3).map(c=>`<span class="tag ${tagCls(c)}">${c}</span>`).join('');
  const links = [
    d.website  ? `<a class="card-link" href="${d.website}"  target="_blank" onclick="event.stopPropagation()" title="Website">↗</a>` : '',
    d.twitter  ? `<a class="card-link" href="${d.twitter}"  target="_blank" onclick="event.stopPropagation()" title="X/Twitter">𝕏</a>` : '',
    d.linkedin ? `<a class="card-link" href="${d.linkedin}" target="_blank" onclick="event.stopPropagation()" title="LinkedIn">in</a>` : '',
  ].join('');
  el.innerHTML = `
    <div class="card-top"><div class="card-avatar">${initials(d.name)}</div><div class="card-links">${links}</div></div>
    <div class="card-name">${d.name}</div>
    <div class="card-hq">📍 ${d.hq || 'Africa'}</div>
    <div class="card-desc">${d.shortDesc || d.longDesc || ''}</div>
    <div class="card-tags">${tags}</div>
    <div class="card-bottom">
      <span class="card-funding">${d.funding || '—'}</span>
      <span class="card-employees">👥 ${d.employees || '—'}</span>
    </div>`;
  return el;
}

function openModal(d) {
  const tags = d.categories.map(c=>`<span class="tag ${tagCls(c)}">${c}</span>`).join('');

  // CEO name — clickable if CEO LinkedIn exists
  const ceoName = d.ceoLinkedin
    ? `<a href="${d.ceoLinkedin}" target="_blank">${d.ceo || '—'}</a>`
    : (d.ceo || '—');

  // Company links
  const companyLinks = [
    d.website  ? `<a href="${d.website}"  target="_blank" class="btn btn-primary">Visit Website ↗</a>` : '',
    d.twitter  ? `<a href="${d.twitter}"  target="_blank" class="btn btn-secondary">𝕏 Follow</a>` : '',
    d.linkedin ? `<a href="${d.linkedin}" target="_blank" class="btn btn-secondary">LinkedIn</a>` : '',
  ].filter(Boolean).join('');

  // CEO links
  const ceoLinks = [
    d.ceoTwitter  ? `<a href="${d.ceoTwitter}"  target="_blank" class="btn btn-secondary">CEO 𝕏</a>` : '',
    d.ceoLinkedin ? `<a href="${d.ceoLinkedin}" target="_blank" class="btn btn-secondary">CEO LinkedIn</a>` : '',
  ].filter(Boolean).join('');

  // Only show divider if BOTH company and CEO links exist
  const divider = (companyLinks && ceoLinks) ? '<div class="modal-divider"></div>' : '';

  document.getElementById('modal-content').innerHTML = `
    <div class="modal-hero">
      <div class="modal-header-row">
        <div class="modal-avatar">${initials(d.name)}</div>
        <div>
          <div class="modal-name">${d.name}</div>
          <div class="modal-hq">📍 ${d.hq || 'Africa'}</div>
        </div>
      </div>
      <div class="modal-tags">${tags}</div>
      <div class="modal-desc">${d.longDesc || d.shortDesc || ''}</div>
    </div>
    <div class="modal-body">
      <div class="modal-grid">
        <div class="modal-field"><label>Total Funding</label><p class="hi">${d.funding || '—'}</p></div>
        <div class="modal-field"><label>Latest Round</label><p>${d.latestRound || '—'}</p></div>
        <div class="modal-field"><label>Team Size</label><p>${d.employees || '—'}</p></div>
        <div class="modal-field"><label>CEO / Founder</label><p>${ceoName}</p></div>
      </div>
      ${d.investors ? `<div class="modal-sub">Investors & Partners</div><div class="modal-investors">${d.investors}</div>` : ''}
      <div class="modal-actions">
        ${companyLinks}
        ${divider}
        ${ceoLinks}
      </div>
    </div>`;
  document.getElementById('modal-overlay').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  document.getElementById('modal-overlay').classList.remove('open');
  document.body.style.overflow = '';
}

function toggleTheme() {
  const root = document.documentElement;
  const btn = document.getElementById('theme-btn');
  if (root.classList.contains('light')) {
    root.classList.remove('light');
    btn.textContent = '🌙 Dark';
  } else {
    root.classList.add('light');
    btn.textContent = '☀️ Light';
  }
}
document.addEventListener('keydown', e => { if(e.key==='Escape') closeModal(); });
applyFilters();
</script>
</body>
</html>"""

# Save as index.html 
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"\n✅ index.html saved successfully!")
print("   Open index.html in your browser to preview.")
print("   Push to GitHub and Vercel will deploy it automatically.")