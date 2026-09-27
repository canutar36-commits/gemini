| Oyuncu | Ort. (±%95 GA) | Medyan | Std | Min | Max | 1. % | 2. % | 3. % | 4. % | El başı |
|---|---|---|---|---|---|---|---|---|---|---|
| A – Standart | -265 ± 57 | -268 | 912 | -3449 | 2535 | 34.4 | 26.4 | 23.0 | 16.2 | -2.65 |
| B – Biraz sabırlı | 422 ± 59 | 427 | 953 | -2891 | 3576 | 12.8 | 18.6 | 26.7 | 41.9 | 4.22 |
| C – Çift fırsatçısı | -197 ± 57 | -224 | 915 | -3154 | 2234 | 28.5 | 27.4 | 25.8 | 18.3 | -1.97 |
| D – Okeyle bitirmeyi kollayan | -43 ± 59 | -108 | 952 | -2622 | 3144 | 24.3 | 27.7 | 24.5 | 23.5 | -0.43 |

| Oyuncu | Bitirme | Normal | Okeyle | Çift | Çift+okey | Elden | İlk açan | Gösterge (adet / puan) | Açamama %* | Okey cezası (elde kalan okey, çarpanlı) | Katlama ek cezası | +101 cezaları (adet) | Çift açtığı el |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | 13802 | 13732 | 53 | 0 | 0 | 17 | 26691 | 21042 / −2125242 | 34.2 | 34643 | 46716 | 221 (islenebilir_atma:221) | 0 |
| B | 12837 | 12768 | 40 | 0 | 0 | 29 | 19004 | 20896 / −2110496 | 40.4 | 28280 | 50137 | 385 (islenebilir_atma:385) | 0 |
| C | 13566 | 13447 | 59 | 42 | 0 | 18 | 27316 | 20877 / −2108577 | 34.5 | 32421 | 43682 | 240 (islenebilir_atma:239, yerden_acamadi:1) | 845 |
| D | 12497 | 12123 | 348 | 0 | 0 | 26 | 26642 | 21034 / −2124434 | 34.3 | 69589 | 25607 | 245 (islenebilir_atma:225, okey_atma:20) | 0 |

\* Açamama %: biri bitirdiği ve oyuncunun bitirmediği ellerde açamama oranı.

| Sonuç türü | El | % |
|---|---|---|
| Normal | 52070 | 52.07 |
| Okeyle | 500 | 0.50 |
| Çift | 42 | 0.04 |
| Çift+okey | 0 | 0.00 |
| Elden | 90 | 0.09 |
| Deste bitti | 47298 | 47.30 |

- Elde ortalama açamayan kişi (biri bitirdiğinde): **1.07**
- Elde ortalama açan kişi (tüm eller): **2.66**
- Deste biten ellerin **%0.7**'inde kimse açamamış
- Ortalama el uzunluğu: **20.78 hamle**
- Okey değiştirme: **55432** kez

## Doğrulama

deste, normal, normal, deste, normal, normal, normal, normal, normal, normal

```
Dağıtan: B, başlayan (22 taş): C
Gösterge: Y3 -> okey: Y4 (elde * ile işaretli; SO = sahte okey = Y4)
  A [duz] eli: K1 K2 K3 K13 S2 S4 S9 S11 S11 S13 M1 M2 M5 M9 M13 Y8 Y11 Y11 Y12 Y12 SO
  B [duz] eli: K2 K5 K6 K7 K10 K10 K12 S4 S5 S6 S10 M1 M6 M8 M12 M13 Y4* Y6 Y9 Y10 Y13
  C [duz] eli: K1 K4 K8 K11 K13 S3 S3 S7 S8 S12 M5 M6 M7 M8 M10 Y1 Y2 Y2 Y5 Y8 Y9 Y13
  D [duz] eli: K4 K5 K6 K7 K8 S1 S1 S2 S6 S7 S13 M2 M3 M7 M10 M11 Y1 Y3 Y4* Y7 Y10
T1 C: (22 taş, çekmeden başlar)
  C S3 attı | el(21): K1 K4 K8 K11 K13 S3 S7 S8 S12 M5 M6 M7 M8 M10 Y1 Y2 Y2 Y5 Y8 Y9 Y13
T2 D: desteden M4 çekti
  D göstergeyi (Y3) gösterdi: −101
  D Y10 attı | el(21): K4 K5 K6 K7 K8 S1 S1 S2 S6 S7 S13 M2 M3 M4 M7 M10 M11 Y1 Y3 Y4* Y7
T3 A: desteden K12 çekti
  A M5 attı | el(21): K1 K2 K3 K12 K13 S2 S4 S9 S11 S11 S13 M1 M2 M9 M13 Y8 Y11 Y11 Y12 Y12 SO
T4 B: yerden M5 aldı
  B DÜZ AÇTI (128): M12 M13 M1 | K5 S5 M5 | K6 S6 M6 Y6 | K10 S10 Y10 | K10 Y4 K12
  B Y13 attı | el(5): K2 K7 S4 M8 Y9
T5 C: desteden S10 çekti
  C S3 attı | el(21): K1 K4 K8 K11 K13 S7 S8 S10 S12 M5 M6 M7 M8 M10 Y1 Y2 Y2 Y5 Y8 Y9 Y13
T6 D: desteden K9 çekti
  D DÜZ AÇTI (102): M2 M3 M4 | K4 K5 K6 | K7 K8 K9 | S7 M7 Y7 | M10 M11 Y4
  D S6 attı | el(6): S1 S1 S2 S13 Y1 Y3
T7 A: desteden S12 çekti
  A Y8 attı | el(21): K1 K2 K3 K12 K13 S2 S4 S9 S11 S11 S12 S13 M1 M2 M9 M13 Y11 Y11 Y12 Y12 SO
T8 B: desteden M3 çekti
  B masaya 1 taş koydu/işledi
  B Y9 attı | el(4): K2 S4 M3 M8
T9 C: desteden K3 çekti
  C K11 attı | el(21): K1 K3 K4 K8 K13 S7 S8 S10 S12 M5 M6 M7 M8 M10 Y1 Y2 Y2 Y5 Y8 Y9 Y13
T10 D: desteden K9 çekti
  D masaya 1 taş koydu/işledi
  D Y3 attı | el(5): S1 S1 S2 S13 Y1
T11 A: desteden Y5 çekti
  A S4 attı | el(21): K1 K2 K3 K12 K13 S2 S9 S11 S11 S12 S13 M1 M2 M9 M13 Y5 Y11 Y11 Y12 Y12 SO
T12 B: desteden S5 çekti
  B M8 attı | el(4): K2 S4 S5 M3
T13 C: desteden S9 çekti
  C S12 attı | el(21): K1 K3 K4 K8 K13 S7 S8 S9 S10 M5 M6 M7 M8 M10 Y1 Y2 Y2 Y5 Y8 Y9 Y13
T14 D: yerden S12 aldı
  D masaya 3 taş koydu/işledi
  D S2 attı | el(2): S1 Y1
T15 A: desteden M4 çekti
  A M4 attı | el(21): K1 K2 K3 K12 K13 S2 S9 S11 S11 S12 S13 M1 M2 M9 M13 Y5 Y11 Y11 Y12 Y12 SO
T16 B: desteden S8 çekti
  B S8 attı | el(4): K2 S4 S5 M3
T17 C: desteden M11 çekti
  C Y2 attı | el(21): K1 K3 K4 K8 K13 S7 S8 S9 S10 M5 M6 M7 M8 M10 M11 Y1 Y2 Y5 Y8 Y9 Y13
T18 D: desteden K11 çekti
  D K11 attı | el(2): S1 Y1
T19 A: yerden K11 aldı
  A DÜZ AÇTI (114): K2 S2 M2 | K11 S11 Y11 | K12 S12 Y12 | K13 S13 M13
  A Y12 attı | el(9): K1 K3 S9 S11 M1 M9 Y5 Y11 SO
T20 B: desteden M12 çekti
  B masaya 3 taş koydu/işledi (okey değiştirme x1)
  B M3 attı | el(1): K2
T21 C: desteden Y6 çekti
  C K4 attı | el(21): K1 K3 K8 K13 S7 S8 S9 S10 M5 M6 M7 M8 M10 M11 Y1 Y2 Y5 Y6 Y8 Y9 Y13
T22 D: desteden Y7 çekti
  D Y7 attı | el(2): S1 Y1
T23 A: desteden M9 çekti
  A masaya 5 taş koydu/işledi
  A Y11 attı | el(4): K1 S9 M9 SO
T24 B: desteden SO çekti
  B son taşı SO atıp BİTİRDİ -> normal
SONUÇ: normal; puanlar: A=23, B=-101, C=202, D=-99
```
