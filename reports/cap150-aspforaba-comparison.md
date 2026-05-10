# Cap150 ASPforABA Comparison

Workflow used: Workstream 3 from `workstreams/post-cap150-solver-frontier.md`.

Local source reread:

- `scratch/sources/aspforaba/aspforaba/README.md`: ASPforABA ICCMA 2023 usage is
  `./aspforaba -f <input_file> -p <problem> [-a <query>]`.
- `scratch/sources/aspforaba/aspforaba/README.md`: supported ABA problems are
  `DC-CO`, `DC-ST`, `DS-PR`, `DS-ST`, `SE-PR`, and `SE-ST`.
- `scratch/sources/aspforaba/aspforaba/aspforaba.py`: preferred single-extension
  solving uses the in-process clingo API in `se_pref`.

Command:

```powershell
uv run tools\iccma_run_timeout_rows.py --timeouts tests\manifests\iccma2025-cap150-timeouts.json --subtrack SE-PR --timeout-seconds 15 --backend iccma --iccma-binary "uv run scratch\sources\aspforaba\aspforaba\aspforaba.py" --output data\iccma\timeouts\cap150-aba-se-pr-aspforaba-rerun.json
```

Result:

- total frozen `SE-PR` rows: 11
- solved by ASPforABA path: 11
- timed out by ASPforABA path: 0

Rows solved by ASPforABA that the package Z3 path had timed out on:

- `ABAs/aba_100_0.1_10_5_7.aba`
- `ABAs/aba_100_0.3_10_5_5.aba`
- `ABAs/aba_100_0.3_10_5_7.aba`
- `ABAs/aba_100_0.3_5_5_1.aba`
- `ABAs/aba_500_0.1_10_5_2.aba`
- `ABAs/aba_500_0.1_10_5_7.aba`
- `ABAs/aba_500_0.3_10_10_1.aba`
- `ABAs/aba_500_0.3_10_10_7.aba`
- `ABAs/aba_500_0.3_10_10_9.aba`
- `ABAs/aba_500_0.3_5_5_2.aba`
- `ABAs/aba_500_0.3_5_5_5.aba`

Decision:

Keep ASPforABA as a comparison path. Do not make it the default solver path from
this workstream alone; it is external tool wiring, and the current default solver
workstream is still source-owned by the package Z3 path.
