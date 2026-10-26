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
  Részleges siker, Bukás, Kritikus bukás.
- Attacks: weapon die + proficiency die, no attribute. Unarmed: 1d2 (1d4/2) with the Pusztakezes harc proficiency.
- Wounds: Könnyű / Mély / Súlyos seb by sebhatár (reaching it counts), plus Kimerültség. Sebdobás: 1d8 + the number
  of Sebek of the same severity (not all Sebek) + the weapon's találati mátrix; 21+ is one fok worse. Wounds must be
  hard to heal; the healing rule comes later.
- Weapon properties are called „jellemző” (never „tulajdonság”, that is the six attributes). The Jellemzők column holds
  base jellemzők; the weapon table's Képzetlen–Mester columns hold jellemzők unlocked at that proficiency level. Each
  jellemző has a description and an effect (Fegyverek › Jellemzők). Damage types should be jellemzők too, and magic
  will get a similar system. „Tag” is design vocabulary only, never in the book. Weapon AP (column „AP”, formerly SZ):
  d4 2, d6 3, d8 4, d10 4, d12 5,
  with individual exceptions.
- Harci távok are abstract: Közelharci táv, Rövid táv, Közepes táv, Nagy táv, Értelmezhetetlen. „reach” and (for now) „Glaive” stay English.

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
reaction or with Beleállás: the attack reaches heavy + unarmoured heavy threshold (18 bare, 22 with Védőérték 4); no
extra Seb per előny. Beleállás: Keménység lowers the value first, and each Beleállás costs 1 Keménység.
D-1 and H-65 are JAVÍTVA: the bid cap is 20 (no escalating repeat cost). The duel simulator lives in the session
scratchpad (duel6.py / study6.py), not in this repo.

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
