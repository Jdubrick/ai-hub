---
name: configs-updater
description: Used when a new version of Lightspeed Core (LCORE) and/or Offline Knowledge Portal (OKP) is available and needs to be pulled into the `lightspeed-configs` or `rhdh-intelligent-assistant-configs` repositories. 
---

# Instructions

## Prerequisites

When using this skill it is important to have the locations of the repository. For local use-cases, if the local clone path is not provided during skill invocation, then request it from the human before proceeding. In remote execution use-cases, the repository may be present in the environment already, or the Github reference will be provided to you. In the event you have a Github reference, you must proceed with the checkout locally to make changes.

For both use cases, local and remote, you should be provided the image tags (versions) that you are updating to, as well as the RHDH release you are targeting. If that is unclear or not provided, request the information from the human in the local case, and do not proceed during the remote case.

It is important to **not** make assumptions and possibly be incorrect during this prerequisite process.

## Guidance

- There was a shift in architecture between RHDH release 1.10 and the following releases (2.1 and onwards), it is important you follow the instructions for the appropriate release when using this skill. OKP does not exist for RHDH 1.10.
- In RHDH 1.10 we call our product 'Lightspeed', in all other releases it is 'Intelligent Assistant'.
- Make surgical edits. Do not make changes unrelated to the image tag update, you are not attempting to maintain the codebase.
- If unsure about something, do not guess. Request help from the user locally, or stop your run remotely.

## Steps

These steps can be applied whether targeting `lightspeed-configs` or `rhdh-intelligent-assistant-configs`. The only difference is `rhdh-intelligent-assistant-configs` will contain the OKP image.

1. Checkout the appropriate repository clone
2. Ensure clone is on the latest commit from the upstream release branch
   1. Release branches follow the `release-X.Y` format. E.g. RHDH 1.10 is `release-1.10`
3. Create new branch based on the appropriate upstream release branch
   1. E.g. `upstream/release-1.10`
   2. Branch naming structure: `chore/ia-images-lcore-x.y.z-okp-x.y.z-123`
   3. E.g `chore/ia-images-lcore-0.7.1-okp-1.3.0-12345`
   4. **Note:** If the update is only LCORE, or only OKP, you can drop the unused name
      1. E.g `chore/ia-images-lcore-0.7.1` when no OKP updates
4. The changes are to be made in the `images.yaml` file
   1. `lightspeed-core.image` and where applicable, `okp.image`.
      1. For all releases except `1.10`, also update `lightspeed-core.latest_release` to the same tag as `lightspeed-core.image` if the `lightspeed-core.image` was changed
   2. **Note:** Only update the provided components
5. After the changes are completed, make a commit
   1. Only LCORE: `chore: update lcore image from x.x.x to x.x.y`
   2. Only OKP: `chore: update okp image from x.x.x-123 to x.x.x-124`
      1. Could also be `x.x.x-123 to x.x.y-123`
6. Push the new branch and open a pull request against the upstream
7. Provide the pull request link 