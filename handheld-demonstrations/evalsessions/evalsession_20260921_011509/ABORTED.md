# Aborted -- no attempts were run

This session recorded zero attempts. It is kept only as the evidence for the
calibration-id trap, and **must not be pooled or scored with anything.**

`run_eval_gated.sh` defaulted to `ROBOT_ID=robotfuel_soarm101_follower_r2`,
which is how the evaluation Mac registers the follower. This machine registers
the same physical arm as `follower_r2`. An unregistered id does not fail
cleanly: lerobot falls through to an interactive recalibration prompt, reads
EOF because stdin is the operator gate, and returns 1. The session then burns
one attempt per placement while the operator moves the box for a policy that
never ran.

Two placements were lost that way before it was stopped. `conditions.jsonl`
holds the session header and no attempt rows, so nothing was scored.

The real block is `evalsession_20260921_011739`.

`run_eval_gated.sh` now checks the id before the first placement and names the
ids the machine actually has.
