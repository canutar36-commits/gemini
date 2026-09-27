"""Standart 101: doğrulama + 1000 oyun + rapor (rapor_standart.md, out_std/)."""
import pickle, sys, time
from okey101 import sim, std_report

if __name__ == "__main__":
    n_games = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    val_res, val_log = std_report.validate()
    print("Doğrulama: 10 el geçti:", [r["kind"] for r in val_res], flush=True)
    t = time.time()
    data = sim.run(n_games, 101, seed=2026, rules="std")
    print(f"{n_games} oyun {time.time()-t:.0f} sn", flush=True)
    pickle.dump(data, open("out_std/raw.pkl", "wb"))
    std_report.build(data, val_res, val_log, n_games)
