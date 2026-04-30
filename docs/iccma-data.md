# ICCMA Data

Use `tools\iccma_data.py` for multi-year ICCMA data preparation. The older
edition archives are self-hosted on `argumentationcompetition.org`; where those
pages do not publish checksums, the tool verifies the published file size only.
Zenodo-hosted 2023 and 2025 archives are verified by size and MD5.

## Covered Editions

- ICCMA 2015: benchmark zip and updated result spreadsheet.
- ICCMA 2017: detailed result zip and benchmark groups A, B, C, D, and T.
- ICCMA 2019: instance tarball.
- ICCMA 2021: instance tarball plus exact and approximate result CSVs.
- ICCMA 2023: Zenodo benchmark and raw-result zips.
- ICCMA 2025: Zenodo instance and raw-result zips.

The 2021 instance archive is about 6.8 GB. Fetch it intentionally rather than
as a casual smoke test.

## Commands

List known archive metadata:

```powershell
uv run tools\iccma_data.py --year all list
```

Fetch, extract, and manifest one edition:

```powershell
uv run tools\iccma_data.py --year 2023 all
```

Fetch only one archive:

```powershell
uv run tools\iccma_data.py --year 2019 fetch instances
```

Build a manifest from already extracted files:

```powershell
uv run tools\iccma_data.py --year 2025 manifest --strict
```

## Manifest Support

The manifest pass classifies and stream-validates:

- numeric `p af <n>` AF files
- numeric `p aba <n>` ABA files
- APX files with `arg(...)` / `att(...)`
- TGF files
- result files, query files, and update files as skipped support artifacts

It does not run solvers.
