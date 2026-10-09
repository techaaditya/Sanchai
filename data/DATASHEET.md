# Datasheet: Nepali Clinical Lexicon and NepClinBench

## Motivation

Existing Nepali NLP resources are news-domain. This dataset supports Nepali *clinical*
language normalization for handwritten, spoken, romanized, code-mixed, and OCR-corrupted
medical input.

## Composition

- `nepali_clinical_lexicon.json` — 261 draft concepts
- `nepali_clinical_lexicon.csv` — CSV export of the same concepts
- `nepclinbench.json` — 60 gold benchmark items

| Concept type | n |
| --- | --- |
| symptom | 57 |
| drug_brand | 54 |
| condition | 30 |
| investigation | 30 |
| body_site | 25 |
| drug_generic | 20 |
| duration | 20 |
| severity | 15 |
| negation | 10 |

### Synthetic demo records

`seed_patients.json` (3 patients) and `seed_entries.json` (4 entries) are entirely
invented. No real person's data is present.

Dates carry two fields, and the split is deliberate:

| Field | Calendar | Purpose |
| --- | --- | --- |
| `record_date` | Gregorian ISO-8601 | Canonical. Sorts, compares against a Gregorian `dob`, and is the only thing a FHIR R4 date element may hold. |
| `record_date_bs` | Bikram Sambat | Display only. Authored per entry, never computed. |

**No AD↔BS conversion exists anywhere in this project.** A correct converter needs the
days-per-month table for each Bikram Sambat year; a date silently one day wrong in a health
record is worse than one shown in an unexpected calendar. The BS strings here are authored
alongside the Gregorian dates and their correspondence is approximate — acceptable because
the records are synthetic, and stated because it would not be acceptable otherwise.

These entries were written by hand rather than extracted, so they carry `extraction_method:
"seed"` and claim no normalization tier. Anything consuming them must not present them as
dictionary-matched.

### Per-concept fields

`devanagari_aliases` holds Devanagari only — this is enforced at generation time, so a
Devanagari-only matcher cannot be corrupted by Latin strings.

`latin_aliases` holds the Latin-script forms that genuinely appear on Nepali lab slips
(`CBC`, `HbA1c`, `SpO2`, `Widal`). They are real signal and are kept in their own field
rather than smuggled into the Devanagari one.

`romanized_aliases` is how a Nepali speaker types the term on a phone (`tauko`, not
`head`). Every entry is hand-written; none is the English gloss lowercased.

`duration_days` and `frequency_per_day` make duration and frequency terms machine-usable
(`सात दिन` → 7; `दिनको दुई पटक` → 2/day).

`negation_scope` records whether a marker follows the concept (`छैन`, post) or precedes
it (`बिना`, pre). Nepali negation is overwhelmingly post-positional, and a forward-only
detection window silently misses the exception.

`generic_of` links every brand to its generic. Real Nepali prescriptions are written in
brand names.

`verify_against`, `review_status` and `sources` record provenance honestly — see
[Collection process](#collection-process-and-what-source-means-here).

### Alias uniqueness

Every surface string maps to exactly one concept, enforced by both the generator and
`scripts/validate_prebuild.mjs` across `devanagari_aliases`, `romanized_aliases`,
`latin_aliases` **and** `code_mixed_patterns` — every field the matcher indexes.
Tier-1 matching is a dictionary lookup; a string owned by two concepts makes the
deterministic tier order-dependent, which defeats its purpose.

Ownership rules, where two concepts contested a string:

- **A brand owns its brand name** (`सिटामोल`, `जीवनजल`); the generic is reached through
  `generic_of`.
- **A symptom owns its symptom phrase.** `chest pain`, `leg pain` and five others were
  also claimed by the corresponding `body_site`. A site is a location, not a complaint,
  so sites keep only patterns that still name a site (`chhati ma pain`).
- **An alias must be a way the concept is written, never a conclusion drawn from
  something else.** `Hb low` was claimed by both Hemoglobin and Anemia; it belongs to
  Hemoglobin, because going from a low haemoglobin to a diagnosis of anemia is clinical
  inference and a lexicon must not perform it silently.

## Collection process, and what "source" means here

These concepts were **authored** for ArogyaKhata. They were not extracted from a
published register, and every row says exactly that:

```json
"source": "authored for ArogyaKhata v0.1; not extracted from a published register"
```

That wording is deliberate. Naming NLEM or the DDA brand list as a *source* would be
a fabricated provenance — a citation nobody followed — and this project spends its
entire design budget on not doing that. Single annotator, working from project
documentation, common Nepal clinical usage, demo requirements and brand-to-generic
mapping needs.

What each row *can* honestly carry is the authority that would settle it, and whether
that check has happened yet. Two fields do this:

| Field | Meaning |
| --- | --- |
| `verify_against` | Who or what settles this row |
| `review_status` | `unreviewed`, or `clinician_reviewed` once someone has signed it off |
| `sources` | Structured form of the same claim: `{"type": "authored" \| "observed_document", "ref": ...}`. Every row is `authored` today — see [Known gaps](#known-gaps). |

| `verify_against` | Rows |
| --- | --- |
| clinician review — Nepali clinical usage | 127 |
| DDA Nepal registered brand list | 54 |
| WHO ICD-11 MMS | 30 |
| hospital laboratory test menu | 30 |
| Nepal NLEM / DDA generic register | 20 |

**`review_status` is `unreviewed` on all 261 rows today.** Anyone can verify that by
counting, which is the point: it is a countable completion state rather than a
promise, and it turns "clinician review pending" from an apology into an audit plan
that names its own authorities. A body site or a severity word is a question about
Nepali clinical usage and needs a clinician; a brand name is a question of fact
against the national drug register.

## Intended uses

- Demonstration of Nepali clinical normalization
- Benchmarking exact, fuzzy, and constrained model matching
- Seeding a clinician-reviewed Nepali clinical terminology resource

## Out-of-scope uses

Do not use this dataset as a clinical authority, a medication safety database, a treatment
guideline, or a claims adjudication engine.

## Known gaps

- **Clinician review pending — 0 of 261 rows reviewed.** Every row carries
  `review_status: "unreviewed"` and a `verify_against` naming who settles it.
- **Voice input is not covered by this dataset and is switched off in the product**
  when running against Ollama (cloud or local) — its API carries no audio field, so
  there is nothing to evaluate. It is available when the llama.cpp backend is
  configured against a multimodal GGUF; see `backend.intake.engines.audio_input_supported`.
- **ICD-11 coverage: 30 of 30 conditions have a WHO-proposed candidate code**, in
  `data/icd_crosswalk.csv` (`scripts/verify_icd.mjs`, run against the live WHO
  container). None of those candidates has been copied into `icd11_code` in the
  lexicon itself — that script deliberately never writes into the lexicon, so
  each candidate still needs a human read before it is cited. 1 of 30 lexicon
  rows carries an `icd11_code` today; the rest carry ICD-10 seeds only, several
  of them category-level (unspecified) codes such as `E14` and `A15`.
- **`sources[]` is populated on all 261 rows**, via `scripts/generate_prebuild_data.mjs`.
  Every row says `{"type": "authored", "ref": "ArogyaKhata v0.1 seed list, unreviewed"}` —
  not `observed_document` — because no demo ticket has actually been photographed yet
  (`data/demo_assets/SHOOT-LIST.md` is still just instructions). Once real tickets exist,
  the concept_ids that genuinely appear in them can be listed in `OBSERVED_IN_PHOTOS` in
  that generator and re-run.
- **Inter-annotator agreement has not been run.** `scripts/make_iaa_sample.mjs` builds a
  reproducible, stratified 30-term sample (`data/iaa_sample.csv`, answer key kept
  separately in `data/iaa_answer_key.csv`) and `scripts/score_iaa.mjs` computes raw
  agreement and Cohen's κ once two people have each filled a column independently — but
  nobody has done that labeling yet, so no number is reported here. Do not report an IAA
  figure until this has actually run against two independent annotations.
- **The abbreviation set (`clinical_shorthand`) was not added.** The planned ~25-120
  entries were meant to be transcribed from the same unphotographed demo tickets;
  scoped out for the same reason, not attempted and hidden.
- **The OCR-corrupted benchmark items are hand-perturbed**, not harvested from observed
  engine failures. Each declares `derivation: "synthetic_perturbation"`. See
  [`../docs/NEPCLINBENCH.md`](../docs/NEPCLINBENCH.md). The benchmark was not extended
  with a sixth, ticket-derived category for the same unphotographed-tickets reason above.
- Brand coverage is useful for demo scope, not exhaustive for Nepal.
- Duration is thinly covered in the benchmark (2 of 60 items); frequency is not covered.
- Benefit-package items require PDF extraction with page-level provenance before any use.
- Full 380–450 concept target was not reached: 261 concepts shipped, scope not a
  limitation being hidden.
- Fine-tuning was scoped out under time constraint: the lexicon ablation (58/60 vs.
  42/60 raw-Gemma-4 baseline, precision 1.000 vs. 0.781) already demonstrates what the
  lexicon contributes; a fine-tuned adapter was not attempted.

## Regenerating

`data/` is generated by `scripts/generate_prebuild_data.mjs` and must never be hand-edited
— `scripts/validate_prebuild.mjs` regenerates into a scratch directory and fails on any
difference.

## License

CC-BY-4.0.
