# Doc audit — `docs/iccma-data.md` — 2026-05-02

Scout audit of `docs/iccma-data.md` (57 lines) against current code reality.
Read-only. All cited line numbers are 1-based.

Truth sources read:
- `tools/iccma_data.py` (645 lines)
- `tools/` directory listing (10 helper scripts)
- `data/iccma/` top-level (sample only: 2015, 2017, 2019, 2021, 2023, 2025, timeouts)
- `data/iccma/2025/` (sample: archives, extracted, manifests, runs)
- `src/argumentation/iccma.py` parser surface (parse_af / write_af / parse_adf / write_adf / parse_aba / write_aba)
- `docs/iccma-2025-data.md` (overlap candidate, 79 lines)
- `notes/readme-sync-2026-05-02.md` (cross-reference)

## 1. Verified gaps

| Doc line | Claim | Code/tool reality | Recommended action |
|---|---|---|---|
| 3 | `tools\iccma_data.py` for multi-year ICCMA data prep | Exists (`tools/iccma_data.py:1-645`); `--year` accepts `{2015, 2017, 2019, 2021, 2023, 2025, all}` (line 197) | PASS — claim matches |
| 4-6 | older editions size-only; Zenodo 2023+2025 size+MD5 | Confirmed: `ArchiveSpec.md5` is `None` for 2015/2017/2019/2021 specs (lines 47-138); set on 2023+2025 (lines 148, 159, 172, 183). `verify_archive` skips MD5 when `spec.md5 is None` (lines 575-576) | PASS |
| 10 | ICCMA 2015: benchmark zip + result spreadsheet | `iccma2015_benchmarks.zip` + `results_iccma2015_upd1.xlsx` (lines 48-61) | PASS |
| 11 | ICCMA 2017: detailed result zip + groups A/B/C/D/T | `results.zip` + `A.tar.gz` / `B.tar.gz` / `C.tar.gz` / `D.tar.gz` / `T.tar.gz` (lines 64-105) | PASS |
| 12 | ICCMA 2019: instance tarball | `iccma-instances.tar.gz` (lines 108-114) | PASS |
| 13 | ICCMA 2021: instance tarball + exact + approximate result CSVs | `instances.tar.gz` + `ICCMA_2021_exact_track.csv` + `ICCMA_2021_approximate_track.csv` (lines 117-137) | PASS |
| 14 | ICCMA 2023: Zenodo benchmark + raw-result zips | Zenodo record 8348039 — `iccma2023_benchmarks.zip` + `iccma2023_results.zip` (lines 140-161) | PASS |
| 15 | ICCMA 2025: Zenodo instance + raw-result zips | Zenodo records 17949380 + 18506390 (lines 164-185) | PASS |
| 17-18 | 2021 archive ~6.8 GB | Spec size `6_793_022_603` bytes ≈ 6.79 GB (line 121) | PASS |
| 25 | `--year all list` example | `list` subparser exists (line 200); `--year` accepts `all` (line 197) | PASS |
| 31 | `--year 2023 all` example | `all` subparser exists (line 213); fetches + extracts + manifests in one shot (lines 235-241) | PASS |
| 37 | `--year 2019 fetch instances` example | `fetch` subparser takes positional `archive` (line 204); `instances` is the 2019 archive name (line 109) | PASS |
| 43 | `--year 2025 manifest --strict` example | `manifest` subparser with `--strict` flag (lines 210-211); strict exits 1 when any row has `parse_status == "error"` (lines 233-234) | PASS |
| 50 | manifest classifies numeric `p af <n>` AF files | `scan_numeric_af_file` at line 404; classifier emits `kind="af"` (line 377) | PASS |
| 51 | manifest classifies numeric `p aba <n>` ABA files | `scan_numeric_aba_file` at line 427; emits `kind="aba"` (line 383) | PASS |
| 52 | APX files with `arg(...)` / `att(...)` | `APX_ARG_RE` / `APX_ATT_RE` at lines 190-191; `looks_like_apx` at line 516; emits `kind="apx"` (line 396) | PASS |
| 53 | TGF files | `scan_tgf_file` at line 490; emits `kind="tgf"` (line 393) | PASS |
| 53 | (omission) compressed `.apx.lzma` / `.tgf.lzma` variants | Tool also emits `kind="compressed_apx"` and `kind="compressed_tgf"` (lines 370, 373); doc does not mention compressed variants | minor — add a sentence noting xz/lzma compressed APX+TGF are streamed through `lzma.open` (`tools/iccma_data.py:557-560`) |
| 54 | "result files, query files, and update files as skipped support artifacts" | Confirmed: results-archive files and `.csv/.xlsx/.xls/.results` skipped (lines 360-361); `.arg/.query/.apxm/.tgfm/.asm` and `_arg.lzma`/`_query.lzma` skipped as `query_or_updates` (lines 362-366) | PASS — but doc's "update files" terminology is loose; tool calls these `query_or_updates` and also skips `.py` dynamic-app files (line 397-398) and `__MACOSX/` archive metadata (lines 358-359). Consider mentioning |
| 56 | "It does not run solvers" | Confirmed — no solver invocation in this tool. (Solver runs live in `tools/iccma2025_run_native.py`, `tools/iccma_run_selected.py`, `tools/iccma_run_timeout_rows.py`) | PASS |
| (omission) | doc never names `data/iccma/<year>/{archives,extracted,manifests}/` layout | The tool writes to `archive_dir = year_root / "archives"` (line 267), `extract_root = year_root / "extracted"` (line 291), `manifest_dir = year_root / "manifests"` (line 320). `docs/iccma-2025-data.md:46-52` documents this layout for 2025 | major — add an "Outputs" section mirroring the 2025 doc's structure |
| (omission) | doc has no mention of `extract` subcommand | `extract_parser` at line 206 supports `--force` flag; doc's command list jumps from `list` → `all` → `fetch` → `manifest` and skips `extract` | major — document the `extract [archive] [--force]` subcommand |
| (omission) | doc does not state the `archive` argument is positional and defaults to `"all"` | `fetch_parser.add_argument("archive", nargs="?", default="all")` (line 204); same for `extract` (line 207) | minor — clarify that omitting the archive name fetches all archives for the year |
| (omission) | doc does not mention `--root` override | `--root` arg at line 196 (default `data/iccma`) | minor — document for users who want a custom cache location |
| (omission) | doc does not mention `--json` output for `list` | `list --json` at line 201 | minor — add to commands section |
| (omission) | doc does not mention strict-mode exit code | `manifest --strict` and `all` both return exit code `1` when any row is `error` (lines 233-234, 240-241) | minor — useful for CI integration |
| (omission) | doc does not mention safe-extract behavior | `safe_extract_zip` and `safe_extract_tar` (lines 604-621) refuse traversal-unsafe members; tar uses `filter="data"` | optional prose — only if rewriter wants a security note |

## 2. Undocumented tooling that belongs here

`tools/` contains ten ICCMA-relevant scripts beyond `iccma_data.py`:

| Tool | One-line role (verified by listing only; not read) | Recommendation |
|---|---|---|
| `tools/iccma2025_data.py` | 2025-only data prep — already documented in `docs/iccma-2025-data.md` | call out the cross-doc relationship (see §6) |
| `tools/iccma2025_run_native.py` | 2025 runner against native or external ICCMA backend (per `docs/iccma-2025-data.md:60-78`) | mention in passing — runner, not data-prep |
| `tools/iccma_compare_range_traces.py` | Range/trace comparison utility (name only) | omit unless rewriter wants a "diagnostics" subsection |
| `tools/iccma_run_selected.py` | Selected-instance runner (name only) | omit |
| `tools/iccma_run_timeout_rows.py` | Timeout-row runner (name only) | omit |
| `tools/iccma_timeout_corpus.py` | Timeout corpus builder (name only) | omit |
| `tools/iccma_trace_classify.py` | Trace classifier (name only) | omit |
| `tools/check_sota_plan_order.py` | SOTA plan ordering check (unrelated to ICCMA data prep) | out of scope |
| `tools/check_workstream_phase_order.py` | Workstream ordering check (unrelated) | out of scope |

Recommendation: add a brief "See also" section listing the four `iccma_*` runners and the dedicated 2025 tool, with one-line summaries. Do not absorb their full surface into this doc.

## 3. Command-line example verification

All four examples (lines 25, 31, 37, 43) are syntactically valid against the argparse setup in `tools/iccma_data.py:194-214`. None were executed at runtime — verification is by reading the parser definitions, not by invocation.

| Example | Parser path | Verdict |
|---|---|---|
| `--year all list` | `--year` accepts `all` (line 197); `list` subparser (line 200) | shape OK |
| `--year 2023 all` | year `2023` valid (line 139); `all` subparser (line 213) | shape OK |
| `--year 2019 fetch instances` | year `2019` valid (line 107); `fetch` subparser (line 203); archive `instances` is the only 2019 spec name (line 109) | shape OK |
| `--year 2025 manifest --strict` | year `2025` valid (line 163); `manifest --strict` (lines 210-211) | shape OK |

Missing example coverage: the `extract` subcommand has no example (despite being a top-level subparser). Recommend adding:

```powershell
uv run tools\iccma_data.py --year 2017 extract benchmarks-a
```

## 4. Citation/reference audit

`docs/iccma-data.md` cites no academic papers or external standards documents. The only external references are:

- `argumentationcompetition.org` (line 4) — verified by appearance in 13 archive URLs (e.g. lines 51, 67, 74, 111, 120, 127).
- "Zenodo" (line 6) — verified by Zenodo URLs at lines 144-145, 154-155, 167-169, 178-180.

No academic citations to audit. No DOI references in this doc; `docs/iccma-2025-data.md:8, 12` does cite Zenodo DOIs (`10.5281/zenodo.17949380`, `10.5281/zenodo.18506390`) — consider adding equivalents for 2023 (`10.5281/zenodo.8348039`, inferable from URL line 144) to this doc.

## 5. Prose recommendations (severe only)

1. **Missing outputs section.** Doc never tells the reader where files end up. The tool deterministically writes to `data/iccma/<year>/{archives,extracted,manifests}/` (verified at `tools/iccma_data.py:267, 291, 320`). `docs/iccma-2025-data.md:44-52` already shows the right shape; mirror it.

2. **`extract` subcommand omitted.** All five subparsers (`list`, `fetch`, `extract`, `manifest`, `all`) are equally important; `extract` is the only one with no example. This is a literal hole.

3. **Doc claims size-only verification "where pages do not publish checksums" (lines 4-5).** Accurate but understated: the 2015/2017/2019/2021 specs simply have `md5=None` in source — there is no detection logic. Reader could mistakenly think the tool probes for checksums. Recommend rewording to "older editions are verified by file size only; Zenodo-hosted 2023 and 2025 archives also verify MD5."

4. **No mention of resumable downloads / partial-file behavior.** `download()` writes to a `.part` sidecar then renames (lines 275-278); existing files are re-verified rather than re-downloaded (lines 271-274). Worth one sentence given the 6.8 GB warning.

Other prose is concise and accurate.

## 6. Cross-doc dependencies — overlap with `docs/iccma-2025-data.md`

There is significant overlap. Findings:

- **Functional overlap.** `docs/iccma-2025-data.md:1-56` describes the same workflow (fetch → extract → manifest) for the 2025 edition specifically, backed by a different tool (`tools/iccma2025_data.py`, not read).
- **Spec duplication.** `docs/iccma-2025-data.md:8-15` restates the 2025 archive sizes and MD5 hashes that are also encoded in `tools/iccma_data.py:163-186`. Two sources of truth for the same numbers.
- **Tool divergence.** Two distinct tools: `tools/iccma_data.py` (multi-year, including 2025) and `tools/iccma2025_data.py` (2025-only, with extra `tasks` subcommand per `docs/iccma-2025-data.md:35` that does not exist in the multi-year tool — `tools/iccma_data.py:198-213` has no `tasks` subparser).
- **Output layout divergence.** `docs/iccma-2025-data.md:51-52` documents `iccma-2025-task-matrix.{json,csv}` — a 2025-specific manifest companion not produced by `tools/iccma_data.py` (no `task_matrix` writes anywhere in the multi-year tool).
- **Runner section.** `docs/iccma-2025-data.md:58-78` covers `tools/iccma2025_run_native.py` — an actual runner, out of scope for `iccma-data.md`.

Recommendation:
- **Do not merge.** The 2025 doc covers a 2025-only `tasks` subcommand, the official subtrack matrix, and a runner that have no equivalent in the multi-year tool. Merging would lose precision.
- **Cross-link instead.** Add to `docs/iccma-data.md` a "See also" pointer to `docs/iccma-2025-data.md` for the official 2025 task matrix and the 2025 runner, and reciprocally add a pointer from `docs/iccma-2025-data.md` to `docs/iccma-data.md` for multi-year archive prep.
- **Sanity check.** Confirm that `tools/iccma2025_data.py` and `tools/iccma_data.py` agree on the 2025 archive sizes and MD5s (both should encode the same Zenodo identifiers); rewriter should call out which is canonical if they ever drift.

## 7. Verdict

`docs/iccma-data.md` is factually accurate where it speaks, but it is incomplete: it omits the `extract` subcommand, never describes the `data/iccma/<year>/{archives,extracted,manifests}/` output layout, and does not cross-reference its 2025-specific sibling doc or the four runner scripts in `tools/`. Health: medium — the rewriter's main job is filling holes, not correcting errors. No claim in the doc contradicts the source; the gaps are all sins of omission.
