import random

import duel11 as sim

BOOK_WOUND = sim.Fighter.wound
BOOK_TAKE_TURN = sim.take_turn
RULES = {'escalation': 0, 'heavy_limit': 0}
STATS = {'attacks': 0}


def counted_attack(attacker, defender, charging):
    STATS['attacks'] += 1
    return BOOK_ATTACK(attacker, defender, charging)


BOOK_ATTACK = sim.attack


def wound(self, severity, matrix, exhaustion_paid=False):
    BOOK_WOUND(self, severity, matrix, exhaustion_paid)
    if RULES['heavy_limit'] and self.counts[sim.HEAVY] >= RULES['heavy_limit']:
        self.out = True


def attack_cost(actor, attacks_made):
    return actor.attack_ap + actor.extra_attack_ap + RULES['escalation'] * attacks_made


def take_turn(actor, target, state):
    ap = max(0, actor.pending - actor.ap_penalty)
    actor.ap_penalty = 0
    actor.pending = 0
    actor.charge_penalty = False
    charged = rearmed = False
    made = 0
    while ap > 0 and not actor.out and not target.out:
        if actor.prone:
            if ap < sim.STAND_AP:
                break
            ap -= sim.STAND_AP
            actor.prone = False
            continue
        if actor.disarmed:
            if rearmed or ap < sim.REARM_AP:
                break
            ap -= sim.REARM_AP
            actor.disarmed = False
            rearmed = True
            continue
        cost = attack_cost(actor, made)
        if not state['engaged']:
            if actor.s.charge and not charged and not actor.no_charge and not actor.temp_no_charge and ap >= sim.CHARGE_AP + cost:
                ap -= sim.CHARGE_AP + cost
                actor.extra_attack_ap = 0
                charged = True
                made += 1
                state['engaged'] = True
                actor.charge_penalty = True
                result = sim.attack(actor, target, True)
                if result == 'disengaged':
                    state['engaged'] = False
                elif result:
                    break
                continue
            if charged or ap < sim.MOVE_AP + cost:
                break
            ap -= sim.MOVE_AP
            state['engaged'] = True
            continue
        if ap < cost:
            break
        ap -= cost
        actor.extra_attack_ap = 0
        made += 1
        result = sim.attack(actor, target, False)
        if result == 'disengaged':
            state['engaged'] = False
        elif result:
            break
    actor.end_own_turn()


def configure(escalation=0, heavy_limit=0):
    RULES['escalation'], RULES['heavy_limit'] = escalation, heavy_limit
    sim.Fighter.wound = wound
    sim.take_turn = take_turn
    sim.attack = counted_attack
