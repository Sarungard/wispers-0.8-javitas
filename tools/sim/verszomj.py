import random
import sys

TRIALS = 4000
DAYS = 60
MENTAL_LIGHT = 3
EVENING_SAVE = (2, 4)

RULES = {
    'mai szöveg (vér: −reggeli dobás)': dict(blood='morning', restless='keep', exhausts=True),
    'C: vér felez, nyugtalan éj felez': dict(blood='half', restless='half', exhausts=True),
    'D: vér felez, nyugtalan éj nulláz': dict(blood='half', restless='zero', exhausts=True),
    'B: nyugtalan éj Kimerültség nélkül': dict(blood='half', restless='keep', exhausts=False),
}
ORCS = (('ork, Állóképesség 3', 2, 3), ('Hadviselő, Állóképesség 3', 3, 3), ('Hadviselő, Állóképesség 4', 3, 4))
BLOOD = ((3, '3 naponta'), (7, 'hetente'), (0, 'soha'))
RECOVERY = ((1, 'pihentető éj −1'), (2, 'meleg étellel −2'))


def roll(count, sides):
    return sum(random.randint(1, sides) for _ in range(count))


def shed_blood(thirst, morning, rule):
    if rule['blood'] == 'morning':
        return max(0, thirst - morning)
    return thirst // 2


def vent_restless_night(thirst, rule):
    return {'keep': thirst, 'half': thirst // 2, 'zero': 0}[rule['restless']]


def live(morning_dice, endurance, blood_every, rule, recovery):
    thirst, exhaustion, restless, daytime = 1, 0, 0, 0
    for day in range(1, DAYS + 1):
        morning = roll(morning_dice, 4)
        thirst += morning
        daytime += thirst
        if blood_every and day % blood_every == 0:
            thirst = shed_blood(thirst, morning, rule)
        thirst = max(0, thirst - roll(*EVENING_SAVE))
        if thirst < MENTAL_LIGHT:
            exhaustion = max(0, exhaustion - recovery)
            continue
        restless += 1
        exhaustion += rule['exhausts']
        thirst = vent_restless_night(thirst, rule)
        if exhaustion > 2 * endurance:
            return day, restless / day, daytime / day
    return None, restless / DAYS, daytime / DAYS


def summarize(runs):
    deaths = [day for day, _, _ in runs if day]
    restless = sum(share for _, share, _ in runs) / len(runs)
    daytime = sum(mean for _, _, mean in runs) / len(runs)
    death = f'{len(deaths) / len(runs):.0%}' + (f' ({sum(deaths) / len(deaths):.0f}. nap)' if deaths else '')
    return f'halál {death}, nyugtalan {restless:.0%}, napközbeni Vérszomj {daytime:.1f}'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    random.seed(5)
    for recovery, recovery_label in RECOVERY:
        for name, rule in RULES.items():
            print(f'=== {name} | {recovery_label}')
            for label, dice, endurance in ORCS:
                for every, blood in BLOOD:
                    runs = [live(dice, endurance, every, rule, recovery) for _ in range(TRIALS)]
                    print(f'  {label} | vér {blood}: {summarize(runs)}')


if __name__ == '__main__':
    main()
