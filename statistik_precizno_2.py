# make_hwk_interpretation_report.py
import pandas as pd
import numpy as np

INPUT = r"D:\One Drive\OneDrive - Faculty of Philosophy in Sarajevo\HWK_analize\HWK_DE_BA_INTERPRETATION.xlsx"
OUTPUT = r"D:\One Drive\OneDrive - Faculty of Philosophy in Sarajevo\HWK_analize\HWK_DE_BA_INTERPRETATION_REPORT.xlsx"
MIN_N = 30  # z.B. 20 oder 30

try:
    from scipy.stats import fisher_exact
    HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False

def bh_fdr(pvals: np.ndarray) -> np.ndarray:
    pvals = np.asarray(pvals, dtype=float)
    m = np.isfinite(pvals).sum()
    q = np.full_like(pvals, np.nan, dtype=float)
    if m == 0:
        return q
    idx = np.where(np.isfinite(pvals))[0]
    order = idx[np.argsort(pvals[idx])]
    ranked = np.arange(1, len(order) + 1)
    qtemp = pvals[order] * len(order) / ranked
    qtemp = np.minimum.accumulate(qtemp[::-1])[::-1]
    q[order] = np.clip(qtemp, 0, 1)
    return q

def main():
    xls = pd.ExcelFile(INPUT)
    comp = pd.read_excel(xls, "Compare_Rates_Long")
    de_n = pd.read_excel(xls, "DE_N_per_Branche").rename(columns={"N_ads": "DE_N_branch"})
    ba_n = pd.read_excel(xls, "BA_N_per_Branche").rename(columns={"N_ads": "BA_N_branch"})

    # Branche -> N mapping
    comp = comp.merge(de_n, on="Branche", how="left").merge(ba_n, on="Branche", how="left")
    comp["DE_N_branch"] = comp["DE_N_branch"].fillna(0).astype(int)
    comp["BA_N_branch"] = comp["BA_N_branch"].fillna(0).astype(int)

    # Fix N überall
    comp["DE_N"] = comp["DE_N_branch"]
    comp["BA_N"] = comp["BA_N_branch"]

    # Recompute rates
    comp["DE_p"] = comp.apply(lambda r: r["DE_count"] / r["DE_N"] if r["DE_N"] > 0 else 0.0, axis=1)
    comp["BA_p"] = comp.apply(lambda r: r["BA_count"] / r["BA_N"] if r["BA_N"] > 0 else 0.0, axis=1)
    comp["Diff_p_DE_minus_BA"] = comp["DE_p"] - comp["BA_p"]

    # Optional significance
    if HAVE_SCIPY:
        def fisher_p(r):
            if r["DE_N"] == 0 or r["BA_N"] == 0:
                return np.nan
            a = int(r["DE_count"]); b = int(r["DE_N"] - r["DE_count"])
            c = int(r["BA_count"]); d = int(r["BA_N"] - r["BA_count"])
            if min(a, b, c, d) < 0:
                return np.nan
            _, p = fisher_exact([[a, b], [c, d]], alternative="two-sided")
            return p

        comp["p_fisher"] = comp.apply(fisher_p, axis=1)
        comp["q_fdr_global"] = bh_fdr(comp["p_fisher"].to_numpy())
    else:
        comp["p_fisher"] = np.nan
        comp["q_fdr_global"] = np.nan

    # Robust filter
    comp["minN"] = comp[["DE_N", "BA_N"]].min(axis=1)
    robust = comp[(comp["minN"] >= MIN_N) & (comp["DE_N"] > 0) & (comp["BA_N"] > 0)].copy()

    top_de = robust.sort_values("Diff_p_DE_minus_BA", ascending=False).head(50)
    top_ba = robust.sort_values("Diff_p_DE_minus_BA", ascending=True).head(50)

    # Branch summary (Top 5 je Richtung)
    rows = []
    for br in sorted(robust["Branche"].unique()):
        sub = robust[robust["Branche"] == br].copy()
        deN = int(sub["DE_N"].iloc[0]); baN = int(sub["BA_N"].iloc[0])

        td = sub.sort_values("Diff_p_DE_minus_BA", ascending=False).head(5)
        tb = sub.sort_values("Diff_p_DE_minus_BA", ascending=True).head(5)

        def fmt(df):
            return " | ".join([f"{r.HWK_feat}: {r.Diff_p_DE_minus_BA:+.3f} (DE {r.DE_p:.3f} vs BA {r.BA_p:.3f})"
                               for r in df.itertuples()])

        rows.append({
            "Branche": br,
            "DE_N": deN,
            "BA_N": baN,
            "DE_higher_top5": fmt(td),
            "BA_higher_top5": fmt(tb),
        })

    branch_summary = pd.DataFrame(rows)

    with pd.ExcelWriter(OUTPUT, engine="openpyxl") as w:
        comp.to_excel(w, sheet_name="Clean_Compare", index=False)
        robust.to_excel(w, sheet_name=f"Robust_minN_{MIN_N}", index=False)
        top_de.to_excel(w, sheet_name="Top_DE_higher", index=False)
        top_ba.to_excel(w, sheet_name="Top_BA_higher", index=False)
        branch_summary.to_excel(w, sheet_name="Branch_Summary", index=False)

    print("OK:", OUTPUT)
    print(f"Robust branches (minN >= {MIN_N}):", sorted(robust["Branche"].unique()))

if __name__ == "__main__":
    main()
