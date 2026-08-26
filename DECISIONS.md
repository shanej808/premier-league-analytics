# Decisions Log — Premier League Predictive Analytics

Record of significant decisions made during development, why they were made, and what alternatives were considered. Intended to make the reasoning behind this project defensible and legible — to future-me, and to anyone reviewing the repo.

---

## Phase 1: Data Pipeline

### Odds data: multi-bookmaker, not single-bookmaker
**Decision:** Widened the `odds` schema to capture Bet365, Pinnacle, and market-average odds (both opening and closing prices), rather than a single bookmaker.

**Why:** Every bookmaker builds in its own margin and can be individually mispriced on specific matches. Benchmarking a model against one bookmaker only answers "did I beat Bet365," not "did I beat the market." Market-average odds (and Pinnacle specifically, regarded as the sharpest book) are the standard reference point in sports-analytics literature for evaluating whether a model's probability estimates are genuinely well-calibrated versus just noise.

**Trade-off accepted:** More schema complexity upfront, in exchange for a materially stronger methodological claim later ("benchmarked against market-average closing odds across multiple bookmakers" vs. "benchmarked against one bookmaker").

---

### Historical odds data source: manual one-off CSV download
**Decision:** Downloaded three seasons of `E0.csv` files (2022-23, 2023-24, 2024-25) directly from football-data.co.uk and committed them to `data/raw/`, rather than relying on an automated fetch.

**Why:** Claude Code web's sandbox blocks direct network access to `football-data.co.uk` (403 from the egress proxy). A GitHub-hosted mirror (`footballcsv/cache.footballdata`) was evaluated as an automated alternative, but its data is reformatted to a minimal "football.csv standard" (date/teams/score only) and does not carry odds columns at all — confirmed by inspecting the mirror's actual CSV headers, which returned only `Date,Team 1,FT,HT,Team 2`.

**Why this is acceptable:** Historical odds are static once a season ends — this is a one-time data load, not a recurring pipeline dependency. The manual step doesn't recur on every pipeline run, only once per historical season added.

**Documented workaround:** README notes the sandbox network restriction and how to re-enable a live fetch from football-data.co.uk directly if run in an environment with unrestricted network access.

---

### API-Football: connectivity verified locally, not in the sandbox
**Decision:** Claude Code web's sandbox also blocks `v3.football.api-sports.io` (and the RapidAPI gateway alternative). Connectivity was proven by running `api_client.py` locally instead.

**Why:** Rather than trying to get the sandbox's network policy changed (not practical for a one-off check), running the script locally once — on a machine with unrestricted internet access — was the fastest path to a genuine proof-of-connectivity, without compromising the cloud-first workflow for everything else.

**Result:** `/status` confirmed a valid, active free-tier API key. `/fixtures` with `next=N` initially returned 0 results with no error — traced through a systematic diagnostic process (raw response inspection, then a control query against a known-good past season) to a definitive root cause: **`next` is a paid-only parameter**, confirmed directly by the API's own error message (`"Free plans do not have access to the Next parameter"`). Not a bug in query construction — league ID and season logic were both correct throughout.

**Fix:** Removed `next` entirely; current-fixtures logic switched to `status=NS` (not-started), filtered/sorted client-side. Running this surfaced a second, distinct free-plan restriction: **the free tier has no access to the current season's fixtures at all** — only 2022–2024 (confirmed via the API's error message: `"Free plans do not have access to this season, try from 2022 to 2024"`).

**Resolution:** Verified end-to-end success against `season=2024` (within the allowed range) — real fixture data returned cleanly. This is the final proof of connectivity. Live current-season fixtures remain unavailable until/unless upgrading to a paid API-Football plan; documented as a known limitation in the README rather than something to keep debugging.

---

### Local environment: Python 3.8 → dedicated conda environment
**Decision:** Created a new conda environment (`football`) running a current Python version, rather than continuing to use the base Anaconda install (Python 3.8).

**Why:** DuckDB dropped support for Python 3.8 in a recent release, so `pip install duckdb` was falling back to compiling from source — which failed due to a missing C++ compiler. Python 3.8 reached end-of-life in October 2024, so this issue would have recurred with other packages regardless of DuckDB specifically.

---

## Process notes

- **Claude Code web branches, then opens a PR** — files added directly to `main` (e.g. the manual CSV drop) don't automatically appear on an in-progress branch; requires merging `main` into the branch first.
- **PR descriptions can go stale mid-session** — caught twice: the network note and the test plan both described an earlier version of the pipeline after the underlying code had changed. Always re-verify PR description against the *current* state of the code before merging, not just the state when the PR was first opened.
- **Nothing merged to `main` until:** the PR description accurately reflects current behaviour, the relevant script has been re-run and verified against the latest changes (not an earlier commit), secrets/`.env` handling has been checked, and the diff has been read end-to-end.
- **Debug via direct evidence, not speculation:** when the API-Football fixtures issue surfaced, the productive path was inspecting raw responses and running a controlled comparison (a known-good past season vs. the failing current-season query) rather than guessing at causes. Refusing to state an unconfirmed theory ("probably a free-tier restriction") as fact, and instead building a test that would prove or disprove it, got to a definitive answer faster than continued guessing would have.

---

*Last updated: 26 August 2026 — Phase 1 substantively complete: ingest, odds, and API-Football connectivity all verified end-to-end. Pending: Qodo review pass and final PR read-through before merge.*
