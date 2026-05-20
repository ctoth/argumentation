# ABA telemetry and ICCMA runner profiling

Date: 2026-05-20

Status: kept on `main`.

Branch: `main`.

Evidence commits:
- `3563737` Use iterative ABA telemetry SCC traversal.
- `05193df` Constrain ABA fixture to dense structural cluster.
- `8695370` Target dense ABA structural fixture cluster.
- `c729c31` Report ABA fixture cluster counts.
- `79f8d96` Target sparse narrow ABA hard cluster.
- `74ff61f` Add sparse narrow ABA 10x10 fixture.
- `33fa190` Add ICCMA runner row filters.
- `959a2db` Bound profiled ICCMA workers inside row timeout.
- `6615bf9` Allow profiled ICCMA rows in CSV output.
- `cc005eb` Tolerate solver metadata in ICCMA CSV output.
- `28a55ec` Record completed ABA telemetry workstream.

Hypothesis: hard ICCMA ABA rows could be made routable only after recording
shape telemetry and profiling evidence inside the real ICCMA row runner.

Gate: focused ICCMA fixture selection, row-filtered runner execution, and
profiled worker metadata accepted by CSV output.

Outcome: kept. This was infrastructure, not a solver win by itself.

Reason: it produced the operational contract surface used by later work:
shape-based row routing, per-row profiling, and hard-cluster fixture replay.
This is not a filename heuristic and is not ICCMA-specific except for the
runner entrypoint.
