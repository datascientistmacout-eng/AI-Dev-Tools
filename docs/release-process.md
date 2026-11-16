# Release process

## Normal release

1. Open a pull request from a branch named after the issue (`issue-<n>-<slug>`).
2. CI must pass (`backend-tests`, `frontend-build`, `docker-build`). Branch protection blocks the merge otherwise.
3. Merge to `main`. The Deploy workflow's `deploy-dev` job runs automatically after CI succeeds and updates the dev service.
4. Check the dev URL.
5. To release to production, run the Deploy workflow manually (Actions, Deploy, Run workflow). The `deploy-production` job waits for approval from a required reviewer, then calls the production deploy hook.

## Rollback

1. Revert the faulty merge with a pull request (GitHub: open the merged PR and click Revert).
2. Merge the revert after CI passes; dev updates automatically.
3. Run the production Deploy workflow again and approve it.

The Render dashboard also lists earlier deploys per service, which can be used for an emergency redeploy where the plan allows it.