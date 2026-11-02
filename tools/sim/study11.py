import random
import sys
from collections import defaultdict
from multiprocessing import Pool

import importlib, os
duel2 = importlib.import_module(os.environ.get("SIM", "duel9"))

ONE_HANDED_ARMOURED = [('parry', 'brace'), ('dodge', 'brace'), ('brace',), ('dodge',), ()]
TWO_HANDED_ARMOURED = [('dodge', 'brace'), ('brace',), ('dodge',), ()]
ONE_HANDED_BARE = [('parry',), ('dodge',), ()]
TWO_HANDED_BARE = [('dodge',), ()]

_pool = None
_cap = None
_armour = None
_trials = None

VARIANTS = {
    'alap': {},
    'rovidkard223': {'Rövidkard': (4, 2, (2, 2, 3), False)},
    'konnyu2': {'Rövidkard': (4, 2, (2, 2, 1), False), 'Csatabárd': (8, 4, (2, 3, 3), False), 'Nagykalapács': (10, 4, (2, 4, 4), True)},
}


def apply_variant(name):
    endurance, dex, reflex = (int(x) for x in name.split('-'))
    duel2.ENDURANCE, duel2.DEX_DIE, duel2.REFLEX_DIE = endurance, dex, reflex


def strategies(cap, armoured):
    openings = sorted({min(b, cap) for b in (2, 4, 6, 8, 12, cap)})
    laters = sorted({min(b, cap) for b in (4, 8, cap)})
    result = []
    for weapon in duel2.WEAPONS:
        for reactions in ((),):
            for reckless in (False, True):
                for charge in (False, True):
                    for opening in openings:
                        for later in laters:
                            result.append(duel2.Strategy(weapon, reactions, reckless, charge, opening, later))
    return result


def init(pool, cap, armour, trials, variant):
    global _pool, _cap, _armour, _trials
    _pool, _cap, _armour, _trials = pool, cap, armour, trials
    apply_variant(variant)


def row(i):
    random.seed(i * 7919 + _cap)
    first = _pool[i]
    return [sum(duel2.duel(first, second, _cap, _armour) for _ in range(_trials)) / _trials for second in _pool]


def fictitious_play(matrix, iterations):
    n, m = len(matrix), len(matrix[0])
    row_payoff = [0.0] * n
    col_payoff = [0.0] * m
    row_counts = [0] * n
    col_counts = [0] * m
    r, c = 0, 0
    for _ in range(iterations):
        row_counts[r] += 1
        col_counts[c] += 1
        for j in range(m):
            col_payoff[j] += matrix[r][j]
        for i in range(n):
            row_payoff[i] += matrix[i][c]
        r = max(range(n), key=row_payoff.__getitem__)
        c = min(range(m), key=col_payoff.__getitem__)
    total = sum(row_counts)
    row_mix = [k / total for k in row_counts]
    col_mix = [k / total for k in col_counts]
    value = sum(row_mix[i] * col_mix[j] * matrix[i][j] for i in range(n) if row_mix[i] for j in range(m) if col_mix[j])
    return row_mix, col_mix, value


def reaction_usage(pool, cap, armour):
    def measure(row_mix, col_mix, samples=4000):
        counts = defaultdict(int)
        original = duel2.Fighter.choose_reaction
        def counting(self, value, advantages, charging):
            choice = original(self, value, advantages, charging)
            counts[choice] += 1
            return choice
        duel2.Fighter.choose_reaction = counting
        rng = random.Random(1)
        rows = rng.choices(pool, weights=row_mix, k=samples)
        cols = rng.choices(pool, weights=col_mix, k=samples)
        for a, b in zip(rows, cols):
            duel2.duel(a, b, cap, armour)
        duel2.Fighter.choose_reaction = original
        total = sum(counts.values()) or 1
        names = {None: 'nincs reakció', 'parry': 'Hárítás', 'dodge': 'Kitérés', 'brace': 'Beleállás'}
        return sorted(((names[k], v / total) for k, v in counts.items()), key=lambda kv: -kv[1])
    return measure


def shares(pool, mix, key):
    out = defaultdict(float)
    for s, w in zip(pool, mix):
        out[key(s)] += w
    return sorted(out.items(), key=lambda kv: -kv[1])


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    trials = int(sys.argv[1])
    variant = sys.argv[3]
    apply_variant(variant)
    armoured = sys.argv[2].startswith('pancel')
    armour = (4, int(sys.argv[2][6:] or 4)) if armoured else (0, 0)
    for cap in map(int, sys.argv[4:]):
        pool = strategies(cap, armoured)
        with Pool(6, initializer=init, initargs=(pool, cap, armour, trials, variant)) as workers:
            matrix = workers.map(row, range(len(pool)), chunksize=8)
        row_mix, col_mix, value = fictitious_play(matrix, 20000)
        reactions = reaction_usage(pool, cap, armour)
        title = f'páncél (Védőérték {armour[0]}, Keménység {armour[1]})' if armoured else 'páncél nélkül'
        print(f'=== [Állóképesség-Ügyességkocka-Reflexkocka {variant}] {title}, felső határ {cap}, {len(pool)} stratégia, {trials} párbaj/párosítás')
        print(f'  a játék értéke a játékosnak (döntetlennél ő lép előbb): {value:.2f}')
        for who, mix in (('játékos', row_mix), ('ellenfél', col_mix)):
            top = sorted(zip(pool, mix), key=lambda sw: -sw[1])[:4]
            print(f'  {who} egyensúlyi keveréke: ' + ' | '.join(f'{w:.0%} {s.label(cap)}' for s, w in top if w > 0.01))
            print('    fegyver: ' + ', '.join(f'{k} {w:.0%}' for k, w in shares(pool, mix, lambda s: s.weapon) if w > 0.01))
            print('    nyitó licit: ' + ', '.join(f'{k} {w:.0%}' for k, w in shares(pool, mix, lambda s: min(s.opening, cap)) if w > 0.01))
            print('    Féktelen: ' + f'{sum(w for s, w in zip(pool, mix) if s.reckless):.0%}' + ', roham: ' + f'{sum(w for s, w in zip(pool, mix) if s.charge):.0%}')
        print('  reakciók az egyensúlyi párbajokban: ' + ', '.join(f'{k} {v:.0%}' for k, v in reactions(row_mix, col_mix)))
        by_weapon = defaultdict(list)
        for i, s in enumerate(pool):
            vs_mix = sum(col_mix[j] * matrix[i][j] for j in range(len(pool)) if col_mix[j])
            by_weapon[s.weapon].append((vs_mix, s.label(cap)))
        print('  fegyverenként a legjobb stratégia az ellenfél egyensúlya ellen:')
        for weapon, rows in by_weapon.items():
            best = max(rows)
            print(f'    {best[0]:.2f}  {best[1]}')
        sys.stdout.flush()


if __name__ == '__main__':
    main()
