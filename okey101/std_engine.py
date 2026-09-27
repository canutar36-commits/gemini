"""Standart (yaygın oynanan) 101 Okey kuralları.

- Gösterge açılır; okey = göstergenin aynı renkte bir üstü (13'ün üstü 1). 2 okey taşı jokerdir.
- Sahte okeyler okey taşının kendisi yerine geçer (normal taş gibi, joker değil).
- 1 hem 1-2-3'te hem 12-13-1'de kullanılabilir (13-1-2 yok).
- Açma: seri+grup ≥101 ya da en az 5 çift. Okey her perde joker.
- Göstergeyi ilk turunda gösteren −101 alır.
- Bitiren −101; okeyle bitiren −202 (diğerlerinin cezası ×2); çift açıp bitiren −202 (×2);
  çift + okeyle −404 (×4); elden bitiren −202 (diğerleri ×2).
- Bitiremeyen: açamayan 202; düz açan kalan taş toplamı + elde kalan okey başına 101;
  çift açan bunun ×2'si. Deste biterse yalnızca ceza (+101) ve gösterge puanları yazılır.
"""
from .engine import HandGame
from .solver import std_pairs
from .tiles import FAKE, NT, tid, num, color, name, new_deck, size

MULT = {"normal": 1, "okey": 2, "cift": 2, "cift_okey": 4, "elden": 2}
BASE = {"normal": -101, "okey": -202, "cift": -202, "cift_okey": -404, "elden": -202}


class StdHandGame(HandGame):
    LO, HI, ACE = 1, 14, True
    FAKE_SPECIAL = False
    OKEY_IN_HAND = 101

    def setup_deck(self):
        self.deck = new_deck(self.rng)
        while self.deck[-1] == FAKE:  # sahte gösterge olamaz
            self.deck.insert(0, self.deck.pop())
        self.gosterge = self.deck.pop()
        c, n = color(self.gosterge), num(self.gosterge)
        self.OK = tid(c, n % 13 + 1)
        self.JK = [self.OK]
        self.gost = [0] * 4

    def log(self, msg):
        if self.log_on:  # tiles.name 1'leri okey (*) diye işaretler; standartta 1 normal taştır
            self.logs.append(msg.replace("1*", "1").replace("(OKEY)", "*"))

    def log_extra(self):
        self.log(f"Gösterge: {name(self.gosterge)} -> okey: {name(self.OK)} (elde (OKEY) ile işaretli; SO = sahte okey = {name(self.OK)})")

    def extra_tiles(self):
        return [self.gosterge]

    # ---- kimlikler
    def isj(self, t):
        return t == self.OK

    def ident(self, t):
        if t == FAKE:
            return self.OK
        return None if t == self.OK else t

    def take_real(self, h, i):
        if i == self.OK:
            assert h[FAKE] > 0
            h[FAKE] -= 1
            return FAKE
        assert h[i] > 0
        h[i] -= 1
        return i

    def has_real(self, h, i):
        return i != self.OK and h[i] > 0

    def pairs(self, h, held):
        cnt, J = self.view(h)
        prs, _, _ = std_pairs(cnt, J - (1 if held else 0))
        hh = list(h)
        out = []
        for a, b in prs:
            pa = self.take_joker(hh) if a is None else self.take_real(hh, a)
            pb = self.take_joker(hh) if b is None else self.take_real(hh, b)
            out.append((pa, pb))
        return out

    def valid_pair(self, a, b):
        return self.isj(a) or self.isj(b) or self.ident(a) == self.ident(b)

    def psum(self, h):
        return sum(h[t] * num(self.ident(t)) for t in range(NT) if h[t] and not self.isj(t))

    def hstr(self, h):
        out = []
        for t in range(NT):
            out += [name(t).rstrip("*") + ("(OKEY)" if t == self.OK else "")] * h[t]
        return " ".join(out)

    def fake_keep_score(self):
        return 0  # standartta sahte her zaman bir kimliğe sahip; buraya düşmez

    def on_first_turn(self, p):
        if self.hands[p][self.gosterge] > 0:
            self.gost[p] = -101
            self.log(f"  {self.bots[p].name} göstergeyi ({name(self.gosterge)}) gösterdi: −101")

    # ---- puanlama
    def finish_hand(self):
        scores, okey_pts, pen_pts, mult_pts = [0] * 4, [0] * 4, [0] * 4, [0] * 4
        for s in range(4):
            pen_pts[s] = 101 * len(self.pen[s])
        if self.result is None:
            kind, fin = "deste", None
            for s in range(4):
                scores[s] = pen_pts[s] + self.gost[s]
        else:
            fin, kind = self.result
            m = MULT[kind]
            for s in range(4):
                if s == fin:
                    scores[s] = BASE[kind]
                else:
                    h, k = self.hands[s], self.nj(self.hands[s])
                    if self.opened[s] is None:
                        base, ok = 202, 0
                    elif self.opened[s] == "duz":
                        base, ok = self.psum(h), k * self.OKEY_IN_HAND
                    else:
                        base, ok = 2 * self.psum(h), 2 * k * self.OKEY_IN_HAND
                    okey_pts[s] = ok * m
                    mult_pts[s] = (base + ok) * (m - 1)
                    scores[s] = (base + ok) * m
                scores[s] += pen_pts[s] + self.gost[s]
        self.validate_std(kind, fin, scores)
        self.log(f"SONUÇ: {kind}; puanlar: " + ", ".join(f"{self.bots[s].name}={scores[s]}" for s in range(4)))
        r = self.result_dict(kind, fin, scores, okey_pts, pen_pts, list(self.gost))
        r["mult_pts"] = mult_pts
        return r

    def validate_std(self, kind, fin, scores):
        self.validate_common(kind, fin)
        for s in range(4):
            assert self.gost[s] in (0, -101)
        if kind == "deste":
            for s in range(4):
                assert scores[s] == 101 * len(self.pen[s]) + self.gost[s]
            return
        m = MULT[kind]
        assert scores[fin] == BASE[kind] + 101 * len(self.pen[fin]) + self.gost[fin]
        for s in range(4):
            if s != fin and self.opened[s] is None:
                assert scores[s] - 101 * len(self.pen[s]) - self.gost[s] == 202 * m
        if kind == "elden":
            assert all(scores[s] - 101 * len(self.pen[s]) - self.gost[s] == 404 for s in range(4) if s != fin)
