"""Per / açma çözücüleri (memoize backtracking)."""
from .tiles import tid, OKEYS, FAKE, is_okey, num

ORDER = [tid(c, n) for n in range(2, 14) for c in range(4)]
_memo = {}
MEMO_LIMIT = 1_500_000


def _solve(cnt, J, i, mode):
    while i < 48 and cnt[ORDER[i]] == 0:
        i += 1
    if i == 48:
        return (0, 0, ())
    key = (cnt, J, mode)
    r = _memo.get(key)
    if r is not None:
        return r
    t = ORDER[i]
    c, n = t // 13, t % 13 + 1
    lst = list(cnt)
    lst[t] -= 1
    base = tuple(lst)
    best = _solve(base, J, i, mode)  # taşı kullanma
    bkey = (best[1], best[0]) if mode == "v" else (best[0], best[1])

    def consider(tiles, val, desc, sub):
        nonlocal best, bkey
        cand = (sub[0] + tiles, sub[1] + val, (desc,) + sub[2])
        ck = (cand[1], cand[0]) if mode == "v" else (cand[0], cand[1])
        if ck > bkey:
            best, bkey = cand, ck

    # Gruplar: aynı sayı farklı renk, 3-4 taş
    others = [cc for cc in range(4) if cc != c and cnt[tid(cc, n)] > 0]
    m = len(others)
    for mask in range(1 << m):
        sub = tuple(others[k] for k in range(m) if mask >> k & 1)
        k = 1 + len(sub)
        if k > 4:
            continue
        l2 = list(base)
        for cc in sub:
            l2[tid(cc, n)] -= 1
        tb = tuple(l2)
        for j in range(max(0, 3 - k), min(J, 4 - k) + 1):
            consider(k + j, n * (k + j), ("G", n, (c,) + sub, j), _solve(tb, J - j, i, mode))
    # Seriler: aynı renk ardışık, 2..13, en az 3; önde L okey olabilir
    for L in range(0, min(J, n - 2) + 1):
        l2 = list(base)
        jl = J - L
        jpos = list(range(n - L, n))
        length, mm = L + 1, n + 1
        while True:
            if length >= 3:
                s = n - L
                e = mm - 1
                consider(length, (s + e) * length // 2, ("R", c, s, e, tuple(jpos)),
                         _solve(tuple(l2), jl, i, mode))
            if mm > 13:
                break
            tm = tid(c, mm)
            if l2[tm] > 0:
                l2[tm] -= 1
            elif jl > 0:
                jl -= 1
                jpos.append(mm)
            else:
                break
            length += 1
            mm += 1
    if len(_memo) > MEMO_LIMIT:
        _memo.clear()
    _memo[key] = best
    return best


def solve_sets(h, J=None, mode="t"):
    """h: 53'lük sayım listesi. J: kullanılacak okey sayısı (varsayılan: elde olan hepsi).
    mode 't': önce kullanılan taş sayısını, sonra değeri maksimize eder.
    mode 'v': önce açma değerini maksimize eder.
    Döner: (kullanılan_taş, değer, set_listesi)."""
    cnt = list(h[:52])
    for o in OKEYS:
        cnt[o] = 0
    if J is None:
        J = sum(h[o] for o in OKEYS)
    return _solve(tuple(cnt), J, 0, mode)


def solve_pairs(h, use_okeys=True):
    """Çift çözücü. Döner: (çift_sayısı, çift_listesi[(t1,t2)], artan_sayım).
    Sahte: yalnız gerçek (okey olmayan) taşla çift olur. Okey: her taşla (sahte hariç)."""
    h = list(h)
    pairs = []
    singles = []
    for t in range(52):
        if is_okey(t):
            continue
        while h[t] >= 2:
            h[t] -= 2
            pairs.append((t, t))
        if h[t] == 1:
            singles.append(t)
    singles.sort(key=num, reverse=True)  # yüksek taşları önce eşle (ceza azalır)
    while h[FAKE] > 0 and singles:
        t = singles.pop(0)
        h[FAKE] -= 1
        h[t] -= 1
        pairs.append((FAKE, t))
    if use_okeys:
        oks = [o for o in OKEYS for _ in range(h[o])]
        while oks and singles:
            o = oks.pop()
            t = singles.pop(0)
            h[o] -= 1
            h[t] -= 1
            pairs.append((o, t))
        while len(oks) >= 2:
            a, b = oks.pop(), oks.pop()
            h[a] -= 1
            h[b] -= 1
            pairs.append((a, b))
    return len(pairs), pairs, h


def set_value(desc):
    if desc[0] == "G":
        return desc[1] * (len(desc[2]) + desc[3])
    _, c, s, e, _ = desc
    return (s + e) * (e - s + 1) // 2


def set_tiles(desc):
    """Setin gerçek (okey olmayan) taşları ve okey sayısı."""
    if desc[0] == "G":
        return [tid(c, desc[1]) for c in desc[2]], desc[3]
    _, c, s, e, jp = desc
    return [tid(c, n) for n in range(s, e + 1) if n not in jp], len(jp)
