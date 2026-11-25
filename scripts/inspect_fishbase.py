"""One-off: dump FishBase table schemas/samples so the species builder can be written against real columns."""
import duckdb, os, re
from huggingface_hub import list_repo_files, hf_hub_download
out = []
REPO = "cboettig/fishbase"
files = list_repo_files(REPO, repo_type="dataset")
vers = sorted({m.group(1) for f in files if (m := re.match(r"data/fb/(v[\d.]+)/parquet/", f))})
out.append("versions: " + ", ".join(vers)); ver = vers[-1]
os.makedirs("/tmp/fb", exist_ok=True)
def get(t):
    return hf_hub_download(REPO, f"data/fb/{ver}/parquet/{t}.parquet", repo_type="dataset", local_dir="/tmp/fb")
TABLES = ["species","country","countrysub","comnames","families","ecology","zweb_foridentification","countref","faoareas"]
for t in TABLES:
    try: get(t)
    except Exception as e: out.append(f"download {t}: {e}")
BASE = f"/tmp/fb/data/fb/{ver}/parquet/"
con = duckdb.connect()
def q(sql, n=8):
    global out
    try:
        r = con.execute(sql); cols = [d[0] for d in r.description]; rows = r.fetchmany(n)
        out.append("SQL: " + sql); out.append(" | ".join(cols))
        out += [" | ".join(str(v)[:80] for v in row) for row in rows]
    except Exception as e:
        out.append(f"SQL: {sql}\nERROR: {e}")
    out.append("")
for t in ["species","country","countrysub","comnames","families","ecology","zweb_foridentification","countref","faoareas"]:
    q(f"DESCRIBE SELECT * FROM '{BASE}{t}.parquet'", 200)
q(f"SELECT * FROM '{BASE}countrysub.parquet' WHERE C_Code IN ('840','124') LIMIT 10")
q(f"SELECT C_Code, CSub_Code, count(*) n FROM '{BASE}countrysub.parquet' WHERE C_Code IN ('840','124') GROUP BY ALL ORDER BY n DESC", 120)
q(f"SELECT * FROM '{BASE}country.parquet' WHERE C_Code='840' LIMIT 5")
q(f"SELECT GameFish, count(*) FROM '{BASE}species.parquet' GROUP BY ALL")
q(f"SELECT Game, count(*) FROM '{BASE}country.parquet' WHERE C_Code IN ('840','124') GROUP BY ALL")
q(f"SELECT * FROM '{BASE}zweb_foridentification.parquet' LIMIT 3")
q(f"SELECT * FROM '{BASE}countref.parquet' WHERE C_Code IN ('840','124') LIMIT 3")
open("data/fishbase_schema.txt","w").write("\n".join(out))
