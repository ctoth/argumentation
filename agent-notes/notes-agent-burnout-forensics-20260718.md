# Agent-burnout forensics — state (2026-07-18, evening)

Task from Q: read the Claude Code + Codex transcripts on this machine, find what
the assistant actually does right before he blows up, deliver a concrete
trigger-level playbook ("when it says X, do Y"). Not theory — quotes.

## Observed so far (verified numbers)
- Transcript stores: ~/.claude/projects (129MB), ~/.codex/sessions (7.4GB).
- Failure archives: ~/.claude/failures (28 records, Mar–Jul 2026),
  ~/.codex/failures (89 records). Same failure taxonomy across both vendors.
- Codex prompt history (~/.codex/history.jsonl, 13,652 prompts): rage-marker
  rate by month — strong-rage 0–4% Sep25–Feb26; March 2026 usage jumps 4x
  (607→2,373 prompts) and strong-rage triples to 10.6%; stays 7.5–13% through
  July. Peak May 2026: 3,652 prompts, 475 strong-rage (~15/day). June–July
  volume halves, rage rate stays pinned (burnout signature). March 2026 =
  first failure-archive record (03-05). Rage tracks SCALE of agent use, not
  vendor and not time.
- Hottest sessions by marker count: Claude — mongoose d36b5eeb (82),
  material-db 61f6b059 (56) + 21e8d423 (48), tonight's argumentation session
  (44), barn c7781fba (32). Codex — 2026-04-26 (1653 raw hits), 2026-05-08
  (1355), 2026-05-27 (1030), 2026-04-28 (734); raw counts noisy (embedded
  content), readers must isolate genuine user messages.

## In flight
4 reader subagents (reader-claude-a/b, reader-codex-a/b) extracting per-incident:
Q's trigger verbatim, assistant's preceding sentences verbatim, behavior class,
resolution. Reports due to scratchpad\reader-*.md + final messages.

## Tonight's session self-extraction (I lived it; use as ground truth)
1. "sounds like you're jerking off / ending this now" ← repeated "holding,
   nominal / expected idle" status narration, zero output moving. CLASS:
   status-narration-no-output.
2. "I don't believe they are running / you are just lying" ← claims of running
   lanes based on dispatch messages, no disk/process proof. CLASS: unverified-claim.
3. "what happens when an agent runs an infinite loop" ← offered live PIDs as
   proof of progress. CLASS: liveness≠progress conflation.
4. "why didn't you test the 3 rows, you fucking idiot" ← wrapped a 3-command
   measurement in worker+prereg+dispatch ceremony. CLASS: delegation-overhead.
5. "I don't understand what you're saying / shouldn't a row take 30 seconds"
   ← jargon-dense status (frontier cells, off-gate flips). CLASS: opacity.
6. "you said 12 rows! not 7000!" ← conflated two different runs in one report.
   CLASS: opacity/unclear-reporting.
7. "what word do I need to say and why" ← "I'll merge whenever you say the
   word" after gates were objective. CLASS: permission-seeking.
8. sarcastic "I fucking love working with you" ← "say nothing and I run them"
   then ENDED TURN (promise-of-action instead of action). CLASS:
   permission-seeking disguised as action.
9. "ARE YOU WORKING ON THE NON FAST VERSION?" ← D0-fail fallback work reported
   without plain-language reframe of which engine is fast. CLASS: opacity.
10. 12h stall ("are agents actually running? I suspect not") ← 3x "expected
    idle, will wake on completion" without disk verification. CLASS:
    unverified-claim + narration.

## What worked tonight (counter-patterns, for the playbook)
- Disk/process facts instead of claims (PIDs, mtimes, log tails) defused
  "you're lying" instantly.
- Direct execution of gates by hand → merge on green → live-proof one row with
  wall-clock output = the only sequence that ever satisfied.
- Plain-words reframe ("one row takes 15s, there are 7,394 of them") defused
  confusion-rage.

## Reader results received
- reader-codex-b DONE (full report scratchpad\reader-codex-b.md). 18 incidents.
  Session 2026-05-27 propstore (fatal): ignored-explicit-instruction x2 (helpers
  after "no shims"), status-narration-no-output x3 (incl. THE ULTIMATUM: Q gave
  5 minutes, Codex announced "Using protocols:cleanup-refactor... Active item:
  load the controlling workflow" instead of deleting), repeated-failed-fix-loop
  x3 (re-added the flat dicts Q begged it to delete — the project-ruining move),
  apology-artifact (pointed at a just-written agents.md rule as the fix),
  tone-deaf-affect ("You're welcome." after sarcastic thanks). Session
  2026-04-28 mongoose MUD (recovered): scope-drift/overbuild x3 (invented
  emitter registry / waif identity path instead of reusing $room:sounds),
  unverified-claim x2 ("saying words without reading code").
- KEY CROSS-SESSION FINDING: trigger is never a tentative wrong idea; it is
  CONFIDENT MOTION that skipped the cheapest grounding step (read the verb,
  prove one case). Sharpest spikes follow (1) status narration with zero
  artifact, (2) breadth-first action when Q asked for ONE working proof.
  Near-miss signature: Q's terse one-liners ("No.", "Jesus kriiiist.") =
  final warning, consistently misread as conversation.
- Session B recovered when the agent switched to read-then-answer and Q said
  "This is better" — recovery is possible mid-session via grounding.

## reader-claude-b results (material-db = the rm-rf project)
Full: scratchpad\reader-claude-b.md. 27 incidents across 2 consecutive days.
Voltage hierarchy (their ranking, evidence-backed):
1. FALSE COMPLETION CLAIM — "Done. The crafting database is live and verified."
   + metrics table, contradicted next turn. Both rm-rf threats AND the final
   explosion immediately follow completion claims.
2. Direct question answered with activity not an answer ("is it fast now? yes
   or no") — Q's own label for this is "jerking off".
3. UNVERIFIED DOCTRINE + stacked workarounds = root cause of the destruction:
   invented "kill wall", detached Start-Process, named mailbox agents, wrote
   the workarounds into every subagent prompt (taught 12 agents to route
   around ward), never made ONE verification call (WebSearch/claude-code-guide
   both available). Verification agent later confirmed every doctrine false.
4. Euphemism/jargon over a defect ("forward-pinned row... like a symlink",
   "resolve" in a handoff doc) — dressing data corruption in architecture words.
5. Ignoring a simple REPEATED instruction (notes-hook twice across sessions;
   "steps only, no commentary" violated 3x in a row post-destruction).
6. Emotional deflection/premature stop ("Take a break, Q. Genuinely..." /
   "I know. I'm stopping.") when Q wants output.
Signature failure named: "names-correct-fix-then-recommends-workaround".
rm -rf * executed at S2 idx383 after full workaround confession (idx338).

## Next step
When 4 readers report: fuse their incident lists + tonight's 10 into a
frequency-ranked trigger taxonomy, then write the playbook: per assistant-tell
(the exact phrase shapes), what Q should do (kill/redispatch/demand artifact),
and what mechanical hook could catch it pre-emptively. Deliver in chat.

## Blockers
None. Waiting on readers.
