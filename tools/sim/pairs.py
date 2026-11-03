import random
import sys
from multiprocessing import Pool
from statistics import mean

import h66sim

sim = h66sim.sim
CONFIGS = {
    'könyv (azonos attack-kód)': {},
    'P2': {'stop_light_escalation': True},
    'P2 + Halálos a Tőrön': {'stop_light_escalation': True, 'deadly': {'Tőr'}},
    'P2 + Halálos a Tőrön és a Rövidkardon': {'stop_light_escalation': True, 'deadly': {'Tőr', 'Rövidkard'}},
}
ARMOURS = ((4, 4), (6, 6), (0, 0))
WEAPONS = list(sim.WEAPONS)
TRIALS = 1500


def win(a, b, armour):
    random.seed(5)
    return mean(sim.duel(a, b, 20, armour) for _ in range(TRIALS))


def pair(task):
    config, armour, w, o = task
    sim.ENDURANCE, sim.DEX_DIE, sim.REFLEX_DIE = 5, 6, 4
    h66sim.configure(**CONFIGS[config])
    a = sim.Strategy(w, (), True, False, 20, 20)
    b = sim.Strategy(o, (), True, False, 20, 20)
    return task, (win(a, b, armour) + 1 - win(b, a, armour)) / 2


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    tasks = [(c, ar, w, o) for c in CONFIGS for ar in ARMOURS for w in WEAPONS for o in WEAPONS if o != w]
    with Pool(6) as workers:
        results = dict(workers.map(pair, tasks, chunksize=4))
    for c in CONFIGS:
        print('===', c)
        for ar in ARMOURS:
            print(f'  páncél {ar}: a fegyver átlagos esélye a többi ellen (mindkét sorrend, Féktelen)')
            for w in WEAPONS:
                vals = [results[(c, ar, w, o)] for o in WEAPONS if o != w]
                print(f'    {w:13s} {mean(vals):.2f}  (' + ', '.join(f'{x:.2f}' for x in vals) + ')')


if __name__ == '__main__':
    main()
