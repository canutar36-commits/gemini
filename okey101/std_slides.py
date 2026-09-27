"""Standart 101 sonuçlarından 16:9 PDF sunum: python3 -m okey101.std_slides"""
import pickle
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from .report import NAMES, COL, KINDS, KIND_TR
from .std_report import STD_LABELS

INK, MUTED, BG, ACC = "#1d2230", "#5b6275", "#ffffff", "#2a78d6"
W, H = 13.333, 7.5
S = pickle.load(open("out_std/stats.pkl", "rb"))
P, T = S["P"], S["T"]
G = 1000
LABELS = STD_LABELS
SHORT = {n: l.replace(" – ", "\n") for n, l in STD_LABELS.items()}


def page(title, subtitle=None, n=[0]):
    n[0] += 1
    fig = plt.figure(figsize=(W, H), facecolor=BG)
    fig.add_artist(plt.Rectangle((0, 0.915), 1, 0.085, color=INK, transform=fig.transFigure))
    fig.text(0.04, 0.955, title, fontsize=24, color="white", weight="bold", va="center")
    if subtitle:
        fig.text(0.04, 0.875, subtitle, fontsize=13, color=MUTED, va="center", style="italic")
    fig.text(0.96, 0.025, f"{n[0]}", fontsize=10, color=MUTED, ha="right")
    fig.text(0.04, 0.025, "Standart 101 Okey · Monte Carlo · 100.000 el", fontsize=9, color=MUTED)
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
    b = ax.bar([SHORT[n] for n in NAMES], vals, color=colors or [COL[n] for n in NAMES], width=0.6)
    for r, v in zip(b, vals):
        ax.text(r.get_x() + r.get_width() / 2, r.get_height(), fmt.format(v), ha="center", va="bottom", fontsize=11, color=INK)
    ax.tick_params(axis="x", labelsize=10)
    style(ax)


def tr(x, d=0):
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


pdf = PdfPages("sunum_standart.pdf")
k = T["kinds"]
N = T["N"]
A, B, C, D = (P[n] for n in NAMES)

# 1 Kapak
fig = plt.figure(figsize=(W, H), facecolor=INK)
fig.text(0.06, 0.62, "Standart 101 Okey", fontsize=44, color="white", weight="bold")
fig.text(0.06, 0.52, "Neredeyse aynı oynayan 4 karakter: olasılıklar ve küçük nüansların bedeli", fontsize=20, color="#c9d3ea")
fig.text(0.06, 0.36, "1.000 oyun × 100 el = 100.000 el · seed = 2026 · tamamen tekrarlanabilir", fontsize=15, color="#c9d3ea")
for i, n in enumerate(NAMES):
    fig.add_artist(plt.Rectangle((0.06 + i * 0.22, 0.12), 0.2, 0.08, color=COL[n], transform=fig.transFigure))
    fig.text(0.07 + i * 0.22, 0.16, SHORT[n], fontsize=11, color="white", weight="bold", va="center")
pdf.savefig(fig); plt.close(fig)

# 2 Özet
fig = page("Yönetici özeti", "Beş maddede sonuç")
bullets(fig, [
    f"Standart 101 büyük ölçüde şans oyunu: bir oyunun puan sapması ~{A['sd']:.0f}, en iyi ve en kötü bot farkı ~{B['mean']-A['mean']:.0f} puan.",
    f"En iyi davranış 101'e ulaşınca hemen açmak: A {A['mean']:.0f} ± {A['ci']:.0f} ile önde, ama masayı yalnızca %{tr(A['rank'][0],1)} ihtimalle kazanıyor (şansa göre %25).",
    f"En pahalı nüans 10 puan fazladan beklemek: B oyun başına ~{B['mean']-A['mean']:.0f} puan geride, oyunların %{tr(B['rank'][3],1)}'inde sonuncu.",
    f"Okeyi son taşa saklamak da zarar: D okeyle bitirmeyi A'nın ~{D['fins']['okey']/A['fins']['okey']:.1f} katı yapıyor ama ~{D['mean']-A['mean']:.0f} puan geride.",
    f"Ellerin %{tr(100*k['normal']/N,1)}'i normal bitiyor, %{tr(100*k['deste']/N,1)}'inde deste tükeniyor. El ortalama {tr(T['turns'],1)} hamle.",
], w=0.9, size=15, gap=0.03)
pdf.savefig(fig); plt.close(fig)

# 3 Kurallar
fig = page("Uygulanan standart kurallar", "Yaygın oynanan 101 · ev kuralına göre değişen noktalar son sayfada")
bullets(fig, [
    "106 taş; gösterge açılır. Okey = göstergenin aynı renkte bir üstü (13'ün üstü 1).",
    "2 okey her perde joker. Sahte okey, okey taşının kendisi yerine geçen normal bir taştır.",
    "1 hem 1-2-3'te hem 12-13-1'de kullanılır; 13-1-2 yok.",
    "Dağıtım 22 / 21 / 21 / 21; destede 20 taş kalır.",
    "Açma: seri + grup ≥101 ya da en az 5 çift. Açan her pere işler, okey değiştirebilir.",
    "Göstergenin eşini ilk turunda gösteren −101 alır.",
], w=0.44, size=12.5)
bullets(fig, [
    "Bitiren: normal −101 · okeyle −202 (diğerleri ×2) · çift −202 (×2) · çift + okey −404 (×4) · elden −202 (×2).",
    "Açamayan 202. Düz açan: kalan taş toplamı + elde kalan okey başına 101. Çift açan: bunun ×2'si. Katsayı üstüne uygulanır.",
    "+101 ceza: yerden alıp açamamak, işlenebilir taş atmak, bitirme dışında okey atmak.",
    "Deste biterse el puansız kapanır; yalnızca cezalar ve gösterge yazılır.",
    "İlk açan bonusu yok.",
], x=0.52, w=0.44, size=12.5)
pdf.savefig(fig); plt.close(fig)

# 4 Botlar
fig = page("Dört benzer karakter", "Aynı çekirdek, tek nüans")
desc = {
    "A": ["101'e ulaştığı ilk anda açar", "Referans oyuncu: ortak çekirdeğin saf hali"],
    "B": ["Açmak için 111 bekler", "Deste ≤8 kalınca 101'e iner", "Yalnızca 10 puanlık güvenlik payı"],
    "C": ["Başlangıçta çift + okey ≥6 ise çifte oynar", "Bu, ellerin ~%1'inde olur; kalan ellerde A ile aynı"],
    "D": ["Bitirmeye ≤2 taş kala bir okeyi son taşa saklar", "Fazla okeyi masaya işlemez", "Hedef: okeyle bitirip rakipleri ×2 yazdırmak"],
}
for i, n in enumerate(NAMES):
    x = 0.04 + i * 0.235
    fig.add_artist(plt.Rectangle((x, 0.72), 0.215, 0.1, color=COL[n], transform=fig.transFigure))
    fig.text(x + 0.01, 0.77, LABELS[n], fontsize=11.5, color="white", weight="bold", va="center")
    bullets(fig, desc[n], x=x, y=0.68, w=0.2, size=12, gap=0.02)
fig.text(0.04, 0.14, "Ortak çekirdek: aynı per çözücü (en çok taş / en yüksek değer), aynı atılacak taş sezgisi (bağlantı skoru),", fontsize=12, color=MUTED)
fig.text(0.04, 0.10, "aynı yerden alma kuralı (yalnızca o tur açabilecekse). Botların hepsi kurallara uygun oynar.", fontsize=12, color=MUTED)
pdf.savefig(fig); plt.close(fig)

# 5 Sıralama
fig = page("Sonuç: ortalama puan ve güven aralıkları", "1.000 oyun · 100 el sonu toplam puan (düşük iyi) · hata çubukları %95 güven aralığı")
img(fig, "out_std/ortalama_ga.png", [0.02, 0.08, 0.58, 0.78])
bullets(fig, [
    f"A ({A['mean']:.0f}) ile C ({C['mean']:.0f}) arasındaki fark güven aralıklarının içinde: istatistiksel olarak başa baş.",
    f"D ({D['mean']:.0f}) A'dan anlamlı biçimde kötü: fark ~{D['mean']-A['mean']:.0f}, aralıklar örtüşmüyor.",
    f"B (+{B['mean']:.0f}) açık ara sonuncu: A'ya göre ~{B['mean']-A['mean']:.0f} puan fark.",
    f"Ortalamaların sıfırın altında olması gösterge puanından: her oyuncu oyun başına ~{A['gost_n']/G:.0f} kez −101 alıyor.",
], x=0.62, y=0.8, w=0.35, size=12)
pdf.savefig(fig); plt.close(fig)

# 6 Şans
fig = page("Şans mı beceri mi?", "Tek bir oyunun sonucu büyük ölçüde şansa bağlı")
ax2 = fig.add_axes([0.06, 0.14, 0.42, 0.64])
bottom = [0] * 4
shades = ["#1baf7a", "#8fd3b8", "#f2b8a0", "#e34948"]
for r in range(4):
    vals = [P[n]["rank"][r] for n in NAMES]
    ax2.bar(NAMES, vals, bottom=bottom, color=shades[r], width=0.6, edgecolor="white", linewidth=2, label=f"{r+1}.")
    for i, v in enumerate(vals):
        if v > 6:
            ax2.text(i, bottom[i] + v / 2, f"%{v:.0f}", ha="center", va="center", fontsize=10, color=INK)
    bottom = [b + v for b, v in zip(bottom, vals)]
ax2.axhline(25, color="#333", lw=0.8, ls="--")
ax2.set_title("Bitiriş sırası dağılımı (%) · kesikli çizgi = şans (%25)", loc="left", fontsize=12, color=INK)
ax2.legend(ncol=4, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.06))
style(ax2)
bullets(fig, [
    f"En iyi bot A bile oyunların yalnızca %{tr(A['rank'][0],1)}'ini kazanıyor ve %{tr(A['rank'][3],1)}'inde sonuncu oluyor.",
    f"Bir oyunun puan sapması (~{A['sd']:.0f}), botlar arasındaki en büyük ortalama farktan (~{B['mean']-A['mean']:.0f}) büyük.",
    "Sonuç: doğru oynamanın avantajı ancak onlarca oyunda belirginleşiyor. Tek oyunda kötü oynayan da kazanabiliyor.",
    f"B'nin bile kazanma şansı %{tr(B['rank'][0],1)}. Sabırlı olmak oyunu kaybettirmiyor, ama uzun vadede açıkça zarar ettiriyor.",
], x=0.54, y=0.8, w=0.42, size=12)
pdf.savefig(fig); plt.close(fig)

# 7 Dağılım
fig = page("Puan dağılımı", "100 el sonu toplam puan, 1.000 oyun")
img(fig, "out_std/puan_dagilimi.png", [0.02, 0.08, 0.58, 0.78])
bullets(fig, [
    "Dört kutu büyük ölçüde üst üste biniyor: botlar gerçekten birbirine benziyor.",
    f"Medyanlar: A {A['median']:.0f}, C {C['median']:.0f}, D {D['median']:.0f}, B {B['median']:.0f}.",
    f"Uç değerler −{-min(p['min'] for p in P.values()):.0f} ile +{max(p['max'] for p in P.values()):.0f} arasında. Tek bir oyunda birkaç okeyle bitirme ya da çok sayıda gösterge sonucu tersine çevirebiliyor.",
    "Özel varyantla kıyasla: orada temkinli D'nin kutusu diğerlerinden tamamen ayrıydı. Burada farklar çok daha ince.",
], x=0.62, y=0.8, w=0.35, size=12)
pdf.savefig(fig); plt.close(fig)

# 8 Örnek oyun
fig = page("Örnek oyun: 100 el boyunca", "Oyun #0 kümülatif puan")
img(fig, "out_std/ornek_oyun_kumulatif.png", [0.02, 0.08, 0.58, 0.78])
bullets(fig, [
    "Çizgiler uzun süre birbirine yakın gidiyor ve sık sık yer değiştiriyor.",
    "Aşağı doğru sıçramalar bitirmeler ve gösterge (−101). Yukarı sıçramalar açamayıp 202 (katlamada 404) yazılan eller.",
    "Tek bir okeyle bitirme, rakiplere çift ceza yazdırarak sıralamayı birkaç elde değiştirebiliyor.",
    "Tek oyunun sonucu nüanslardan çok el dağılımının şansını yansıtıyor.",
], x=0.62, y=0.8, w=0.35, size=12)
pdf.savefig(fig); plt.close(fig)

# 9 El sonuç türleri
fig = page("El nasıl bitiyor?", "100.000 elin sonuç türleri")
img(fig, "out_std/el_sonuc_turleri.png", [0.02, 0.08, 0.58, 0.78])
bullets(fig, [
    f"Normal bitiş %{tr(100*k['normal']/N,1)}, deste bitti %{tr(100*k['deste']/N,1)}.",
    f"Okeyle bitiş %{tr(100*k['okey']/N,2)} (bunun ~%{100*D['fins']['okey']/k['okey']:.0f}'i D'den). Çift %{tr(100*k['cift']/N,2)}, elden %{tr(100*k['elden']/N,2)}.",
    f"El ortalama {tr(T['turns'],1)} hamle. Elde ortalama {tr(T['opened_avg'],2)} kişi açıyor; biri bitirdiğinde {tr(T['unopened_avg'],2)} kişi açamamış.",
    "Yüksek deste oranı: 20 taşlık deste ve yalnızca 2 joker. Botlar yerden yalnızca açabileceklerinde aldığı için gerçek masalardan yüksek olabilir.",
], x=0.62, y=0.8, w=0.35, size=12)
pdf.savefig(fig); plt.close(fig)

# 10 Açma eşiği
fig = page("En pahalı nüans: 10 puan fazladan beklemek", "B (111 bekler) ile A (101'de açar) karşılaştırması")
ax = fig.add_axes([0.06, 0.14, 0.42, 0.62])
hbars(ax, [P[n]["unopened"] for n in NAMES], fmt="%{:.1f}")
ax.set_title("Biri bitirdiğinde açamamış olma oranı", loc="left", fontsize=12, color=INK)
bullets(fig, [
    f"B biri bitirdiğinde %{tr(B['unopened'],1)} oranla açamamış oluyor; A'da bu oran %{tr(A['unopened'],1)}. Açamamak 202, katlamalı ellerde 404 demek.",
    f"B {tr(A['nfin']-B['nfin'])} bitirme kaybediyor ({tr(B['nfin'])}'e karşı {tr(A['nfin'])}).",
    f"Açmadan beklerken işlenebilir taşları atmak zorunda kalıyor: {sum(B['pens'].values())} ceza, A'da {sum(A['pens'].values())}.",
    f"Toplam etki: oyun başına ~{B['mean']-A['mean']:.0f} puan. 101'de 'biraz daha güçlü el beklemek' açıkça kaybettiriyor.",
], x=0.54, y=0.8, w=0.42, size=12)
pdf.savefig(fig); plt.close(fig)

# 11 Okey saklama
fig = page("Okeyle bitirmeyi kollamak (D)", "Okeyle bitirme ödülü, gecikmenin maliyetini karşılamıyor")
ax = fig.add_axes([0.06, 0.14, 0.42, 0.62])
vals = [A["fins"]["okey"], D["fins"]["okey"]]
b = ax.bar(["A – okeyle bitirme", "D – okeyle bitirme"], vals, color=[COL["A"], COL["D"]], width=0.5)
for r, v in zip(b, vals):
    ax.text(r.get_x() + r.get_width() / 2, v, str(v), ha="center", va="bottom", fontsize=11)
ax.set_title("Okeyle bitirme sayısı (100.000 el)", loc="left", fontsize=12, color=INK)
style(ax)
bullets(fig, [
    f"D okeyle {D['fins']['okey']} kez bitiriyor, A {A['fins']['okey']} kez. Okeyle bitirmek −202 getiriyor ve rakiplerin cezasını ikiye katlıyor.",
    f"Ama okeyi saklamak bitirmeyi geciktiriyor: D {tr(D['nfin'])} bitirme yapıyor, A'dan {tr(A['nfin']-D['nfin'])} eksik. Bu oyun başına ~{(A['nfin']-D['nfin'])*101/G:.0f} puan kaybı.",
    f"Rakip bitirdiğinde elde kalan okey 101 (katlamada 202) yazılıyor: D'nin okey cezası {tr(D['okey_pts'])}, A'nınki {tr(A['okey_pts'])}.",
    f"Net: D, A'nın ~{D['mean']-A['mean']:.0f} puan gerisinde. Okeyle bitirme fırsatı gelirse değerlendirin, ama onu beklemeyin.",
], x=0.54, y=0.8, w=0.42, size=12)
pdf.savefig(fig); plt.close(fig)

# 12 Çift + gösterge
fig = page("Çift oynamak ve gösterge", "İki küçük etken")
ax = fig.add_axes([0.06, 0.14, 0.42, 0.62])
vals = [C["cift_open"], C["fins"]["cift"] + C["fins"]["cift_okey"]]
b = ax.bar(["C çift açtı", "C çift bitirdi"], vals, color=[COL["C"], "#8fd3b8"], width=0.5)
for r, v in zip(b, vals):
    ax.text(r.get_x() + r.get_width() / 2, v, str(v), ha="center", va="bottom", fontsize=11)
ax.set_title("Çift açma ve çift bitirme (el sayısı)", loc="left", fontsize=12, color=INK)
style(ax)
bullets(fig, [
    f"Tek joker kaynağı 2 okey, sahteler normal taş. Bu yüzden 5+ çiftle açmak bile zor: C {C['cift_open']} kez çift açtı, yalnızca {C['fins']['cift']+C['fins']['cift_okey']}'sinde (%{100*(C['fins']['cift']+C['fins']['cift_okey'])/C['cift_open']:.0f}) bitirdi.",
    "C bu eller dışında A ile aynı oynadığı için toplam etki küçük ve istatistiksel olarak anlamsız.",
    f"Gösterge: eşi ellerin ~%84'ünde birinin elinde. Her oyuncu oyun başına ~{A['gost_n']/G:.0f} kez −101 alıyor, yani oyun başına ~{A['bonus']/G:,.0f} puan.".replace(",", "."),
    "Gösterge en büyük tekil puan kaynağı, ama herkese eşit dağıldığından sıralamayı etkilemiyor.",
], x=0.54, y=0.8, w=0.42, size=12)
pdf.savefig(fig); plt.close(fig)

# 13 Göstergeler
fig = page("Masa geneli göstergeler", "100.000 el")
tiles = [
    (tr(T["turns"], 1), "ortalama el uzunluğu (hamle)"),
    (tr(T["opened_avg"], 2), "elde ortalama açan kişi"),
    (f"%{tr(100*k['deste']/N,1)}", "deste bitti"),
    (tr(T["swap"]), "okey değiştirme"),
    (f"%{tr(100*k['okey']/N,2)}", "okeyle bitirme"),
    (f"%{tr(100*k['elden']/N,2)}", "elden bitme"),
]
for i, (v, l) in enumerate(tiles):
    x = 0.05 + (i % 3) * 0.31
    y = 0.5 if i < 3 else 0.14
    fig.add_artist(plt.Rectangle((x, y), 0.28, 0.3, color="#f3f5f9", transform=fig.transFigure))
    fig.text(x + 0.02, y + 0.17, v, fontsize=34, color=INK, weight="bold")
    fig.text(x + 0.02, y + 0.07, l, fontsize=13, color=MUTED)
pdf.savefig(fig); plt.close(fig)

# 14 Varyant karşılaştırması
fig = page("Özel varyant ile karşılaştırma", "Aynı motor, iki kural seti")
rows = [("", "Özel varyant", "Standart 101"),
        ("Joker sayısı", "8 okey (tüm 1'ler) + 2 sahte (çiftte)", "2 okey"),
        ("Destede kalan taş", "21", "20"),
        ("Ortalama el uzunluğu", "12,4 hamle", f"{tr(T['turns'],1)} hamle"),
        ("Deste bitti", "%3,0", f"%{tr(100*k['deste']/N,1)}"),
        ("Okeyle bitirme", "%3,2", f"%{tr(100*k['okey']/N,2)}"),
        ("Elden bitme", "%1,1", f"%{tr(100*k['elden']/N,2)}"),
        ("En iyi stratejinin kazanma oranı", "%58,8 (A)", f"%{tr(A['rank'][0],1)} (A)"),
        ("En kötü stratejinin sonuncu olma oranı", "%86,7 (D)", f"%{tr(B['rank'][3],1)} (B)")]
for r, row in enumerate(rows):
    y = 0.78 - r * 0.072
    if r % 2 == 1:
        fig.add_artist(plt.Rectangle((0.05, y - 0.045), 0.9, 0.07, color="#f3f5f9", transform=fig.transFigure))
    for c, (x, t) in enumerate(zip((0.07, 0.42, 0.72), row)):
        fig.text(x, y - 0.01, t, fontsize=13, color=INK, weight="bold" if r == 0 or c == 0 else "normal", va="center")
fig.text(0.05, 0.08, "İki kural setinde de ders aynı: erken aç, okeyi saklama. Varyantta farklar çok keskin; standartta gerçek ama şansın gölgesinde.",
         fontsize=13, color=MUTED)
pdf.savefig(fig); plt.close(fig)

# 15 Sonuç
fig = page("Sonuç: standart 101'de nasıl oynamalı?")
bullets(fig, [
    "101'e ulaştığın anda aç. Güvenlik payı beklemek en pahalı hata.",
    "Okeyle bitirme fırsatı kendiliğinden gelirse değerlendir, ama okeyi bunun için saklama. Elde kalan okey rakip bitirince 101 (katlamada 202) yazıyor.",
    "Çift, yalnızca olağanüstü çift ellerinde düşünülmeli. 2 jokerle 5+ çiftle bitirmek nadir.",
    "Göstergeyi her zaman göster: bedava −101.",
    "Tek bir oyunun sonucuna fazla anlam yükleme. Doğru oynayan bile masaların üçte ikisini kaybediyor. Fark uzun vadede ortaya çıkıyor.",
], w=0.9, size=16, gap=0.03)
pdf.savefig(fig); plt.close(fig)

# 16 Varsayımlar
fig = page("Varsayımlar ve sınırlar", "Ev kuralına göre değişen noktalar · ayrıntı rapor_standart.md'de")
bullets(fig, [
    "Gösterge sahte çıkarsa destenin altına konup yenisi açılıyor. Botlar göstergenin eşini ilk turda her zaman gösteriyor.",
    "12-13-1 serisindeki 1 değer olarak 1 sayılıyor (bazı evlerde 11 ya da 14).",
    "Deste bitince el puansız kapanıyor. Bazı evlerde açamayanlar yine 202 yazar; bu, deste bitişlerini çok daha pahalı yapardı.",
    "Elden bitmede diğerleri ×2, çift + okeyle bitirmede ×4.",
], w=0.44, size=12)
bullets(fig, [
    "Açamayan oyuncuya elde kalan okey için ek ceza yok (sabit 202). Açanlarda elde kalan her okey 101.",
    "Yalnızca bir önceki oyuncunun son attığı taş alınabiliyor. Botlar yerden yalnızca o tur açabilecekse alıyor; bu, deste bitme oranını yükseltiyor olabilir.",
    "Açılan turda işleme yapılmıyor. Çift açan yeni seri/grup açamıyor, ama tek taş işleyebiliyor.",
    "Botlar greedy. Hafıza, rakip okuma ve blöf modellenmedi. Sınırlamalar dört botta ortak olduğundan sıralama etkilenmez.",
], x=0.52, w=0.44, size=12)
pdf.savefig(fig); plt.close(fig)

pdf.close()
print("sunum_standart.pdf hazır")
