"""Bot stratejileri. Motor, botlara yalnızca karar noktalarını sorar."""
from .solver import solve_pairs
from .tiles import FAKE, OKEYS, is_okey


class Bot:
    name = "?"
    label = ""

    def start_hand(self, h, g=None):
        self.mode = "duz"

    # --- açma eşiği ---
    def open_threshold(self, g, p):
        return 101

    def cift_open_ok(self, g, p, npairs):
        return False

    # --- okey yönetimi ---
    def hold_okey(self, g, p, leftover_wo_okey, has_okey):
        return False

    def isle_jokers(self, g, p, leftover_real):
        """Açtıktan sonra perlere girmeyen okeyleri masaya işlesin mi?"""
        return leftover_real <= 1

    def keep_fake(self):
        return True


class FastOpener(Bot):
    name, label = "A", "Hızlı açan"

    def isle_jokers(self, g, p, leftover_real):
        return True  # okeyi saklamaz


class OkeyHolder(Bot):
    name, label = "B", "Okey saklayan"

    def hold_okey(self, g, p, left, has_okey):
        if not has_okey or left > 3:
            return False
        p_self = 1.0 / (1 + left)
        p_other = 0.0
        for q in range(4):
            if q == p:
                continue
            ns = sum(g.hands[q])
            est = 1.0 / max(1, ns - 1) if g.opened[q] else 0.02
            p_other = max(p_other, min(1.0, est))
        return p_self * 101 > p_other * g.okey_ceza

    def isle_jokers(self, g, p, leftover_real):
        return False  # fazladan okeyleri sadece yeni perlerde kullanır


class PairPlayer(Bot):
    name, label = "C", "Çift oyuncusu"
    PAIR_POTENTIAL = 5

    def start_hand(self, h, g=None):
        real_pairs = sum(h[t] // 2 for t in range(52) if not is_okey(t))
        pot = real_pairs + sum(h[o] for o in OKEYS) + h[FAKE]
        self.mode = "cift" if pot >= self.PAIR_POTENTIAL else "duz"

    def cift_open_ok(self, g, p, npairs):
        return npairs >= 6 or (npairs >= 5 and len(g.deck) <= 10)


class Cautious(Bot):
    name, label = "D", "Klasik/temkinli"

    def open_threshold(self, g, p):
        # 121 bekler; deste azaldıysa (güvenlik payı bitti) 101 ile açar
        return 101 if len(g.deck) <= 8 else 121


def make_bots():
    return [FastOpener(), OkeyHolder(), PairPlayer(), Cautious()]
