import random, sys
from multiprocessing import Pool
import h67_diag as d
sim = d.sim
OLD_MIX = [('Rövidkard', (20, 8), False, True, 33), ('Rövidkard', (20, 8), False, False, 18), ('Rövidkard', (12, 20), False, False, 18), ('Rövidkard', (20, 20), True, True, 18)]
NEW_MIX = [('Rövidkard', (20, 8), True, True, 43), ('Rövidkard', (20, 20), False, True, 14), ('Rövidkard', (20, 8), False, True, 14), ('Rövidkard', (20, 20), True, True, 11), ('Nagykalapács', (20, 20), True, True, 11)]
PLAYERS = {'Hosszúkard sima 20→20': ('Hosszúkard', False, False), 'Hosszúkard F+R 20→20': ('Hosszúkard', True, True), 'Nagykalapács F+R 20→20': ('Nagykalapács', True, True), 'Rövidkard F 20→20': ('Rövidkard', True, False)}
def task(args):
    var, pname, mixname = args
    sim.ENDURANCE, sim.DEX_DIE, sim.REFLEX_DIE = 5, 6, 4
    d.configure(var); random.seed(29)
    w, r, c = PLAYERS[pname]
    p = sim.Strategy(w, (), r, c, 20, 20)
    mix = OLD_MIX if mixname == 'régi keverék' else NEW_MIX
    tot = wt = 0
    for ow, (o, l), orr, oc, k in mix:
        q = sim.Strategy(ow, (), orr, oc, o, l)
        tot += k * sum(sim.duel(p, q, 20, (4, 4)) for _ in range(3000)) / 3000; wt += k
    return args, tot / wt
if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    jobs = [(v, p, m) for v in ('régi táblák', 'új táblák') for p in PLAYERS for m in ('régi keverék', 'új keverék')]
    with Pool(6) as pool: out = dict(pool.map(task, jobs))
    for p in PLAYERS:
        for m in ('régi keverék', 'új keverék'):
            print(f'{p:26} {m:13} régi {out[("régi táblák",p,m)]:.3f}  új {out[("új táblák",p,m)]:.3f}')
