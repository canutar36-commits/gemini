"""Standart 101 için birbirine çok benzeyen 4 bot. Hepsi aynı greedy çekirdeği kullanır;
yalnızca tek bir nüansta ayrışırlar."""
from .bots import Bot


class StdBase(Bot):
    name, label = "A", "A – Standart"


class Patient(StdBase):
    name, label = "B", "B – Biraz sabırlı"

    def open_threshold(self, g, p):
        return 101 if len(g.deck) <= 8 else 111  # 10 puanlık güvenlik payı


class PairOpportunist(StdBase):
    name, label = "C", "C – Çift fırsatçısı"

    def start_hand(self, h, g=None):
        cnt, J = g.view(h)
        pot = sum(c // 2 for c in cnt) + J
        self.mode = "cift" if pot >= 6 else "duz"  # yalnızca çok güçlü çift elinde

    def cift_open_ok(self, g, p, npairs):
        return npairs >= 6 or (npairs >= 5 and len(g.deck) <= 10)


class OkeyKeeper(StdBase):
    name, label = "D", "D – Okeyle bitirmeyi kollayan"

    def hold_okey(self, g, p, left, has_okey):
        return has_okey and left <= 2  # bitirmeye 2 taş kalınca bir okeyi son taşa saklar

    def isle_jokers(self, g, p, leftover_real):
        return False


def make_std_bots():
    return [StdBase(), Patient(), PairOpportunist(), OkeyKeeper()]
