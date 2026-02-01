# interpret_de_ba_hwk.py
from __future__ import annotations
import re
from pathlib import Path
import pandas as pd
import numpy as np

DE_PATH = r"D:\One Drive\OneDrive - Faculty of Philosophy in Sarajevo\HWK_analize\hwk_de_oktobar.xlsx"
BA_PATH = r"D:\One Drive\OneDrive - Faculty of Philosophy in Sarajevo\HWK_analize\HWK_mit_API_BA_ANUBIH.xlsx"
OUT_PATH = r"D:\One Drive\OneDrive - Faculty of Philosophy in Sarajevo\HWK_analize\HWK_DE_BA_INTERPRETATION.xlsx"

# DE columns
DE_BRANCHE_COL = "Branche"
DE_FEAT_COL    = "HWK_feat"
DE_TEXT_COL    = "HWK_Text"

# BA columns (für Vergleich am besten deutsch)
BA_FILE_COL    = "Datei"
BA_BRANCHE_COL = "Branche_DE"
BA_FEAT_COL    = "HWK_DE"

IGNORE_BRANCHE = None  # z.B. "Unbekannt"
SPLIT_PATTERN = r"[;,|\n]+"

# --- Canonicalization: bring alles auf Umlaut-Form ---
FEAT_CANON = {
    "Qualitaet":"Qualität",
    "Ernaehrung":"Ernährung",
    "Schoenheit":"Schönheit",
    "Oekologie":"Ökologie",
    "Leistungsfaehigkeit":"Leistungsfähigkeit",
    "Aesthetik":"Ästhetik",
}

BRANCH_CANON = {
    "Reise – Tourismus":"Reisen und Tourismus",
}

def canon_feat(x: str) -> str:
    x = str(x).strip()
    return FEAT_CANON.get(x, x)

def canon_branch(x: str) -> str:
    x = str(x).strip()
    return BRANCH_CANON.get(x, x)

def build_de_adid(df: pd.DataFrame) -> pd.Series:
    req = ["Medium", "Branche", "Produkt", "Brand", DE_TEXT_COL]
    miss = [c for c in req if c not in df.columns]
    if miss:
        raise ValueError(f"DE: Missing columns for AdID: {miss}")

    def norm(v) -> str:
        v = "" if pd.isna(v) else str(v)
        v = re.sub(r"\s+", " ", v.strip().lower())
        return v

    base = (
        df["Medium"].map(norm) + "||" +
        df["Branche"].map(norm) + "||" +
        df["Produkt"].map(norm) + "||" +
        df["Brand"].map(norm) + "||" +
        df[DE_TEXT_COL].map(norm)
    )
    return pd.util.hash_pandas_object(base, index=False).astype("int64").astype(str)

def explode_features(df: pd.DataFrame, branche_col: str, feat_col: str, file_col: str) -> pd.DataFrame:
    tmp = df[[branche_col, feat_col, file_col]].copy()
    tmp = tmp.dropna(subset=[branche_col, feat_col, file_col])

    tmp = tmp.rename(columns={branche_col:"Branche", feat_col:"FeatureRaw", file_col:"FileID"})
    tmp["Branche"] = tmp["Branche"].astype(str).str.strip().map(canon_branch)
    tmp["FileID"]  = tmp["FileID"].astype(str).str.strip()
    tmp["FeatureRaw"] = tmp["FeatureRaw"].astype(str).str.replace("\r","\n", regex=False)

    if IGNORE_BRANCHE is not None:
        tmp = tmp[tmp["Branche"] != str(IGNORE_BRANCHE)]

    tmp["HWK_feat"] = tmp["FeatureRaw"].str.split(SPLIT_PATTERN, regex=True)
    tmp = tmp.explode("HWK_feat")
    tmp["HWK_feat"] = tmp["HWK_feat"].astype(str).str.strip()
    tmp = tmp[(tmp["HWK_feat"]!="") & (tmp["HWK_feat"]!="nan")]
    tmp["HWK_feat"] = tmp["HWK_feat"].map(canon_feat)

    # Dedupe: pro Anzeige zählt Feature nur 1x
    tmp = tmp.drop_duplicates(subset=["Branche","FileID","HWK_feat"])
    return tmp[["Branche","FileID","HWK_feat"]]

def compute_rates(exploded: pd.DataFrame) -> tuple[pd.DataFrame,pd.DataFrame]:
    # N_ads pro Branche
    n_branch = exploded.groupby("Branche")["FileID"].nunique().rename("N_ads").reset_index()

    # Count ads-with-feature
    counts = (exploded.groupby(["Branche","HWK_feat"])["FileID"]
              .nunique().rename("count_ads_with_feat").reset_index())

    # merge to get rates
    long = counts.merge(n_branch, on="Branche", how="left")
    long["p"] = long["count_ads_with_feat"] / long["N_ads"]
    return long, n_branch

def main():
    de_df = pd.read_excel(DE_PATH, engine="openpyxl")
    ba_df = pd.read_excel(BA_PATH, engine="openpyxl")

    de_df = de_df.copy()
    de_df["AdID"] = build_de_adid(de_df)

    de_exp = explode_features(de_df, DE_BRANCHE_COL, DE_FEAT_COL, "AdID")
    ba_exp = explode_features(ba_df, BA_BRANCHE_COL, BA_FEAT_COL, BA_FILE_COL)

    de_long, de_n = compute_rates(de_exp)
    ba_long, ba_n = compute_rates(ba_exp)

    de_long = de_long.rename(columns={"count_ads_with_feat":"DE_count","N_ads":"DE_N","p":"DE_p"})
    ba_long = ba_long.rename(columns={"count_ads_with_feat":"BA_count","N_ads":"BA_N","p":"BA_p"})

    comp = pd.merge(de_long, ba_long, on=["Branche","HWK_feat"], how="outer").fillna(0)
    comp["DE_count"] = comp["DE_count"].astype(int)
    comp["BA_count"] = comp["BA_count"].astype(int)
    comp["DE_N"] = comp["DE_N"].astype(int)
    comp["BA_N"] = comp["BA_N"].astype(int)

    comp["Diff_p_DE_minus_BA"] = comp["DE_p"] - comp["BA_p"]

    # Ratio der Raten (mit kleinem epsilon gegen 0)
    eps = 1e-9
    comp["Ratio_p_DE_div_BA"] = (comp["DE_p"] + eps) / (comp["BA_p"] + eps)

    # Top-Listen
    top_de = comp.sort_values("Diff_p_DE_minus_BA", ascending=False).head(50)
    top_ba = comp.sort_values("Diff_p_DE_minus_BA", ascending=True).head(50)

    # Pivot views
    p_de_piv = comp.pivot(index="Branche", columns="HWK_feat", values="DE_p")
    p_ba_piv = comp.pivot(index="Branche", columns="HWK_feat", values="BA_p")
    diff_piv = comp.pivot(index="Branche", columns="HWK_feat", values="Diff_p_DE_minus_BA")

    with pd.ExcelWriter(OUT_PATH, engine="openpyxl") as w:
        comp.to_excel(w, sheet_name="Compare_Rates_Long", index=False)
        top_de.to_excel(w, sheet_name="Top_DE_higher", index=False)
        top_ba.to_excel(w, sheet_name="Top_BA_higher", index=False)
        de_n.to_excel(w, sheet_name="DE_N_per_Branche", index=False)
        ba_n.to_excel(w, sheet_name="BA_N_per_Branche", index=False)
        p_de_piv.to_excel(w, sheet_name="DE_p_Pivot")
        p_ba_piv.to_excel(w, sheet_name="BA_p_Pivot")
        diff_piv.to_excel(w, sheet_name="Diff_p_Pivot")

    print("Fertig ✅", OUT_PATH)
    print("Hinweis: Diff_p ist die saubere interpretierbare Größe (pro Branche normalisiert).")

if __name__ == "__main__":
    main()
