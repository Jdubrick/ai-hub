---
name: Lightspeed Core Version Bump
description: This skill is used when a new version of Lightspeed Core (LCORE) needs to be pulled into the RHDH Operator, Helm chart, and RHDH Local. The version number has a source of truth at github.com/redhat-ai-dev/lightspeed-configs/images.yaml for the appropriate release branch. The RHDH Operator and Helm chart have unique steps that must be completed when updating the image tag. RHDH Local has a more straightforward update cycle, but makes logical sense to be included in this skill.
---

# Instructions

## Prerequisites

When using this skill, make sure to ask the user to provide the paths to their local clones of the RHDH Operator, Helm chart, and Local repositories. Do **not** assume where they are and possibly be incorrect.

Additionally, make sure to gather the appropriate release version from the user.

## Steps

These steps can be applied to all 3 locations (Operator, Helm, local), with repository specific steps outlined in future sections.

1. Checkout the appropriate local repository clone.
2. Fetch from the upstream (request from user if necessary). 
3. Create new branch that is based off of the upstream release branch.
4. Follow the repository specific instructions below.
5. After changes are completed, make a commit such as:
`chore: update lcore image from x.x.x to x.x.y` 
6. Push the changes to the users remote repository (NOT THE UPSTREAM) so the user can review and open the pull request themselves.

### Operator Steps

There are plenty of generated files in this repository that will contain the image tag we are trying to update. There are automations in place to update those locations. We only need to make the update to the default-config for Lightspeed in the deployment for the profile.

After making that change we need to run:
```make bundle build-installer` to generate/update the remaining references automatically.

### Helm chart Steps

We need to update 2 values here, then run the precommit to ensure the remaining references are updated. We need to update the image tag in the `values.yaml` file, and then update the Chart version in `Chart.yaml` by a patch release. I.e. `1.1.1` Chart version bumps to `1.1.2`.


### Local steps

Local is the simplest update. You only need to update the image tag in the `compose.yaml` file.

## Guidance

- Make surgical edits. Do not make changes unrelated to the image tag bump, you are not attempting to maintain the codebase.
- If unsure about something, request input from the user.