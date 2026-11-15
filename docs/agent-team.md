# Agent Team

The project is built and operated by a small team of agents with a human owner who sets priorities, reviews PRs, and approves production deploys.

## Roles

### Spec agent
- **Responsibility:** turns `product-spec.md` into GitHub issues, each with acceptance criteria.
- **Inputs:** the spec, feedback from the human owner.
- **Outputs:** labeled issues (`spec`, `ready`), updates to the spec when scope changes.
- **Must not:** write application code.

### Builder agent
- **Responsibility:** implements one `ready` issue at a time.
- **Inputs:** an issue, `AGENTS.md`, `openapi.yaml`.
- **Outputs:** a branch named `issue-<n>-<slug>` and a PR that references the issue and meets its acceptance criteria.
- **Must not:** merge its own PR, change acceptance criteria, or touch deploy configuration without an issue for it.

### Test agent
- **Responsibility:** writes and maintains unit and integration tests derived from each issue's acceptance criteria.
- **Inputs:** an issue and the builder's PR.
- **Outputs:** tests in the same PR or a follow-up PR, plus a comment on the issue stating which criteria are covered.
- **Must not:** weaken or delete a failing test to make CI pass.

### Responder agent (on-call)
- **Responsibility:** wakes on the user-impact alert (failed or slow result submissions) and works the incident.
- **Inputs:** the alert payload, logs from Loki, traces from Tempo, metrics from Prometheus, recent deploys.
- **Outputs:** an incident issue with findings, then either a fix PR or a rollback proposal, plus a note on the alert's resolution.
- **Must not:** deploy to production without human approval, or read secrets and personal data.

### Human owner
- **Responsibility:** sets priorities, reviews and merges PRs, approves production deploys, and makes the final call in an incident.

## Handoffs

1. Human owner changes the spec.
2. Spec agent opens or updates issues.
3. Builder agent takes an issue and opens a PR.
4. Test agent adds tests for the acceptance criteria.
5. CI runs; the human owner reviews and merges.
6. CD deploys to dev automatically; the human owner approves the production deploy.
7. If the alert fires, the responder agent takes over (see [observability.md](observability.md)).

## Coordination

The GitHub issue is the single source of truth. Agents communicate through issue comments, PR descriptions, and labels, not through private state. Status labels: `spec`, `ready`, `in-progress`, `in-review`, `incident`.
