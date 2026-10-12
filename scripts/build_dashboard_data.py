"""Exports docs/data.json for the dashboard. Run from the repo root:  python scripts/build_dashboard_data.py"""
import json

import wiesn

overview = wiesn.load_overview()
cpi = wiesn.load_cpi().set_index("jahr")["vpi"]
wage = wiesn.load_minimum_wage().set_index("jahr")["mindestlohn_eur"]
tents = wiesn.load_tents()
menu = wiesn.load_menu()

years = overview["jahr"].tolist()
out = {
    "years": years,
    "price": overview["bier_preis"].tolist(),
    "cpi": {int(y): float(v) for y, v in cpi.items()},
    "visitors": overview["besucher_gesamt"].tolist(),
    "beer_litres": overview["beer_litres"].tolist(),
    "minimum_wage": {int(y): float(v) for y, v in wage.items()},
    "tents_2025": tents[tents["jahr"] == 2025].sort_values("preis")[["tent", "preis"]].values.tolist(),
    "menu": [
        {"item": item_en, "de": item, "2018": float(g.loc[g["jahr"] == 2018, "preis"].iloc[0]),
         "2025": float(g.loc[g["jahr"] == 2025, "preis"].iloc[0])}
        for (item, item_en), g in menu.groupby(["item", "item_en"], sort=False)
    ],
}
(wiesn.ROOT / "docs").mkdir(exist_ok=True)
(wiesn.ROOT / "docs/data.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
print(f"docs/data.json written: {len(years)} years, {len(out['menu'])} menu items")
