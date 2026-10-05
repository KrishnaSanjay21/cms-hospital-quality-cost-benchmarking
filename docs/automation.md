# Refresh automation

The pipeline is designed for a monthly scheduled refresh because the upstream CMS products do
not all update on the same cadence. `orchestration/github-actions/refresh.yml.example` is a
reviewable GitHub Actions template that runs linting and tests before the live refresh and keeps
reporting marts as short-lived artifacts.

It is intentionally stored as an example rather than under `.github/workflows/` because the
repository publication credential used for this portfolio build did not have GitHub workflow
scope. To activate it, copy it to `.github/workflows/refresh.yml` using a credential permitted to
manage workflows, review the schedule, and run it manually once.

For local containers:

```powershell
docker compose run --rm cms-hospital-refresh refresh
```

The mounted `data/` and `warehouse/` directories retain manifests and reporting outputs outside
the container. Production scheduling should also archive raw checksums and alert on failed
critical data-quality checks.

