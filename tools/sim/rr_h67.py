import random
import sys
from multiprocessing import Pool
from statistics import mean, median

import tables67
import tsim

sim = tsim.sim
VARIANTS = {'régi páros sorok': tables67.use_book_tables, 'H-67 táblák': tables67.use_h67_tables}
ARMOURS = ((4, 4), (0, 0))
WEAPONS = list(sim.WEAPONS)
TRIALS = 1000
CAP = 20


def task(args):
    variant, armour, w, o = args
    sim.ENDURANCE, sim.DEX_DIE, sim.REFLEX_DIE = 5, 6, 4
    VARIANTS[variant]()
    random.seed(17)
    a = sim.Strategy(w, (), True, False, CAP, CAP)
    b = sim.Strategy(o, (), True, False, CAP, CAP)
    results, attacks, rolls = [], [], []
    for _ in range(TRIALS):
        tsim.STATS['attacks'] = tsim.STATS['rolls'] = 0
        results.append(sim.duel(a, b, CAP, armour))
        attacks.append(tsim.STATS['attacks'])
        rolls.append(tsim.STATS['rolls'])
    return args, mean(results), attacks, rolls


def report(out, variant):
    print(f'=== {variant} (fordulópont 12+, licitplafon {CAP})')
    for ar in ARMOURS:
        title = 'páncél 4/4' if ar[0] else 'páncél nélkül'
        avg = {w: mean((out[(variant, ar, w, o)][0] + 1 - out[(variant, ar, o, w)][0]) / 2 for o in WEAPONS if o != w) for w in WEAPONS}
        attacks = [n for w in WEAPONS for o in WEAPONS for n in out[(variant, ar, w, o)][1]]
        rolls = [n for w in WEAPONS for o in WEAPONS for n in out[(variant, ar, w, o)][2]]
        mirror = mean(out[(variant, ar, w, w)][0] for w in WEAPONS)
        print(f'  {title}: ' + ' / '.join(f'{avg[w]:.2f}' for w in WEAPONS)
              + f'  | támadás/párbaj medián {median(attacks):.0f}, átlag {mean(attacks):.0f}'
              + f' | sebdobás/párbaj medián {median(rolls):.0f}, átlag {mean(rolls):.0f}'
              + f' | tükörben az első {mirror:.2f}')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    jobs = [(v, ar, w, o) for v in VARIANTS for ar in ARMOURS for w in WEAPONS for o in WEAPONS]
    with Pool(6) as workers:
        out = {args: rest for args, *rest in workers.map(task, jobs, chunksize=4)}
    for variant in VARIANTS:
        report(out, variant)
    print('(fegyverek: ' + ' / '.join(WEAPONS) + '; Féktelen, reakció nélkül, mindkét sorrend átlaga)')


if __name__ == '__main__':
    main()
