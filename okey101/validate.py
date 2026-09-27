"""10 ellik doğrulama koşusu: taş korunumu + puan/tür assert'leri + örnek el logu."""
import random

from .bots import make_bots
from .engine import HandGame


def validate(okey_ceza=50, seed=7, n=10):
    rng = random.Random(seed)
    bots = make_bots()
    results, sample_log = [], None
    for k in range(n):
        g = HandGame(bots, k % 4, rng, okey_ceza, log=True, check=True)
        r = g.play()
        results.append(r)
        C = okey_ceza
        # ek dış kontroller
        if r["kind"] == "deste":
            assert all(v % C == 0 for v in r["scores"])
        else:
            f = r["fin"]
            exp = {"normal": -101, "okey": -202, "cift": -202, "cift_okey": -404, "elden": -202}[r["kind"]]
            assert r["scores"][f] == exp + r["bonus"][f] + r["pen_pts"][f]
            if r["kind"] == "elden":
                assert sorted(r["scores"])[1:] == [404, 404, 404]
        if sample_log is None and r["kind"] != "deste" and len(g.logs) > 12:
            sample_log = g.logs
    return results, sample_log or g.logs
