# Doc audit — `docs/iccma-2025-data.md` (2026-05-02)

Read-only scout audit. Line numbers are 1-based. Audit target lives at
`C:\Users\Q\code\argumentation\docs\iccma-2025-data.md` (79 lines).

## 1. Verified gaps

| Doc line | Claim | Code/tool reality | Recommended action |
|---|---|---|---|
| iccma-2025-data.md:8 | Instances "Zenodo record `10.5281/zenodo.17949380`" | `tools/iccma2025_data.py:33-35` uses URL `https://zenodo.org/api/records/17949380/files/ICCMA-2025-instances.zip/content`. The numeric id `17949380` is a Zenodo record id, not the DOI suffix; presenting it as a DOI is a category error. | Either drop the `10.5281/zenodo.` prefix and call it "Zenodo record id 17949380", or verify the DOI separately and cite both. |
| iccma-2025-data.md:12 | Raw results "Zenodo record `10.5281/zenodo.18506390`" | `tools/iccma2025_data.py:43-45` uses record id `18506390`. Same DOI-vs-record-id confusion as above. | Same as above. |
| iccma-2025-data.md:9-11, 13-15 | size and md5 values | Match `iccma2025_data.py:36-37` (instances 866_229_263 / `5b3231eb...`) and 47-48 (results 1_351_761 / `262ea636...`). | PASS. |
| iccma-2025-data.md:22 | `uv run tools\iccma2025_data.py fetch` (no archive arg) | `iccma2025_data.py:114-115` declares `archive` positional with `default="all", nargs="?"` so bare `fetch` works and downloads both. | PASS. |
| iccma-2025-data.md:34 | `manifest --strict` "fail if any parsed AF/ABA instance is malformed" | `iccma2025_data.py:133-136`: returns 1 only when `args.strict` and at least one row has `parse_status == "error"`. Matches doc. | PASS. |
| iccma-2025-data.md:35 | `tasks` subcommand | Defined at `iccma2025_data.py:124`, dispatched at 137-138, writes `iccma-2025-task-matrix.{json,csv}` (218-220). | PASS. |
| iccma-2025-data.md:41 | `all` runs the whole flow "without invoking any solver" | `iccma2025_data.py:139-145` runs fetch + extract + manifest + tasks; no solver call. | PASS. |
| iccma-2025-data.md:46-52 | Output paths under `data/iccma/2025/{archives,extracted/instances,extracted/results,manifests}` | Confirmed in code: archives `iccma2025_data.py:150`, extract dirs `extracted/instances` (38) and `extracted/results` (49), manifests directory `186-189`, task matrix paths `217-220`. Sampled tree shows `archives`, `extracted`, `manifests`, `runs` in `data/iccma/2025/`. | PASS. |
| iccma-2025-data.md:55-56 | "parses official numeric `p af <n>` AF files and official numeric `p aba <n>` flat-ABA files" | `iccma2025_data.py:248,259` — header dispatch on `"p af "` and `"p aba"`. Validators at 279-340 enforce flat-ABA shape (rule heads disjoint from assumptions, exactly one contrary per assumption). | PASS. |
| iccma-2025-data.md:56-57 | "Dynamic-track applications are classified but not executed" | `iccma2025_data.py:272-273` classifies `.py` files as `dynamic_app` with `parse_status="skipped"`. | PASS. |
| iccma-2025-data.md:61-62 | Runner "can use either the package-native reference backend or an ICCMA-compatible AF subprocess backend through `argumentation.solver`" | `iccma2025_run_native.py:93` declares `--backend choices=["auto","native","iccma"]`. Doc only mentions native and iccma; the actual third option `auto` is undocumented. | Add `auto` to the doc, or cite a default and note that `auto` exists. |
| iccma-2025-data.md:66 | Example `--backend native --max-af-arguments 100 --max-aba-assumptions 10 --timeout-seconds 5` | All flags exist with those types: `iccma2025_run_native.py:99-101`. Defaults match (100 / 10 / 5.0). | PASS. |
| iccma-2025-data.md:72 | `--iccma-binary path\to\solver.exe` | Flag at `iccma2025_run_native.py:95-98`; defaults to env `ICCMA_AF_SOLVER`. The doc never mentions the env-var fallback. | Add a sentence about `ICCMA_AF_SOLVER`. |
| iccma-2025-data.md:75 | `--max-af-arguments -1` disables the AF size cap | `iccma2025_run_native.py:243` skips the cap branch when `config.max_af_arguments < 0`. | PASS. |
| iccma-2025-data.md:75-78 | "still solves ABA jobs through the package-native ABA path"; "library-level `solve_aba_*` surfaces separately support ICCMA-compatible ABA subprocess dispatch through `ICCMAConfig(...)`" | The runner does run ABA jobs (manifest filter `iccma2025_run_native.py:148`). The library-level claim refers to `argumentation.solver`/`ICCMAConfig`; not contradicted but also not directly verified for ABA in this audit. | Doc is plausibly correct; flag for spot-check during README rewrite. |
| iccma-2025-data.md (entire) | Doc never mentions the runner output layout | `iccma2025_run_native.py:120-132` writes `data/iccma/2025/runs/{tag}-{label}.{json,csv}` plus `-summary.json`. Sampled tree confirms a `runs/` directory exists. | Add an "Outputs (runner)" subsection or extend the existing Outputs list. |
| iccma-2025-data.md (entire) | Doc does not mention `--label` or `--no-progress` flags on the runner | `iccma2025_run_native.py:102-107`: `--label` (default `"native-bounded"`, used in output filenames) and `--no-progress` (silences per-row stderr JSON). | Mention both; `--label` is load-bearing because it ends up in artifact filenames. |
| iccma-2025-data.md (entire) | Doc does not mention the task matrix definitions | `iccma2025_data.py:69-106` hard-codes MAIN_TRACK, HEURISTICS_TRACK, DYNAMIC_TRACK, ABA_TRACK with per-subtrack timeouts (1200s for main/aba, 60s for heuristics) and `certificate_required` flags. | Mention that `tasks` emits an authoritative subtrack/timeout matrix; reference the four track groups. |

## 2. Undocumented tooling that belongs here

- `tools/iccma2025_run_native.py:102` `--label` flag — affects artifact naming (`runs/{tag}-{label}.json`, `iccma2025_run_native.py:123-125`).
- `tools/iccma2025_run_native.py:104-107` `--no-progress` — disables stderr JSON progress events emitted at 216-231.
- `tools/iccma2025_run_native.py:93` `--backend auto` — undocumented third option.
- `tools/iccma2025_run_native.py:96-98` `ICCMA_AF_SOLVER` env-var fallback for `--iccma-binary`.
- Runner output layout: `data/iccma/2025/runs/iccma-2025-{label}.{json,csv}` + `iccma-2025-{label}-summary.json` (`iccma2025_run_native.py:121-132`).
- The contest tag `iccma-2025` is inferred from the `--root` directory name (`iccma2025_run_native.py:161-168`); worth a one-line note for users running with custom `--root`.
- `tools/iccma2025_run_native.py:87-88` reserves the first argv slot `_worker` for a subprocess worker mode; not user-facing but worth a brief implementation note if the doc ever covers internals.

## 3. Command-line example verification

| Doc command | Verdict | Notes |
|---|---|---|
| `uv run tools\iccma2025_data.py fetch` (line 22) | PASS | `archive` is optional with `default="all"` (`iccma2025_data.py:114-115`). |
| `uv run tools\iccma2025_data.py extract` (line 28) | PASS | Same default-all (`iccma2025_data.py:117-119`). `--force` exists but doc does not mention it; minor. |
| `uv run tools\iccma2025_data.py manifest --strict` (line 34) | PASS | `--strict` flag at `iccma2025_data.py:122`; exit code 1 path at 135-136. |
| `uv run tools\iccma2025_data.py tasks` (line 35) | PASS | Subcommand at `iccma2025_data.py:124`. |
| `uv run tools\iccma2025_data.py all` (line 41) | PASS | Subcommand at `iccma2025_data.py:125`, dispatch at 139-145. |
| Native runner example (line 66) | PASS | All flags resolve to defined argparse args. |
| ICCMA backend runner example (line 72) | PASS — caveat | Works, but the example uses `--max-aba-assumptions 0`, which means every ABA instance with assumptions ≥ 1 is skipped. Doc does not call this out. The `--iccma-binary` env-var default is also not mentioned. |

No commands were actually executed; verdicts are based on argparse declarations and dispatch logic.

## 4. Citation/reference audit

- The doc has no bibliographic citations — only Zenodo record identifiers.
- "Zenodo record `10.5281/zenodo.17949380`" (line 8) and `10.5281/zenodo.18506390` (line 12) are presented in DOI form, but the underlying tool uses these as Zenodo record ids in the API URL (`iccma2025_data.py:32-35, 42-46`). Treat as **needs-update**: either mark them as Zenodo record ids (no DOI prefix) or cite the actual DOI string after verifying it resolves.
- No paper references on the page. The 2025 ICCMA edition itself is not cited; if the README rewrite wants a paper anchor it would have to come from external proceedings rather than this doc.

## 5. Prose recommendations (severe issues only)

1. **DOI vs. Zenodo record id** (lines 8, 12). Misclassifying record ids as DOIs is a correctness issue, not style. Fix wording.
2. **Outputs section silently omits `runs/`** (lines 46-52). The runner writes here unconditionally; readers running the runner will find an undocumented sibling directory. Add it.
3. **`--max-aba-assumptions 0` in the ICCMA-backend example** (line 72) effectively disables ABA. If that is intentional, say so. If not, change the example.

Otherwise the prose is terse and accurate.

## 6. Cross-doc dependencies — overlap with `docs/iccma-data.md`

`docs/iccma-data.md` (57 lines) is the multi-year doc. Overlap and contradictions:

| Topic | `iccma-data.md` | `iccma-2025-data.md` | Conflict? |
|---|---|---|---|
| 2025 archive verification | "verified by size and MD5" (iccma-data.md:6) | size + md5 listed inline (iccma-2025-data.md:9-15) | No conflict; 2025-specific doc is the only place with the actual values. |
| Manifest classes | numeric `p af`, numeric `p aba`, APX, TGF, results/query/update artifacts (iccma-data.md:50-54) | numeric `p af`, numeric `p aba`, plus `dynamic_app` `.py` skip (iccma-2025-data.md:55-57) | Different scope: 2025 tool emits `dynamic_app` (`iccma2025_data.py:272-273`), older tool covers APX/TGF. The two manifests are produced by different scripts (`iccma_data.py` vs `iccma2025_data.py`). |
| Tooling | `tools\iccma_data.py --year 2025 manifest --strict` (iccma-data.md:43) | `tools\iccma2025_data.py manifest --strict` (iccma-2025-data.md:34) | **Latent conflict.** Two separate tools both claim to manifest 2025 data. Whether they produce identical output is not verified by this audit. The 2025 tool is richer (writes `iccma-2025-task-matrix.{json,csv}`, classifies dynamic apps, hard-codes the 4-track timeout matrix). |
| Runner | not covered | runner section (iccma-2025-data.md:58-78) | No conflict; complementary. |

**Merge recommendation.** The two docs *should not* be silently merged. The 2025 doc covers a year-specific tool (`iccma2025_data.py`) and a year-specific runner (`iccma2025_run_native.py`) that the multi-year tool does not encompass. Options for the rewriter:

- (a) Keep both, but cross-link: `iccma-data.md` should explicitly say "for 2025-specific workflows including the task matrix and native runner, see `iccma-2025-data.md`"; `iccma-2025-data.md` should say "for other editions (2015/2017/2019/2021/2023), see `iccma-data.md`".
- (b) Promote `iccma-data.md` to a single canonical doc with a per-year section, and fold the 2025 tool + runner under a "2025" subsection. This requires confirming whether `iccma_data.py --year 2025` and `iccma2025_data.py` are intended to coexist or one is the successor. Not verifiable from docs alone.

Recommendation: ship (a) now and put (b) on the dependency list for the README workstream — it requires a code-level decision the audit cannot make.

The cross-reference from `notes/readme-sync-2026-05-02.md` does not mention either ICCMA doc; the README scout focused on package-surface drift, not data-tool docs. No conflict between the two scouts.

## 7. Verdict

`docs/iccma-2025-data.md` is short, accurate where it speaks, and silent on three load-bearing surfaces (the `runs/` output directory, the `--label`/`--no-progress`/`auto` runner flags, and the `ICCMA_AF_SOLVER` env-var fallback). The Zenodo "DOI" wording is wrong and should be corrected. Overall health: **good with minor gaps** — a rewriter can act on the table in §1 without needing further investigation.
