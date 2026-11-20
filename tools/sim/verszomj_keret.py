import random
import sys

TRIALS = 4000
DAYS = 60
ENDURANCE = 3
RECOVERY = 1
THRESHOLD = 3
SPIRIT = 3
ROUNDS = 2
FOSZTOGATO_ATTACKS = 4
FIGHTS = ((3, 'harc 3 naponta'), (7, 'harc hetente'), (0, 'harc soha'))


def roll(count, sides):
    return sum(random.randint(1, sides) for _ in range(count))


def kezdo_willpower():
    return roll(1, 4) + roll(1, 4)


def kepzett_willpower():
    return roll(1, 4) + roll(1, 6)


def hadviselo_attack_roll():
    return roll(1, 8) + roll(1, 4)


def fosztogato_attack_roll():
    return roll(1, 6) + roll(1, 4)


def skill_roll():
    return roll(1, 6) + roll(1, 4)


def raging(thirst):
    return thirst > THRESHOLD


def hadviselo_attack(thirst, stats):
    if raging(thirst):
        stats['bonus'] += thirst
        stats['bonus_attacks'] += 1
    return max(0, thirst - hadviselo_attack_roll())


def hadviselo_fight(thirst, stats):
    stats['fights'] += 1
    for _ in range(ROUNDS):
        thirst = hadviselo_attack(thirst, stats)
        if raging(thirst):
            stats['verlaz'] += 1
            thirst = hadviselo_attack(thirst, stats)
    return thirst


def hadviselo_day(thirst, fight, stats):
    return hadviselo_fight(thirst, stats) if fight else thirst


def fosztogato_check(thirst, stats):
    stats['checks'] += 1
    if raging(thirst):
        return thirst
    stats['calm_checks'] += 1
    return thirst + skill_roll()


def fosztogato_fight(thirst):
    for _ in range(FOSZTOGATO_ATTACKS):
        if raging(thirst):
            thirst = max(0, thirst - fosztogato_attack_roll())
    return thirst


def fosztogato_day(thirst, fight, stats):
    thirst = fosztogato_check(thirst, stats)
    if fight:
        thirst = fosztogato_fight(thirst)
    return fosztogato_check(thirst, stats)


def nomad_heal_day(thirst, fight, stats):
    return max(0, thirst - SPIRIT) if fight else thirst


def no_day(thirst, fight, stats):
    return thirst


def no_evening(thirst):
    return thirst


def nomad_evening(thirst):
    return max(0, thirst - SPIRIT)


def live(orc, fight_every, stats):
    morning_dice, daytime, evening, willpower = orc
    thirst, exhaustion, restless = 1, 0, 0
    for day in range(1, DAYS + 1):
        thirst += roll(morning_dice, 4)
        stats['days'] += 1
        stats['calm_mornings'] += not raging(thirst)
        thirst = daytime(thirst, bool(fight_every) and day % fight_every == 0, stats)
        thirst = evening(max(0, thirst - willpower()))
        if raging(thirst):
            restless += 1
            exhaustion += 1
        else:
            exhaustion = max(0, exhaustion - RECOVERY)
        if exhaustion > 2 * ENDURANCE:
            return day, restless / day
    return None, restless / DAYS


ORCS = {
    'alap ork, Kezdő Eltökéltség': (2, no_day, no_evening, kezdo_willpower),
    'Hadviselő, Kezdő Eltökéltség': (3, hadviselo_day, no_evening, kezdo_willpower),
    'Hadviselő, Képzett Eltökéltség': (3, hadviselo_day, no_evening, kepzett_willpower),
    'Fosztogató, Kezdő Eltökéltség': (2, fosztogato_day, no_evening, kezdo_willpower),
    'Fosztogató, Képzett Eltökéltség': (2, fosztogato_day, no_evening, kepzett_willpower),
    'Nomád (a) gyógyításkor −Szellem': (2, nomad_heal_day, no_evening, kezdo_willpower),
    'Nomád (b) minden este −Szellem': (2, no_day, nomad_evening, kezdo_willpower),
}


def extras(stats):
    parts = [f'nyugodt reggel {stats["calm_mornings"] / stats["days"]:.0%}']
    if stats['fights']:
        parts.append(f'bónuszos támadás/harc {stats["bonus_attacks"] / stats["fights"]:.2f}')
        parts.append(f'átlagbónusz {stats["bonus"] / max(1, stats["bonus_attacks"]):.1f}')
        parts.append(f'Vérláz/harc {stats["verlaz"] / stats["fights"]:.2f}')
    if stats['checks']:
        parts.append(f'próba előnnyel {stats["calm_checks"] / stats["checks"]:.0%}')
    return ', '.join(parts)


def summarize(runs, stats):
    deaths = [day for day, _ in runs if day]
    restless = sum(share for _, share in runs) / len(runs)
    death = f'{len(deaths) / len(runs):.1%}' + (f' ({sum(deaths) / len(deaths):.0f}. nap)' if deaths else '')
    return f'halál {death}, nyugtalan {restless:.0%}, {extras(stats)}'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    random.seed(5)
    for name, orc in ORCS.items():
        print(f'=== {name}')
        for fight_every, fights in FIGHTS:
            stats = dict(days=0, calm_mornings=0, fights=0, bonus=0, bonus_attacks=0, verlaz=0, checks=0, calm_checks=0)
            runs = [live(orc, fight_every, stats) for _ in range(TRIALS)]
            print(f'  {fights}: {summarize(runs, stats)}')


if __name__ == '__main__':
    main()
