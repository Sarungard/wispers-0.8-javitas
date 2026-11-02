import random
from functools import lru_cache

DICE = [4, 6, 8, 10, 12]
ENDURANCE = 3
BASE_THRESHOLD = 4
SHIELD_DIE = 6
PROF_DIE = 4
DEX_DIE = 4
REFLEX_DIE = 4
REACTION_AP = {'parry': 1, 'dodge': 2, 'brace': 0}
MOVE_AP = 2
CHARGE_AP = 2
STAND_AP = 1
REARM_AP = 1
MAX_ROUNDS = 40
LIGHT, DEEP, HEAVY = 0, 1, 2

WEAPONS = {
    'Tőr': (4, 2, (1, 1, 4), False),
    'Rövidkard': (4, 2, (2, 2, 3), False),
    'Hosszúkard': (6, 3, (2, 2, 3), False),
    'Csatabárd': (8, 4, (1, 4, 2), False),
    'Nagykalapács': (10, 4, (3, 4, 3), True),
}

REACTION_NAMES = {'parry': 'Hárítás', 'dodge': 'Kitérés', 'brace': 'Beleállás'}


def duel_endurance():
    return ENDURANCE


def mode_of(advantages, disadvantages):
    return (1 if advantages > 0 else 0) - (1 if disadvantages > 0 else 0)


def sign(net):
    return (net > 0) - (net < 0)


def roll(dice, net):
    t, j = dice
    a, b = random.randint(1, t), random.randint(1, j)
    net = sign(net)
    if net == 0:
        return a + b
    x = random.randint(1, min(t, j))
    if net > 0:
        return max(a, b) + max(min(a, b), x)
    if j <= t:
        return a + min(b, x)
    return min(a, x) + b


@lru_cache(maxsize=None)
def distribution(dice, net):
    t, j = dice
    small = min(t, j)
    dist = {}
    for a in range(1, t + 1):
        for b in range(1, j + 1):
            if net == 0:
                dist[a + b] = dist.get(a + b, 0.0) + 1 / (t * j)
                continue
            for x in range(1, small + 1):
                if net > 0:
                    v = max(a, b) + max(min(a, b), x)
                elif j <= t:
                    v = a + min(b, x)
                else:
                    v = min(a, x) + b
                dist[v] = dist.get(v, 0.0) + 1 / (t * j * small)
    return tuple(sorted(dist.items()))


def chance_above(dice, net, exhaustion, threshold):
    return sum(p for total, p in distribution(tuple(dice), sign(net)) if total - exhaustion > threshold)


def chance_at_most(dice, net, exhaustion, threshold):
    return sum(p for total, p in distribution(tuple(dice), sign(net)) if total - exhaustion <= threshold)


HARM = {0: 0.4, 1: 1.5, 2: 4.0}
AP_WEIGHT = 0.3
END_TURN_BONUS = 1.0
DISENGAGE_BONUS = 0.3
HARDNESS_WEIGHT = 0.1
ARMOUR_BREAK_WEIGHT = 1.0


class Strategy:
    __slots__ = ('weapon', 'reactions', 'reckless', 'charge', 'opening', 'later')

    def __init__(self, weapon, reactions, reckless, charge, opening, later):
        self.weapon, self.reactions, self.reckless = weapon, reactions, reckless
        self.charge, self.opening, self.later = charge, opening, later

    def label(self, cap):
        bids = f'{min(self.opening, cap)}→{min(self.later, cap)}'
        extras = ''.join([', Féktelen' if self.reckless else '', ', roham' if self.charge else ''])
        return f'{self.weapon}, licit {bids}{extras}'


class Fighter:
    def __init__(self, strategy, cap, armour, first_on_ties):
        self.s = strategy
        die, ap, matrix, two_handed = WEAPONS[strategy.weapon]
        self.weapon_die, self.attack_ap, self.matrix = die, ap, matrix
        self.has_shield = not two_handed
        self.defence_value, self.hardness = armour
        self.first_on_ties = first_on_ties
        self.opening, self.later = max(1, min(strategy.opening, cap)), max(1, min(strategy.later, cap))
        self.pending = self.opening
        self.exhaustion = 0
        self.counts = [0, 0, 0]
        self.out = False
        self.prone = self.disarmed = self.no_charge = False
        self.temp_attack_dis = self.temp_defence_dis = self.no_react = 0
        self.next_attack_double_dis = False
        self.perm_attack_dis = self.perm_defence_dis = 0
        self.bleeding = self.bleed_pending = 0
        self.open_fracture = False
        self.charge_penalty = False
        self.dodge_dis = 1 if self.defence_value > 0 else 0
        self.no_dodge = self.temp_no_charge = 0
        self.extra_attack_ap = self.ap_penalty = 0

    def thresholds(self):
        light = BASE_THRESHOLD + self.defence_value
        return light, light + 5

    def overstrike_threshold(self):
        return self.thresholds()[1] + BASE_THRESHOLD + 5

    def add_exhaustion(self, amount):
        self.exhaustion += amount
        if self.exhaustion > duel_endurance():
            self.out = True

    def severity(self, value):
        light, heavy = self.thresholds()
        return HEAVY if value >= heavy else DEEP if value >= light else LIGHT

    def wound(self, severity, matrix, exhaustion_paid=False):
        if self.out:
            return
        self.counts[severity] += 1
        face = random.randint(1, 8) + self.counts[severity] + matrix[severity]
        if face >= 21:
            if severity == HEAVY:
                self.out = True
                return
            self.counts[severity] -= 1
            self.wound(severity + 1, matrix, exhaustion_paid=severity >= DEEP)
            return
        (self.light_effect, self.deep_effect, self.heavy_effect)[severity](face)

    def fracture(self, limb):
        if limb == 'kar':
            self.perm_attack_dis = 1
        elif limb == 'láb':
            self.dodge_dis = 1
            self.no_charge = True

    def amputation(self):
        self.perm_attack_dis = self.perm_defence_dis = 1
        if not self.bleeding and not self.bleed_pending:
            self.bleed_pending = random.randint(1, 4)

    def severe_bleeding(self):
        if not self.bleeding:
            self.bleeding = sum(random.randint(1, 4) for _ in range(3))

    def internal_bleeding(self):
        timer = sum(random.randint(1, 4) for _ in range(2))
        self.bleeding = min(self.bleeding, timer) if self.bleeding else timer

    def light_effect(self, face):
        if face == 7:
            self.no_dodge = 1
        elif face == 9:
            self.extra_attack_ap = 1
        elif face == 10:
            self.ap_penalty = 2
        elif face == 12:
            self.temp_no_charge = 1
        elif face == 13:
            self.no_react = 1
        elif face == 15:
            self.prone = True
        elif face in (16, 17):
            self.disarmed = True
        elif face == 20:
            self.prone = True
            self.no_react = 1

    def deep_effect(self, face):
        if face == 6:
            self.perm_attack_dis = 1
        elif face == 7:
            self.no_react = 1
        elif face == 8:
            self.disarmed = True
        elif face == 9:
            self.no_charge = True
        elif face == 11:
            self.fracture('kar')
        elif face == 13:
            self.fracture('láb')
        elif face == 14:
            if random.random() < 0.5:
                self.perm_attack_dis = 1
            if not self.bleeding and not self.bleed_pending:
                self.bleed_pending = random.randint(1, 4)
        elif face in (18, 19):
            self.perm_attack_dis = self.perm_defence_dis = 1
        elif face == 20:
            self.amputation()

    def heavy_effect(self, face):
        if face in (4, 5):
            self.fracture('kar')
        elif face == 6:
            self.fracture('láb')
        elif face in (7, 20):
            self.out = True
        elif face == 8:
            self.perm_attack_dis = self.perm_defence_dis = 1
        elif face in (9, 11):
            self.amputation()
        elif face == 12:
            self.severe_bleeding()
        elif face == 13:
            self.severe_bleeding()
            self.fracture(random.choice(('kar', 'láb')))
        elif face == 14:
            self.internal_bleeding()
        elif face == 15:
            self.amputation()
            self.severe_bleeding()
        elif face in (16, 17):
            self.internal_bleeding()
            self.fracture(random.choice(('kar', 'láb')))
        elif face in (18, 19):
            self.internal_bleeding()

    def defence_net(self):
        return -(self.temp_defence_dis + self.perm_defence_dis + (1 if self.charge_penalty else 0))

    def dodge_net(self):
        return self.defence_net() - self.dodge_dis

    def choose_reaction(self, value, advantages, charging):
        hits = CHARGE_AP if charging else 1
        severity = self.severity(value)
        unanswered_overstrike = value >= self.overstrike_threshold()
        options = {None: HARM[2] if unanswered_overstrike else hits * HARM[severity]}
        if self.no_react:
            return None
        overstrike_harm = HARM[2]
        net = self.defence_net()
        if self.has_shield and self.pending >= REACTION_AP['parry']:
            success = chance_above((SHIELD_DIE, PROF_DIE), net, self.exhaustion, value)
            ends = chance_above((SHIELD_DIE, PROF_DIE), net, self.exhaustion, 2 * value - 1)
            options['parry'] = (1 - success) * overstrike_harm - ends * END_TURN_BONUS + REACTION_AP['parry'] * AP_WEIGHT
        if self.pending >= REACTION_AP['dodge'] and not self.no_dodge:
            avoid = chance_above((DEX_DIE, REFLEX_DIE), self.dodge_net(), self.exhaustion, value)
            over = chance_at_most((DEX_DIE, REFLEX_DIE), self.dodge_net(), self.exhaustion, value // 2)
            hit = max(0.0, 1 - avoid - over)
            options['dodge'] = over * overstrike_harm + hit * hits * HARM[severity] - avoid * DISENGAGE_BONUS + REACTION_AP['dodge'] * AP_WEIGHT
        if self.hardness > 0:
            absorbed = min(value, self.hardness)
            remaining = value - absorbed
            breaks = self.hardness <= 1
            light = BASE_THRESHOLD + (0 if breaks else self.defence_value)
            braced = 2 if remaining >= light + 5 else 1 if remaining >= light else 0
            harm = HARM[2] if remaining >= light + 5 + BASE_THRESHOLD + 5 else hits * HARM[braced]
            options['brace'] = harm + HARDNESS_WEIGHT + (ARMOUR_BREAK_WEIGHT if breaks else 0)
        return min(options, key=options.get)

    def end_own_turn(self):
        self.temp_attack_dis = self.temp_defence_dis = 0
        if self.no_react:
            self.no_react -= 1
        if self.no_dodge:
            self.no_dodge -= 1
        if self.temp_no_charge:
            self.temp_no_charge -= 1
        self.pending = self.later

    def end_round(self):
        if self.bleed_pending:
            self.bleed_pending -= 1
            if not self.bleed_pending:
                self.severe_bleeding()
        elif self.bleeding:
            self.bleeding -= 1
            if not self.bleeding:
                self.out = True


def attack(attacker, defender, charging):
    """Resolves one attack; returns True when it ends the attacker's turn."""
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
    value = roll([attacker.weapon_die, PROF_DIE], mode_of(advantages, disadvantages)) - attacker.exhaustion
    value = max(value, 1)
    reaction = defender.choose_reaction(value, advantages, charging)
    overstrike = not reaction and value >= defender.overstrike_threshold()
    ends_turn = False
    hit_value = value
    if reaction:
        defender.pending -= REACTION_AP[reaction]
        if reaction == 'parry':
            parry = roll([SHIELD_DIE, PROF_DIE], defender.defence_net()) - defender.exhaustion
            if parry > value:
                return parry >= 2 * value
            overstrike = True
        elif reaction == 'dodge':
            dodge = roll([DEX_DIE, REFLEX_DIE], defender.dodge_net()) - defender.exhaustion
            if dodge > value:
                return 'disengaged'
            overstrike = value >= 2 * max(dodge, 1)
        else:
            hardness = defender.hardness
            absorbed = min(value, hardness)
            defender.hardness -= 1
            hit_value = value - absorbed
            overstrike = hit_value >= defender.overstrike_threshold()
            if defender.hardness <= 0:
                defender.hardness = 0
                defender.defence_value = 0
    if overstrike:
        defender.wound(HEAVY, attacker.matrix)
        return ends_turn
    for _ in range(CHARGE_AP if charging else 1):
        defender.wound(defender.severity(hit_value), attacker.matrix)
    return ends_turn


def take_turn(actor, target, state):
    ap = max(0, actor.pending - actor.ap_penalty)
    actor.ap_penalty = 0
    actor.pending = 0
    actor.charge_penalty = False
    charged = False
    rearmed = False
    while ap > 0 and not actor.out and not target.out:
        if actor.prone:
            if ap < STAND_AP:
                break
            ap -= STAND_AP
            actor.prone = False
            continue
        if actor.disarmed:
            if rearmed or ap < REARM_AP:
                break
            ap -= REARM_AP
            actor.disarmed = False
            rearmed = True
            continue
        if not state['engaged']:
            cost = actor.attack_ap + actor.extra_attack_ap
            if actor.s.charge and not charged and not actor.no_charge and not actor.temp_no_charge and ap >= CHARGE_AP + cost:
                ap -= CHARGE_AP + cost
                actor.extra_attack_ap = 0
                charged = True
                state['engaged'] = True
                actor.charge_penalty = True
                result = attack(actor, target, True)
                if result == 'disengaged':
                    state['engaged'] = False
                elif result:
                    break
                continue
            if charged or ap < MOVE_AP + actor.attack_ap + actor.extra_attack_ap:
                break
            ap -= MOVE_AP
            state['engaged'] = True
            continue
        if ap < actor.attack_ap + actor.extra_attack_ap:
            break
        ap -= actor.attack_ap + actor.extra_attack_ap
        actor.extra_attack_ap = 0
        result = attack(actor, target, False)
        if result == 'disengaged':
            state['engaged'] = False
        elif result:
            break
    actor.end_own_turn()


def duel(first_strategy, second_strategy, cap, armour):
    a = Fighter(first_strategy, cap, armour, True)
    b = Fighter(second_strategy, cap, armour, False)
    state = {'engaged': False}
    for _ in range(MAX_ROUNDS):
        order = sorted((a, b), key=lambda f: (f.pending, 0 if f.first_on_ties else 1))
        for actor in order:
            target = b if actor is a else a
            if actor.out or target.out:
                break
            take_turn(actor, target, state)
        for fighter in (a, b):
            fighter.end_round()
        if a.out or b.out:
            break
    if a.out and not b.out:
        return 0.0
    if b.out and not a.out:
        return 1.0
    return 0.5
