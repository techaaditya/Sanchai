# Demo assets — what to write, and how to photograph it

Four files. Roughly forty minutes. Without them, *"it reads handwriting"* is a
claim rather than a demonstration, and it is the one gap no amount of code fixes.

> ## ⚠️ Write these yourself. Do not photograph a real prescription.
>
> Every asset here is **synthetic** — that is what `data/DATASHEET.md` says and it
> has to stay true. A real prescription carries a real patient's name, a real
> doctor's registration number and a real illness. Photographing one and putting
> it in a public repository is a privacy breach that no demo is worth, and it
> would make the datasheet a lie.
>
> Write them by hand on blank paper. Invent the names. **राम बहादुर श्रेष्ठ** is
> the seeded patient — use that.

Everything below deliberately uses concepts that are already in the lexicon, so
the pipeline resolves them at tier 1 and the demo shows green badges rather than
a shrug. Stick to the words as written; improvise the handwriting, not the terms.

---

## 1 · `prescription_01.jpg` — the money shot

The one that goes on screen at 0:25. Everything else is support.

**Write, by hand, in Devanagari, laid out like an actual prescription:**

```
        धुलिखेल अस्पताल
        बिरामी: राम बहादुर श्रेष्ठ        उमेर: ३४
        मिति: २०८३ साउन १२

        निदान: टाइफाइड ज्वरो

        Rx
        १. सिप्रोफ्लोक्सासिन ५०० एमजी
           दिनको दुई पटक — सात दिन

        २. प्यारासिटामोल ५०० एमजी
           ज्वरो भए मात्र

                            डा. सुमन के.सी.
```

**Resolves to:** Typhoid fever · Ciprofloxacin · Paracetamol · twice daily ·
seven days — `NCL-0058, 0089, 0088, 0228, 0236`, and `duration_days: 7`.

**Handwriting:** natural doctor's hand. Slightly rushed, connected, real. Do
**not** print it and do not write in careful block letters — clean typed text is
what every other team will demo, and the whole claim is that this handles what
they avoid. It must still be readable by a human who is trying; illegible is a
different demo.

---

## 2 · `prescription_02.jpg` — brand names and a negation

The backup asset, and secretly the more interesting one. Two beats
`prescription_01` cannot show: **brand→generic resolution** and **negation**.

```
        धुलिखेल अस्पताल
        बिरामी: राम बहादुर श्रेष्ठ
        मिति: २०८३ साउन १२

        ज्वरो छैन, तर खोकी छ

        Rx
        १. सिटामोल ५०० एमजी — दिनको तीन पटक
        २. सिफ्रान ५०० एमजी — सात दिन

        एलर्जी छैन
```

**Why this one earns its place:**

- **सिटामोल → Paracetamol** and **सिफ्रान → Ciprofloxacin**. The record stores the
  generic. That is the beat where a clinician in the room sits up, because brand
  proliferation is a real problem in Nepali pharmacy practice.
- **ज्वरो छैन** — fever, negated, rendered struck through with ⊘. **खोकी छ** —
  cough, recorded. Same line. This is the ten seconds your pitch script tells you
  to pause on, and having it in *handwriting* rather than typed is much stronger.
- **एलर्जी छैन** — a second negation, in a different position.

Write this one in a **different hand** from `prescription_01` if you can — a
second person, or your other hand. Two documents in identical handwriting looks
like what it is.

---

## 3 · `bill_01.jpg` — the second document type

Mixed Devanagari and Latin with numerals, which is exactly how Nepali hospital
bills actually print.

```
        धुलिखेल अस्पताल — बिल
        बिरामी: राम बहादुर श्रेष्ठ
        मिति: २०८३ साउन १२

        रगत कल्चर (Blood culture)      रु. ८५०
        इन्जेक्सन                       रु. ३२०
        सेवा शुल्क                      रु. १५०
        ──────────────────────────────────────
        जम्मा                          रु. १,३२०
```

**Resolves to:** Blood culture — `NCL-0169`.

Handwritten on a receipt pad is ideal; a printed bill photographed at an angle
also works. **Keep the Nepali numerals** (`८५०`, not `850`) in at least two lines —
numeral normalization is a real thing the pipeline does and nothing else in the
demo exercises it.

**What it will say:** *unextracted*, not *not covered*. The benefit package PDF
has not been extracted, and the surface is built to never report a miss over a
document it could not read. If asked, that is the answer — it is the same
discipline as the microphone.

---

## 4 · `lab_report_01.pdf` — the digital path

**A PDF, not a photograph.** This one proves the router: a digital PDF goes to
PyMuPDF in about ten milliseconds and never touches the model. Type it in Word or
Docs and export.

```
        DHULIKHEL HOSPITAL — LABORATORY
        Patient: Ram Bahadur Shrestha        Date: 2026-07-26

        COMPLETE BLOOD COUNT (CBC)
        WBC            12,400 /µL      (H)
        Hemoglobin     13.2  g/dL
        Platelet      185,000 /µL

        Blood culture: pending
```

**Resolves to:** CBC · Hemoglobin · Platelet count · Blood culture —
`NCL-0162, 0163, 0190, 0169`.

Latin script on purpose. Nepali lab slips genuinely print `CBC` and `Hb`, which
is why `latin_aliases` exists as a field. This asset is what justifies it.

**Optional, if you have five spare minutes:** export a second copy as a flat
image PDF (print to PDF from a photo). That forces the scanned-PDF branch instead
of the digital one, and having both makes the routing diagram real rather than
theoretical.

---

## Photographing

| | |
|---|---|
| **Light** | Daylight near a window. No flash — it blows out ink and casts your phone's shadow. |
| **Angle** | Straight down. Not skewed. |
| **Frame** | Paper fills the frame, small margin. Not the table. |
| **Focus** | Tap the text, wait for it to sharpen, then shoot. |
| **Format** | JPEG, roughly 1500–2500 px on the long edge. Bigger is slower to upload and no more accurate. |
| **Paper** | Plain white or a real prescription pad. Not lined notebook paper — the rules confuse the OCR for no benefit. |

**Shoot two or three of each and keep the best.** You are on site tomorrow with
no chance to reshoot.

---

## When they exist

```bash
node scripts/readiness_check.mjs        # the four flip from warn to pass
```

Then push a real one through and see what actually happens:

```bash
uvicorn backend.main:app --port 8000
# open the app, drop prescription_01.jpg into Intake
```

**Look at the result honestly.** If a concept comes back at tier 2 instead of
tier 1, that is worth knowing tonight — it may be a missing alias you can add to
the generator in two minutes. If something fails entirely, you have a demo you
can navigate around instead of one that surprises you at 0:25.

---

## The fifth asset that is deliberately absent

`voice_note_01.webm` is **not** on this list and
[`scripts/readiness_check.mjs`](../../scripts/readiness_check.mjs) says why in a
comment: voice intake is closed, so an asset for it would be a prop for a feature
that does not run.

Note that `data/seed_entries.json` still contains `entry_voice_negation_01` — a
seeded historical voice note in Ram's record. That is intentional and defensible:
it is a *record entry that already exists*, not a claim that you can create one
today. If a judge spots it and asks, that is a good question with a good answer —
and it is a natural opening for the microphone beat.
