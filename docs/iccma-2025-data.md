# ICCMA 2025 Data

This repo keeps ICCMA benchmark data out of git. Use the local cache under
`data/iccma/2025/`.

## Sources

- Instances: Zenodo record `10.5281/zenodo.17949380`
  - file: `ICCMA-2025-instances.zip`
  - size: `866229263`
  - md5: `5b3231eb3206b78494db2b451ac3ab55`
- Raw results: Zenodo record `10.5281/zenodo.18506390`
  - file: `ICCMA-2025-results.zip`
  - size: `1351761`
  - md5: `262ea63627603d8906737d32228296c2`

## Commands

Fetch and verify both archives:

```powershell
uv run tools\iccma2025_data.py fetch
```

Extract both archives:

```powershell
uv run tools\iccma2025_data.py extract
```

Build manifests and fail if any parsed AF/ABA instance is malformed:

```powershell
uv run tools\iccma2025_data.py manifest --strict
uv run tools\iccma2025_data.py tasks
```

Run the whole data-preparation flow without invoking any solver:

```powershell
uv run tools\iccma2025_data.py all
```

## Outputs

- `data/iccma/2025/archives/` stores downloaded zip files.
- `data/iccma/2025/extracted/instances/` stores extracted benchmark instances.
- `data/iccma/2025/extracted/results/` stores extracted raw results.
- `data/iccma/2025/manifests/iccma-2025-manifest.{json,csv}` classifies and
  validates extracted files.
- `data/iccma/2025/manifests/iccma-2025-task-matrix.{json,csv}` records the
  official 2025 subtracks used for later dry-run or solver execution.

The data workflow parses official numeric `p af <n>` AF files and official
numeric `p aba <n>` flat-ABA files. Dynamic-track applications are classified
but not executed by this data-preparation flow.
