---
name: ia-updater
description: Used when a new version of Lightspeed Core (LCORE) and/or Offline Knowledge Portal (OKP) is available and needs to be pulled into the RHDH Operator, Helm chart, and RHDH Local repositories.
---

# Instructions

## Prerequisites

When using this skill it is important to have the locations of the RHDH Operator, Helm chart, and Local repositories. For local use-cases, if the local clone paths are not provided during skill invocation, then request them from the human before proceeding. In remote execution use-cases, the repositories may be present in the environment already, or the Github references will be provided to you. In the event you have a Github reference, you must proceed with the checkout locally to make changes.

For both use cases, local and remote, you should be provided the image tags (versions) that you are updating to, as well as the RHDH release you are targeting. If that is unclear or not provided, request the information from the human in the local case, and do not proceed during the remote case.

It is important to **not** make assumptions and possibly be incorrect during this prerequisite process.

## Guidance

- There was a shift in architecture between RHDH release 1.10 and the following releases (2.1 and onwards), it is important you follow the instructions for the appropriate release when using this skill. OKP does not exist for RHDH 1.10.
- In RHDH 1.10 we call our product 'Lightspeed', in all other releases it is 'Intelligent Assistant'.
- Make surgical edits. Do not make changes unrelated to the image tag update, you are not attempting to maintain the codebase.
- If unsure about something, do not guess. Request help from the user locally, or stop your run remotely.

## General Steps

These steps can be applied to all 3 repositories (Operator, Helm, Local), with repository specific steps outlined in the following sections.

1. Checkout the appropriate repository clone
2. Ensure clone is on the latest commit from the upstream release branch
   1. Release branches follow the `release-X.Y` structure. E.g. RHDH 1.10 is `release-1.10`
3. Create new branch based on the appropriate upstream release branch
   1. Branch naming structure: `chore/ia-images-lcore-x.y.z-okp-x.y.z-123`
   2. E.g `chore/ia-images-lcore-0.7.1-okp-1.3.0-12345`
   3. **Note:** If the update is only LCORE, or only OKP, you can drop the unused name
      1. E.g `chore/ia-images-lcore-0.7.1` when no OKP updates
4. Follow the repository speicifc instructions below
5. After the changes are completed, make a commit
   1. Only LCORE: `chore: update lcore image from x.x.x to x.x.y`
   2. Only OKP: `chore: update okp image from x.x.x-123 to x.x.x-124`
      1. Could also be `x.x.x-123 to x.x.y-123`
6. Push the new branch and open a pull request against the upstream
7. Provide the pull request links

### Operator Steps

There are plenty of generated files in this repository that will contain the image tag(s) we are trying to update. There are automations in place to update those locations. The change you have to make differs depending on the RHDH release. For RHDH 1.10, there is only LCORE, no OKP, and it is located at `config/profile/rhdh/default-config/flavours/lightspeed/deployment.yaml`. For all releases other than RHDH 1.10, LCORE is located at `config/profile/rhdh/default-config/flavours/intelligent-assistant/deployment.yaml` and OKP is located at `config/profile/rhdh/plugin-deps/okp.yaml`. OKP has 2 references for both Kubernetes and OpenShift, update both.

After the changes are made, run the following to generate the remaining references:
```
make bundle build-installer
```

### Helm chart Steps

For RHDH 1.10 the chart is `charts/backstage` with `charts/backstage/values.yaml` being where the LCORE image is updated. `charts/backstage/Chart.yaml` requires a version bump after we update the image tag. This version update should be by a single z-stream vaue. E.g. `1.1.1` becomes `1.1.2`.

For all other releases the chart is `charts/rhdh` with `charts/rhdh/values.yaml` being where the LCORE and OKP image references are to be updated. Similar to RHDH 1.10, the chart itself needs a version update after these changes, located at `charts/rhdh/Chart.yaml`.

For all releases the precommit must be run to ensure all generation is completed after changes are made.

### Local Steps

For RHDH 1.10, only the root `compose.yaml` needs to be updated with the new LCORE image.

For all other RHDH releases, you update the root `compose.yaml` for the LCORE image and `intelligent-assistant/compose-with-okp.yaml` for OKP.
