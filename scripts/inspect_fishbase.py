"""One-off: dump FishBase table schemas/samples so the species builder can be written against real columns."""
import duckdb
BASE = "https://huggingface.co/datasets/cboettig/fishbase/resolve/main/data/fb/v24.07/parquet/"
con = duckdb.connect(); con.execute("INSTALL httpfs; LOAD httpfs;")
out = []
def q(sql, n=8):
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
