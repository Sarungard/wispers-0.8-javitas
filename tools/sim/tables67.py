import random

import tsim

sim = tsim.sim
TURN = 12
BOOK = (sim.Fighter.light_effect, sim.Fighter.deep_effect, sim.Fighter.heavy_effect, sim.take_turn)


def light_effect(self, face):
    if face == 5:
        self.no_dodge = 1
    elif face == 7:
        self.extra_attack_ap = 1
    elif face == 8:
        self.ap_penalty = 2
    elif face == 9:
        self.temp_no_charge = 1
    elif face == 10:
        self.prone = True
    elif face == 11:
        self.no_react = 1


def lose_finger_or_ear(self):
    if random.random() < 0.5:
        self.perm_attack_dis = 1
    if not self.bleeding and not self.bleed_pending:
        self.bleed_pending = random.randint(1, 4)


def deep_effect(self, face):
    if face == 5:
        self.no_react = 1
    elif face == 6:
        self.perm_attack_dis = 1
    elif face == 7:
        self.no_charge = True
    elif face == 8:
        self.disarmed = True
    elif face == 9:
        self.fracture('kar')
    elif face == 10:
        self.fracture('láb')
    elif face == 11:
        lose_finger_or_ear(self)


def heavy_effect(self, face):
    if face == 3:
        self.fracture(random.choice(('kar', 'láb')))
    elif face == 4:
        self.shocked = True
    elif face == 6:
        self.perm_attack_dis = self.perm_defence_dis = 1
    elif face == 7:
        self.amputation()
    elif face in (8, 11):
        self.out = True
    elif face == 9:
        self.severe_bleeding()
    elif face == 10:
        self.internal_bleeding()


def wound(self, severity, matrix, exhaustion_paid=False):
    if self.out:
        return
    tsim.STATS['rolls'] += 1
    self.counts[severity] += 1
    face = random.randint(1, 8) + self.counts[severity] + matrix[severity]
    if face >= TURN:
        if severity == sim.HEAVY:
            self.out = True
            return
        self.counts[severity] -= 1
        wound(self, severity + 1, matrix, exhaustion_paid=severity >= sim.DEEP)
        return
    (self.light_effect, self.deep_effect, self.heavy_effect)[severity](face)


def skip_shocked_turn(actor):
    actor.shocked = False
    actor.pending = actor.ap_penalty = 0
    actor.charge_penalty = False
    actor.end_own_turn()


def take_turn(actor, target, state):
    if getattr(actor, 'shocked', False):
        skip_shocked_turn(actor)
        return
    BOOK[3](actor, target, state)


def use_book_tables():
    tsim.configure(TURN)
    sim.Fighter.light_effect, sim.Fighter.deep_effect, sim.Fighter.heavy_effect, sim.take_turn = BOOK


def use_h67_tables():
    tsim.configure(TURN)
    sim.Fighter.wound = wound
    sim.Fighter.light_effect, sim.Fighter.deep_effect, sim.Fighter.heavy_effect = light_effect, deep_effect, heavy_effect
    sim.take_turn = take_turn
