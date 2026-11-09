# Wispers 0.8 fix pass

Item-by-item fix of the Wispers 0.8 rulebook (Hungarian TTRPG by Sorbán Zoltán, "Zoz").

## Files

- `homebrewery/wispers-0.8-munkalista.txt`: the worklist. Each item has Állapot / Döntés / Javítás / Megjegyzés,
  plus the ÖSSZESÍTŐ counts at the top and the NAPLÓ log at the bottom.
- `homebrewery/wispers-0.8-javitott.txt`: the working text. All fixes go here.
- `homebrewery/wispers-0.8.md`: the base text. Never edit it.
- `wispers-DDD.txt`: draft of the DDD subsystem (Discipline, Devotion, Divinity).

## Workflow

1. Take the next item, state the problem in one or two lines, and give a short proposal.
2. Zoz decides (often just „Mehet”). Apply exactly that decision to `wispers-0.8-javitott.txt`.
3. Update the item block, the ÖSSZESÍTŐ counts and add one NAPLÓ line. Check that the counts match the Állapot lines.
4. Commit and push after each item.

Keep replies short and in Hungarian. Put the proposal and the question at the end of the reply.

## Hard rules

- All game content is Hungarian. Hungarian quotes: „…”.
- Never invent a term. Propose it in an `ÚJ KIFEJEZÉS:` block and wait for approval.
- Never fill a `<redacted>` placeholder.
- No frontmatter, no tags.
- If something touches the narrative canon (the Obsidian vault, not in this repo), flag it with ⚠ DIVERGENCIA and do
  not pick a side.
- Not in this repo: the CRPG (`C:/dev/wispers/wispers-crpg`), `RTFC/`, and the HEAD rulebook `wispers-0.7.0b.docx`.
  Where a fix differs from the CRPG, note it in the item's Megjegyzés; do not change the CRPG.

## Decisions to keep in mind

- Képzettségpróba: tulajdonságkocka + jártasságkocka. The sum against the célérték decides success. The two faces
  decide the mode: jártasság ≥ tulajdonság is szakértelem, otherwise erőltetés. Four outcomes: Abszolút siker,
  Részleges siker, Bukás, Kritikus bukás. Where a rule names only siker/bukás, Részleges siker counts as siker with
  its side effect and Kritikus bukás as bukás with its consequence (V-06). The GM picks a Kritikus bukás consequence
  from a list (Idő, Eszköz, Figyelem, Ár, Fáradtság; Helyzet was removed in V-07) or makes one up; no Seb on that
  list. Zoz's principle: mechanics should have narrative consequences, not mechanical ones; a Kritikus bukás causes
  narrative trouble, not a mechanical penalty. Social conflict has all four outcomes; combat stays two-state. The four
  outcomes apply to képzettségpróbák only: mentődobás and combat reactions (Kitérés, Hárítás) are two-state.
- Előny / hátrány (V-07): a third die the size of the smaller of the two dice. Előny: it may replace either die and
  takes its role. Hátrány: the smaller die and the third die, the lower roll counts (on equal sizes the jártasságkocka
  is the smaller); always erőltetés, and no die-comparison effect (Halálos) applies. No stacking; előny and hátrány
  cancel. Social Részleges siker moves the counter by half the siker mértéke (no hátrány). Casting at Közelharci táv
  costs +1 AP instead of hátrány. Zoz wants fewer előny/hátrány sources so they matter: keep the situational ones the
  player chooses (harcmodor, roham, tempó, position); cut or narrow the lasting, broad, minor ones; express grades
  by scope, duration or „nem kísérelhető meg”, never by extra dice. Racial attribute penalties are „−1-es módosító”,
  never „hátrány”, and every racial penalty is −1 (the mnemór −2 was a typo, fixed under H-08; at Világstandard 3
  the mnemór Erő is 2). Wound tables: Könnyű seb never gives hátrány; Mély seb a narrow one until rest; Súlyos seb a broad
  one. V-07 is JAVÍTVA (2026-11-02).
- Core rules state rules, not situational GM advice: do not write into them what only happens in some cases or what a
  GM can deduce (e.g. rizikós próba under hátrány). Such notes may go into a later chapter for GMs.
- Attacks: weapon die + proficiency die, no attribute. Unarmed: 1d2 (1d4/2) with the Pusztakezes harc proficiency.
  Unarmed Ellökés, Megragadás, Elrángatás, Feldöntés and Lefegyverzés roll the Erőkocka instead of 1d2 (V-10).
  Minimum Erő (V-10, JAVÍTVA): an Erő column in the weapon and armour tables; weapons d4 none, d6 3, d8 4, d10 5,
  Íjpuskák none; armour Könnyű none, Közepes 4, Nehéz 5. Each missing point costs +1 AP on actions and reactions
  with that weapon, and in armour +1 AP on every action (not reactions); never a ban. H-69 (NYITOTT): slot-based inventory on the
  character sheet, Erő unlocks new slots; the Hungarian word for the slot still needs an ÚJ KIFEJEZÉS proposal.
- Célérték (V-03): the GM sets the check's level, which gates who may try and suggests the célérték: Képzetlen 3, Kezdő 5,
  Képzett 7, Haladó 9, Tapasztalt 11, Mester 13. Only a recommendation; the GM may and should adjust it.
- Képzetlen (V-04): may try Képzetlen-level checks only, rolls the attribute die alone, always erőltetés. The 42-skill
  list stays; do not propose trimming it.
- Kimerültség: −1 per level to the result of every próbadobás (V-08), so it never changes the die comparison; death
  when it exceeds 2× Állóképesség; wounds never give Kimerültség (V-01). Próbadobás is not yet defined (H-68): Zoz's
  working definition is every roll that uses a jártasságkocka; the Képzetlen próba is the exception (no jártasságkocka).
  Sebdobás, vérzés, Vérszomj, Rettegés and the 1d100 tables are not próbadobások.
- Wounds: Könnyű / Mély / Súlyos seb by sebhatár (reaching it counts). Sebdobás: 1d8 + the number
  of Sebek of the same severity (not all Sebek) + the weapon's találati mátrix; 12+ is one fok worse (V-22, was 21+;
  the CRPG still uses 21), on the Súlyos table death. Wounds must be
  hard to heal: Súlyos → Mély → Könnyű → healed, no roll on each step, a healed wound leaves a heg (scar).
- Weapon properties are called „jellemző” (never „tulajdonság”, that is the six attributes). The Jellemzők column holds
  base jellemzők; the weapon table's Képzetlen–Mester columns hold jellemzők unlocked at that proficiency level. Each
  jellemző has a description and an effect (Fegyverek › Jellemzők). Damage types should be jellemzők too, and magic
  will get a similar system. „Tag” is design vocabulary only, never in the book. Weapon AP (column „AP”, formerly SZ):
  d4 2, d6 3, d8 4, d10 4, d12 5,
  with individual exceptions.
- Advancement (H-62): one shared point pool for tulajdonságok and jártasságok; 24 at level 0, then 8 per level (no
  Tudás bonus) plus points kasztok may add. Every advanceable thing is priced individually; design baseline for a
  jártasság is cumulative 1/4/10/19/31. Faji and kezdő talentek and kasztok are guaranteed at the table's levels;
  általános talentek are bought with points.
- Prices anchor on a 20 Réz daily wage. Basic gear is iron (Vas), better gear (mostly in cities) steel (Acél).
  Materials are jellemzők too: Vas repels magic (no enchanting, no casting in iron armour), Réz conducts, Ezüst holds,
  Arany amplifies. Exotic and race-specific metals come later. Armour (V-09): all armour is iron except Steppelt zeke
  and Keményített bőrvért, so casters wear those (Védőérték up to 2); casting in steel armour comes later (H-29).
  Beleállás stays 0 AP, limited by Keménység (1 per use); a broken armour gives no Védőérték and no Beleállás until
  1 Keménység is restored (the CRPG removes it instead).
- Kasztok are feat-like one-time picks at set levels with prerequisites (follow-up kaszt or a new direction), built on
  exception-based design (H-03).
- Harci távok are abstract: Közelharci táv, Rövid táv, Közepes táv (same zone), Nagy táv (another zone), Értelmezhetetlen. „reach” and (for now) „Glaive” stay English.

## State (2026-10-25)

No NYITOTT item is left. H-63 is FOLYAMATBAN: everything is in the text except the Fegyelem scale
(Gyűlölt → … → Bajnok, Zoz has the steps and points) and the per-Suttogó lists; both come later. DDD names in
Hungarian: Diszciplína, Fegyelem (Devotion), Áhítat (Divinity), Tilalom, Erény, Gyűlölt / Üldözött, Bajnok,
lénytípus; no „DDD” abbreviation in game text.

Vérdal decided (2026-10-25): reading B, the evening Eltökéltség mentődobás is subtracted from the vérszomj; H-11, H-20,
H-21 are JAVÍTVA. The vérszomj cannot go below 0.

H-65 (new, FOLYAMATBAN): a duel simulation showed combat is decided by who acts first (bid 1 + Féktelen + Hárítás;
the first mover wins 91% of mirror duels). Done: Féktelen lost its guaranteed túlütés. Kept: players act first on ties.
Hárítás: a success blocks the Seb and ends the attacker's turn only when the parry is at least twice the attack.
Reactions are chosen after seeing the attack value. Rohamozás costs 2–3 AP plus the weapon's AP. Túlütés without a
reaction or with Beleállás (V-11): the attack reaches the könnyű + súlyos sebhatár (13 + 2×VÉ; armour counts twice on
purpose, less math). A túlütés deals the hit's own Seb plus one extra Súlyos seb, so an undefended túlütés is two
Súlyos sebek; the sim does not model this yet. Rohamozás adds its own 2–3 AP to every sebdobás of the hit (no extra
Sebek). Színlelt: on a hit everyone else attacks the target with előny until the end of their own next turn.
Megragadott: break free with Ellökés. Közepes táv = same zone, Nagy táv = another zone. Hárítás (V-11):
shield or parry-weapon die + proficiency die against the attack value (reaching it succeeds); the parry weapon is the
Kétfegyveres second weapon; only a shield stops missiles; failure stays túlütés. Shields have their own table after
armour (not with weapons): Kis pajzs 1d4 Könnyű, Pajzs 1d6 Erő 3 Közepes, Nagy pajzs 1d8 Erő 4 Kitérés-gátlás Nehéz;
the proficiency is the shield's Páncélcsoport; missing Erő makes the Hárítás dearer. Prices: Kis pajzs 50, Pajzs 100,
Nagy pajzs 200 Réz. V-11 is JAVÍTVA (2026-11-09).
Beleállás: Keménység lowers the value first, and each Beleállás costs 1 Keménység.
D-1 and H-65 are JAVÍTVA: the bid cap is 20 (no escalating repeat cost). The duel simulator is in `tools/sim/`:
duel9 (H-65 baseline), duel10 (V-07 dice only), duel11 (the current book) and study11, the equilibrium study. Run it
from `tools/sim/` as `SIM=duel11 python study11.py 40 csupasz 5-6-4 20` (`pancel` for armour; about 8 minutes).
Results so far are in `tools/sim/out/`.

H-66 (new, FOLYAMATBAN, 2026-11-08): the V-07 re-run showed that since V-01 combat has no attrition. The first-mover
edge is nearly gone (mirror duels 48–63%). In armour only Rövidkard and Tőr with Féktelen stayed competitive (heavy
weapons 0.18–0.36): the sebdobás ladder killed through any armour after about 35 hits, and 2-AP weapons hit twice as
often. The 1–7% „draws” are mutual knockouts (one falls, the other bleeds out at round end), not 40-round stalemates.
Keep the first-mover fix while solving this.

V-22 is JAVÍTVA (2026-11-08): the sebdobás turning point is 12 instead of 21; the bid cap stays 20. Duels are about a
quarter as long (armour 19 attacks instead of 64), the loser falls with about 2 Súlyos sebek, and in armour Hosszúkard
0.61 and Nagykalapács 0.60 now match the light weapons (0.62). Left for H-66: Csatabárd (0.39, Súlyos mátrix 2).
H-67 (new, NYITOTT): the three wound tables must shrink to rows 2–11; Zoz picks which 10 of the 15 rows stay. The
simulation used the current even rows; re-run V-22 and H-66 after the pick. Simulator: `tools/sim/tsim.py` and
`duel_turn.py` (`SIM=duel_turn TURN=12 python study11.py …`), round-robin `rr_turn.py`.

V-08 is JAVÍTVA (2026-11-09): Kimerültség affects próbadobások only. H-68 (new, NYITOTT): define próbadobás; the
suggestion is to tie it to the jártasság, not its die, so the Képzetlen próba counts too.

The four remaining DÖNTÉSRE VÁR items (H-03, H-17, H-19, H-47) all wait on content: kasztok, the varázslat chapter, the
Kegy rework. Open decisions: the D-1 bid cap or repeat cost (H-45, H-14, H-30), Sebgyógyítás (H-58), Szusztörő (H-13).
`wispers-0.8-nyitott-tetelek.pdf` (2026-10-25, local only) lists every unfinished item.

H-53 is FOLYAMATBAN: Fegyvert nem igénylő cselekvések stays a placeholder for now.
H-55 is FOLYAMATBAN: Zoz gives the seven Mágiaosztály descriptions; Entrópia stays „Rend- és rendbontó mágia.”
H-58 is FOLYAMATBAN: the Sebgyógyítás rule (cap, above the cap) comes later.
H-59 is FOLYAMATBAN: Sebzéstípusok stays a placeholder for now.
H-60 is FOLYAMATBAN: the származási helyek reference waits for a chapter.
H-62 is FOLYAMATBAN: Karakterfejlődés table and tulajdonság cost are in; 0. szint math, jártasság costs, talent/kaszt cost, varázslattanulás are open (Zoz's OneNote note).
See the worklist for FOLYAMATBAN and DÖNTÉSRE VÁR items.
