# Capstone Main holdout review — verifier state checkpoint

Task: prompts/capstone-main-holdout-review.md → write reports/capstone-main-holdout-review.md (PASS/FAIL).

## Verified facts so far
- Frozen hashes: main-dev.json, main-holdout.json, nolimits-dev.json, nolimits-portfolio.json all match FRAME.md sha256 exactly (hashed holdout without reading contents).
- Receipts: only receipts/nolimits-holdout-access.json exists. No Main receipt → Main holdout unspent. Matches FRAME.
- main-dev-results.json: 104 rows, all (instance,subtrack) keys unique, exactly 8 manifest instances × 13 subtracks, zero missing pairs. All status=solved, track=main, backend=auto (selected sat), error=None, accounting=cpu_time, budget=1200s, max cpu 2.44s, max wall 2.64s. elapsed==wall for all rows. source_archive_hashes uniform and equal to manifest source md5s.
- git_commit uniform across all 104 rows: 2bf2225d69a07fd6bb6e4acbea303e370e271c12 = "frame(iccma): freeze development and sealed holdouts" (same commit that froze the frame).
- Certificate validation: 69/104 accepted (authority=argumentation.solver_adapters.iccma_af), 35/104 not_applicable (authority=None). not_applicable = DC-false rows, DS-true rows, ALL 8 DS-PR rows, 1 SE-ST row. → missing-oracle angle: DS-PR has zero validated rows.
- Raw protocol outputs are ICCMA-2023-shaped (YES/NO + "w ..." witness lines; SE rows answer=null with witness list; SE-ID empty "w\n" allowed). My naive mismatch list was my own wrong expectation, not a defect — re-audited manually.
- Disjointness (minimal disclosure): no dev instance path substring appears in main-holdout.json or nolimits-holdout.json.
- Both holdout manifests committed in PLAINTEXT at freeze commit 2bf2225 alongside .sealed copies → seal is procedural (receipt-gated), not cryptographic. Trust-boundary point to discuss.
- Dirty worktree: uncommitted deletion of tests/structured/aba/test_aba_cadical2_eager_arc_contract.py (ABA, not AF-main path); many untracked notes/logs/prompts. No tracked modification under experiments/, tools/, src/.

## Round 2 findings
- SE-ST not_applicable row = WS_100_6_10_30 SE-ST: answer null, output "NO\n" (no stable extension exists) — valid ICCMA output; nonexistence has no certificate → not_applicable is honest.
- "instances": 7 in iccma_manifest_loaded event = len(manifest dict keys) (7 top-level keys), a cosmetic logging bug, NOT missing instance.
- Event log: 1231 events = run_start + manifest_loaded + task_matrix(104) + jobs_built + 104 row_start + 1018 sat_check + 104 row + rows_complete. No label field recorded anywhere (FRAME command has --label capstone-main-dev; runner apparently doesn't log it). No seal/receipt events in dev log (dev manifest is not sealed — fine).
- CSV == JSON on (instance,subtrack,status), 104 rows each.
- DIRTY-WORKTREE FINDING (main one): dev results committed at d0de71d together with an 18-line runner modification (empty-witness "w\n" fix, event-log/CSV newline fixes). Freeze-commit code would emit "w \n" for empty extension; committed results contain "w\n" → run was executed with the modified runner while HEAD was 2bf2225, so rows' git_commit=2bf2225 stamp does NOT identify the code that ran. Runner has no dirty-worktree detection.
- Mitigation: git diff d0de71d..HEAD on tools/iccma_run_native.py is EMPTY → HEAD runner is byte-identical to the runner that produced the evidence (as committed at d0de71d). git diff 2bf2225..HEAD on src/ shows nothing → solver library unchanged since freeze. Net d0de71d..HEAD = experiment records/prompts/reports + the aaf5b2f/b401bfc/route-test commits all fully reverted (runner diff empty proves net-zero on runner).
- Sealed files contain sha256-of-manifest text; both match FRAME hashes. Receipt exists only for nolimits (commit 7825b4d, manifest hash matches nolimits frozen hash). Main receipt absent → unspent.
- Frame test (tests/interop/test_iccma_capstone_frame.py): frozen hashes, 8+8 instances, 13 subtracks, same 8 families both partitions, dev/holdout path disjointness, cpu_time accounting for main, sealed-file contents; runner rejects sealed holdout without --open-sealed-holdout before starting; holdout access is one-time + receipted; main track forbids --portfolio-config (No-Limits portfolio cannot enter Main path via CLI).
- Answer authority test: classify_result_authority — candidate "cannot be its own authority"; agreement-only = observed, not truth.
- BASELINE.md gate: 104/104 solved, 69 accepted certificates, 35 one-sided/no-witness rows "uncounted, not inferred correct", CPU sum 25.765625s, results sha256 94ded371bbd752975c407af244f86d4d18349e13c4c1fc2fc253df196b13be0d. My independent counts match (104 solved, 69 accepted, 35 not_applicable).

## Round 3 findings — TASK COMPLETE
- Results sha256 94ded371... matches BASELINE.md; CPU sum 25.765625 matches; 69 accepted / 0 rejected confirmed.
- Cert checker (_validate_witness_certificate, iccma_af.py:347): stable/complete/grounded full; preferred/ideal = admissibility ONLY; semi-stable = complete-extension ONLY; stage = conflict-free ONLY; never receives query → DC-true membership / DS-false exclusion never checked on native path. Query-aware validation exists only on external-binary parse path (unused by Main). Frozen evaluator, applies equally to dev+holdout → finding F2, not blocker.
- Gate tests: 33 passed (frame + result-authority + runner).
- Re-execution of the exact frozen Main dev command at HEAD (d29059f) into tmp outputs: all 104 rows IDENTICAL to committed evidence on every substantive field (answer, witness, raw_protocol_output, certificate_validation, backend, route_metadata, status, source hashes, resource contract); only git_commit stamp + timing differ. Dirty-worktree attack neutralized empirically.
- Tree hashes: src identical 2bf2225==d0de71d==HEAD (09f7f9ef); tools and tests HEAD==d0de71d (bf454d0a / ba0f7811). Net d0de71d..HEAD = 23 files, +54028/-0, all experiments/prompts/reports. No-Limits route commits fully reverted.
- Sealed sidecars contain exactly the frozen manifest hashes. Only nolimits receipt exists (manifest hash matches, commit 7825b4d). Main receipt absent.

## Deliverable
reports/capstone-main-holdout-review.md written: **PASS**, Main holdout AUTHORIZED with conditions (clean checkout at d29059f trees; verbatim FRAME command; interpret under partial-certificate caveat F2). Findings F1–F5: F1 dirty-worktree provenance (git_commit=2bf2225 misidentifies producing code; neutralized by reproduction), F2 partial certificates + no query-membership check, F3 plaintext holdout manifests (procedural seal; Main src untouched since freeze so no exploitation), F4 current worktree dirty (holdout must run from clean checkout), F5 cosmetic (instances:7 = len(dict); label not recorded).
- tmp-verify-* files deleted.

## Blockers
None. Done.
