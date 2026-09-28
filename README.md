# RobotFuel research

Open records from RobotFuel's experiments on getting real-world experience into
robot policies — the models, the datasets, the raw evaluation logs, and the
scripts that recompute every published number from them.

Each study lives in its own folder and is self-contained: a README stating what
was tested and what came back, the per-attempt records, and a verifier that
exits non-zero if any quoted rate stops reproducing.

## Studies

| Study | Question | Answer |
|---|---|---|
| [`handheld-demonstrations/`](handheld-demonstrations/) | Can handheld GoPro demonstrations replace robot teleoperation for training a manipulation policy? | Yes, at matched count. 16 handheld demos recovered ~9/10 of what a second teleop session bought — 65% against 70%, from a 17% baseline. |

## Models and datasets

Trained checkpoints and datasets are on HuggingFace under
[`robotfuel`](https://huggingface.co/robotfuel), linked from each study.

## How to read these

Three conventions apply across every study here.

**Rates come with their sample size.** An n=12 rate and an n=100 rate are not
the same evidence, and small samples are reported as small rather than rounded
into confidence.

**Skipped attempts leave the denominator.** An attempt aborted for lighting, a
rig fault, or an interruption never put the policy in front of the task, so it
is recorded as skipped rather than failed. Counting those as failures would
silently deflate every rate.

**Claims are checked against the record, not asserted.** Each study ships a
verifier:

```bash
cd handheld-demonstrations && python3 verify_results.py
```

## What is not here

The collection and retargeting pipeline. These repositories hold its outputs
and the evidence for what those outputs are worth.

## License

Apache-2.0.
