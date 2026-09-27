"""İstatistikler, grafikler ve rapor.md üretimi."""
import statistics as st
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAMES = ["A", "B", "C", "D"]
LABELS = {"A": "A – Hızlı açan", "B": "B – Okey saklayan", "C": "C – Çift oyuncusu", "D": "D – Temkinli"}
COL = {"A": "#2a78d6", "B": "#eb6834", "C": "#1baf7a", "D": "#eda100"}
KINDS = ["normal", "okey", "cift", "cift_okey", "elden", "deste"]
KIND_TR = {"normal": "Normal", "okey": "Okeyle", "cift": "Çift", "cift_okey": "Çift+okey",
           "elden": "Elden", "deste": "Deste bitti"}
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": "#e6e6e6", "grid.linewidth": 0.6})


def stats(games):
    hands = [h for g in games for h in g]
    N = len(hands)
    totals = {n: [sum(h["scores"][n] for h in g) for g in games] for n in NAMES}
    ranks = {n: Counter() for n in NAMES}
    for gi in range(len(games)):
        sc = {n: totals[n][gi] for n in NAMES}
        for n in NAMES:
            ranks[n][1 + sum(1 for m in NAMES if sc[m] < sc[n])] += 1  # beraberlikte paylaşılan sıra
    P = {}
    for n in NAMES:
        fins = Counter(h["kind"] for h in hands if h["fin"] == n)
        pens = Counter(p for h in hands for p in h["pens"][n])
        P[n] = {
            "mean": st.mean(totals[n]), "median": st.median(totals[n]), "sd": st.pstdev(totals[n]),
            "min": min(totals[n]), "max": max(totals[n]),
            "rank": [100 * ranks[n][r] / len(games) for r in (1, 2, 3, 4)],
            "fins": fins, "nfin": sum(fins.values()),
            "first": sum(1 for h in hands if h["first"] == n),
            "bonus": -sum(h["bonus"][n] for h in hands),
            "bonus_n": sum(1 for h in hands if h["bonus"][n]),
            "unopened": 100 * sum(1 for h in hands if h["kind"] != "deste" and h["fin"] != n and h["opened"][n] is None)
                        / max(1, sum(1 for h in hands if h["kind"] != "deste" and h["fin"] != n)),
            "okey_pts": sum(h["okey_pts"][n] for h in hands),
            "pens": pens, "pen_pts": sum(h["pen_pts"][n] for h in hands),
            "cift_open": sum(1 for h in hands if h["opened"][n] == "cift"),
            "hand_mean": st.mean(h["scores"][n] for h in hands),
        }
    kinds = Counter(h["kind"] for h in hands)
    nonfin = [h for h in hands if h["kind"] not in ("deste", "elden")]
    T = {
        "N": N, "kinds": kinds,
        "unopened_avg": st.mean(sum(1 for n in NAMES if h["opened"][n] is None) for h in nonfin),
        "turns": st.mean(h["turns"] for h in hands),
        "fake": sum(h["fake"] for h in hands), "swap": sum(h["swap"] for h in hands),
    }
    return P, T, totals


def charts(data, out="out"):
    P50, T50, tot50 = stats(data[50])
    # 1) boxplot
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bp = ax.boxplot([tot50[n] for n in NAMES], tick_labels=[LABELS[n] for n in NAMES], patch_artist=True,
                    widths=0.5, medianprops={"color": "#222", "linewidth": 2}, flierprops={"markersize": 3})
    for patch, n in zip(bp["boxes"], NAMES):
        patch.set_facecolor(COL[n]); patch.set_alpha(0.85); patch.set_edgecolor("white")
    ax.axhline(0, color="#888", lw=0.8)
    ax.set_title("100 el sonu toplam puan dağılımı (OKEY_CEZASI=50, 1000 oyun) — düşük iyi", loc="left")
    ax.set_ylabel("Toplam puan")
    fig.tight_layout(); fig.savefig(f"{out}/puan_dagilimi.png", dpi=130); plt.close(fig)
    # 2) örnek oyun kümülatif
    g = data[50][0]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for n in NAMES:
        cum, s = [], 0
        for h in g:
            s += h["scores"][n]; cum.append(s)
        ax.plot(range(1, len(cum) + 1), cum, color=COL[n], lw=2, label=LABELS[n])
        ax.annotate(f" {n}: {cum[-1]}", (len(cum), cum[-1]), color="#333", fontsize=9, va="center")
    ax.axhline(0, color="#888", lw=0.8)
    ax.set_xlabel("El"); ax.set_ylabel("Kümülatif puan")
    ax.set_title("Örnek oyun (oyun #0, C=50): kümülatif puan", loc="left")
    ax.legend(frameon=False); ax.set_xlim(1, 112)
    fig.tight_layout(); fig.savefig(f"{out}/ornek_oyun_kumulatif.png", dpi=130); plt.close(fig)
    # 3) el sonuç türleri (C=50 vs C=20)
    P20, T20, _ = stats(data[20])
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = range(len(KINDS)); w = 0.38
    v50 = [100 * T50["kinds"][k] / T50["N"] for k in KINDS]
    v20 = [100 * T20["kinds"][k] / T20["N"] for k in KINDS]
    b1 = ax.bar([i - w / 2 - 0.01 for i in x], v50, w, color=COL["A"], label="OKEY_CEZASI=50")
    b2 = ax.bar([i + w / 2 + 0.01 for i in x], v20, w, color=COL["B"], label="OKEY_CEZASI=20")
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.5, f"{b.get_height():.1f}", ha="center", fontsize=8)
    ax.set_xticks(list(x)); ax.set_xticklabels([KIND_TR[k] for k in KINDS])
    ax.set_ylabel("Ellerin yüzdesi (%)"); ax.legend(frameon=False)
    ax.set_title("El sonuç türleri (100.000 el / senaryo)", loc="left")
    fig.tight_layout(); fig.savefig(f"{out}/el_sonuc_turleri.png", dpi=130); plt.close(fig)
    return (P50, T50), (P20, T20)


def player_table(P):
    L = ["| Oyuncu | Ort. | Medyan | Std | Min | Max | 1. % | 2. % | 3. % | 4. % | El başı ort. |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for n in NAMES:
        p = P[n]
        L.append(f"| {LABELS[n]} | {p['mean']:.0f} | {p['median']:.0f} | {p['sd']:.0f} | {p['min']} | {p['max']} | "
                 + " | ".join(f"{r:.1f}" for r in p["rank"]) + f" | {p['hand_mean']:.1f} |")
    L += ["", "| Oyuncu | Bitirme | Normal | Okeyle | Çift | Çift+okey | Elden | İlk açan (el) | Bonus alınan el | Bonus puanı | Açamama % | Okey cezası (toplam) | +101 cezaları (adet / puan) | Çift açtığı el |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for n in NAMES:
        p = P[n]; f = p["fins"]
        pens = ", ".join(f"{k}:{v}" for k, v in sorted(p["pens"].items())) or "0"
        L.append(f"| {n} | {p['nfin']} | {f['normal']} | {f['okey']} | {f['cift']} | {f['cift_okey']} | {f['elden']} | "
                 f"{p['first']} | {p['bonus_n']} | −{p['bonus']} | {p['unopened']:.1f} | {p['okey_pts']} | "
                 f"{sum(p['pens'].values())} ({pens}) / {p['pen_pts']} | {p['cift_open']} |")
    return "\n".join(L)


def table_general(T):
    L = ["| Sonuç türü | El | % | 100 elde |", "|---|---|---|---|"]
    for k in KINDS:
        L.append(f"| {KIND_TR[k]} | {T['kinds'][k]} | {100*T['kinds'][k]/T['N']:.2f} | {100*T['kinds'][k]/T['N']:.1f} |")
    L += ["", f"- Toplam el: **{T['N']}**",
          f"- Elde ortalama açamayan kişi sayısı (normal/okey/çift bitişli ellerde): **{T['unopened_avg']:.2f}**",
          f"- Ortalama el uzunluğu: **{T['turns']:.2f} tur** (bir tur = bir oyuncunun hamlesi)",
          f"- Sahte okey özel işleme kuralı kullanımı: **{T['fake']}** kez",
          f"- Okey değiştirme kullanımı: **{T['swap']}** kez"]
    return "\n".join(L)


def build(data, val_res, val_log, n_games, out="out"):
    (P50, T50), (P20, T20) = charts(data, out)
    ctx = {"P50": P50, "T50": T50, "P20": P20, "T20": T20, "n_games": n_games,
           "val_res": val_res, "val_log": val_log}
    import pickle
    with open(f"{out}/stats.pkl", "wb") as f:
        pickle.dump(ctx, f)
    with open(f"{out}/tablolar.md", "w") as f:
        for C, P, T in ((50, P50, T50), (20, P20, T20)):
            f.write(f"## OKEY_CEZASI={C}\n\n{player_table(P)}\n\n{table_general(T)}\n\n")
        f.write("## Doğrulama\n\n" + ", ".join(r["kind"] for r in val_res) + "\n\n```\n" + "\n".join(val_log) + "\n```\n")
