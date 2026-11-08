import random
import sys
from multiprocessing import Pool
from statistics import mean, median

import tsim

sim = tsim.sim
VARIANTS = [tuple(map(int, v.split('/'))) for v in sys.argv[1:]] or [(t, 20) for t in (21, 18, 16, 14, 12)]
ARMOURS = ((4, 4), (0, 0))
WEAPONS = list(sim.WEAPONS)
TRIALS = 1000


def task(args):
    (turn, cap), armour, w, o = args
    sim.ENDURANCE, sim.DEX_DIE, sim.REFLEX_DIE = 5, 6, 4
    tsim.configure(turn)
    random.seed(17)
    a = sim.Strategy(w, (), True, False, cap, cap)
    b = sim.Strategy(o, (), True, False, cap, cap)
    results, attacks, rolls = [], [], []
    for _ in range(TRIALS):
        tsim.STATS['attacks'] = tsim.STATS['rolls'] = 0
        results.append(sim.duel(a, b, cap, armour))
        attacks.append(tsim.STATS['attacks'])
        rolls.append(tsim.STATS['rolls'])
    return args, mean(results), attacks, rolls


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    jobs = [(t, ar, w, o) for t in VARIANTS for ar in ARMOURS for w in WEAPONS for o in WEAPONS]
    with Pool(6) as workers:
        out = {args: rest for args, *rest in workers.map(task, jobs, chunksize=4)}
    for t in VARIANTS:
        print(f'=== fordulópont {t[0]}+, licitplafon {t[1]}')
        for ar in ARMOURS:
            title = 'páncél 4/4' if ar[0] else 'páncél nélkül'
            avg = {w: mean((out[(t, ar, w, o)][0] + 1 - out[(t, ar, o, w)][0]) / 2 for o in WEAPONS if o != w) for w in WEAPONS}
            attacks = [n for w in WEAPONS for o in WEAPONS for n in out[(t, ar, w, o)][1]]
            rolls = [n for w in WEAPONS for o in WEAPONS for n in out[(t, ar, w, o)][2]]
            mirror = mean(out[(t, ar, w, w)][0] for w in WEAPONS)
            print(f'  {title}: ' + ' / '.join(f'{avg[w]:.2f}' for w in WEAPONS)
                  + f'  | támadás/párbaj medián {median(attacks):.0f}, átlag {mean(attacks):.0f}'
                  + f' | sebdobás/párbaj medián {median(rolls):.0f}, átlag {mean(rolls):.0f}'
                  + f' | tükörben az első {mirror:.2f}')
    print('(fegyverek: ' + ' / '.join(WEAPONS) + '; Féktelen, reakció nélkül, mindkét sorrend átlaga)')


if __name__ == '__main__':
    main()
