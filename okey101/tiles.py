"""Taş temsili: 0..51 = renk*13 + (sayı-1); 52 = sahte okey. Tüm 1'ler okeydir."""
import random

COLORS = ["K", "S", "M", "Y"]  # kırmızı, sarı, mavi, siyah
FAKE = 52
NT = 53


def tid(c, n):
    return c * 13 + n - 1


def color(t):
    return t // 13


def num(t):
    return t % 13 + 1


def is_okey(t):
    return t < 52 and t % 13 == 0


OKEYS = [tid(c, 1) for c in range(4)]


def name(t):
    if t == FAKE:
        return "SO"
    return f"{COLORS[color(t)]}{num(t)}" + ("*" if is_okey(t) else "")


def new_deck(rng: random.Random):
    deck = list(range(52)) * 2 + [FAKE, FAKE]
    rng.shuffle(deck)
    return deck


def empty():
    return [0] * NT


def n_okey(h):
    return sum(h[o] for o in OKEYS)


def size(h):
    return sum(h)


def point_sum(h):
    """Elde kalan sayı toplamı (okey ve sahte 0 sayılır; okey ayrıca cezalandırılır)."""
    return sum(h[t] * num(t) for t in range(52) if not is_okey(t))


def hand_str(h):
    out = []
    for t in range(NT):
        out += [name(t)] * h[t]
    return " ".join(out)


def take_okeys(h, k):
    """Elden k adet okey taşı kimliği seç (eli değiştirmez)."""
    res = []
    for o in OKEYS:
        res += [o] * h[o]
    return res[:k]
