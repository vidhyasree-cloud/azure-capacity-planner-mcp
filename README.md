# Azure Capacity Planner MCP Server

Personal portfolio project, independent of any employer.

A Python + FastMCP server that turns Azure SQL DB capacity work into
usable planning tools for Claude Desktop (stdio transport).

## Tools

| Tool | What it does |
| --- | --- |
| `estimate_capacity` | Projects size at 3/6/12 months from current size + monthly growth, with headroom |
| `plan_ring_migration` | Phased migration checklist (SPO→Gen8, QCS, Regional→MAZ, RDFE→PaaSv2) with zero-downtime guardrails |
| `decommission_tracker` | Weekly pace needed to decommission N rings in a window, with behind-pace warning |
| `zonal_readiness_check` | Gap to the 91.8% zonal benchmark for Business Critical / Premium |
| `rcs_automation_playbook` | Validate → dynamic retry with backoff → log every attempt |
| `capacity_summary` | All of the above in one brief, with assumptions listed |

## Honest limits

- No live Azure API calls, no subscription data, no internal company data.
- All outputs are calculations from user-supplied inputs plus labelled
  worked examples from the author's confirmed capacity work.
- This is a planning aid. It does not read, resize, provision, migrate,
  or decommission any live Azure resource.

## Worked examples (labelled as examples, not live data)

- PaaSv2 adoption to 100% ahead of schedule, incl. RDFE→PaaSv2
- SPO→Gen8, QCS, and Regional→MAZ migrations, zero customer downtime
- Gen3/Gen4 fully decommissioned, 98.28% Gen7 return rate
- 125 rings to decommission in a 90-day window
- Zonal onboarding to 91.8% for Business Critical and Premium databases
- Capacity workflows across all Azure regions worldwide

## Run

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python server.py
```

A stdio MCP server prints nothing and waits for a client — that is normal.
Connect it in Claude Desktop via `mcpServers` in `claude_desktop_config.json`.
