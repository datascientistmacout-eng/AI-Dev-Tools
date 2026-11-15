# Development Process

## Lifecycle of a change

1. **Specify.** The spec agent writes an issue with a problem statement and acceptance criteria, then labels it `ready`.
2. **Build.** The builder agent creates a branch `issue-<n>-<slug>`, implements the issue, and opens a PR that says "Closes #<n>".
3. **Test.** The test agent covers each acceptance criterion with unit tests and, where the criterion crosses components, integration tests.
4. **Verify.** CI runs the full test suite on every PR. A PR cannot merge while CI is red.
5. **Review.** The human owner reviews the diff against the acceptance criteria and merges.
6. **Deploy to dev.** Merging to `main` triggers CD to the dev environment automatically.
7. **Promote to production.** The human owner triggers the manual production deploy after checking dev.
8. **Observe.** The submit-result journey is monitored. If the user-impact alert fires, the responder agent starts the incident flow.

## Definition of done

- All acceptance criteria on the issue are met.
- Unit and integration tests exist and pass with one command.
- `openapi.yaml` and docs are updated if behavior changed.
- No secrets or personal data in code, logs, or telemetry.
- The PR references the issue and CI is green.

## Incident flow

1. Alert fires on failed or slow result submissions.
2. The responder agent opens an `incident` issue and gathers logs, traces, and metrics for the affected window using the trace ID.
3. It identifies the cause and opens either a fix PR or a rollback proposal.
4. The human owner approves. Production changes always need human approval.
5. The incident issue records the cause, the fix, and what to prevent next time.

## Branching and commits

- `main` is protected; changes arrive by PR only.
- Commit messages reference the issue number, for example `Add standings tiebreakers (#3)`.
