"""Build data/species.js for the Game Fish ID Quiz.

Base list: FishBase species recorded in the United States or Canada that FishBase flags as
game fish (country-level `Game` or species-level `GameFish`), plus the hand-curated species in
scripts/curated.tsv (which supply common names, field-guide sections and ID tips).
Each species gets its FishBase state/province checklist and an iNaturalist taxon id + photo.

Run by .github/workflows/build-species.yml. Locally: pip install duckdb huggingface_hub; python scripts/build_species.py
"""
import duckdb, json, os, re, sys, time, urllib.parse, urllib.request
from huggingface_hub import list_repo_files, hf_hub_download

REPO = "cboettig/fishbase"
OUT = "data/species.js"
REPORT = []
log = lambda *a: (print(*a), REPORT.append(" ".join(str(x) for x in a)))

# ---------- FishBase download
files = list_repo_files(REPO, repo_type="dataset")
ver = sorted({m.group(1) for f in files if (m := re.match(r"data/fb/(v[\d.]+)/parquet/", f))})[-1]
log("FishBase version", ver)
P = {}
for t in ["species", "country", "countrysub", "families", "morphdat"]:
    try:
        P[t] = hf_hub_download(REPO, f"data/fb/{ver}/parquet/{t}.parquet", repo_type="dataset", local_dir="/tmp/fb")
    except Exception as e:
        log("could not download", t, e)
con = duckdb.connect()
cols = lambda t: [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM '{P[t]}'").fetchall()] if t in P else []

KEEP = "('native','endemic','introduced','reintroduced')"
cand = con.execute(f"""
  WITH c AS (
    SELECT SpecCode, list(DISTINCT CASE C_Code WHEN '840' THEN 'US' ELSE 'CA' END) AS countries,
           max(CASE WHEN Game=1 THEN 1 ELSE 0 END) AS game
    FROM '{P["country"]}' WHERE C_Code IN ('840','124') AND lower(Status) IN {KEEP} GROUP BY SpecCode)
  SELECT s.SpecCode, s.Genus, s.Species, s.FBname, f.Family, f.CommonName AS famname,
         s.Fresh, s.Brack, s.Saltwater, s.Length, s.DepthRangeDeep, s.DemersPelag, s.Comments,
         c.countries, c.game, s.GameFish
  FROM '{P["species"]}' s JOIN c USING (SpecCode) LEFT JOIN '{P["families"]}' f USING (FamCode)
""").fetchall()
names = ["code","genus","species","fbname","family","famname","fresh","brack","salt","length","depth","demers","comments","countries","game","gamefish"]
fb = {f"{r[1]} {r[2]}": dict(zip(names, r)) for r in cand}
log("FishBase species in US/Canada:", len(fb))

states = {}
for code, sub in con.execute(f"""SELECT SpecCode, CSub_Code FROM '{P["countrysub"]}'
     WHERE C_Code IN ('840','124') AND lower(Status) IN {KEEP}""").fetchall():
    states.setdefault(code, set()).add(sub)

diag = {}
if "AddChars" in cols("morphdat"):
    for code, txt in con.execute(f"SELECT SpecCode, AddChars FROM '{P['morphdat']}' WHERE AddChars IS NOT NULL").fetchall():
        if txt and len(txt) > 20: diag.setdefault(code, txt)
log("species with FishBase diagnosis text:", len(diag))

# ---------- curated list
curated = []
for line in open("scripts/curated.tsv"):
    if line.startswith("#") or not line.strip(): continue
    g, h, c, sci, tip = line.rstrip("\n").split("|")
    curated.append(dict(g=g, h=h, c=c, sci=sci.split(";"), tip=tip))

FAM_SECTION = {
    "Salmonidae": "trout", "Centrarchidae": "bass", "Percidae": "perch", "Esocidae": "pike", "Ictaluridae": "cat",
    "Moronidae": "temp", "Lepisosteidae": "rough", "Amiidae": "rough", "Acipenseridae": "rough", "Polyodontidae": "rough",
    "Cyprinidae": "rough", "Xenocyprididae": "rough", "Catostomidae": "rough", "Hiodontidae": "rough", "Lotidae": "rough",
    "Sciaenidae": "drum", "Lutjanidae": "snap", "Serranidae": "snap", "Epinephelidae": "snap", "Carangidae": "jack",
    "Scombridae": "tuna", "Istiophoridae": "pel", "Xiphiidae": "pel", "Coryphaenidae": "pel", "Rachycentridae": "pel",
    "Megalopidae": "pel", "Albulidae": "pel", "Centropomidae": "pel", "Pomatomidae": "pel", "Sphyraenidae": "pel",
    "Elopidae": "pel", "Paralichthyidae": "bottom", "Pleuronectidae": "bottom", "Bothidae": "bottom", "Labridae": "bottom",
    "Sparidae": "bottom", "Gadidae": "bottom", "Hexagrammidae": "bottom", "Sebastidae": "bottom", "Haemulidae": "bottom",
    "Ariidae": "bottom", "Merlucciidae": "bottom", "Malacanthidae": "bottom", "Balistidae": "bottom", "Ephippidae": "bottom",
    "Lamnidae": "shark", "Carcharhinidae": "shark", "Sphyrnidae": "shark", "Alopiidae": "shark", "Squalidae": "shark",
    "Triakidae": "shark", "Odontaspididae": "shark", "Ginglymostomatidae": "shark", "Hexanchidae": "shark",
}
FRESH_SECTIONS = {"trout", "bass", "perch", "pike", "cat", "temp", "rough"}

def habitat(r):
    fresh, salt = bool(r["fresh"]), bool(r["salt"] or r["brack"])
    return "b" if fresh and salt else "f" if fresh else "s"

def section(r, h):
    g = FAM_SECTION.get(r["family"] or "")
    if h == "f" and g not in FRESH_SECTIONS: return "rough"
    if g is None: return "rough" if h == "f" else "other"
    return g

def clean(txt, words):
    txt = re.sub(r"\(Ref\.[^)]*\)", "", txt or "")
    for w in words:
        if w: txt = re.sub(re.escape(w), "this fish", txt, flags=re.I)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt[:400]

records, used = [], set()
def add(sci_names, r, cur=None):
    h = cur["h"] if cur else habitat(r)
    rec = {
        "c": cur["c"] if cur else None, "sci": sci_names,
        "g": cur["g"] if cur else section(r, h), "h": h,
        "tip": cur["tip"] if cur else "",
        "cur": 1 if cur else 0,
    }
    if r:
        used.add(r["code"])
        rec.update(fb=r["code"], fam=r["family"], famc=r["famname"], len=r["length"],
                   cn=r["countries"], st=sorted(states.get(r["code"], [])), fbname=r["fbname"])
        words = [r["fbname"], r["genus"] + " " + r["species"], r["genus"]] + ([cur["c"]] if cur else [])
        if r["code"] in diag: rec["diag"] = clean(diag[r["code"]], words)
        elif r["comments"]: rec["about"] = clean(r["comments"].split(". ")[0] + ".", words)
    records.append(rec)

for cur in curated:
    r = next((fb[s] for s in cur["sci"] if s in fb), None)
    add(cur["sci"], r, cur)
for sci, r in fb.items():
    if r["code"] in used: continue
    if not (r["game"] or r["gamefish"]): continue
    add([sci], r)
log("curated:", len(curated), " total records:", len(records))

# ---------- iNaturalist taxon ids, common names and default photos (cached between builds)
old = {}
if os.path.exists(OUT):
    try:
        prev = json.loads(open(OUT).read().split("=", 1)[1].rstrip().rstrip(";"))
        old = {r["sci"][0]: r for r in prev["species"] if r.get("inat")}
    except Exception as e:
        log("could not read previous build:", e)

def inat(q):
    url = "https://api.inaturalist.org/v1/taxa?" + urllib.parse.urlencode({"q": q, "per_page": 10, "is_active": "true"})
    req = urllib.request.Request(url, headers={"User-Agent": "gamefish-quiz build (github.com/Jtrouern/gamefish-quiz)"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp: return json.load(resp).get("results", [])
        except Exception as e:
            time.sleep(5 * (attempt + 1))
    return []

missing = 0
for rec in records:
    o = old.get(rec["sci"][0])
    if o:
        for k in ("inat", "inatc", "ph"):
            if o.get(k): rec[k] = o[k]
        continue
    hit = None
    for s in rec["sci"]:
        res = inat(s); time.sleep(1.1)
        hit = next((t for t in res if t["name"].lower() == s.lower() and t["rank"] in ("species", "subspecies", "hybrid")), None) \
           or next((t for t in res if (t.get("matched_term") or "").lower() == s.lower() and t["rank"] == "species"), None)
        if hit: break
    if not hit:
        missing += 1; log("no iNaturalist match:", rec["sci"][0]); continue
    rec["inat"] = hit["id"]
    if hit.get("preferred_common_name"): rec["inatc"] = hit["preferred_common_name"]
    ph = hit.get("default_photo") or {}
    if ph.get("medium_url"): rec["ph"] = [ph["medium_url"], ph.get("attribution", "")]
log("iNaturalist unmatched:", missing)

for rec in records:
    if not rec["c"]:
        rec["c"] = rec.get("inatc") or (rec.get("fbname") or rec["sci"][0])
# drop duplicate common names (keep curated / first)
seen, final = set(), []
for rec in records:
    k = rec["c"].lower()
    if k in seen: continue
    seen.add(k); final.append(rec)

for i, rec in enumerate(final): rec["i"] = i
os.makedirs("data", exist_ok=True)
payload = {"built": time.strftime("%Y-%m-%d"), "fishbase": ver, "species": final}
open(OUT, "w").write("window.GAMEFISH_DATA=" + json.dumps(payload, separators=(",", ":"), ensure_ascii=False) + ";\n")
from collections import Counter
log("written", len(final), "species; by section:", dict(Counter(r["g"] for r in final)))
log("by habitat:", dict(Counter(r["h"] for r in final)))
open("data/build_report.txt", "w").write("\n".join(REPORT) + "\n")
