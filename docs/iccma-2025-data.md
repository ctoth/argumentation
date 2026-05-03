# ICCMA 2025 data

This repo keeps ICCMA benchmark data out of git. Use the local cache under
`data/iccma/2025/`.

For other editions (2015 / 2017 / 2019 / 2021 / 2023), see
[`iccma-data.md`](iccma-data.md).

## Sources

- **Instances** — Zenodo record `17949380`
  - file: `ICCMA-2025-instances.zip`
  - size: `866229263`
  - md5: `5b3231eb3206b78494db2b451ac3ab55`
- **Raw results** — Zenodo record `18506390`
  - file: `ICCMA-2025-results.zip`
  - size: `1351761`
  - md5: `262ea63627603d8906737d32228296c2`

The numeric ids above are Zenodo *record ids*, used directly in the API
URLs `https://zenodo.org/api/records/{id}/files/...`. Resolved DOIs (if
needed) should be verified against Zenodo's record metadata.

## Data preparation

Fetch and verify both archives (omit the archive name to fetch all):

```powershell
uv run tools\iccma2025_data.py fetch
```

Extract both archives (`--force` overwrites existing extraction):

```powershell
uv run tools\iccma2025_data.py extract
```

Build manifests:

```powershell
uv run tools\iccma2025_data.py manifest --strict
uv run tools\iccma2025_data.py tasks
```

`--strict` exits status `1` if any parsed AF/ABA instance has
`parse_status == "error"`. The `tasks` subcommand emits the official
2025 subtrack matrix:

- **MAIN_TRACK** — 1200 s timeout, certificate required.
- **HEURISTICS_TRACK** — 60 s timeout.
- **DYNAMIC_TRACK** — 60 s timeout, certificate required.
- **ABA_TRACK** — 1200 s timeout, certificate required.

Run the whole data-preparation flow (fetch + extract + manifest + tasks),
without invoking any solver:

```powershell
uv run tools\iccma2025_data.py all
```

## Data outputs

```
data/iccma/2025/
├── archives/                                  # downloaded zip files
├── extracted/
│   ├── instances/                             # benchmark instances
│   └── results/                               # raw competition results
├── manifests/
│   ├── iccma-2025-manifest.{json,csv}         # classification + validation
│   └── iccma-2025-task-matrix.{json,csv}      # official subtrack matrix
└── runs/                                      # native-runner artifacts (see below)
```

The data workflow parses official numeric `p af <n>` AF files and official
numeric `p aba <n>` flat-ABA files. Flat-ABA validators enforce that rule
heads are disjoint from assumptions and that each assumption has exactly one
contrary. Dynamic-track applications are classified as `dynamic_app` but
not executed.

## Native runner

`tools/iccma2025_run_native.py` executes the benchmark suite. Backend
options: `native` (package reference), `iccma` (subprocess via
`ICCMAConfig`), or `auto` (route based on task and capability).

Skip oversized native jobs:

```powershell
uv run tools\iccma2025_run_native.py --backend native --max-af-arguments 100 --max-aba-assumptions 10 --timeout-seconds 5
```

Run AF jobs through an external ICCMA solver:

```powershell
uv run tools\iccma2025_run_native.py --backend iccma --iccma-binary path\to\solver.exe --max-af-arguments -1 --max-aba-assumptions 1000 --timeout-seconds 1200
```

`--max-af-arguments -1` disables the AF size cap. **Note:**
`--max-aba-assumptions 0` silently skips every ABA instance with one or
more assumptions; pass a high cap (or omit the flag) to actually run ABA
jobs.

If `--iccma-binary` is omitted, the runner falls back to the
`ICCMA_AF_SOLVER` environment variable.

Other useful flags:

- `--label <name>` — appears in artifact filenames. Default
  `native-bounded`. Load-bearing for distinguishing parallel runs.
- `--no-progress` — silences per-row stderr JSON progress events.

The runner writes:

```
data/iccma/2025/runs/iccma-2025-{label}.json
data/iccma/2025/runs/iccma-2025-{label}.csv
data/iccma/2025/runs/iccma-2025-{label}-summary.json
```

The contest tag (`iccma-2025`) is inferred from the `--root` directory
name; if you pass a custom `--root`, the tag changes accordingly.

The runner uses the package-native ABA path. Library-level
`argumentation.solver.solve_aba_*` surfaces separately support
ICCMA-compatible ABA subprocess dispatch via `ICCMAConfig(...)`.
