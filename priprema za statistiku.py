# hwk_compare_custom_columns_FIXED.py

from __future__ import annotations
from pathlib import Path
import pandas as pd
import re

DE_PATH = r"D:\One Drive\OneDrive - Faculty of Philosophy in Sarajevo\HWK_analize\hwk_de_oktobar.xlsx"
BA_PATH = r"D:\One Drive\OneDrive - Faculty of Philosophy in Sarajevo\HWK_analize\HWK_mit_API_BA_ANUBIH.xlsx"

OUT_PATH = r"D:\One Drive\OneDrive - Faculty of Philosophy in Sarajevo\HWK_analize\HWK_DE_BA_agg_noDupes_COMPARE.xlsx"

# ---- DE Struktur ----
DE_BRANCHE_COL = "Branche"
DE_FEAT_COL    = "HWK_feat"
DE_TEXT_COL    = "HWK_Text"   # für AdID-Bau

# ---- BA Struktur ----
BA_FILE_COL    = "Datei"
BA_BRANCHE_COL = "Branche_DE" # oder "Branche_BA"
BA_FEAT_COL    = "HWK_DE"     # oder "HWK_BA"

IGNORE_BRANCHE = None  # z.B. "Unbekannt"

# Mehrere Features pro Zelle trennen (z.B. "A;B" oder "A, B" etc.)
SPLIT_PATTERN = r"[;,|\n]+"


def build_de_adid(df: pd.DataFrame) -> pd.Series:
    """
    DE hat keine Datei/ID -> Surrogat-ID aus Medium+Branche+Produkt+Brand+HWK_Text.
    Beste Näherung mit deinen Spalten, aber nicht mathematisch “perfekt”, falls echte Dubletten existieren.
    """
    required = ["Medium", "Branche", "Produkt", "Brand", DE_TEXT_COL]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"DE-Datei: Spalten fehlen für AdID: {missing}")

    def norm(x) -> str:
        x = "" if pd.isna(x) else str(x)
        x = x.strip().lower()
        x = re.sub(r"\s+", " ", x)
        return x

    base = (
        df["Medium"].map(norm) + "||" +
        df["Branche"].map(norm) + "||" +
        df["Produkt"].map(norm) + "||" +
        df["Brand"].map(norm) + "||" +
        df[DE_TEXT_COL].map(norm)
    )
    return pd.util.hash_pandas_object(base, index=False).astype("int64").astype(str)


def aggregate(df: pd.DataFrame, branche_col: str, feat_col: str, file_col: str, ignore_branche: str | None):
    """
    Liefert:
      pivot: Branche x Feature (Counts = Anzahl eindeutiger Dateien/AdIDs)
      long : Branche, HWK_feat, count_files
    """
    # prüfen
    for c in [branche_col, feat_col, file_col]:
        if c not in df.columns:
            raise ValueError(f"Spalte fehlt: {c}. Vorhanden: {list(df.columns)}")

    tmp = df[[branche_col, feat_col, file_col]].copy()
    tmp = tmp.dropna(subset=[branche_col, feat_col, file_col])

    # intern standardisieren -> NIE wieder Name-Kollisionen
    tmp = tmp.rename(columns={
        branche_col: "Branche",
        feat_col: "FeatureRaw",
        file_col: "FileID"
    })

    tmp["Branche"] = tmp["Branche"].astype(str).str.strip()
    tmp["FileID"]  = tmp["FileID"].astype(str).str.strip()
    tmp["FeatureRaw"] = tmp["FeatureRaw"].astype(str)

    if ignore_branche is not None:
        tmp = tmp[tmp["Branche"] != str(ignore_branche)]

    # Features splitten & explodieren
    tmp["FeatureRaw"] = tmp["FeatureRaw"].str.replace("\r", "\n", regex=False)
    tmp["HWK_feat"] = tmp["FeatureRaw"].str.split(SPLIT_PATTERN, regex=True)
    tmp = tmp.explode("HWK_feat")

    tmp["HWK_feat"] = tmp["HWK_feat"].astype(str).str.strip()
    tmp = tmp[tmp["HWK_feat"].ne("") & tmp["HWK_feat"].ne("nan")]

    # Dedupe: pro (Branche, Datei/AdID, Feature) nur 1x
    unique = tmp.drop_duplicates(subset=["Branche", "FileID", "HWK_feat"])

    # zählen: wie viele eindeutige Files pro Branche haben das Feature?
    agg_long = (
        unique.groupby(["Branche", "HWK_feat"])
        .size()
        .rename("count_files")
        .reset_index()
    )

    pivot = agg_long.pivot(index="Branche", columns="HWK_feat", values="count_files").fillna(0).astype(int)
    pivot["TOTAL_per_Branche"] = pivot.sum(axis=1)

    meta = {
        "rows_original": len(df),
        "rows_unique": len(unique),
        "used_branche_col": branche_col,
        "used_feat_col": feat_col,
        "used_file_col": file_col,
    }
    return pivot, agg_long, meta


def main():
    de_path = Path(DE_PATH)
    ba_path = Path(BA_PATH)

    if not de_path.exists():
        raise FileNotFoundError(f"DE Input nicht gefunden: {de_path}")
    if not ba_path.exists():
        raise FileNotFoundError(f"BA Input nicht gefunden: {ba_path}")

    de_df = pd.read_excel(de_path, engine="openpyxl")
    ba_df = pd.read_excel(ba_path, engine="openpyxl")

    # DE: AdID bauen
    de_df = de_df.copy()
    de_df["AdID"] = build_de_adid(de_df)

    # Aggregieren
    de_pivot, de_long, de_meta = aggregate(de_df, DE_BRANCHE_COL, DE_FEAT_COL, "AdID", IGNORE_BRANCHE)
    ba_pivot, ba_long, ba_meta = aggregate(ba_df, BA_BRANCHE_COL, BA_FEAT_COL, BA_FILE_COL, IGNORE_BRANCHE)

    # Vergleich (Long)
    de_cmp = de_long.rename(columns={"count_files": "DE_count"})
    ba_cmp = ba_long.rename(columns={"count_files": "BA_count"})

    compare = pd.merge(de_cmp, ba_cmp, on=["Branche", "HWK_feat"], how="outer").fillna(0)
    compare["DE_count"] = compare["DE_count"].astype(int)
    compare["BA_count"] = compare["BA_count"].astype(int)
    compare["Diff_DE_minus_BA"] = compare["DE_count"] - compare["BA_count"]
    compare["Ratio_DE_div_BA"] = compare.apply(
        lambda r: (r["DE_count"] / r["BA_count"]) if r["BA_count"] != 0 else (float("inf") if r["DE_count"] > 0 else 0.0),
        axis=1
    )

    # Diff Pivot
    de_feats = [c for c in de_pivot.columns if c != "TOTAL_per_Branche"]
    ba_feats = [c for c in ba_pivot.columns if c != "TOTAL_per_Branche"]

    all_branches = sorted(set(de_pivot.index) | set(ba_pivot.index))
    all_feats = sorted(set(de_feats) | set(ba_feats))

    de_aligned = de_pivot.reindex(index=all_branches, columns=all_feats, fill_value=0)
    ba_aligned = ba_pivot.reindex(index=all_branches, columns=all_feats, fill_value=0)
    diff_pivot = (de_aligned - ba_aligned).astype(int)
    diff_pivot["TOTAL_diff"] = diff_pivot.sum(axis=1)

    # Export
    out_path = Path(OUT_PATH)
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        de_pivot.to_excel(writer, sheet_name="DE_Pivot")
        ba_pivot.to_excel(writer, sheet_name="BA_Pivot")
        diff_pivot.to_excel(writer, sheet_name="Compare_Diff_Pivot")

        de_long.to_excel(writer, sheet_name="Long_DE", index=False)
        ba_long.to_excel(writer, sheet_name="Long_BA", index=False)
        compare.sort_values(["Branche", "HWK_feat"]).to_excel(writer, sheet_name="Compare_Long", index=False)

        meta_df = pd.DataFrame([
            {"Dataset": "DE", **de_meta},
            {"Dataset": "BA", **ba_meta},
            {"Dataset": "INFO", "rows_original": "", "rows_unique": "",
             "used_branche_col": f"BA Branche={BA_BRANCHE_COL}",
             "used_feat_col": f"BA Features={BA_FEAT_COL}",
             "used_file_col": "DE uses AdID(surrogate)"},
        ])
        meta_df.to_excel(writer, sheet_name="Meta", index=False)

    print("Fertig ✅")
    print(f"Output: {out_path}")
    print("DE meta:", de_meta)
    print("BA meta:", ba_meta)


if __name__ == "__main__":
    main()
