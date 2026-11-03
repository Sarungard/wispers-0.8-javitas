import random

import duel11 as sim

BOOK_WOUND = sim.Fighter.wound
BOOK_ATTACK = sim.attack
DEADLY = set()
RULES = {'armour_stops_light_escalation': False}


def roll_with_roles(dice, net):
    t, j = dice
    a, b = random.randint(1, t), random.randint(1, j)
    if net == 0:
        return a + b, b > a
    x = random.randint(1, min(t, j))
    if net > 0:
        if x > min(a, b):
            if a <= b:
                a = x
            else:
                b = x
        return a + b, b > a
    if j <= t:
        return a + min(b, x), False
    return min(a, x) + b, False


def wound(self, severity, matrix, exhaustion_paid=False):
    if RULES['armour_stops_light_escalation'] and severity == sim.LIGHT and self.defence_value:
        if self.out:
            return
        self.counts[0] += 1
        face = random.randint(1, 8) + self.counts[0] + matrix[0]
        if face < 21:
            self.light_effect(face)
        return
    return BOOK_WOUND(self, severity, matrix, exhaustion_paid)


def attack(attacker, defender, charging):
    advantages = 0
    if attacker.s.reckless or defender.s.reckless:
        advantages += 1
    if charging:
        advantages += 1
    if defender.prone:
        advantages += 1
    if defender.charge_penalty:
        advantages += 1
    disadvantages = attacker.temp_attack_dis + attacker.perm_attack_dis
    if attacker.next_attack_double_dis:
        disadvantages += 2
        attacker.next_attack_double_dis = False
    total, deadly_faces = roll_with_roles((attacker.weapon_die, sim.PROF_DIE), sim.mode_of(advantages, disadvantages))
    deadly = deadly_faces and attacker.s.weapon in DEADLY
    value = max(total - attacker.exhaustion, 1)
    reaction = defender.choose_reaction(value, advantages, charging)
    overstrike = not reaction and value >= defender.overstrike_threshold()
    hit_value = value
    if reaction:
        defender.pending -= sim.REACTION_AP[reaction]
        if reaction == 'parry':
            parry = sim.roll([sim.SHIELD_DIE, sim.PROF_DIE], defender.defence_net()) - defender.exhaustion
            if parry > value:
                return parry >= 2 * value
            overstrike = True
        elif reaction == 'dodge':
            dodge = sim.roll([sim.DEX_DIE, sim.REFLEX_DIE], defender.dodge_net()) - defender.exhaustion
            if dodge > value:
                return 'disengaged'
            overstrike = value >= 2 * max(dodge, 1)
        else:
            absorbed = min(value, defender.hardness)
            defender.hardness -= 1
            hit_value = value - absorbed
            overstrike = hit_value >= defender.overstrike_threshold()
            if defender.hardness <= 0:
                defender.hardness = 0
                defender.defence_value = 0
    if overstrike:
        defender.wound(sim.HEAVY, attacker.matrix)
        return False
    severity = defender.severity(hit_value)
    if deadly:
        severity = min(severity + 1, sim.HEAVY)
    for _ in range(sim.CHARGE_AP if charging else 1):
        defender.wound(severity, attacker.matrix)
    return False


def configure(stop_light_escalation=False, deadly=()):
    RULES['armour_stops_light_escalation'] = stop_light_escalation
    DEADLY.clear()
    DEADLY.update(deadly)
    sim.Fighter.wound = wound
    sim.attack = attack
