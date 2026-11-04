"""Smoke tests: call tool functions directly with known inputs."""
import server


def main():
    est = server.estimate_capacity(1000, 5)
    assert est["projections_gb"]["12 months"] == 1795.86, est
    assert est["recommended_capacity_gb_12m"] == 2155.03, est

    mig = server.plan_ring_migration("SPO->Gen8", 125, 90)
    assert mig["rings_per_week_needed"] == 9.72, mig
    assert len(mig["phases"]) == 5

    dec = server.decommission_tracker(125, 90, 25)
    assert dec["pct_complete"] == 20.0, dec
    assert dec["rings_remaining"] == 100, dec

    zon = server.zonal_readiness_check("Business Critical", 80.0)
    assert zon["gap_pct_points"] == 11.8, zon

    rcs = server.rcs_automation_playbook("validation")
    assert len(rcs["pattern"]) == 5

    summary = server.capacity_summary(1000, 5, "Regional->MAZ", 125, 90, "Premium", 80.0)
    assert "assumptions" in summary and "capacity_projection" in summary

    print("ALL SMOKE TESTS PASSED")


if __name__ == "__main__":
    main()
