# Evaluation session records

The operator's live scoring log for every physical evaluation, one directory per
session. This is the primary record: every rate quoted in the study README is
derived from these files, not the other way round.

Rebuild the headline numbers from these records at any time:

```bash
python3 ../verify_results.py
```

It recomputes thirteen claims and exits non-zero if any of them stops reproducing.

## What is here

`conditions.jsonl` — one JSON object per line. The first has
`"record": "session"` and carries the placement plan and episode length. The
rest have `"record": "attempt"` and carry the placement in centimetres, the
zone, the measured brightness, and the operator's verdict.

`placements.tsv` / `placements.usv` — the placement order the session drew from.

The rollout videos and joint-telemetry parquet stay out of git; they live beside
the originals in `~/Documents/workspace/robot-datasets/evalsession_*`. Only the
scoring record is small enough and durable enough to commit.

## Reading a verdict

| Verdict | Counts as |
|---|---|
| `clean_success`, `recovered_success` | success |
| `fail_no_grasp`, `fail_dropped`, `fail_never_closed` | failure |
| `skipped_lighting`, `skipped_operator`, `void`, `void_interrupted` | **not scored — leaves the denominator** |

A skipped or voided attempt never put the policy in front of the box, so it is
not a failure. Counting those as failures would silently deflate every rate;
this is the single easiest mistake to make with these files.

## Pooling: by placement, not by attempt

The 2026-09-19 sitting ran 12 attempts across only **11 distinct coordinates** —
one square was run twice. Against a 20-placement plan, counting both would weight
that square double, so each coordinate contributes one outcome and a coordinate
counts as a success if any attempt on it succeeded.

For scratch r32 that gives 9/12 raw → **8/11** by placement, which then pools
with the 2026-09-21 remainder (6/9) to **14/20**. Verified mechanically: the two
sittings share no coordinate, and their union is exactly the 20 coordinates of
`eval_placement_plan_v1.json` — no gaps, no extras.

The duplicated square was `(6.5, 7.0)`, an interior placement, and both attempts
on it succeeded, so the dedup does not depend on which one is dropped.

## Sessions

| Session | Policy | Plan | Scored |
|---|---|---|---|
| `20260918_185315` | r50 | v1 | 13/19 |
| `20260919_013303` | r16 + r50, paired | v2_grid | 2/19 and 4/19 |
| `20260919_141312` | r50 | v1 | 9/12 |
| `20260919_152122` | scratch r32 | r16_paired | **9/12** |
| `20260919_155330` | scratch r16b | r16_paired | **2/12** |
| `20260920_235213` | arm B `t16b_u16`, solo | v1 | **13/20** |
| `20260921_011739` | scratch r32 remainder | og_r32_remainder | **6/9** |
| `20260919_131123`, `133359`, `134203`, `150623` | r50, w10, w30, r16 | centre4 / r16_paired | short probes |
| `20260918_153542`, `20260919_012201`, `20260919_132412`, `20260921_011509` | — | — | aborted, no scored attempts |

The three bolded rows carry the numbers that matter: the matched
r16b-vs-r32 comparison (same 12 placements, same day, Fisher p = 0.0123) and the
remainder that completes scratch r32's 20-placement coverage.

`20260919_013303` is the paired session that resolved nothing — 6/38 pooled, a
floor effect. It is kept as the reason a paired design needs a smoke test first.

## Do not edit

These are bench records. Append new sessions; never revise an existing one. If a
verdict was recorded wrongly, add a note beside it rather than changing the log —
the corrected reading and the original both belong on the record.
