"""Oyun (100 el) ve toplu Monte Carlo koşusu; seed ile tekrarlanabilir."""
import random
from multiprocessing import Pool

from .bots import make_bots
from .engine import HandGame
from .std_bots import make_std_bots
from .std_engine import StdHandGame

HANDS_PER_GAME = 100
NAMES = ["A", "B", "C", "D"]


def play_game(args):
    game_idx, seed, okey_ceza = args[:3]
    std = len(args) > 3 and args[3] == "std"
    Game, mk = (StdHandGame, make_std_bots) if std else (HandGame, make_bots)
    rng = random.Random(seed * 1_000_003 + game_idx)
    order = NAMES[:]
    rng.shuffle(order)  # oturma sırası
    by_name = {b.name: b for b in mk()}
    bots = [by_name[n] for n in order]
    dealer0 = rng.randrange(4)
    hands = []
    for k in range(HANDS_PER_GAME):
        dealer = (dealer0 + k) % 4  # her elde saat yönünde değişir
        r = Game(bots, dealer, rng, okey_ceza).play()
        # koltuk -> oyuncu adı eşlemesi
        r["seat_names"] = order
        hands.append(compact(r, order))
    return hands


def compact(r, order):
    """Koltuk bazlı sonucu oyuncu adı bazlı sözlüğe çevir."""
    def m(lst):
        return {order[s]: lst[s] for s in range(4)}
    return {
        "kind": r["kind"],
        "fin": order[r["fin"]] if r["fin"] is not None else None,
        "first": order[r["first_opener"]] if r["first_opener"] is not None else None,
        "scores": m(r["scores"]), "okey_pts": m(r["okey_pts"]), "pen_pts": m(r["pen_pts"]),
        "pens": m(r["pens"]), "bonus": m(r["bonus"]), "opened": m(r["opened"]),
        "turns": r["turns"], "fake": r["fake"], "swap": r["swap"],
        "mult_pts": m(r.get("mult_pts", [0] * 4)),
    }


def run(n_games, okey_ceza, seed=2026, procs=4, rules="variant"):
    args = [(i, seed, okey_ceza, rules) for i in range(n_games)]
    with Pool(procs) as pool:
        return pool.map(play_game, args, chunksize=5)
