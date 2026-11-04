"""Azure Capacity Planner MCP server.

Personal portfolio project, independent of any employer.
Input-driven planning tools based on Azure SQL DB capacity work.
No live Azure API calls, no subscription data, no internal data.
All outputs are calculations from user-supplied inputs plus labelled
worked examples from the author's confirmed capacity work.
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("azure-capacity-planner")

# Worked examples are labelled as examples, never presented as live data.
WORKED_EXAMPLES = {
    "paasv2_adoption": "100% ahead of schedule, incl. RDFE->PaaSv2 conversion",
    "ring_migrations": "SPO->Gen8, QCS, and Regional->MAZ, zero customer downtime",
    "decommission": "Gen3/Gen4 fully decommissioned, 98.28% Gen7 return rate",
    "decommission_window": "125 rings to decommission in a 90-day window",
    "zonal_onboarding": "91.8% for Business Critical and Premium databases",
    "scope": "capacity workflows across all Azure regions worldwide",
}


def _compound(size, pct, months):
    return size * ((1 + pct / 100.0) ** months)


@mcp.tool()
def estimate_capacity(current_size_gb: float, monthly_growth_pct: float,
                      target_headroom_pct: float = 20.0) -> dict:
    """Project database size and headroom from user-supplied inputs.

    Returns projected size at 3/6/12 months and the size including
    target headroom. Math is shown in the assumptions, not hidden.
    """
    if current_size_gb <= 0:
        return {"error": "current_size_gb must be > 0"}
    projections = {f"{m} months": round(_compound(current_size_gb, monthly_growth_pct, m), 2)
                   for m in (3, 6, 12)}
    return {
        "current_size_gb": current_size_gb,
        "monthly_growth_pct": monthly_growth_pct,
        "target_headroom_pct": target_headroom_pct,
        "projections_gb": projections,
        "recommended_capacity_gb_12m": round(projections["12 months"] * (1 + target_headroom_pct / 100.0), 2),
        "assumptions": "Compound monthly growth applied to current size; headroom applied to the 12-month projection only.",
        "note": "Planning aid only. It does not read, resize, or provision any live Azure resource.",
    }


@mcp.tool()
def plan_ring_migration(ring_type: str, ring_count: int, window_days: int) -> dict:
    """Return a phased ring-migration checklist for a named migration type.

    ring_type examples: SPO->Gen8, QCS, Regional->MAZ, RDFE->PaaSv2.
    """
    if ring_count <= 0 or window_days <= 0:
        return {"error": "ring_count and window_days must be > 0"}
    per_week = round(ring_count / max(window_days / 7.0, 1), 2)
    return {
        "ring_type": ring_type,
        "ring_count": ring_count,
        "window_days": window_days,
        "rings_per_week_needed": per_week,
        "phases": [
            "1. Baseline: capture current utilisation, errors, and customer impact per ring.",
            "2. Pilot: migrate one ring, validate, and hold for a full monitoring window.",
            "3. Rollout: migrate in batches at the pace above, with a pause gate between batches.",
            "4. Validation: confirm utilisation, latency, and error rates match baseline before closing a batch.",
            "5. Rollback trigger: stop and roll back a batch on sustained error/latency regression, do not push through.",
        ],
        "zero_downtime_guardrails": [
            "Migrate, validate, then decommission — never decommission first.",
            "Keep the previous ring available until the new ring passes validation.",
            "Freeze other changes during a migration batch.",
        ],
        "worked_example": WORKED_EXAMPLES["ring_migrations"],
        "note": "Checklist only. It does not migrate any live ring.",
    }


@mcp.tool()
def decommission_tracker(total_rings: int, window_days: int, rings_done: int = 0) -> dict:
    """Track decommission pace against a window, with a behind-pace warning."""
    if total_rings <= 0 or window_days <= 0 or rings_done < 0:
        return {"error": "total_rings and window_days must be > 0; rings_done must be >= 0"}
    remaining = max(total_rings - rings_done, 0)
    weeks = window_days / 7.0
    pace_needed = round(remaining / weeks, 2) if weeks else remaining
    pct_done = round(rings_done / total_rings * 100, 2)
    return {
        "total_rings": total_rings,
        "rings_done": rings_done,
        "rings_remaining": remaining,
        "pct_complete": pct_done,
        "rings_per_week_needed_from_here": pace_needed,
        "status": "On pace if you can sustain this weekly rate" if remaining else "Complete",
        "warning": ("Behind pace: weekly rate needed is rising as the window shrinks. "
                    "Re-plan the window or add parallel batches; do not compress validation.")
        if pct_done < 50 and weeks < 4 else None,
        "worked_example": WORKED_EXAMPLES["decommission_window"] + "; " + WORKED_EXAMPLES["decommission"],
        "note": "Tracker only. It does not decommission any hardware.",
    }


@mcp.tool()
def zonal_readiness_check(tier: str, current_zonal_pct: float) -> dict:
    """Check the gap to the 91.8% zonal benchmark for Business Critical/Premium."""
    benchmark = 91.8
    if not (0 <= current_zonal_pct <= 100):
        return {"error": "current_zonal_pct must be between 0 and 100"}
    gap = round(benchmark - current_zonal_pct, 2)
    return {
        "tier": tier,
        "current_zonal_pct": current_zonal_pct,
        "benchmark_pct": benchmark,
        "gap_pct_points": gap,
        "status": "At or above benchmark" if gap <= 0 else f"{gap} points below benchmark",
        "remediation_checklist": [
            "Confirm the region and tier actually support zonal deployment.",
            "List databases blocked by legacy hardware or region constraints.",
            "Migrate unblocked databases first; track blockers separately, do not average them away.",
            "Re-measure after each batch; report Business Critical and Premium separately.",
        ],
        "worked_example": WORKED_EXAMPLES["zonal_onboarding"],
        "note": "Benchmark is the author's confirmed worked example, not a live Azure measurement.",
    }


@mcp.tool()
def rcs_automation_playbook(workflow_type: str) -> dict:
    """Return the RCS automation pattern: validate, retry with backoff, log."""
    return {
        "workflow_type": workflow_type,
        "pattern": [
            "1. Validate inputs before any action (ring, region, target state).",
            "2. Execute one step; on failure, retry with dynamic backoff, not a fixed loop.",
            "3. Log every attempt with outcome, so a retry is auditable, not invisible.",
            "4. Stop after a defined retry budget and surface the failure for triage.",
            "5. Never retry a destructive step (decommission, delete) without re-validation.",
        ],
        "triage_inputs": ["KQL telemetry", "SQL utilisation data", "IcM incident records"],
        "note": "Playbook only. It runs no live automation and touches no production system.",
    }


@mcp.tool()
def capacity_summary(current_size_gb: float, monthly_growth_pct: float,
                     ring_type: str, total_rings: int, window_days: int,
                     tier: str, current_zonal_pct: float) -> dict:
    """Combine the other planners into one brief, with assumptions listed."""
    est = estimate_capacity(current_size_gb, monthly_growth_pct)
    mig = plan_ring_migration(ring_type, total_rings, window_days)
    dec = decommission_tracker(total_rings, window_days)
    zon = zonal_readiness_check(tier, current_zonal_pct)
    return {
        "assumptions": "All figures are calculated from the inputs you supplied in this call. No live Azure data was read.",
        "capacity_projection": est,
        "ring_migration": mig,
        "decommission": dec,
        "zonal_readiness": zon,
        "worked_examples": WORKED_EXAMPLES,
        "next_step": "Re-run with updated inputs after each batch; do not treat one summary as a final plan.",
    }


if __name__ == "__main__":
    mcp.run()
