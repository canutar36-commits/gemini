"""Ana giriş: doğrulama + C=50 ve C=20 senaryoları + rapor/grafik üretimi."""
import json, pickle, sys, time
from okey101 import sim, validate, report

if __name__ == "__main__":
    n_games = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    val_res, val_log = validate.validate()
    print("Doğrulama: 10 el, tüm assert'ler geçti:", [r["kind"] for r in val_res])
    data = {}
    for C in (50, 20):
        t = time.time()
        data[C] = sim.run(n_games, C, seed=2026)
        print(f"C={C}: {n_games} oyun {time.time()-t:.0f} sn")
    with open("out/raw.pkl", "wb") as f:
        pickle.dump(data, f)
    report.build(data, val_res, val_log, n_games)
