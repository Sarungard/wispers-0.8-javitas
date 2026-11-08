import random
import sys
from multiprocessing import Pool
from statistics import mean, median

import v22sim

sim = v22sim.sim
VARIANTS = {
    'könyv': (20, {}),
    'licitplafon 12': (12, {}),
    'licitplafon 10': (10, {}),
    'emelkedő támadásár (+1 AP minden korábbi támadásért a körben)': (20, {'escalation': 1}),
    'Súlyos-korlát 3 (a 3. Súlyos seb kiejt)': (20, {'heavy_limit': 3}),
    'emelkedő támadásár + Súlyos-korlát 3': (20, {'escalation': 1, 'heavy_limit': 3}),
}
ARMOURS = ((4, 4), (0, 0))
WEAPONS = list(sim.WEAPONS)
TRIALS = 1000


def task(args):
    variant, armour, w, o = args
    cap, rules = VARIANTS[variant]
    sim.ENDURANCE, sim.DEX_DIE, sim.REFLEX_DIE = 5, 6, 4
    v22sim.configure(**rules)
    random.seed(17)
    a = sim.Strategy(w, (), True, False, cap, cap)
    b = sim.Strategy(o, (), True, False, cap, cap)
    results, attacks = [], []
    for _ in range(TRIALS):
        v22sim.STATS['attacks'] = 0
        results.append(sim.duel(a, b, cap, armour))
        attacks.append(v22sim.STATS['attacks'])
    return args, mean(results), attacks


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    jobs = [(v, ar, w, o) for v in VARIANTS for ar in ARMOURS for w in WEAPONS for o in WEAPONS]
    with Pool(6) as workers:
        out = {args: (score, attacks) for args, score, attacks in workers.map(task, jobs, chunksize=4)}
    for v in VARIANTS:
        print('===', v)
        for ar in ARMOURS:
            title = 'páncél 4/4' if ar[0] else 'páncél nélkül'
            avg = {w: mean((out[(v, ar, w, o)][0] + 1 - out[(v, ar, o, w)][0]) / 2 for o in WEAPONS if o != w) for w in WEAPONS}
            all_attacks = [n for w in WEAPONS for o in WEAPONS for n in out[(v, ar, w, o)][1]]
            mirror = mean(out[(v, ar, w, w)][0] for w in WEAPONS)
            print(f'  {title}: ' + ' / '.join(f'{avg[w]:.2f}' for w in WEAPONS)
                  + f'  | támadás/párbaj medián {median(all_attacks):.0f}, átlag {mean(all_attacks):.0f}'
                  + f' | tükörben az első {mirror:.2f}')
    print('(fegyverek: ' + ' / '.join(WEAPONS) + '; Féktelen, mindkét sorrend átlaga)')


if __name__ == '__main__':
    main()
