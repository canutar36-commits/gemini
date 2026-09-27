"""Standart 101 raporu için doğrulama ve grafik/tablo üretimi."""
import random

from . import report
from .std_bots import make_std_bots
from .std_engine import StdHandGame

STD_LABELS = {b.name: b.label for b in make_std_bots()}


def validate(seed=11, n=10):
    rng = random.Random(seed)
    bots = make_std_bots()
    res, sample = [], None
    for k in range(n):
        g = StdHandGame(bots, k % 4, rng, 101, log=True, check=True)
        r = g.play()
        res.append(r)
        if sample is None and r["kind"] != "deste" and len(g.logs) > 12:
            sample = g.logs
    return res, sample or g.logs


def build(data, val_res, val_log, n_games, out="out_std"):
    pass  # rapor ayrı adımda üretilir


# ---------------------------------------------------------------- rapor
import math
import pickle
import statistics as st
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAMES = report.NAMES
COL = report.COL
KINDS = report.KINDS
KIND_TR = report.KIND_TR


def compute(games):
    report.LABELS = STD_LABELS
    P, T, totals = report.stats(games)
    hands = [h for g in games for h in g]
    for n in NAMES:
        P[n]["ci"] = 1.96 * P[n]["sd"] / math.sqrt(len(games))
        P[n]["gost_n"] = P[n]["bonus_n"]
        P[n]["mult"] = sum(h["mult_pts"][n] for h in hands)
        P[n]["unopened_all"] = 100 * sum(1 for h in hands if h["fin"] != n and h["opened"][n] is None) / len(hands)
        P[n]["deste_open"] = 100 * sum(1 for h in hands if h["kind"] == "deste" and h["opened"][n]) / max(1, T["kinds"]["deste"])
    T["deste_nobody"] = 100 * sum(1 for h in hands if h["kind"] == "deste" and not any(h["opened"].values())) / max(1, T["kinds"]["deste"])
    T["opened_avg"] = st.mean(sum(1 for v in h["opened"].values() if v) for h in hands)
    return P, T, totals


def charts(games, P, T, totals, out="out_std"):
    L = STD_LABELS
    # 1) ortalama + %95 GA
    fig, ax = plt.subplots(figsize=(8, 4.5))
    xs = range(4)
    ax.bar(xs, [P[n]["mean"] for n in NAMES], color=[COL[n] for n in NAMES], width=0.6,
           yerr=[P[n]["ci"] for n in NAMES], capsize=6, error_kw={"ecolor": "#333", "lw": 1.2})
    for i, n in enumerate(NAMES):
        ax.text(i, P[n]["mean"] + P[n]["ci"] + 20, f"{P[n]['mean']:.0f}", ha="center", fontsize=10)
    ax.set_xticks(list(xs)); ax.set_xticklabels([L[n] for n in NAMES], fontsize=9)
    ax.axhline(0, color="#888", lw=0.8)
    ax.set_ylabel("100 el sonu ortalama puan")
    ax.set_title("Standart 101: ortalama puan ve %95 güven aralığı (1000 oyun)", loc="left")
    fig.tight_layout(); fig.savefig(f"{out}/ortalama_ga.png", dpi=130); plt.close(fig)
    # 2) boxplot
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bp = ax.boxplot([totals[n] for n in NAMES], tick_labels=[L[n] for n in NAMES], patch_artist=True, widths=0.5,
                    medianprops={"color": "#222", "linewidth": 2}, flierprops={"markersize": 3})
    for patch, n in zip(bp["boxes"], NAMES):
        patch.set_facecolor(COL[n]); patch.set_alpha(0.85); patch.set_edgecolor("white")
    ax.axhline(0, color="#888", lw=0.8)
    ax.tick_params(axis="x", labelsize=9)
    ax.set_title("Standart 101: 100 el sonu toplam puan dağılımı — düşük iyi", loc="left")
    fig.tight_layout(); fig.savefig(f"{out}/puan_dagilimi.png", dpi=130); plt.close(fig)
    # 3) örnek oyun
    g = games[0]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for n in NAMES:
        cum, s = [], 0
        for h in g:
            s += h["scores"][n]; cum.append(s)
        ax.plot(range(1, 101), cum, color=COL[n], lw=2, label=L[n])
        ax.annotate(f" {n}: {cum[-1]}", (100, cum[-1]), fontsize=9, va="center", color="#333")
    ax.axhline(0, color="#888", lw=0.8); ax.set_xlim(1, 112)
    ax.set_xlabel("El"); ax.set_ylabel("Kümülatif puan"); ax.legend(frameon=False, fontsize=9)
    ax.set_title("Standart 101 – örnek oyun (#0): kümülatif puan", loc="left")
    fig.tight_layout(); fig.savefig(f"{out}/ornek_oyun_kumulatif.png", dpi=130); plt.close(fig)
    # 4) el sonuç türleri
    fig, ax = plt.subplots(figsize=(8, 4.5))
    v = [100 * T["kinds"][k] / T["N"] for k in KINDS]
    b = ax.bar([KIND_TR[k] for k in KINDS], v, color="#2a78d6", width=0.6)
    for r, x in zip(b, v):
        ax.text(r.get_x() + r.get_width() / 2, x + 0.5, f"{x:.1f}", ha="center", fontsize=9)
    ax.set_ylabel("Ellerin yüzdesi (%)")
    ax.set_title("Standart 101: el sonuç türleri (100.000 el)", loc="left")
    fig.tight_layout(); fig.savefig(f"{out}/el_sonuc_turleri.png", dpi=130); plt.close(fig)


def tables(P, T):
    L = STD_LABELS
    rows = ["| Oyuncu | Ort. (±%95 GA) | Medyan | Std | Min | Max | 1. % | 2. % | 3. % | 4. % | El başı |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    for n in NAMES:
        p = P[n]
        rows.append(f"| {L[n]} | {p['mean']:.0f} ± {p['ci']:.0f} | {p['median']:.0f} | {p['sd']:.0f} | {p['min']} | {p['max']} | "
                    + " | ".join(f"{r:.1f}" for r in p["rank"]) + f" | {p['hand_mean']:.2f} |")
    rows += ["", "| Oyuncu | Bitirme | Normal | Okeyle | Çift | Çift+okey | Elden | İlk açan | Gösterge (adet / puan) | Açamama %* | Okey cezası (elde kalan okey, çarpanlı) | Katlama ek cezası | +101 cezaları (adet) | Çift açtığı el |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for n in NAMES:
        p = P[n]; f = p["fins"]
        pens = ", ".join(f"{k}:{v}" for k, v in sorted(p["pens"].items())) or "0"
        rows.append(f"| {n} | {p['nfin']} | {f['normal']} | {f['okey']} | {f['cift']} | {f['cift_okey']} | {f['elden']} | {p['first']} | "
                    f"{p['gost_n']} / −{p['bonus']} | {p['unopened']:.1f} | {p['okey_pts']} | {p['mult']} | {sum(p['pens'].values())} ({pens}) | {p['cift_open']} |")
    rows += ["", "\\* Açamama %: biri bitirdiği ve oyuncunun bitirmediği ellerde açamama oranı.", "",
             "| Sonuç türü | El | % |", "|---|---|---|"]
    for k in KINDS:
        rows.append(f"| {KIND_TR[k]} | {T['kinds'][k]} | {100*T['kinds'][k]/T['N']:.2f} |")
    rows += ["", f"- Elde ortalama açamayan kişi (biri bitirdiğinde): **{T['unopened_avg']:.2f}**",
             f"- Elde ortalama açan kişi (tüm eller): **{T['opened_avg']:.2f}**",
             f"- Deste biten ellerin **%{T['deste_nobody']:.1f}**'inde kimse açamamış",
             f"- Ortalama el uzunluğu: **{T['turns']:.2f} hamle**",
             f"- Okey değiştirme: **{T['swap']}** kez"]
    return "\n".join(rows)


def build_all(out="out_std"):
    games = pickle.load(open(f"{out}/raw.pkl", "rb"))
    P, T, totals = compute(games)
    charts(games, P, T, totals, out)
    val_res, val_log = validate()
    pickle.dump({"P": P, "T": T}, open(f"{out}/stats.pkl", "wb"))
    open(f"{out}/tablolar.md", "w").write(tables(P, T) + "\n\n## Doğrulama\n\n"
                                         + ", ".join(r["kind"] for r in val_res) + "\n\n```\n" + "\n".join(val_log) + "\n```\n")
    return P, T
