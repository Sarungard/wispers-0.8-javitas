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
- Harci távok are abstract: Közelharci táv, Rövid táv, Közepes táv, Nagy táv, Értelmezhetetlen. „reach” stays English.

## State (2026-10-23)

Next item: **H-59** (Állapotok and Sebzéstípusok). Proposal waiting for Zoz:

- The two headings come back after Sebgyógyítás, as in the HEAD.
- Állapotok, only those the book already uses: Megragadott (no Elmozdulás, no Kihátrálás); Földön fekvő (attacks
  with egyes hátrány; attacks against it from Közelharci táv get egyes előny); Öntudatlan (cannot act or react; anyone
  can kill it; „elájul” means this state); Vakság (rolls as in teljes sötétség, Látási viszonyok table); Kimerültség (pointer to its rule).
- Félelem, Zoz's rule: dobj egy kockával; páros: addig harcolsz, amíg a félelmed forrását meg nem ölöd vagy bele nem
  halsz; páratlan: mindent eldobva menekülsz, amíg biztos távra nem kerülsz tőle. Waiting for Zoz to confirm the rest.
- Sebzéstípusok: placeholder for now.

H-53 is FOLYAMATBAN: Fegyvert nem igénylő cselekvések stays a placeholder for now.
H-55 is FOLYAMATBAN: Zoz gives the seven Mágiaosztály descriptions; Entrópia stays „Rend- és rendbontó mágia.”
H-58 is FOLYAMATBAN: the Sebgyógyítás rule (cap, above the cap) comes later.
Still NYITOTT after H-59: H-60 to H-63. See the worklist for FOLYAMATBAN and DÖNTÉSRE VÁR items.
