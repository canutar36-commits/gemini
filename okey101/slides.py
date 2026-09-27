"""rapor sonuçlarından 16:9 PDF sunum üretir: python3 -m okey101.slides"""
import pickle
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from .report import NAMES, LABELS, COL, KINDS, KIND_TR

INK, MUTED, BG, ACC = "#1d2230", "#5b6275", "#ffffff", "#2a78d6"
W, H = 13.333, 7.5
S = pickle.load(open("out/stats.pkl", "rb"))
P50, P20, T50, T20 = S["P50"], S["P20"], S["T50"], S["T20"]
G = 1000


def page(title, subtitle=None, n=[0]):
    n[0] += 1
    fig = plt.figure(figsize=(W, H), facecolor=BG)
    fig.add_artist(plt.Rectangle((0, 0.915), 1, 0.085, color=INK, transform=fig.transFigure))
    fig.text(0.04, 0.955, title, fontsize=24, color="white", weight="bold", va="center")
    if subtitle:
        fig.text(0.04, 0.875, subtitle, fontsize=13, color=MUTED, va="center", style="italic")
    fig.text(0.96, 0.025, f"{n[0]}", fontsize=10, color=MUTED, ha="right")
    fig.text(0.04, 0.025, "101 Okey Monte Carlo · 200.000 el", fontsize=9, color=MUTED)
    return fig


def bullets(fig, items, x=0.04, y=0.82, w=0.42, size=13, gap=0.012):
    chars = int(w * W * 72 / (size * 0.55))
    for it in items:
        sub = it.startswith("  ")
        txt = it.strip()
        lines = textwrap.wrap(txt, chars - (4 if sub else 0))
        fig.text(x + (0.02 if sub else 0), y, "–" if sub else "●", fontsize=size - 3 if not sub else size,
                 color=ACC if not sub else MUTED, va="top")
        for ln in lines:
            fig.text(x + (0.045 if sub else 0.025), y, ln, fontsize=size - (1 if sub else 0),
                     color=INK if not sub else MUTED, va="top")
            y -= size * 1.45 / (H * 72)
        y -= gap
    return y


def img(fig, path, rect):
    ax = fig.add_axes(rect)
    ax.imshow(mpimg.imread(path))
    ax.axis("off")


def style(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#e6e6e6", lw=0.6)
    ax.set_axisbelow(True)


def hbars(ax, vals, fmt="{:.0f}", colors=None):
    b = ax.bar([LABELS[n] for n in NAMES], vals, color=colors or [COL[n] for n in NAMES], width=0.6)
    for r, v in zip(b, vals):
        ax.text(r.get_x() + r.get_width() / 2, r.get_height(), fmt.format(v), ha="center", va="bottom", fontsize=11, color=INK)
    ax.tick_params(axis="x", labelsize=10)
    style(ax)


pdf = PdfPages("sunum.pdf")

# 1 Kapak
fig = plt.figure(figsize=(W, H), facecolor=INK)
fig.text(0.06, 0.62, "101 Okey – Özel Kural Varyantı", fontsize=40, color="white", weight="bold")
fig.text(0.06, 0.52, "Monte Carlo simülasyonu ile kural dengesi ve strateji analizi", fontsize=20, color="#c9d3ea")
fig.text(0.06, 0.36, "4 bot · 1.000 oyun × 100 el × 2 senaryo (OKEY_CEZASI = 50 ve 20) = 200.000 el", fontsize=15, color="#c9d3ea")
fig.text(0.06, 0.30, "Python · seed = 2026 · tamamen tekrarlanabilir", fontsize=13, color="#8f9ab5")
for i, n in enumerate(NAMES):
    fig.add_artist(plt.Rectangle((0.06 + i * 0.22, 0.12), 0.2, 0.08, color=COL[n], transform=fig.transFigure))
    fig.text(0.07 + i * 0.22, 0.16, LABELS[n], fontsize=13, color="white", weight="bold", va="center")
pdf.savefig(fig); plt.close(fig)

# 2 Yönetici özeti
fig = page("Yönetici özeti", "Dört maddede sonuç")
bullets(fig, [
    f"Baskın strateji A (hızlı açan): oyunların %{P50['A']['rank'][0]:.1f}'ini kazanıyor, 100 el sonu ortalama {P50['A']['mean']:.0f} puan (düşük iyi).",
    f"Dengeyi en çok bozan kural açamama cezası (+202). El ortalama {T50['turns']:.1f} hamle sürüyor; bekleyen D ellerin %{P50['D']['unopened']:.1f}'inde açamıyor ve oyunların %{P50['D']['rank'][3]:.1f}'inde sonuncu.",
    "Okey saklamak (B) ve çift oynamak (C) ortalamada A'nın gerisinde kalıyor: B okey cezasıyla, C iki katlı çift cezasıyla puan kaybediyor.",
    "OKEY_CEZASI 50'den 20'ye inince sıralama değişmiyor (A < B < C < D). Okeyle bitirme oranı neredeyse aynı: %3,18'den %3,20'ye.",
], w=0.9, size=16, gap=0.03)
pdf.savefig(fig); plt.close(fig)

# 3 Kurallar
fig = page("Oyun kuralları (özet)", "Simülasyonda eksiksiz uygulanan varyant")
bullets(fig, [
    "106 taş: 1–13, 4 renk, her taştan 2 adet + 2 sahte okey. Gösterge yok.",
    "Tüm 1'ler (8 adet) sabit okey: seri, grup ve çiftte joker, ama sayı olarak 1 kullanılamaz.",
    "Dağıtanın sağındaki oyuncu 22, diğerleri 21 taş alır. Destede sadece 21 taş kalır.",
    "Düz açma: seri + grup toplamı ≥101. Çift açma: en az 5 çift.",
    "Sahte okey yalnızca çiftte joker olur. Düz açan oyuncu (sahte + taş) çiftini başkasının çift alanına işleyebilir.",
    "Okey değiştirme: yalnızca açmış oyuncu, gerçek taşı koyup masadaki okeyi alabilir.",
], w=0.44, size=12)
bullets(fig, [
    "Bitiren: normal −101, okeyle −202, çift −202, çift+okey −404, elden −202.",
    "  İlk açan bitirirse ek −20 (elden bitmede uygulanmaz).",
    "Açamayan: +202 + okey başına OKEY_CEZASI.",
    "Düz açan: elde kalan taşların toplamı + okey cezası.",
    "Çift açan: (taş toplamı + okey cezası) × 2.",
    "Elden bitmede diğerlerine sabit +404. Deste biterse yalnızca okey cezası yazılır.",
    "Ceza hamleleri +101: bitirme dışında okey atmak, işlenebilir taş atmak, yerden alıp açamamak.",
], x=0.52, w=0.44, size=12)
pdf.savefig(fig); plt.close(fig)

# 4 Botlar
fig = page("Dört strateji", "Hepsi kurallara uygun oynayan greedy botlar; fark açma ve okey politikasında")
desc = {
    "A": ["101'e ulaştığı ilk anda açar", "Okeyi saklamaz; fazla okeyi hemen masaya işler", "Hedefi −20 ilk açan bonusu"],
    "B": ["101'de açar", "Bitirmeye ≤3 taş kalınca p_kendi×101 > p_rakip×C ise bir okeyi son taş olarak saklar", "p = 1/(kalan taş + 1)"],
    "C": ["El başında gerçek çift + okey + sahte ≥ 5 ise çift oynar", "≥6 çiftle (deste azsa ≥5 çiftle) açar", "Sahteleri biriktirir; değilse A gibi düz oynar"],
    "D": ["≥121 değer bekler", "Deste ≤8 kalınca 101'e iner (güvenlik payı)", "Okeyi normal perde kullanır, bitirmeye yakın işler"],
}
for i, n in enumerate(NAMES):
    x = 0.04 + i * 0.235
    fig.add_artist(plt.Rectangle((x, 0.72), 0.215, 0.1, color=COL[n], transform=fig.transFigure))
    fig.text(x + 0.012, 0.77, LABELS[n], fontsize=14, color="white", weight="bold", va="center")
    bullets(fig, desc[n], x=x, y=0.68, w=0.2, size=12, gap=0.02)
fig.text(0.04, 0.12, "Ortak altyapı: atılacak taş, pere girmeyen taşlar arasından bağlantı skoruna göre seçilir "
         "(aynı renk ±1/±2, aynı sayı farklı renk). Bitirmeye yakınlık = pere girmeyen taş sayısı.",
         fontsize=12, color=MUTED, wrap=True)
pdf.savefig(fig); plt.close(fig)

# 5 Yöntem
fig = page("Yöntem ve doğrulama", "Çözücü, motor ve kontroller")
bullets(fig, [
    "Per çözücü: memoize edilmiş backtracking. Eldeki taşlar ve okeylerle en iyi seri+grup kombinasyonunu iki modda arar: 'en çok taş' ve 'en yüksek açma değeri'.",
    "Çift çözücü: gerçek çiftler, sonra sahte + tek taş, sonra okey + tek taş, en son okey + okey.",
    "Bitirme denemesi: her aday son taş için (önce okey) elin kalanının tamamen masaya konup konamayacağı kontrol edilir.",
    "Oturma sırası her oyunda rastgele, dağıtan her elde saat yönünde döner. 4 çekirdekte paralel, 1000 oyun ≈ 7 dk.",
], w=0.44, size=12)
bullets(fig, [
    "Her elin sonunda assert'ler (200.000 elin hepsinde):",
    "  Bitirme türü açma türüyle uyumlu; okeyle bitirmede son taş okey",
    "  Bonus yalnızca ilk açana, elden bitmede yok; elden bitmede diğerleri tam +404",
    "  Deste bitince puan = okey × C; açamayanın puanı ≥202",
    "  Çiftlerin geçerliliği (sahte+okey, sahte+sahte yasak)",
    "10 ellik doğrulama koşusu: her hamleden sonra 106 taşın korunumu ve masadaki perlerin geçerliliği kontrol edildi.",
    "Örnek bir elin hamle hamle logu rapor.md'de.",
], x=0.52, w=0.44, size=12)
pdf.savefig(fig); plt.close(fig)

# 6 Sıralama
fig = page("Sonuç: strateji sıralaması", "OKEY_CEZASI = 50 · 1.000 oyun · 100 el sonu toplam puan (düşük iyi)")
ax = fig.add_axes([0.06, 0.12, 0.4, 0.68])
hbars(ax, [P50[n]["mean"] for n in NAMES])
ax.set_title("Ortalama toplam puan", loc="left", fontsize=13, color=INK)
ax2 = fig.add_axes([0.55, 0.12, 0.4, 0.68])
bottom = [0] * 4
shades = ["#1baf7a", "#8fd3b8", "#f2b8a0", "#e34948"]
for r in range(4):
    vals = [P50[n]["rank"][r] for n in NAMES]
    ax2.bar(NAMES, vals, bottom=bottom, color=shades[r], width=0.6, edgecolor="white", linewidth=2, label=f"{r+1}.")
    for i, v in enumerate(vals):
        if v > 6:
            ax2.text(i, bottom[i] + v / 2, f"%{v:.0f}", ha="center", va="center", fontsize=10, color=INK)
    bottom = [b + v for b, v in zip(bottom, vals)]
ax2.set_title("Bitiriş sırası dağılımı (%)", loc="left", fontsize=13, color=INK)
ax2.legend(ncol=4, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.06))
style(ax2)
pdf.savefig(fig); plt.close(fig)

# 7 Dağılım
fig = page("Puan dağılımı ve oynaklık", "Oyunlar arası standart sapma ≈ 1.100 puan")
img(fig, "out/puan_dagilimi.png", [0.02, 0.08, 0.58, 0.78])
bullets(fig, [
    "Kutular çeyrekler arası aralığı, çizgi medyanı gösteriyor.",
    f"A'nın medyanı {P50['A']['median']:.0f}, D'ninki {P50['D']['median']:.0f}. D'nin kutusu diğerleriyle neredeyse hiç örtüşmüyor.",
    "B ve C birbirine çok yakın: ortalama farkı ~170 puan, standart hatanın (~50) birkaç katı.",
    "Uç değerlerin kaynağı tek tük elden bitmeler (diğerlerine +404) ve okey cezası birikmesi.",
    "Tek bir oyunda A bile %13 ihtimalle 3. ya da 4. oluyor. Sıralama ancak birçok oyunda netleşiyor.",
], x=0.62, y=0.8, w=0.35, size=12)
pdf.savefig(fig); plt.close(fig)

# 8 Örnek oyun
fig = page("Örnek oyun: 100 el boyunca", "Oyun #0 (C=50) kümülatif puan")
img(fig, "out/ornek_oyun_kumulatif.png", [0.02, 0.08, 0.58, 0.78])
bullets(fig, [
    "D (temkinli) erken ellerde birkaç kez açamayıp +202 yiyor ve fark 20. elden sonra hızla açılıyor.",
    "A ve C uzun süre başa baş gidiyor; C çift bitirdiği ellerde (−202) sıçrama yapıyor.",
    "60.–80. eller arasındaki düşüşler bitirilen ellerin etkisi: tek bir −121 (bitirme + bonus) bile sırayı değiştirebiliyor.",
    "Bu oyunun galibi C, ama 1000 oyunun ortalamasında A önde. Tek oyun yanıltıcı olabilir.",
], x=0.62, y=0.8, w=0.35, size=12)
pdf.savefig(fig); plt.close(fig)

# 9 El sonuç türleri
fig = page("El sonuç türleri", "Masa geneli · 100.000 el / senaryo")
img(fig, "out/el_sonuc_turleri.png", [0.02, 0.08, 0.58, 0.78])
k = T50["kinds"]
bullets(fig, [
    f"100 elin ~{100*k['normal']/T50['N']:.0f}'i normal bitiriyor. Okeyle bitirme %{100*k['okey']/T50['N']:.1f}, çift %{100*k['cift']/T50['N']:.1f}, elden %{100*k['elden']/T50['N']:.1f}.",
    f"Çift+okey (−404) yalnızca {k['cift_okey']} kez oldu, pratikte ölü bir kural.",
    f"Deste yalnızca %{100*k['deste']/T50['N']:.1f} elde tükeniyor. Kısa desteye rağmen botlar neredeyse her elde bitiriyor.",
    f"Ortalama el uzunluğu {T50['turns']:.1f} hamle; normal bitişli bir elde ortalama {T50['unopened_avg']:.2f} kişi açamıyor.",
    "İki ceza değerinde dağılım neredeyse aynı: okey cezası el akışını değil, yalnızca puanlamayı etkiliyor.",
], x=0.62, y=0.8, w=0.35, size=12)
pdf.savefig(fig); plt.close(fig)

# 10 Açamama cezası
fig = page("Kırılma noktası: açamama cezası (+202)", "21 taşlık destede beklemek pahalı")
ax = fig.add_axes([0.06, 0.12, 0.42, 0.66])
hbars(ax, [P50[n]["unopened"] for n in NAMES], fmt="%{:.1f}")
ax.set_title("Bitiremediği ellerde açamama oranı", loc="left", fontsize=13, color=INK)
est = (P50["D"]["unopened"] - P50["A"]["unopened"]) / 100 * 202 * 75
bullets(fig, [
    f"D, 121 beklediği için ellerin %{P50['D']['unopened']:.1f}'inde açamıyor; A'da bu oran %{P50['A']['unopened']:.1f}.",
    f"Kaba hesap: oran farkı × 202 × ~75 bitiremediği el ≈ oyun başına +{est:,.0f} puan.".replace(",", "."),
    f"D'nin A'ya toplam açığı {P50['D']['mean']-P50['A']['mean']:,.0f} puan; bunun üçte ikiye yakını bu tek kuraldan.".replace(",", "."),
    "Neden? Dağıtımdan sonra destede 106 − 85 = 21 taş kalıyor. Her oyuncu elde ~5 taş çekebiliyor. Güvenlik payı bekleyenin zamanı yok.",
    "Öneri: açamama cezasını düşürmek (ör. +101) ya da destede daha fazla taş bırakmak.",
], x=0.54, y=0.8, w=0.42, size=12)
pdf.savefig(fig); plt.close(fig)

# 11 Bonus
fig = page("İlk açan bonusu (−20): küçük etki", "Bonus puanı, oyun başına")
ax = fig.add_axes([0.06, 0.12, 0.42, 0.66])
hbars(ax, [P50[n]["bonus"] / G for n in NAMES])
ax.set_title("Oyun başına kazanılan bonus puanı", loc="left", fontsize=13, color=INK)
bullets(fig, [
    f"A ilk açan olduğu {P50['A']['first']/G:.1f} elin (oyun başına) {P50['A']['bonus_n']/G:.1f}'inde bitirip bonusu alıyor.",
    f"A ile D arasındaki bonus farkı oyun başına yalnızca ~{(P50['A']['bonus']-P50['D']['bonus'])/G:.0f} puan.",
    "Yani A'yı öne çıkaran bonus değil: erken açarak +202'den kaçması ve daha çok bitirmesi.",
    f"Bitirme sayıları: A {P50['A']['nfin']:,}, B {P50['B']['nfin']:,}, C {P50['C']['nfin']:,}, D {P50['D']['nfin']:,} (100.000 elde).".replace(",", "."),
    "Bonusun stratejik ağırlığı istenirse −50 gibi daha anlamlı bir değer denenebilir.",
], x=0.54, y=0.8, w=0.42, size=12)
pdf.savefig(fig); plt.close(fig)

# 12 Okey saklama
fig = page("Okey saklamak (B) neden zarar ediyor?", "B'nin A'ya göre farkı, oyun başına puan (C=50)")
gain = -(P50["B"]["fins"]["okey"] - P50["A"]["fins"]["okey"]) * 101 / G
okc = (P50["B"]["okey_pts"] - P50["A"]["okey_pts"]) / G
pen = P50["B"]["pens"]["okey_atma"] * 101 / G
ax = fig.add_axes([0.06, 0.12, 0.42, 0.66])
labels = ["Ek okeyle\nbitirme", "Ek okey\ncezası", "Zorunlu okey\natma (+101)", "Net"]
vals = [gain, okc, pen, gain + okc + pen]
cols = ["#1baf7a", "#e34948", "#e34948", COL["B"]]
b = ax.bar(labels, vals, color=cols, width=0.6)
for r, v in zip(b, vals):
    ax.text(r.get_x() + r.get_width() / 2, v, f"{v:+.0f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=11)
ax.axhline(0, color="#888", lw=0.8)
ax.set_title("Kazanç (−) ve kayıp (+)", loc="left", fontsize=13, color=INK)
style(ax)
bullets(fig, [
    f"B okeyle bitirmeyi A'nın ~5 katı yapıyor ({P50['B']['fins']['okey']:,} / {P50['A']['fins']['okey']}): oyun başına {gain:.0f} puan kazanç.".replace(",", "."),
    f"Ama rakip bitirdiğinde elde kalan okey cezası oyun başına {okc:.0f} puan fazla.",
    f"Başka taşı kalmayınca sakladığı okeyi atmak zorunda kalıp {P50['B']['pens']['okey_atma']} kez +101 yiyor.",
    f"Net: oyun başına ~{gain+okc+pen:+.0f} puan. B'nin A'ya olan açığının ~%40'ı.",
    "Karar formülü rakip bitirme olasılığını hafife alıyor: el kısa, rakipler hızlı bitiriyor.",
], x=0.54, y=0.8, w=0.42, size=12)
pdf.savefig(fig); plt.close(fig)

# 13 Çift
fig = page("Çift oynamak (C): yüksek risk, düşük getiri", "C'nin çift açtığı eller ve sonuçları (C=50)")
ax = fig.add_axes([0.06, 0.12, 0.42, 0.66])
co = P50["C"]["cift_open"]; cf = P50["C"]["fins"]["cift"]; cfo = P50["C"]["fins"]["cift_okey"]
vals = [co, cf + cfo, cfo]
b = ax.bar(["Çift açtı", "Çift bitirdi", "Çift + okeyle\nbitirdi"], vals, color=[COL["C"], "#8fd3b8", "#eda100"], width=0.6)
for r, v in zip(b, vals):
    ax.text(r.get_x() + r.get_width() / 2, v, f"{v:,}".replace(",", "."), ha="center", va="bottom", fontsize=11)
ax.set_title("El sayısı (100.000 elde)", loc="left", fontsize=13, color=INK)
style(ax)
bullets(fig, [
    f"C {co:,} elde çift açıyor, yalnızca {cf+cfo:,}'inde (%{100*(cf+cfo)/co:.0f}) çift bitiriyor.".replace(",", "."),
    "Bitiremediği ellerde kalan taşlar ve okey cezası iki katı yazılıyor.",
    "21 taşı tamamen çiftlere bölmek zor. Seri/gruplara işleme hakkı bunu kısmen hafifletiyor.",
    f"Çift+okey (−404) {cfo} kez oldu: en büyük ödül pratikte ulaşılamaz.",
    f"Sonuç: C ortalamada B ile başa baş ({P50['C']['mean']:.0f} / {P50['B']['mean']:.0f}), A'nın gerisinde.",
], x=0.54, y=0.8, w=0.42, size=12)
pdf.savefig(fig); plt.close(fig)

# 14 C=20 vs 50
fig = page("Karşılaştırma: OKEY_CEZASI = 50 ve 20", "Sıralama değişiyor mu?")
ax = fig.add_axes([0.06, 0.12, 0.42, 0.66])
w = 0.38
x = range(4)
b1 = ax.bar([i - w / 2 - 0.01 for i in x], [P50[n]["mean"] for n in NAMES], w, color="#2a78d6", label="C = 50")
b2 = ax.bar([i + w / 2 + 0.01 for i in x], [P20[n]["mean"] for n in NAMES], w, color="#eb6834", label="C = 20")
for bb in (b1, b2):
    for r in bb:
        ax.text(r.get_x() + r.get_width() / 2, r.get_height(), f"{r.get_height():.0f}", ha="center", va="bottom", fontsize=9)
ax.set_xticks(list(x)); ax.set_xticklabels([LABELS[n] for n in NAMES], fontsize=9)
ax.legend(frameon=False); ax.set_title("Ortalama 100 el sonu puan", loc="left", fontsize=13, color=INK)
style(ax)
ok50 = 100 * (T50["kinds"]["okey"] + T50["kinds"]["cift_okey"]) / T50["N"]
ok20 = 100 * (T20["kinds"]["okey"] + T20["kinds"]["cift_okey"]) / T20["N"]
bullets(fig, [
    "Sıralama aynı: A < B < C < D.",
    f"Okeyle bitirme oranı: %{ok50:.2f} → %{ok20:.2f}. B'nin okeyle bitirmesi {P50['B']['fins']['okey']:,} → {P20['B']['fins']['okey']:,}.".replace(",", "."),
    f"A'nın kazanma oranı %{P50['A']['rank'][0]:.1f} → %{P20['A']['rank'][0]:.1f}; B'nin A'ya açığı {P50['B']['mean']-P50['A']['mean']:.0f} → {P20['B']['mean']-P20['A']['mean']:.0f} puan.",
    f"B'nin yediği okey cezası oyun başına {P50['B']['okey_pts']/G:.0f} → {P20['B']['okey_pts']/G:.0f}.",
    "Yorum: 20–50 aralığında okey cezası stratejiyi değil, yalnızca farkların büyüklüğünü belirliyor.",
], x=0.54, y=0.8, w=0.42, size=12)
pdf.savefig(fig); plt.close(fig)

# 15 Masa geneli
fig = page("Masa geneli göstergeler", "OKEY_CEZASI = 50 · 100.000 el")
tiles = [
    (f"{T50['turns']:.1f}", "ortalama el uzunluğu (hamle)"),
    (f"{T50['unopened_avg']:.2f}", "elde ortalama açamayan kişi"),
    (f"{T50['swap']:,}".replace(",", "."), "okey değiştirme (el başına ~1,8)"),
    (f"{T50['fake']:,}".replace(",", "."), "sahte okey özel işleme"),
    (f"%{100*T50['kinds']['elden']/T50['N']:.1f}", "elden bitme (diğerlerine +404)"),
    (f"%{100*T50['kinds']['deste']/T50['N']:.1f}", "deste bitti"),
]
for i, (v, l) in enumerate(tiles):
    x = 0.05 + (i % 3) * 0.31
    y = 0.5 if i < 3 else 0.14
    fig.add_artist(plt.Rectangle((x, y), 0.28, 0.3, color="#f3f5f9", transform=fig.transFigure))
    fig.text(x + 0.02, y + 0.17, v, fontsize=34, color=INK, weight="bold")
    fig.text(x + 0.02, y + 0.07, l, fontsize=13, color=MUTED)
pdf.savefig(fig); plt.close(fig)

# 16 Sonuç
fig = page("Sonuçlar ve öneriler")
bullets(fig, [
    "Bu kural setinde en iyi strateji: mümkün olan ilk anda 101 ile aç, okeyi elde tutma.",
    "Dengeyi en çok belirleyen iki parametre: kısa deste (21 taş) ve +202 açamama cezası. Birlikte temkinli oyunu cezalandırıyorlar.",
    "Okey cezası (20–50) sıralamayı değiştirmiyor; okey saklama stratejisinin maliyetini ölçekliyor.",
    "Çift açma ve çift+okey ödülleri kâğıt üzerinde büyük, ama gerçekleşme olasılığı düşük.",
    "Denge önerileri:",
    "  Açamama cezasını +101'e indirmek ya da daha az taş dağıtıp desteyi uzatmak",
    "  İlk açan bonusunu artırmak (ör. −50), böylece erken açma daha görünür biçimde ödüllendirilir",
    "  Çift açma eşiğini 4'e indirmek ya da çift cezası çarpanını ×1,5'e düşürmek",
    "  Her öneri aynı simülatörle tek parametre değiştirilerek test edilebilir.",
], w=0.9, size=15, gap=0.02)
pdf.savefig(fig); plt.close(fig)

# 17 Varsayımlar
fig = page("Varsayımlar ve sınırlar", "Ayrıntılı liste rapor.md'de")
bullets(fig, [
    "Yalnızca bir önceki oyuncunun son attığı taş yerden alınabilir. Alınan taşın açmada kullanılması zorunlu tutulmadı, sadece o turda açma şartı var.",
    "Açma tek hamlede, tek türde yapılır. Açılan turda işleme yapılmaz. Açma + bitirme aynı hamlede olabilir; masada kimse açmamışsa bu elden sayılır.",
    "Düz açan yeni per koyabilir. Çift açan yeni çift koyar ve seri/gruplara tek taş işler, ama yeni seri/grup açamaz.",
    "Gruptaki okey eksik renklerden ilkini temsil eder. Aynı renkten iki 1 de iki okey sayılır; okey + okey geçerli bir çift.",
], w=0.44, size=12)
bullets(fig, [
    "İşlenebilir taş cezası herkese uygulanır (bitirme hamlesi hariç). Çift alanı işlenebilirliğe dahil değil.",
    "Elde kalan okey sayı toplamına 0 olarak girer; sahte 0 sayılır.",
    "'Başka ceza eklenmez' ve 'SADECE' harfiyen uygulandı: deste bittiğinde ve elden bitmede +101'ler puana yazılmıyor.",
    "Botlar yalnızca açabileceklerinde yerden alıyor, bu yüzden 'yerden alıp açamama' cezası hiç oluşmadı.",
    "Botlar greedy. Gerçek oyuncuların hafıza, rakip okuma ve blöf gibi davranışları modellenmedi.",
], x=0.52, w=0.44, size=12)
pdf.savefig(fig); plt.close(fig)

pdf.close()
print("sunum.pdf hazır")
