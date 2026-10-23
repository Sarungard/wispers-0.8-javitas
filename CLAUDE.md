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
- Harci távok are abstract: Közelharci táv, Rövid táv, Közepes táv, Nagy táv, Értelmezhetetlen. „reach” and (for now) „Glaive” stay English.

## State (2026-10-23)

Next item: **H-62** (pontbefektetés). Source: Zoz's unfinished OneNote page „Playtest › Karakterfejlődés”
(uploaded as a PDF image, not in the repo). It has:

- „Karakterfejlődés szintenként” table, szint 0–13: Elosztható pontok 8 per szint, 0. szint „T”; Faji talent at
  0, 3, 6, 9, 12; Általános talent at 0, 2, 4, 6, 8, 10, 12; Kaszt at 1, 5, 9, 13; Kezdő talent at 0.
- Tulajdonság +1 costs 1 + the value to reach (1: 2 pont, 5: 6 pont).
- Jártasság costs „változó”; talent and kaszt locked behind jártasság, tulajdonság, szint; „Pontköltség vagy
  garantált?” is open. Varázslat from fóliánsok or mesterek, locked behind the mágiaosztály jártasság.
- Footer, cut off: „Fejlődéspontok blokk: 8 + (Tudás Tulajdonság) + (Egyéb bónusz, ha van) / szint”.

Clashes with the book: the note orders Kezdő, Haladó, Képzett (book: Kezdő, Képzett, Haladó); one Kezdő talent at
0. szint (book: two, kulturális + társadalmi); „mágiaiskola” (now mágiaosztály, H-55). Proposal waiting for Zoz:
write the table and the tulajdonság cost into Játék magasabb szinten, the open points as a Szerkesztői megjegyzés,
item FOLYAMATBAN.

H-53 is FOLYAMATBAN: Fegyvert nem igénylő cselekvések stays a placeholder for now.
H-55 is FOLYAMATBAN: Zoz gives the seven Mágiaosztály descriptions; Entrópia stays „Rend- és rendbontó mágia.”
H-58 is FOLYAMATBAN: the Sebgyógyítás rule (cap, above the cap) comes later.
H-59 is FOLYAMATBAN: Sebzéstípusok stays a placeholder for now.
H-60 is FOLYAMATBAN: the származási helyek reference waits for a chapter.
Still NYITOTT after H-62: H-63. See the worklist for FOLYAMATBAN and DÖNTÉSRE VÁR items.
