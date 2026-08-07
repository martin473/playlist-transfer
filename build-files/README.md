# Pi Playlist Bridge sequential dispatch package v4.2 — implementation freeze

This is the final pre-implementation planning package. It preserves the v4.1 sequence and changes only four implementation blockers.

## Contents

- **Sequential dispatches:** 597
- **Source micro-steps:** 758
- **Dependency waves:** 241
- **Source plan:** 2.6

## V4.2 corrections

1. `TransferRequest` has seven exact Python field names: `source_url`, `source_profile`, `spotify_profile`, `destination_name`, `mode`, `match_policy`, and `public`.
2. TypeScript tool input types and TypeBox schema steps agree on auth `action`, transfer `visibility`, and defaultable mode/policy/visibility fields.
3. Review repositories include source-track lookup; manual review derives and stores corrections by `source_fingerprint`.
4. Jobs list/show and review list/apply construct production repositories through `bootstrap.py`.

## Implementation freeze

Do not revise the complete plan or regenerate the package unless a running implementation dispatch encounters a concrete contradiction, missing dependency, or impossible acceptance check. Attach a small amendment to that blocked dispatch instead. Do not reopen planning for naming preferences, theoretical adapters, optional hardening, unobserved concurrency scenarios, or broader test completeness.

## Start execution

Execute `steps/` in the exact order in `manifests/execution-order.json`, beginning with dispatch `0001`. Runtime PASS is earned only when the controller reaches and successfully executes a dispatch.

The first product-level acceptance target remains the narrow vertical slice: authenticate both providers, read one YouTube playlist, match a small set, create one private Spotify playlist, add tracks, read it back, report failures, and invoke the same operation through Pi.

## Validate this package

```bash
python3 tools/validate_dispatch_package.py .
```
