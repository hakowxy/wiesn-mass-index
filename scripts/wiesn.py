"""Loading and cleaning shared by the notebook and the dashboard export."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw"

# Tent names change over the years (sponsors, spelling). Map every variant to one current name.
TENT_NAMES = {
    "Armbrustschützen": "Armbrustschützen-Festzelt",
    "Armbrustschützen-Festzelt": "Armbrustschützen-Festzelt",
    "Augustiner": "Augustiner-Festhalle",
    "Augustiner-Festhalle": "Augustiner-Festhalle",
    "Bräurosl": "Bräurosl",
    "Fischer Vroni": "Fischer-Vroni",
    "Fischer-Vroni": "Fischer-Vroni",
    "Hacker": "Hacker-Festzelt",
    "Hackerbräu-Festzelt": "Hacker-Festzelt",
    "Hacker-Festzelt": "Hacker-Festzelt",
    "Hippodrom": "Hippodrom",
    "Hofbräuhaus": "Hofbräu-Festzelt",
    "HofbräuFestzelt": "Hofbräu-Festzelt",
    "Hofbräufestzelt": "Hofbräu-Festzelt",
    "Hofbräu-Festzelt": "Hofbräu-Festzelt",
    "Hofbräuhaus-Festzelt": "Hofbräu-Festzelt",
    "Käfer Wies´n Schänke": "Käfer Wiesn-Schänke",
    "Käfer Wiesn Schänke": "Käfer Wiesn-Schänke",
    "Löwenbräu": "Löwenbräu-Festzelt",
    "Löwenbräu-Festzelt": "Löwenbräu-Festzelt",
    "Marstall": "Marstall",
    "Ochsenbraterei": "Ochsenbraterei",
    "Winzerer Fähndl": "Paulaner-Festzelt",
    "Paulanerbräu Winzerer Fähndl": "Paulaner-Festzelt",
    "Paulaner-Festzelt": "Paulaner-Festzelt",
    "Schottenhamel": "Schottenhamel-Festhalle",
    "Schottenhamel-Festhalle": "Schottenhamel-Festhalle",
    # The source lists "Sportschützen" until 2009 and "Schützen-Festzelt" from 2010, which is the same tent.
    "Sportschützen": "Schützen-Festzelt",
    "Schützen-Festzelt": "Schützen-Festzelt",
}

# Menu items as translated labels for charts
MENU_EN = {
    "Leberknödelsuppe": "Liver dumpling soup", "Pfannkuchen-/Tagessuppe": "Pancake / daily soup",
    "Gulaschsuppe": "Goulash soup", "Obatzda mit Brot": "Obatzda with bread", "Münchner Wurstsalat": "Sausage salad",
    "2 Weißwürste": "2 white sausages", "Schweinswürstl mit Kraut": "Pork sausages with kraut",
    "Käsespätzle": "Cheese spätzle", "Schwammerl mit Semmelknödel": "Mushrooms with dumpling",
    "½ Brathendl ohne Salat": "½ roast chicken", "½ Ente mit Knödel": "½ duck with dumpling",
    "Sauerbraten": "Sauerbraten", "Schweinsbraten mit Knödel": "Roast pork with dumpling",
    "Schweinshaxe (Portion)": "Pork knuckle", "Spanferkel mit Knödel": "Suckling pig with dumpling",
    "Tellerfleisch/Tafelspitz": "Boiled beef", "Wiener Schnitzel": "Wiener Schnitzel",
    "Apfelstrudel": "Apple strudel", "Dampfnudel": "Dampfnudel", "Kaiserschmarrn": "Kaiserschmarrn",
    "1 Maß Bier": "1 Maß of beer (1 l)", "Erfrischungsgetränke 0,5 l": "Soft drink (0.5 l)",
    "Tafel-/Mineralwasser 0,5 l": "Water (0.5 l)",
}


def load_overview():
    """One row per year: duration, visitors (millions), beer price and volume (hl), chicken price and count."""
    df = pd.read_csv(RAW / "oktoberfest_gesamt_1985_2025.csv")
    df["beer_litres"] = df["bier_konsum"] * 100
    return df


def load_cpi():
    """German consumer price index (2020 = 100), annual, from Destatis table 61111-0001."""
    cpi = pd.read_csv(RAW / "destatis_61111-0001_vpi.csv", sep=";", skiprows=6, header=None,
                      usecols=[0, 1], names=["jahr", "vpi"], decimal=",", encoding="utf-8-sig")
    cpi = cpi[pd.to_numeric(cpi["jahr"], errors="coerce").notna()].astype({"jahr": int, "vpi": float})
    return cpi


def load_minimum_wage():
    return pd.read_csv(RAW / "mindestlohn.csv")


def load_tents():
    df = pd.read_csv(RAW / "oktoberfest_bierpreise_festzelte_2000_2025.csv", na_values="NA")
    df["tent"] = df["zelt"].map(TENT_NAMES)
    unmapped = df.loc[df["tent"].isna(), "zelt"].unique()
    if len(unmapped):
        raise ValueError(f"Unknown tent names: {unmapped}")
    return df.dropna(subset=["preis"])


def load_menu():
    df = pd.read_csv(RAW / "oktoberfest_speisen_getraenke_2018_2025.csv")
    # 2025 writes "0.5 l" where earlier years write "0,5 l"
    df["item"] = df["speisen-getraenke"].str.replace("0.5 l", "0,5 l", regex=False)
    unmapped = set(df["item"]) - set(MENU_EN)
    if unmapped:
        raise ValueError(f"Unknown menu items: {unmapped}")
    df["item_en"] = df["item"].map(MENU_EN)
    return df


def load_bavaria_wages():
    """Nominal and real wage index for Bavaria (2025 = 100), Destatis table 62361-0102. Starts in 2022."""
    df = pd.read_csv(RAW / "destatis_62361-0102_lohnindex_laender.csv", sep=";", skiprows=5, header=None,
                     usecols=[0, 1, 2, 6], names=["land", "jahr", "reallohn", "nominallohn"],
                     encoding="utf-8-sig", decimal=",", na_values=["...", "."])
    df = df[df["land"] == "Bayern"].dropna()
    return df.astype({"jahr": int, "reallohn": float, "nominallohn": float}).drop(columns="land")
