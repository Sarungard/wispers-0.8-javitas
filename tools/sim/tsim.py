import random

import duel11 as sim

BOOK_ATTACK = sim.attack
BOOK_TURN = 21
RULES = {'turn': BOOK_TURN}
STATS = {'attacks': 0, 'rolls': 0}


def book_row(face):
    turn = RULES['turn']
    if face < 2 or turn == BOOK_TURN:
        return face
    return min(20, 2 + round((face - 2) * 18 / (turn - 3)))


def wound(self, severity, matrix, exhaustion_paid=False):
    if self.out:
        return
    STATS['rolls'] += 1
    self.counts[severity] += 1
    face = random.randint(1, 8) + self.counts[severity] + matrix[severity]
    if face >= RULES['turn']:
        if severity == sim.HEAVY:
            self.out = True
            return
        self.counts[severity] -= 1
        wound(self, severity + 1, matrix, exhaustion_paid=severity >= sim.DEEP)
        return
    (self.light_effect, self.deep_effect, self.heavy_effect)[severity](book_row(face))


def counted_attack(attacker, defender, charging):
    STATS['attacks'] += 1
    return BOOK_ATTACK(attacker, defender, charging)


def configure(turn=BOOK_TURN):
    RULES['turn'] = turn
    sim.Fighter.wound = wound
    sim.attack = counted_attack
