## Context

The live dashboards live in the Grafana add-on's database and are edited there, through the UI or the `grafana-home` MCP server. Two records of them existed: hand-synced copies here, and ha-config's nightly export of all of them.

## Decisions

- **One record, the automatic one.** ha-config's export covers every dashboard, keeps history, and needs no step after an edit. A hand-kept copy can only lag behind it.
- **No importable example either.** Keeping `heatpump-dashboard.json` as an example for other add-on users was considered and declined: it would still need re-exporting to stay useful, and the live dashboard is now house-specific (Swedish titles, panels for this house's meters).
- **Not Grafana provisioning.** Loading dashboards from files would make a repo the source, but provisioned dashboards cannot be saved from the UI or the API, which is how they are edited.

## Risks / Trade-offs

- Someone installing the add-on gets no ready-made dashboard. Accepted; the HA package's entity names are documented in the repo.
