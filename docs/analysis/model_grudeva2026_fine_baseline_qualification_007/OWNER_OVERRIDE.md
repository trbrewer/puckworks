# 007 owner execution override

This continues MODEL-GRUDEVA2026-FINE-BASELINE-QUALIFICATION-007 in draft PR #329.
It is the same scientific task. G1 / NO_GOVERNING_PHYSICS_CHANGE; execution-policy
and accounting changes are G0. PHYSICAL_VALIDATION=NOT_ESTABLISHED.

The owner explicitly superseded the original execution allocations, quotas,
no-retry restrictions and closed-campaign restrictions after the original
incomplete result. The operative authorization is:

> Remove the task-imposed 300-second pilot timeout and other per-run wall-clock
> deadlines; 4,800-second aggregate execution budget; six-full/three-short
> invocation quotas; fixed 32 GiB application-imposed memory ceiling.
>
> Do not replace these with another arbitrary timeout or attempt budget.
> Elapsed time alone is not grounds to terminate a calculation.
>
> Remove these restrictions from BOTH controller and worker enforcement,
> including timers, subprocess timeouts and admission/accounting checks.
> Update execution-policy bindings explicitly; do not bypass scientific
> source or evidence-integrity checks.
>
> The original pilot was terminated without a complete result. Restart it
> under this authorization, let it finish, and then complete the existing
> control, repeat and four refinement runs.
>
> Reuse the verified 006 baseline and passing readout evidence. Do not
> repeat completed work unnecessarily.
>
> Keep the scientific configurations, equations, solver, observer,
> tolerances, comparison support and acceptance criteria unchanged.
>
> Use an execution arrangement supported by the environment that allows
> long-running work to survive ordinary command/session timeouts. Do not
> launch duplicate processes when reconnecting. Do not claim execution
> has started or completed without verifying it.
>
> Respect actual operating-system and hosting limits. Monitor memory,
> disk space and process activity, with progress logging that does not
> alter the scientific calculation.
>
> Do not terminate solely because output is quiet or runtime exceeds an
> estimate. Investigate suspected stalls before declaring them.
>
> Stop for owner cancellation, actual execution failure, a genuine
> scientific stop condition, or an evidenced machine-safety problem.
> Do not purchase compute, change system-wide limits or affect unrelated
> work without authorization.
>
> Operational retries are authorized where needed, with their causes
> recorded. Do not rerun or tune scientific failures until they pass.
>
> Keep the original timeout, results and accounting unchanged as history.
> Record this override and subsequent attempts separately within the same
> PR. Do not create a new research task merely to obtain more runtime.
>
> Finish the declared qualification and report its actual result,
> including any genuine failures. Keep physical validation unestablished
> unless separately demonstrated.
>
> Keep the PR unmerged and auto-merge disabled.
>
> Proceed without another request for runtime authorization.

The original PLAN, CONTRACT, RESULTS, ACCOUNTING, pre-execution review, numerical
outputs and ledger remain historical and byte-identical. Their resource-policy
paragraphs describe the original attempt only. EXECUTION_POLICY_OVERRIDE.json
explicitly binds this authorization, the original PLAN, original closed evidence,
and the current orchestration sources. Production and all 001–006 scientific
implementations and evidence stay protected by the unchanged PLAN hashes.

The mathematical work remains exactly the declared pilot, control, repeat and
four refinements, with the same observer, masks and acceptance criteria. The
passing A readout is referenced in place. Complete source/configuration/Result,
persistence/replay, repeatability, 22 individual audits and all four refinement
comparisons remain mandatory. A scientific or integrity failure stops later rows
and is retained; an operational retry needs a recorded cause and cannot convert
such a scientific failure into retry authority.

The controller runs in a transient user systemd service with no application
runtime limit or memory assignment. It does not change system-wide limits.
The service survives ordinary tool/session command timeouts; restarting a tool
connection only reads status. One original-root lock and an inherited worker lock
prevent concurrent calculations. Boot ID and process start ticks prevent PID reuse
from being mistaken for a live process. Orphan protection terminates a worker if
its supervising controller actually dies; verified dead unresolved starts are
closed explicitly and charged conservatively through reconciliation.

Continuation attempts have separate immutable directories and unique ledger
identities. Metadata retains the same task and scientific row, with a distinct
execution ID and policy hash. Existing successful attempts are reused. Repeating
a completed solver or reduction with identical inputs is rejected. A reduction
may assemble a changed completed input set after an operational retry; it never
launches a solver. Original and continuation accounting are reported separately
and combined without deleting any attempt or imposing a new budget.

Progress sampling every 15 seconds reads OS CPU ticks, process state, resident and
virtual memory, host/ancestor-cgroup limits and usage, memory pressure and disk
space. Sampling adds no diagnostic callbacks to production. Elapsed time and
quiet output never trigger termination. A 1% host/hard-cgroup operating margin
and 1 GiB filesystem margin are machine safeguards, not worker memory ceilings.
A low-margin live sample is logged; sustained low headroom plus increasing worker
resident use or decreasing disk space is required for an automatic safety stop.
Conservative archive estimates inform pre-start disk checks, never elapsed-time
or output-size termination. The actual OS limits are retained and recorded.

Final reduction, source proof, results and handoff use separate CONTINUATION
artifacts. Original 005/006 dispositions and the original 007 timeout remain
unchanged. Issue #67 stays open; EWP and its dependency lock stay unchanged.
