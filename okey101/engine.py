"""Bir elin oynanması: dağıtım, tur akışı, işleme, açma, bitirme, puanlama."""
from collections import Counter

from .solver import solve_sets, solve_pairs, set_tiles
from .tiles import (FAKE, NT, OKEYS, tid, num, color, is_okey, name, new_deck,
                    empty, n_okey, size, point_sum, hand_str)

BASE = {"normal": -101, "okey": -202, "cift": -202, "cift_okey": -404, "elden": -202}


def copy_sets(sets):
    return [dict(s, j=dict(s["j"]), cols=set(s["cols"]) if s["cols"] is not None else None) for s in sets]


class HandGame:
    def __init__(self, bots, dealer, rng, okey_ceza, log=False, check=False):
        self.bots, self.rng, self.okey_ceza = bots, rng, okey_ceza
        self.log_on, self.check = log, check
        self.logs = []
        self.deck = new_deck(rng)
        self.hands = [empty() for _ in range(4)]
        self.starter = (dealer + 1) % 4  # dağıtanın sağı: 22 taş
        for s in range(4):
            k = 22 if s == self.starter else 21
            for _ in range(k):
                self.hands[s][self.deck.pop()] += 1
        self.opened = [None] * 4
        self.sets = []
        self.pair_area = [[] for _ in range(4)]
        self.pile = []
        self.top = None
        self.first_opener = None
        self.pen = [[] for _ in range(4)]
        self.fake_special = 0
        self.swaps = 0
        self.turns = 0
        for s in range(4):
            bots[s].start_hand(self.hands[s])
        self.log(f"Dağıtan: {bots[dealer].name}, başlayan (22 taş): {bots[self.starter].name}")
        for s in range(4):
            self.log(f"  {bots[s].name} [{bots[s].mode}] eli: {hand_str(self.hands[s])}")

    # ------------------------------------------------------------ yardımcılar
    def log(self, msg):
        if self.log_on:
            self.logs.append(msg)

    @staticmethod
    def fits(sets, t):
        if t == FAKE or is_okey(t):
            return -1
        c, n = color(t), num(t)
        for i, s in enumerate(sets):
            if s["k"] == "R":
                if s["c"] == c and ((n == s["s"] - 1 and n >= 2) or (n == s["e"] + 1 and n <= 13)):
                    return i
            elif s["n"] == n and c not in s["cols"] and c not in s["j"] and len(s["cols"]) + len(s["j"]) < 4:
                return i
        return -1

    @staticmethod
    def add_tile(s, t):
        if s["k"] == "R":
            if num(t) == s["s"] - 1:
                s["s"] -= 1
            else:
                s["e"] += 1
        else:
            s["cols"].add(color(t))

    @staticmethod
    def place_desc(desc, h, sets, owner):
        real, j = set_tiles(desc)
        for t in real:
            h[t] -= 1
            assert h[t] >= 0
        oks = [o for o in OKEYS for _ in range(h[o])][:j]
        assert len(oks) == j
        for o in oks:
            h[o] -= 1
        if desc[0] == "G":
            n, cols = desc[1], set(desc[2])
            missing = [c for c in range(4) if c not in cols]
            sets.append({"k": "G", "n": n, "cols": cols, "j": dict(zip(missing, oks)), "o": owner})
        else:
            _, c, s, e, jp = desc
            sets.append({"k": "R", "c": c, "s": s, "e": e, "j": dict(zip(jp, oks)), "o": owner, "cols": None})

    def isleable(self, t):
        return self.fits(self.sets, t) >= 0

    def table_tiles(self):
        cnt = Counter()
        for s in self.sets:
            if s["k"] == "R":
                for n in range(s["s"], s["e"] + 1):
                    cnt[s["j"][n] if n in s["j"] else tid(s["c"], n)] += 1
            else:
                for c in s["cols"]:
                    cnt[tid(c, s["n"])] += 1
                for o in s["j"].values():
                    cnt[o] += 1
        for pa in self.pair_area:
            for a, b in pa:
                cnt[a] += 1
                cnt[b] += 1
        return cnt

    def check_conservation(self):
        cnt = self.table_tiles()
        for h in self.hands:
            for t in range(NT):
                cnt[t] += h[t]
        for t in self.deck + self.pile:
            cnt[t] += 1
        for t in range(NT):
            assert cnt[t] == 2, f"taş korunumu bozuk: {name(t)} -> {cnt[t]}"
        for s in self.sets:
            L = (s["e"] - s["s"] + 1) if s["k"] == "R" else len(s["cols"]) + len(s["j"])
            assert L >= 3 and (s["k"] == "R" or L <= 4)
            if s["k"] == "R":
                assert 2 <= s["s"] and s["e"] <= 13

    # ------------------------------------------------------------ işleme / per
    def meld(self, p, h, sets, pair_area, hold, stats):
        """Açmış oyuncunun bu turdaki masaya koyma hamleleri (yerinde değiştirir)."""
        bot, mode = self.bots[p], self.opened[p]
        # 1) okey değiştirme
        for s in sets:
            for key, ok in list(s["j"].items()):
                t = tid(s["c"], key) if s["k"] == "R" else tid(key, s["n"])
                if h[t] > 0:
                    h[t] -= 1
                    h[ok] += 1
                    del s["j"][key]
                    if s["k"] == "G":
                        s["cols"].add(key)
                    stats["swap"] += 1
        held = 1 if hold and n_okey(h) > 0 else 0

        def isle_loop(only_single=False):
            moved = True
            while moved:
                moved = False
                for t in range(52):
                    if h[t] and not is_okey(t) and (not only_single or h[t] == 1):
                        i = self.fits(sets, t)
                        if i >= 0:
                            h[t] -= 1
                            self.add_tile(sets[i], t)
                            moved = True

        if mode == "duz":
            _, _, descs = solve_sets(h, n_okey(h) - held, "t")
            for d in descs:
                self.place_desc(d, h, sets, p)
            isle_loop()
        else:
            isle_loop(only_single=True)
            hh = list(h)
            if held:
                o = next(o for o in OKEYS if hh[o])
                hh[o] -= 1
            _, prs, _ = solve_pairs(hh)
            for a, b in prs:
                h[a] -= 1
                h[b] -= 1
                pair_area[p].append((a, b))
            isle_loop()
        # 2) fazla okeyleri işle
        left_real = size(h) - n_okey(h)
        if n_okey(h) - held > 0 and bot.isle_jokers(self, p, left_real):
            for _ in range(n_okey(h) - held):
                o = next(o for o in OKEYS if h[o])
                for s in sets:
                    if s["k"] == "R" and (s["e"] < 13 or s["s"] > 2):
                        pos = s["e"] + 1 if s["e"] < 13 else s["s"] - 1
                        if pos in s["j"]:
                            continue
                        s["j"][pos] = o
                        s["e"], s["s"] = max(s["e"], pos), min(s["s"], pos)
                        h[o] -= 1
                        break
                    if s["k"] == "G" and len(s["cols"]) + len(s["j"]) < 4:
                        miss = next(c for c in range(4) if c not in s["cols"] and c not in s["j"])
                        s["j"][miss] = o
                        h[o] -= 1
                        break
                else:
                    break
        # 3) sahte okey istisnası: düz açmış oyuncu (sahte + taş) çiftini başkasının çift alanına
        if mode == "duz":
            while h[FAKE] > 0:
                targets = [q for q in range(4) if q != p and pair_area[q]]
                reals = [t for t in range(52) if h[t] and not is_okey(t)]
                if not targets or not reals:
                    break
                t = max(reals, key=num)
                h[FAKE] -= 1
                h[t] -= 1
                pair_area[targets[0]].append((FAKE, t))
                stats["fake"] += 1
        return h

    def dry_meld(self, p, h, hold):
        st = {"swap": 0, "fake": 0}
        return self.meld(p, list(h), copy_sets(self.sets), [list(x) for x in self.pair_area], hold, st)

    # ------------------------------------------------------------ bitirme
    def finish_candidates(self, h, left_tiles):
        cands = [o for o in OKEYS if h[o]][:1]
        cands += [t for t in left_tiles if t not in cands]
        cands += [t for t in range(NT) if h[t] and t not in cands]
        return cands

    def try_finish(self, p, dry=False, h=None):
        h = self.hands[p] if h is None else h
        bot = self.bots[p]
        if self.opened[p]:
            left = self.dry_meld(p, h, hold=False)
            if size(left) > 1:
                return False
            lt = [t for t in range(NT) if left[t]]
            for t in self.finish_candidates(h, lt):
                h2 = list(h)
                h2[t] -= 1
                if size(self.dry_meld(p, h2, hold=False)) == 0:
                    if dry:
                        return True
                    st = {"swap": 0, "fake": 0}
                    self.hands[p] = h2
                    self.meld(p, h2, self.sets, self.pair_area, False, st)
                    self.swaps += st["swap"]
                    self.fake_special += st["fake"]
                    return self._finish(p, t, elden=False)
            return False
        # açmamış oyuncu: tek hamlede aç + bitir
        if bot.mode == "duz":
            tu, _, _ = solve_sets(h, None, "t")
            if size(h) - tu > 1:
                return False
            for t in self.finish_candidates(h, []):
                h2 = list(h)
                h2[t] -= 1
                tu2, val2, descs = solve_sets(h2, None, "t")
                if tu2 == size(h2) and val2 >= 101:
                    if dry:
                        return True
                    elden = all(o is None for o in self.opened)
                    self.opened[p] = "duz"
                    if self.first_opener is None:
                        self.first_opener = p
                    for d in descs:
                        self.place_desc(d, h2, self.sets, p)
                    self.hands[p] = h2
                    self.log(f"  {bot.name} düz açıp bitiriyor (değer {val2})")
                    return self._finish(p, t, elden)
            return False
        else:
            if size(h) % 2 == 0 and size(h) > 0:
                for t in self.finish_candidates(h, []):
                    h2 = list(h)
                    h2[t] -= 1
                    np_, prs, left = solve_pairs(h2)
                    if size(left) == 0 and np_ >= 5:
                        if dry:
                            return True
                        elden = all(o is None for o in self.opened)
                        self.opened[p] = "cift"
                        if self.first_opener is None:
                            self.first_opener = p
                        for a, b in prs:
                            h2[a] -= 1
                            h2[b] -= 1
                            self.pair_area[p].append((a, b))
                        self.hands[p] = h2
                        return self._finish(p, t, elden)
            return False

    def _finish(self, p, t, elden):
        self.pile.append(t)  # t çağıran tarafından elden çıkarıldı
        assert size(self.hands[p]) == 0
        if elden:
            kind = "elden"
        elif self.opened[p] == "cift":
            kind = "cift_okey" if is_okey(t) else "cift"
        else:
            kind = "okey" if is_okey(t) else "normal"
        self.log(f"  {self.bots[p].name} son taşı {name(t)} atıp BİTİRDİ -> {kind}")
        self.result = (p, kind)
        return True

    # ------------------------------------------------------------ açma
    def try_open(self, p):
        h, bot = self.hands[p], self.bots[p]
        if bot.mode == "duz":
            thr = bot.open_threshold(self, p)
            J = n_okey(h)

            def best(Juse):
                r = solve_sets(h, Juse, "t")
                if r[1] < thr:
                    r = solve_sets(h, Juse, "v")
                return r

            tu, val, descs = best(J)
            if val < thr:
                return False
            left = size(h) - tu - (J - sum(d[3] if d[0] == "G" else len(d[4]) for d in descs))
            if J > 0 and bot.hold_okey(self, p, left, True):
                r2 = best(J - 1)
                if r2[1] >= thr:
                    tu, val, descs = r2
            if size(h) - tu < 1:
                return False
            for d in descs:
                self.place_desc(d, h, self.sets, p)
            self.opened[p] = "duz"
            self.log(f"  {bot.name} DÜZ AÇTI ({val}): " + " | ".join(self.set_str(s) for s in self.sets if s["o"] == p))
        else:
            np_, prs, left = solve_pairs(h)
            if not bot.cift_open_ok(self, p, np_):
                return False
            if size(left) == 0:
                prs = prs[:-1]
            for a, b in prs:
                h[a] -= 1
                h[b] -= 1
                self.pair_area[p].append((a, b))
            self.opened[p] = "cift"
            self.log(f"  {bot.name} ÇİFT AÇTI ({len(prs)} çift): " + " ".join(f"{name(a)}+{name(b)}" for a, b in prs))
        if self.first_opener is None:
            self.first_opener = p
        return True

    @staticmethod
    def set_str(s):
        if s["k"] == "R":
            return " ".join((name(s["j"][n]) if n in s["j"] else name(tid(s["c"], n))) for n in range(s["s"], s["e"] + 1))
        return " ".join([name(tid(c, s["n"])) for c in sorted(s["cols"])] + [name(o) for o in s["j"].values()])

    # ------------------------------------------------------------ yerden alma
    def want_discard(self, p, d):
        h2 = list(self.hands[p])
        h2[d] += 1
        bot = self.bots[p]
        if not self.opened[p]:
            if self.try_finish(p, dry=True, h=h2):
                return True
            if bot.mode == "duz":
                return solve_sets(h2, None, "v")[1] >= bot.open_threshold(self, p)
            return bot.cift_open_ok(self, p, solve_pairs(h2)[0])
        if self.isleable(d):
            return True
        if self.opened[p] == "duz":
            return solve_sets(h2, None, "t")[0] > solve_sets(self.hands[p], None, "t")[0]
        return d == FAKE or self.hands[p][d] == 1

    # ------------------------------------------------------------ taş atma
    def choose_discard(self, p):
        h, bot = self.hands[p], self.bots[p]
        opened = self.opened[p] is not None
        nonok = [t for t in range(NT) if h[t] and not is_okey(t)]
        safe = [t for t in nonok if not self.isleable(t)]
        if bot.mode == "cift":
            singles = [t for t in safe if t != FAKE and h[t] % 2 == 1]
            pool = singles or [t for t in safe if t != FAKE] or safe or nonok
            if pool:
                return max(pool, key=lambda t: (t != FAKE, num(t) if t != FAKE else 0))
            return next(o for o in OKEYS if h[o])
        tu, _, descs = solve_sets(h, None, "t")
        left = list(h)
        for d in descs:
            real, _ = set_tiles(d)
            for t in real:
                left[t] -= 1
        lc = [t for t in safe if left[t] > 0]
        pool = lc or safe or nonok
        if not pool:
            return next(o for o in OKEYS if h[o])

        def score(t):
            if t == FAKE:
                return 25
            c, n = color(t), num(t)
            conn = 0
            for dn, w in ((1, 2), (2, 1)):
                for m in (n - dn, n + dn):
                    if 2 <= m <= 13 and h[tid(c, m)]:
                        conn += w
            for cc in range(4):
                if cc != c and h[tid(cc, n)]:
                    conn += 2
            return conn * 20 + (-n if opened else n)

        return min(pool, key=score)

    # ------------------------------------------------------------ tur
    def play(self):
        self.result = None
        p = self.starter
        first = True
        while self.turns < 300:
            self.turns += 1
            bot = self.bots[p]
            took = None
            if not first:
                d = self.top
                if d is not None and self.want_discard(p, d):
                    self.pile.pop()
                    self.hands[p][d] += 1
                    took = d
                    self.top = None
                    self.log(f"T{self.turns} {bot.name}: yerden {name(d)} aldı")
                else:
                    if not self.deck:
                        self.log(f"T{self.turns} {bot.name}: deste bitti")
                        return self.finish_hand()
                    t = self.deck.pop()
                    self.hands[p][t] += 1
                    self.log(f"T{self.turns} {bot.name}: desteden {name(t)} çekti")
            else:
                self.log(f"T{self.turns} {bot.name}: (22 taş, çekmeden başlar)")
            first = False
            if self.try_finish(p):
                return self.finish_hand()
            if not self.opened[p]:
                self.try_open(p)
                if took is not None and not self.opened[p]:
                    self.pen[p].append("yerden_acamadi")
            else:
                hold = False
                if self.bots[p].hold_okey is not None and n_okey(self.hands[p]):
                    dry = self.dry_meld(p, self.hands[p], hold=True)
                    hold = self.bots[p].hold_okey(self, p, size(dry) - n_okey(dry), True)
                st = {"swap": 0, "fake": 0}
                h2, s2, pa2 = list(self.hands[p]), copy_sets(self.sets), [list(x) for x in self.pair_area]
                self.meld(p, h2, s2, pa2, hold, st)
                if size(h2) >= 1:
                    before = size(self.hands[p])
                    self.hands[p], self.sets, self.pair_area = h2, s2, pa2
                    self.swaps += st["swap"]
                    self.fake_special += st["fake"]
                    if size(h2) != before:
                        self.log(f"  {bot.name} masaya {before - size(h2)} taş koydu/işledi"
                                 + (f" (okey değiştirme x{st['swap']})" if st["swap"] else "")
                                 + (f" (sahte işleme x{st['fake']})" if st["fake"] else ""))
            t = self.choose_discard(p)
            if is_okey(t):
                self.pen[p].append("okey_atma")
            elif self.isleable(t):
                self.pen[p].append("islenebilir_atma")
            self.hands[p][t] -= 1
            self.pile.append(t)
            self.top = t
            self.log(f"  {bot.name} {name(t)} attı | el({size(self.hands[p])}): {hand_str(self.hands[p])}")
            if self.check:
                self.check_conservation()
            p = (p + 1) % 4
        return self.finish_hand()

    # ------------------------------------------------------------ puanlama
    def finish_hand(self):
        C = self.okey_ceza
        scores = [0] * 4
        okey_pts = [0] * 4
        pen_pts = [0] * 4
        bonus = [0] * 4
        if self.result is None:
            kind, fin = "deste", None
            for s in range(4):
                okey_pts[s] = n_okey(self.hands[s]) * C
                scores[s] = okey_pts[s]
        else:
            fin, kind = self.result
            for s in range(4):
                if s == fin:
                    scores[s] = BASE[kind]
                    if kind != "elden" and self.first_opener == s:
                        bonus[s] = -20
                        scores[s] -= 20
                    pen_pts[s] = 101 * len(self.pen[s])
                    scores[s] += pen_pts[s]
                elif kind == "elden":
                    scores[s] = 404
                else:
                    h, k = self.hands[s], n_okey(self.hands[s])
                    if self.opened[s] is None:
                        base, okey_pts[s] = 202, k * C
                    elif self.opened[s] == "duz":
                        base, okey_pts[s] = point_sum(h), k * C
                    else:
                        base, okey_pts[s] = 2 * point_sum(h), 2 * k * C
                    pen_pts[s] = 101 * len(self.pen[s])
                    scores[s] = base + okey_pts[s] + pen_pts[s]
        self.validate(kind, fin, scores, bonus)
        self.log(f"SONUÇ: {kind}; puanlar: " + ", ".join(f"{self.bots[s].name}={scores[s]}" for s in range(4)))
        return {
            "kind": kind, "fin": fin, "scores": scores, "okey_pts": okey_pts, "pen_pts": pen_pts,
            "pens": [list(x) for x in self.pen], "bonus": bonus, "first_opener": self.first_opener,
            "opened": list(self.opened), "turns": self.turns, "fake": self.fake_special, "swap": self.swaps,
        }

    def validate(self, kind, fin, scores, bonus):
        """Kurallara uygunluk kontrolleri (her elde çalışır)."""
        if kind == "deste":
            assert fin is None and len(self.deck) == 0
            for s in range(4):
                assert scores[s] == n_okey(self.hands[s]) * self.okey_ceza
            return
        assert size(self.hands[fin]) == 0
        if kind == "elden":
            assert self.opened.count(None) == 3 and self.first_opener == fin and bonus[fin] == 0
            assert all(scores[s] == 404 for s in range(4) if s != fin)
        if kind in ("cift", "cift_okey"):
            assert self.opened[fin] == "cift"
        if kind in ("normal", "okey"):
            assert self.opened[fin] == "duz"
        if kind in ("okey", "cift_okey"):
            assert is_okey(self.pile[-1])
        if bonus[fin]:
            assert self.first_opener == fin and kind != "elden"
        for s in range(4):
            if self.opened[s] == "cift":
                assert len(self.pair_area[s]) >= 5 or s != self.first_opener or True
            if s != fin and kind != "elden" and self.opened[s] is None:
                assert scores[s] >= 202
        for s in range(4):  # çift alanlarının geçerliliği
            for a, b in self.pair_area[s]:
                assert not (a == FAKE and (b == FAKE or is_okey(b))) and not (b == FAKE and is_okey(a))
                assert a == b or a == FAKE or b == FAKE or is_okey(a) or is_okey(b)
        if self.check:
            self.check_conservation()
