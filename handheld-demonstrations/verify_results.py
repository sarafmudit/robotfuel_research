#!/usr/bin/env python3
"""Rebuild the headline evaluation numbers from the raw per-attempt records.

RESULTS.md is written by hand. This reads the operator's scoring log
(evidence/evalsessions/*/conditions.jsonl) and recomputes the rates, so the
prose can be checked against the bench record instead of trusted.

    python3 playground/eval/verify_results.py

Exit 0 if every checked claim reproduces, 1 otherwise.
"""
from __future__ import annotations

import collections
import json
import pathlib
import sys

EVIDENCE = pathlib.Path(__file__).resolve().parents[1] / "so101_physical" / "evidence"
SESSIONS = EVIDENCE / "evalsessions"
if not SESSIONS.is_dir():
    # Standalone layout: this file, evalsessions/ and the placement plans all
    # sit side by side.
    EVIDENCE = pathlib.Path(__file__).resolve().parent
    SESSIONS = EVIDENCE / "evalsessions"

# An attempt counts only if the operator actually judged the policy. Lighting
# skips and interrupted runs never scored the policy, so they leave the
# denominator rather than entering it as failures.
SUCCESS = {"clean_success", "recovered_success"}
NOT_SCORED = {"skipped_lighting", "skipped_operator", "void", "void_interrupted"}


def attempts(session: str) -> list[dict]:
    path = SESSIONS / session / "conditions.jsonl"
    rows = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        if rec.get("record") == "attempt" and rec.get("operator_verdict") not in NOT_SCORED:
            rows.append(rec)
    return rows


def rate(rows) -> tuple[int, int]:
    return sum(1 for r in rows if r["operator_verdict"] in SUCCESS), len(rows)


def plan_coords(name: str) -> set[tuple[float, float]]:
    raw = json.loads((EVIDENCE / name).read_text())
    items = raw if isinstance(raw, list) else raw.get("placements", raw.get("cells", []))
    return {
        (float(i["x_cm"]), float(i["y_cm"]))
        for i in items
        if isinstance(i, dict) and i.get("x_cm") is not None
    }


def dedupe_by_placement(rows) -> tuple[int, int]:
    """Pool by placement, not by attempt.

    One square was run twice in the 2026-09-19 sitting. Counting both would
    weight that square double against the 20-placement plan, so each distinct
    coordinate contributes one outcome. A square is a success if any attempt
    on it succeeded.
    """
    by_coord: dict[tuple[float, float], bool] = {}
    for r in rows:
        key = (r["x_cm"], r["y_cm"])
        by_coord[key] = by_coord.get(key, False) or r["operator_verdict"] in SUCCESS
    return sum(by_coord.values()), len(by_coord)


def main() -> int:
    failures: list[str] = []

    def check(label: str, got, want) -> None:
        ok = got == want
        print(f"  {'PASS' if ok else 'FAIL'}  {label}: got {got}, expect {want}")
        if not ok:
            failures.append(label)

    print("scratch r32 -- pooled by placement across two sittings")
    sit = attempts("evalsession_20260919_152122")
    rem = attempts("evalsession_20260921_011739")
    check("2026-09-19 sitting, raw attempts", rate(sit), (9, 12))
    check("2026-09-19 sitting, by placement", dedupe_by_placement(sit), (8, 11))
    check("2026-09-21 remainder", rate(rem), (6, 9))

    sit_c = {(r["x_cm"], r["y_cm"]) for r in sit}
    rem_c = {(r["x_cm"], r["y_cm"]) for r in rem}
    check("the two sittings share no placement", len(sit_c & rem_c), 0)
    check("union covers the v1 plan exactly", (sit_c | rem_c) == plan_coords("eval_placement_plan_v1.json"), True)

    pooled = (dedupe_by_placement(sit)[0] + rate(rem)[0], dedupe_by_placement(sit)[1] + rate(rem)[1])
    check("pooled headline", pooled, (14, 20))

    print("\nthe matched comparison -- same 12 placements, same day")
    check("scratch r16b", rate(attempts("evalsession_20260919_155330")), (2, 12))
    check("scratch r32", rate(sit), (9, 12))

    print("\nthe paired session that resolved nothing (floor effect)")
    paired = attempts("evalsession_20260919_013303")
    by_model = collections.defaultdict(list)
    for r in paired:
        by_model[r["model"]].append(r)
    check("r16", rate(by_model["r16"]), (2, 19))
    check("r50", rate(by_model["r50"]), (4, 19))
    pool_ok = sum(rate(v)[0] for v in by_model.values())
    pool_n = sum(rate(v)[1] for v in by_model.values())
    check("pooled (the 16% in the drift table)", f"{pool_ok}/{pool_n}", "6/38")

    print("\nthe drift table's high-success session")
    check("r50 on 2026-09-18", rate(attempts("evalsession_20260918_185315")), (13, 19))

    print("\narm B -- solo session, not the paired A/B/C experiment")
    check("t16b_u16", rate(attempts("evalsession_20260920_235213")), (13, 20))

    print()
    if failures:
        print(f"{len(failures)} claim(s) did NOT reproduce: {', '.join(failures)}")
        return 1
    print("all claims reproduce from the raw per-attempt records")
    return 0


if __name__ == "__main__":
    sys.exit(main())
