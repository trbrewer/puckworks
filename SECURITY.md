# Security & responsible disclosure

## Reporting a vulnerability

Please do **not** open a public issue for a security problem. Report privately via GitHub's
**Security → Report a vulnerability** (private advisory) on this repository, or by direct
message to the maintainer (@trbrewer). Include a description, reproduction steps, and impact.
We aim to acknowledge within a few days.

## Scope of particular concern

- **Privacy of harvested data.** The Visualizer corpus is PII-stripped on ingest (salted
  one-way user hash; free-text dropped). Report any path that could re-identify users, leak
  raw payloads (including in logs or CI artifacts), or place private/non-redistributable shot
  data into a repo or release artifact.
- **Secrets.** Report any committed token/secret, or a workflow that could expose one. The
  live canary is variable-gated and retains nothing.
- **Supply chain.** Report dependency or build-artifact tampering concerns.

## Handling

Confirmed issues are fixed on a private branch, released, and disclosed after users can update.
Data-exposure incidents also trigger the retention/deletion review in the data-use policy.
