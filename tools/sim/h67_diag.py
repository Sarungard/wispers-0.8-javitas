import random
import sys
from multiprocessing import Pool

import tables67
import tsim

sim = tsim.sim
OLD = tables67.BOOK[:3]
NEW = (tables67.light_effect, tables67.deep_effect, tables67.heavy_effect)
ARMOUR = (4, 4)
CAP = 20
TRIALS = 2000
PLAYERS = ['Rövidkard', 'Hosszúkard', 'Csatabárd', 'Nagykalapács']
OPPONENTS = [((20, 8), False, True, 33), ((20, 8), False, False, 18), ((12, 20), False, False, 18), ((20, 20), True, True, 18)]


def heavy_with(face_overrides):
    def heavy(self, face):
        if face in face_overrides:
            face_overrides[face](self)
            return
        tables67.heavy_effect(self, face)
    return heavy


VARIANTS = {
    'régi táblák': ((False, False, False), None),
    'új táblák': ((True, True, True), None),
    'csak az új Könnyű': ((True, False, False), None),
    'csak az új Mély': ((False, True, False), None),
    'csak az új Súlyos': ((False, False, True), None),
    'új, de Ájulás → belső vérzés': ((True, True, True), {8: sim.Fighter.internal_bleeding}),
    'új, de Csonkolás → súlyos vérzés': ((True, True, True), {7: sim.Fighter.severe_bleeding}),
    'új, de Sokk → eltört láb': ((True, True, True), {4: lambda f: f.fracture('láb')}),
}


def effect_for(new_flags, heavy_override, severity):
    if not new_flags[severity]:
        return lambda self, face: OLD[severity](self, tsim.book_row(face))
    if severity == sim.HEAVY and heavy_override:
        return heavy_with(heavy_override)
    return NEW[severity]


def configure(name):
    new_flags, heavy_override = VARIANTS[name]
    tables67.use_h67_tables()
    effects = [effect_for(new_flags, heavy_override, s) for s in range(3)]

    def wound(self, severity, matrix, exhaustion_paid=False):
        if self.out:
            return
        self.counts[severity] += 1
        face = random.randint(1, 8) + self.counts[severity] + matrix[severity]
        if face >= tables67.TURN:
            if severity == sim.HEAVY:
                self.out = True
                return
            self.counts[severity] -= 1
            wound(self, severity + 1, matrix)
            return
        effects[severity](self, face)

    sim.Fighter.wound = wound


def task(args):
    name, weapon = args
    sim.ENDURANCE, sim.DEX_DIE, sim.REFLEX_DIE = 5, 6, 4
    configure(name)
    random.seed(23)
    player = sim.Strategy(weapon, (), True, True, CAP, CAP)
    total = weight = 0
    for (opening, later), reckless, charge, w in OPPONENTS:
        opponent = sim.Strategy('Rövidkard', (), reckless, charge, opening, later)
        score = sum(sim.duel(player, opponent, CAP, ARMOUR) for _ in range(TRIALS)) / TRIALS
        total += w * score
        weight += w
    return args, total / weight


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    jobs = [(name, weapon) for name in VARIANTS for weapon in PLAYERS]
    with Pool(6) as workers:
        out = dict(workers.map(task, jobs))
    print(f'páncél 4/4; játékos: licit 20→20, Féktelen, roham; ellenfél: a régi egyensúly Rövidkard-keveréke; {TRIALS} párbaj/párosítás')
    print('változat'.ljust(36) + ''.join(w.rjust(14) for w in PLAYERS))
    for name in VARIANTS:
        print(name.ljust(36) + ''.join(f'{out[(name, w)]:14.3f}' for w in PLAYERS))


if __name__ == '__main__':
    main()
