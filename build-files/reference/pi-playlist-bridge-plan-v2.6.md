# Pi Playlist Bridge — Mini-LLM Atomic Build Plan

**Plan version:** 2.6 — implementation freeze

## Goal

Build the same local YouTube-to-Spotify playlist bridge described by the source plan, expressed as dependency-audited micro-steps suitable for a mini-sized coding agent. The product architecture and security boundaries remain unchanged; this edition additionally freezes public contracts, numeric defaults, migration behavior, concurrency rules, reproducible dependency installation, benchmark gates, and milestone checks.

**Conformance note:** This document is the intended version-one implementation specification. It does not prove that any existing repository conforms; conformance requires running the plan validator, automated suites, milestone gates, and final acceptance against the actual implementation.

## Version 2.6 implementation-freeze corrections

This final planning patch makes only four implementation-blocking corrections: exact `TransferRequest` fields, TypeScript/TypeBox input alignment, fingerprint-safe review access to source tracks, and composition-root wiring for jobs/review commands.

### Implementation freeze

After this version, do not revise the complete plan or regenerate the package unless an implementation dispatch encounters a concrete contradiction, missing dependency, or impossible acceptance check. Record any such issue as a small amendment attached to the blocked dispatch. Naming preferences, theoretical adapters, additional abstractions, unobserved concurrency cases, and optional hardening do not reopen planning.

This section is authoritative and is reflected directly in the groups, step headings, embedded registry, and external registry below.

- `ports.py` owns credential, profile, repository, clock, report-path, runner, review, and matcher dependency contracts.
- Concrete keyring and SQLAlchemy adapters implement those ports without exposing backends or sessions to orchestration and CLI code.
- `bootstrap.py` is the sole production composition root for directories, migrations, repositories, credentials, provider clients/adapters, matching configuration, and `RuntimeDependencies`.
- User-facing CLI commands call the composition-root builders; they do not accept unexplained dependency objects.
- `extension/types.ts` owns all TypeScript input, result, event, invocation, and process-boundary types.
- Step 159.07 and Step 160.06 are defined in their source groups and implement the public aggregators.
- The embedded registry below is byte-for-byte equivalent after YAML parsing to `reference/symbol-contracts.yaml`.
- The dispatch-package validator compares the exact source-plan step-heading set with the execution manifest; no hardcoded step count is authoritative.

## Version-one scope decisions

1. Version one accepts standard YouTube and YouTube Music playlist URLs through the official YouTube Data API. It does **not** support YouTube Music liked songs, library browsing, music-specific private-client operations, or other `ytmusicapi` capabilities. `ytmusicapi` is not a version-one runtime dependency.
2. Version one supports **YouTube-to-Spotify only**. Spotify source adapters, reverse transfer, bidirectional synchronization, and scheduled synchronization are deferred and are not implied by the name “playlist bridge.” User-facing documentation must call the initial product a YouTube-to-Spotify playlist bridge.
3. Version-one matching is implemented locally with RapidFuzz and deterministic project-owned normalization, query generation, scoring, and policy code. A bounded spotDL audit may identify compatible MIT-licensed behavior or tests, but spotDL is not a runtime dependency. Downloading, media extraction, FFmpeg integration, and spotDL execution are prohibited.
4. Browser interaction is used only for official Spotify and Google/YouTube OAuth authorization. Playlist reading, metadata retrieval, matching, creation, insertion, replacement, and verification use provider APIs and must not use browser automation.

## Deferred post-v1 adapters

Future work may add the following only through new plan versions and isolated provider contracts:

```text
Future source adapters
├── YouTube Music library/liked songs through an isolated ytmusicapi adapter
└── Spotify source adapter

Future destination adapters
├── Regular YouTube through the official YouTube Data API
└── YouTube Music through an isolated ytmusicapi adapter
```

These adapters are not version-one acceptance requirements and must not leak music-client, downloading, or browser-automation behavior into the current YouTube source or Spotify destination modules.

## How to execute this plan

1. Treat every `NNN.NN` identifier as a stable traceability ID, **not** as the execution order.
2. Execute groups and micro-steps from the dependency DAG. A step becomes ready only when every dependency named by that step has passed.
3. Before coding begins, the controller must parse every dependency, reject missing references, reject cycles, and produce a topological ready queue.
4. A dependency on **Group NNN** means every micro-step in that group must have passed. Micro-steps inside one group remain sequential unless a step explicitly states otherwise.
5. Give a mini coding agent one atomic dispatch bundle at a time. A bundle may contain one to three consecutive micro-steps from the same group only when they touch the same primary symbol or configuration artifact.
6. Prefer bundling an implementation step with its immediately following focused test step. Generic acceptance such as “imports or type-checks” is not sufficient by itself when a paired behavioral test exists.
7. Report every bundled micro-step separately using its original step ID and acceptance result.
8. Do not implement behavior from a step that is not in the current dispatch bundle.
9. Do not dispatch a coding step until the controller supplies the complete task envelope defined below.
10. Never use live provider accounts in unit, property, contract, migration, or concurrency tests.
11. Never store or print access tokens, refresh tokens, passwords, OAuth callback codes, or real client-secret contents.
12. Do not automate provider password entry. Browser interaction is limited to official OAuth authorization pages.
13. Machine-readable stdout must remain valid JSON or JSONL. Diagnostics belong on stderr or in report files.
14. The Pi extension must spawn an executable with an argument array and `shell: false`.
15. A failed acceptance check blocks all downstream dependents. Do not “work around” a failed prerequisite in a later step.
16. Changes to frozen contracts or numeric defaults require a new plan version and rerunning all affected downstream gates.

## Required task envelope for every coding-agent dispatch

The deterministic controller must add these fields when it hands a step or bundle to a coding agent:

- **Step IDs:** one to three consecutive IDs from one group.
- **Goal:** the exact behavior being added.
- **Target files:** exact paths; no repository-wide freedom.
- **Primary symbols:** exact class, function, constant, command, schema, or table names.
- **Signature contract:** parameter names and types, return type, typed errors, and allowed side effects.
- **Inputs and fixtures:** exact existing models, fixture paths, and fake interfaces to use.
- **Allowed edits:** target production file, paired test file, and explicitly named fixture/config files only.
- **Forbidden edits:** unrelated modules, public contracts, frozen defaults, lockfiles unless the task is a lockfile task, and generated credentials.
- **Acceptance:** the assertion already written in this plan.
- **Verification:** one exact command run from one exact working directory.
- **Completion report:** changed files, verification output, pass/fail result, and deferred work.

A step missing any field above is **not runnable**. Route it back to the specification/controller stage rather than allowing a mini model to invent repository structure or public APIs.

## Phase 0 — Contract and dependency freeze

Phase 0 is a controller preflight, not application code. Complete it before dispatching Group 001.

### Preflight P0.01: Validate dependency references

Parse every group-level and micro-step dependency. Reject unknown group IDs, unknown step IDs, malformed ranges, and self-dependencies.

**Acceptance:** Every dependency resolves to exactly one existing group or micro-step.

### Preflight P0.02: Validate the dependency DAG

Topologically sort the corrected group graph and the micro-step graph.

**Acceptance:** Both graphs are acyclic and produce at least one initial ready step.

### Preflight P0.03: Validate task envelopes

Confirm that every dispatchable step can be assigned an exact target file, primary symbol, signature, and verification command from this plan and the module ownership map.

**Acceptance:** No step is placed in the ready queue with an incomplete task envelope.

### Preflight P0.04: Freeze public contracts

Use the public signatures below. A coding agent may add private helpers but may not change these names, parameter meanings, return models, or error boundaries.

**Acceptance:** The contract set is copied into the controller context and hashed with the plan version.

### Preflight P0.05: Freeze numeric defaults

Use the v1 defaults below until the labeled benchmark gate is run. A failed benchmark stops the build; it does not authorize a mini agent to tune values ad hoc.

**Acceptance:** One canonical configuration fixture contains every default exactly once.

### Preflight P0.06: Freeze persistence policy

Use the migration, transaction, datetime, and job-lease rules below.

**Acceptance:** Persistence-related task envelopes cite the same policy version.

### Preflight P0.07: Freeze dependency resolution

Python development and CI use `uv.lock` in frozen mode. Node development and CI use `package-lock.json` with `npm ci`. Generated lockfiles change only in explicit dependency-update steps.

**Acceptance:** Install and verification tasks name frozen-install commands.

### Preflight P0.08: Register milestone gates

The controller records each gate below and refuses to open the next release stage until the current gate passes.

**Acceptance:** Every gate has explicit prerequisite groups and one deterministic verification result.

### Preflight P0.09: Generate the initial ready queue

Resolve group prerequisites to their terminal micro-step IDs and emit the initial set of runnable micro-steps with complete task envelopes.

**Acceptance:** Every emitted step has zero unsatisfied dependencies and no blocked step is emitted.

### Preflight P0.10: Lock plan provenance

Record the plan version, dependency-graph hash, public-contract hash, frozen-defaults hash, and lockfile policy in the controller run manifest.

**Acceptance:** A changed plan, contract, or frozen default invalidates the prior ready queue and requires preflight to run again.

### Preflight P0.11: Audit reusable spotDL matcher behavior

Review a pinned spotDL release or commit before dispatching matching Groups 070–115. Record the exact upstream revision, files, functions, tests, normalization rules, query strategies, license notices, and attribution obligations examined in `docs/research/spotdl-matcher-audit.md`. Select only small compatible MIT-licensed routines or tests whose behavior fits the frozen local contracts. Do not add spotDL, downloading, media extraction, or FFmpeg as dependencies. The audit may conclude that no code should be ported.

**Acceptance:** The audit record names the pinned upstream revision, records adopt/reproduce/reject decisions for each reviewed behavior, includes required attribution for anything ported, and confirms that runtime dependencies contain no spotDL, downloader, or FFmpeg package.

### Preflight P0.12: Freeze controller artifact paths

Use these exact checked-in controller artifacts before coding begins:

- Plan: `docs/build/pi-playlist-bridge-plan.md`
- Machine-readable contract registry: `docs/build/symbol-contracts.yaml`
- DAG validator: `scripts/validate-build-plan.py`
- Validator contract test: `runtime/tests/contract/test_build_plan.py`

The canonical validation command is run from the repository root:

```bash
python3 scripts/validate-build-plan.py docs/build/pi-playlist-bridge-plan.md docs/build/symbol-contracts.yaml
```

**Acceptance:** The four paths are recorded in the controller manifest, the command exits zero, and moving, renaming, or omitting either input causes deterministic failure.

## Corrected group topological order

The controller may choose any currently ready group, but this validated ordering proves the graph is executable:

```text
001 008 002 003 004 005 006 156 013 093 066 007 015 014 019 017
056 009 016 018 157 189 190 039 020 101 010 158 040 021 022 057
041 011 042 047 023 116 012 058 043 048 025 026 049 028 027 031
032 044 050 045 051 029 030 059 033 060 046 118 024 119 037 035
036 034 061 052 083 062 063 053 126 123 064 065 054 084 067 055
117 124 068 038 120 069 085 086 089 090 096 087 092 094 095 097
070 071 072 091 125 073 074 075 076 077 127 078 128 132 079 129
080 081 099 100 102 103 104 130 082 105 088 133 098 131 106 107
110 182 108 137 113 109 111 112 114 115 121 122 134 135 153 136
161 146 154 149 151 152 141 142 143 144 145 164 150 138 166 147
139 148 140 159 155 160 183 185 184 167 162 163 165 168 170 169
186 177 171 172 175 173 174 176 181 178 179 180 187 188
```

## Repository module ownership map

Use this map to construct exact target-file fields in task envelopes. Do not create competing modules for the same responsibility.

```text
runtime/
  pyproject.toml
  uv.lock
  src/playlist_bridge/
    __init__.py
    cli.py
    paths.py
    settings.py
    ports.py
    bootstrap.py
    domain/
      enums.py
      models.py
      events.py
    persistence/
      engine.py
      base.py
      models.py
      repositories.py
      migrations.py
    credentials/
      store.py
    auth/
      spotify.py
      youtube.py
      status.py
    providers/
      errors.py
      youtube.py
      spotify.py
    matching/
      normalize.py
      scoring.py
      matcher.py
    jobs/
      cancellation.py
      runner.py
      reports.py
  tests/
    unit/
    property/
    contract/
    integration/
    migration/
    fixtures/
extension/
  package.json
  package-lock.json
  index.ts
  process.ts
  schemas.ts
  jsonl.ts
  render.ts
  types.ts
scripts/
  validate-build-plan.py
  verify-runtime.sh
  verify-all.sh
  install.sh
  uninstall.sh
fixtures/
docs/
  build/
    pi-playlist-bridge-plan.md
    symbol-contracts.yaml
  research/
    spotdl-matcher-audit.md
```

Production code for a responsibility must remain in its owned module. Tests may import public symbols but must not duplicate production algorithms.

## Group target-file registry

This registry resolves the production and verification ownership needed by the task envelope. For a row covering multiple files, a dispatch may edit only the file owning the current symbol plus its named paired test/fixture. Any additional file must appear explicitly in **Allowed edits**.

| Groups | Owned production/configuration targets | Paired verification targets |
|---|---|---|
| 001 | repository directories only | filesystem checks |
| 002–004 | `runtime/pyproject.toml`, `runtime/uv.lock` | clean/frozen environment checks |
| 005 | `runtime/src/playlist_bridge/__init__.py` | `runtime/tests/unit/test_package.py` |
| 006 | `runtime/src/playlist_bridge/cli.py` | `runtime/tests/unit/test_cli_version.py` |
| 007 | no production file | `runtime/tests/unit/test_cli_version.py` |
| 008 | `.gitignore` | deterministic `git check-ignore` checks |
| 009 | `runtime/pyproject.toml` | deliberate lint/type/test probes |
| 010 | `scripts/verify-runtime.sh` | shell syntax and fail-fast probes |
| 011–012 | `runtime/src/playlist_bridge/paths.py` | `runtime/tests/unit/test_paths.py` |
| 013–015 | `runtime/src/playlist_bridge/domain/enums.py` | `runtime/tests/unit/test_enums.py` |
| 016–022 | `runtime/src/playlist_bridge/domain/models.py` | `runtime/tests/unit/test_domain_models.py` |
| 023 | `runtime/src/playlist_bridge/domain/events.py` | `runtime/tests/unit/test_events.py` |
| 024 | no production file | `runtime/tests/fixtures/domain/`, `runtime/tests/unit/test_domain_fixtures.py` |
| 025 | `runtime/src/playlist_bridge/persistence/engine.py` | `runtime/tests/unit/persistence/test_engine.py` |
| 026 | `runtime/src/playlist_bridge/persistence/base.py` | `runtime/tests/unit/persistence/test_base.py` |
| 027–032 | `runtime/src/playlist_bridge/persistence/models.py` | `runtime/tests/unit/persistence/test_models.py` |
| 033 | `runtime/src/playlist_bridge/persistence/migrations.py`, `runtime/alembic.ini`, `runtime/migrations/` | `runtime/tests/migration/test_migrations.py` |
| 034–037 | `runtime/src/playlist_bridge/persistence/repositories.py` | `runtime/tests/unit/persistence/test_repositories.py` |
| 038 | no new production algorithm | `runtime/tests/integration/test_transactions_and_leases.py` |
| 039–042 | `runtime/src/playlist_bridge/credentials/store.py` | `runtime/tests/unit/credentials/test_store.py` |
| 043–046 | `runtime/src/playlist_bridge/settings.py`, `runtime/src/playlist_bridge/auth/spotify.py` | `runtime/tests/unit/auth/test_spotify_auth.py` |
| 047–051 | `runtime/src/playlist_bridge/settings.py`, `runtime/src/playlist_bridge/auth/youtube.py` | `runtime/tests/unit/auth/test_youtube_auth.py` |
| 052 | provider auth modules plus `persistence/repositories.py` | `runtime/tests/unit/auth/test_status_logout.py` |
| 053 | `runtime/src/playlist_bridge/auth/status.py` | `runtime/tests/unit/auth/test_status_logout.py` |
| 054 | provider auth modules plus `persistence/repositories.py` | `runtime/tests/unit/auth/test_status_logout.py` |
| 055 | no production file | `runtime/tests/contract/test_auth_commands.py` |
| 056 | `runtime/src/playlist_bridge/providers/errors.py` | `runtime/tests/unit/providers/test_errors.py` |
| 057–068 | `runtime/src/playlist_bridge/providers/youtube.py` | `runtime/tests/unit/providers/test_youtube.py` |
| 069 | no production file | `runtime/tests/fixtures/youtube/`, `runtime/tests/contract/test_youtube_adapter.py` |
| 070–082 | `runtime/src/playlist_bridge/matching/normalize.py` | `runtime/tests/unit/matching/test_normalize.py`, `runtime/tests/property/test_normalize_properties.py` |
| 083–097 | `runtime/src/playlist_bridge/providers/spotify.py` | `runtime/tests/unit/providers/test_spotify.py` |
| 098 | no production file | `runtime/tests/contract/test_spotify_adapter.py` |
| 099–110 | `runtime/src/playlist_bridge/matching/scoring.py` | `runtime/tests/unit/matching/test_scoring.py` |
| 111–113 | `runtime/src/playlist_bridge/matching/matcher.py` | `runtime/tests/unit/matching/test_matcher.py` |
| 114 | no production file | `runtime/tests/property/test_matching_properties.py` |
| 115 | no production file | `runtime/tests/fixtures/matching/`, `runtime/tests/contract/test_matching_benchmark.py` |
| 116–117 | `runtime/src/playlist_bridge/jobs/runner.py`, `persistence/repositories.py` | `runtime/tests/unit/jobs/test_job_creation.py` |
| 118 | `runtime/src/playlist_bridge/jobs/cancellation.py`, `domain/events.py` | `runtime/tests/unit/jobs/test_interfaces.py` |
| 119 | `runtime/src/playlist_bridge/jobs/runner.py` | `runtime/tests/unit/jobs/test_jsonl_emitter.py` |
| 120–135 | `runtime/src/playlist_bridge/jobs/runner.py`, `jobs/cancellation.py` | `runtime/tests/unit/jobs/test_stages.py`, `runtime/tests/integration/test_resume_reconciliation.py` |
| 136–137 | `runtime/src/playlist_bridge/jobs/reports.py` | `runtime/tests/unit/jobs/test_reports.py` |
| 138–140 | `runtime/src/playlist_bridge/jobs/runner.py` | `runtime/tests/integration/test_runner.py` |
| 141–154 | `runtime/src/playlist_bridge/cli.py` | `runtime/tests/unit/test_cli_commands.py` |
| 155 | no production file | `runtime/tests/integration/test_cli.py` |
| 156 | `extension/package.json`, `extension/package-lock.json` | `npm ci` and package-script checks |
| 157 | `extension/index.ts` | extension loading probe |
| 158–160 | `extension/process.ts` | `extension/test/process.test.ts` |
| 161 | `extension/jsonl.ts` | `extension/test/jsonl.test.ts` |
| 162–163 | `extension/process.ts` | `extension/test/process-control.test.ts` |
| 164, 166 | `extension/schemas.ts` | `extension/test/schemas.test.ts` |
| 165, 167–171 | `extension/index.ts` | `extension/test/tools.test.ts` |
| 172 | `extension/render.ts` | `extension/test/render.test.ts` |
| 173 | no production file | `extension/test/` |
| 174 | `scripts/verify-pi-extension.sh` | local Pi load smoke run |
| 175–178 | `SKILL.md`, `README.md`, `docs/`, and example configuration files | documentation, scope, attribution, and configuration checks |
| 179 | `scripts/install.sh` | clean and repeated install checks |
| 180 | `scripts/uninstall.sh` | preserve/purge matrix checks |
| 181 | `scripts/verify-all.sh`, `scripts/validate-build-plan.py`, `docs/build/pi-playlist-bridge-plan.md`, `docs/build/symbol-contracts.yaml` | `runtime/tests/contract/test_build_plan.py` and deliberate fail-fast probes |
| 182 | `fixtures/providers/` | consumed-field contract tests |
| 183–186 | `docs/acceptance/` | recorded manual/live acceptance evidence |
| 187 | build/package configuration and release scripts | clean release installation |
| 188 | no new production behavior | final acceptance record and reports |
| 189 | `runtime/src/playlist_bridge/ports.py`, `runtime/src/playlist_bridge/credentials/store.py`, `runtime/src/playlist_bridge/persistence/repositories.py`, `runtime/src/playlist_bridge/bootstrap.py` | `runtime/tests/unit/test_ports.py`, repository/bootstrap tests, composition integration test |
| 190 | `extension/types.ts` | `extension/test/types.test.ts` |

## Symbol registry for previously unnamed production behavior

Backticked names inside a micro-step remain authoritative. For production behavior that previously had only a prose title, use these exact names; do not create aliases or competing public functions.

| Group | Exact primary symbol(s) |
|---:|---|
| 039 | `credential_key_name` |
| 041 | `CredentialCorruptionError` |
| 042 | `KeyringCacheHandler` |
| 043 | `SpotifyOAuthSettings` |
| 044 | `create_spotify_pkce_manager` |
| 045 | `authenticate_spotify_profile` |
| 047 | `GoogleOAuthSettings`, `load_google_client_config` |
| 048 | `serialize_google_credentials`, `deserialize_google_credentials` |
| 049 | `authenticate_youtube_profile` |
| 050 | `refresh_google_credentials` |
| 053 | `get_auth_status` |
| 057 | `parse_youtube_playlist_id` |
| 058 | `SourceAdapter` |
| 059 | `fetch_youtube_playlist_metadata` |
| 060 | `map_youtube_error` |
| 061 | `fetch_youtube_playlist_item_page` |
| 062 | `iter_youtube_playlist_items` |
| 064 | `unique_video_ids` |
| 065 | `fetch_youtube_video_metadata` |
| 068 | `YouTubeSourceAdapter.load_playlist` |
| 070 | `normalize_unicode_text` |
| 071 | `comparison_text` |
| 072 | `REMOVABLE_NOISE_PHRASES` |
| 073 | `remove_bracketed_noise` |
| 074 | `extract_version_tokens` |
| 075 | `detect_unwanted_version_flags` |
| 078 | `classify_source_item` |
| 079 | `normalize_source_track` |
| 080 | `source_fingerprint` |
| 081 | `build_spotify_queries` |
| 083 | `SpotifyAdapter` |
| 084 | `map_spotify_error` |
| 085 | `AuthenticatedSpotifyAdapter` |
| 086 | `search_spotify_query` |
| 088 | `search_spotify_candidates` |
| 089 | `get_spotify_identity` |
| 090 | `list_owned_spotify_playlists` |
| 091 | `find_owned_playlist_by_name` |
| 092 | `create_spotify_playlist` |
| 093 | `chunk_uris` |
| 094 | `add_uri_batch` |
| 095 | `add_all_uri_batches` |
| 096 | `read_spotify_playlist_items` |
| 097 | `replace_playlist_items` |
| 099 | `title_similarity` |
| 100 | `artist_similarity` |
| 102 | `version_agreement_score` |
| 103 | `unwanted_version_penalty` |
| 104 | `explicit_state_score` |
| 105 | `matching_config_v1`, `score_candidate` |
| 106 | `MATCH_POLICY_THRESHOLDS` |
| 107 | `rank_candidates` |
| 108 | `decide_match` |
| 109 | `resolve_manual_correction` |
| 110 | `resolve_cached_match` |
| 111 | `match_source_track` |
| 112 | `cache_accepted_match` |
| 113 | `apply_manual_review` |
| 116 | `new_job_id` |
| 117 | `create_transfer_job` |
| 119 | `JsonlEventEmitter` |
| 120 | `load_source_stage` |
| 121 | `match_one_stage` |
| 122 | `run_match_loop` |
| 123 | `calculate_transfer_counts` |
| 124 | `complete_dry_run` |
| 125 | `resolve_destination` |
| 126 | `accepted_uris_in_source_order` |
| 127 | `DestinationWritePlan` |
| 128 | `write_batch_key` |
| 129 | `save_write_checkpoint` |
| 130 | `reconcile_pending_batch` |
| 131 | `execute_write_plan` |
| 132 | `compare_destination_items` |
| 133 | `verify_destination` |
| 134 | `CancellationController`, `install_signal_handlers` |
| 135 | `handle_job_failure` |
| 136 | `write_json_report` |
| 137 | `write_review_csv` |
| 138 | `RuntimeDependencies`, `run_transfer` |
| 139 | `resume_transfer` |
| 140 | `rerun_unresolved_reviews` |
| 153 | `ExitCode` |
| 154 | `configure_output_streams` |
| 158 | `locatePlaylistBridgeExecutable` |
| 161 | `JsonlEventParser` |
| 163 | `BoundedProcessOutput` |
| 167 | `confirmDestructiveTransfer` |
| 172 | `renderToolCall`, `renderToolResult` |

## Frozen v1 defaults

These values are explicit product-design decisions for this plan, not claims about permanent provider limits. Provider adapters must additionally enforce any stricter limit returned by or documented for the provider.

### Matching and search

- Score range: `0.0` through `100.0`.
- Positive weights: title `40`, artist `30`, duration `15`, version agreement `10`, explicit-state agreement `5`.
- Penalties: unwanted version `30`, direct version contradiction `20`, explicit mismatch `3`.
- Duration full-credit band: `delta <= max(2500 ms, source_duration * 0.02)`.
- Duration zero-credit band: `delta >= max(15000 ms, source_duration * 0.10)`.
- Duration score declines linearly between the two bands.
- Spotify search queries per track: at most `4`.
- Spotify results requested per query: `10`.
- Unique candidates retained per track: at most `25`.
- Cached automatic match freshness: `30 days`.
- Manual corrections do not expire automatically.

### Match policies

| Policy | Auto-accept score | Minimum runner-up gap | Review floor |
|---|---:|---:|---:|
| strict | 93 | 12 | 75 |
| balanced | 86 | 8 | 65 |
| loose | 80 | 5 | 55 |

Decision rule:

1. Auto-match only when `top_score >= auto_accept_score` and `top_score - second_score >= minimum_gap`.
2. Otherwise mark ambiguous when `top_score >= review_floor`.
3. Otherwise mark unmatched.

### Provider, retry, and batching behavior

- YouTube video metadata lookup batch: at most `50` IDs.
- Spotify playlist write batch: at most `100` URIs and never above the adapter/provider limit.
- Temporary provider failures: at most `4` total attempts.
- Fallback retry delays: `1`, `2`, then `4` seconds, capped at `8` seconds.
- A provider `Retry-After` value takes precedence over fallback delay.
- Authentication, permission, not-found, malformed-response, and validation failures are never retried automatically.

### Persistence and runtime

- All persisted timestamps are timezone-aware UTC and serialize as ISO 8601 with `Z`.
- SQLite busy timeout: `5000 ms`.
- Job lease duration: `90 seconds`.
- Job lease heartbeat interval: `30 seconds`.
- A checkpoint write must verify the active lease token in the same transaction.
- JSONL event schema version: `1`.
- JSON report schema version: `1`.
- Extension in-memory child-output cap: `65536 bytes`; complete diagnostics go to a report file.
- Coverage gate: branch measurement enabled and total coverage at least `85%`.

## Frozen cross-boundary model contracts

The following field sets are public cross-step contracts. Pydantic configuration must reject unknown fields at these boundaries unless a later versioned schema explicitly allows them. Collections serialize in deterministic order.

```python
class TransferRequest(BaseModel):
    source_url: str
    source_profile: str
    spotify_profile: str
    destination_name: str
    mode: TransferMode = TransferMode.dry_run
    match_policy: MatchPolicy = MatchPolicy.balanced
    public: bool = False


class SourcePlaylistMetadata(BaseModel):
    reference: PlaylistReference
    description: str | None
    privacy_status: str | None
    owner_channel_id: str | None
    owner_channel_title: str | None
    item_count: int  # >= 0


class LoadedSourcePlaylist(BaseModel):
    metadata: SourcePlaylistMetadata
    tracks: list[SourceTrack]  # strictly ordered by SourceTrack.position


class NormalizedTrackHint(BaseModel):
    source_item_id: str
    normalized_title: str
    artist_hints: tuple[str, ...]
    version_tokens: tuple[str, ...]  # sorted, unique lowercase tokens
    unwanted_flags: tuple[str, ...]  # sorted, unique lowercase flags
    duration_ms: int | None
    classification: str
    explicit_evidence: bool | None


class PolicyThresholds(BaseModel):
    auto_accept_score: float
    minimum_runner_up_gap: float
    review_floor: float


class MatchingConfig(BaseModel):
    schema_version: Literal[1]
    title_weight: float
    artist_weight: float
    duration_weight: float
    version_weight: float
    explicit_weight: float
    unwanted_version_penalty: float
    version_contradiction_penalty: float
    explicit_mismatch_penalty: float
    duration_full_credit_floor_ms: int
    duration_full_credit_ratio: float
    duration_zero_credit_floor_ms: int
    duration_zero_credit_ratio: float
    max_queries_per_track: int
    results_per_query: int
    max_unique_candidates: int
    cache_freshness_days: int
    policy_thresholds: dict[MatchPolicy, PolicyThresholds]
```

`MatchingConfig` is constructed from the frozen v1 defaults exactly once by `matching_config_v1()`. Coding agents may not introduce duplicate literals for those values.

## Frozen public API contracts

The precise Pydantic field definitions are implemented by their model groups, but orchestration uses these signatures. `CancellationToken` is read-only to consumers; only signal/process adapters may request cancellation.

```python
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Protocol


def config_dir() -> Path: ...
def data_dir() -> Path: ...
def cache_dir() -> Path: ...
def jobs_dir() -> Path: ...
def reports_dir() -> Path: ...
def database_path() -> Path: ...
def ensure_app_directories() -> None: ...


def create_engine_for_path(path: Path): ...
def initialize_schema(engine) -> None: ...
def upgrade_schema(engine, database_file: Path) -> None: ...


class CancellationToken(Protocol):
    def is_cancelled(self) -> bool: ...
    def raise_if_cancelled(self) -> None: ...


EventEmitter = Callable[["JobEvent"], None]


class SourceAdapter(Protocol):
    def load_playlist(
        self,
        reference: "PlaylistReference",
        *,
        cancel: CancellationToken,
    ) -> "LoadedSourcePlaylist": ...


class SpotifyAdapter(Protocol):
    def search_tracks(
        self,
        queries: Sequence[str],
        *,
        market: str | None,
        cancel: CancellationToken,
    ) -> list["SpotifyCandidate"]: ...

    def create_playlist(
        self,
        name: str,
        description: str,
        public: bool,
    ) -> "DestinationPlaylist": ...

    def add_items(self, playlist_id: str, uris: Sequence[str]) -> str: ...
    def replace_items(self, playlist_id: str, uris: Sequence[str]) -> str: ...
    def read_items(self, playlist_id: str) -> list[str | None]: ...


def matching_config_v1() -> "MatchingConfig": ...
def normalize_source_track(track: "SourceTrack") -> "NormalizedTrackHint": ...
def source_fingerprint(hint: "NormalizedTrackHint") -> str: ...
def build_spotify_queries(hint: "NormalizedTrackHint") -> list[str]: ...
def score_candidate(
    hint: "NormalizedTrackHint",
    candidate: "SpotifyCandidate",
    config: "MatchingConfig",
) -> "MatchScore": ...
def decide_match(
    source_item_id: str,
    ranked: Sequence[tuple["SpotifyCandidate", "MatchScore"]],
    policy: "MatchPolicy",
    config: "MatchingConfig",
) -> "MatchDecision": ...


def run_transfer(
    request: "TransferRequest",
    *,
    dependencies: "RuntimeDependencies",
    emit: EventEmitter,
    cancel: CancellationToken,
) -> "TransferResult": ...

def resume_transfer(
    job_id: str,
    *,
    allow_failed: bool,
    allow_cancelled: bool,
    dependencies: "RuntimeDependencies",
    emit: EventEmitter,
    cancel: CancellationToken,
) -> "TransferResult": ...
```

TypeScript process boundaries:

```ts
export type ProcessResult = {
  exitCode: number;
  events: PlaylistBridgeEvent[];
  stderrReportPath?: string;
};

export function buildCliInvocation(input: TypedToolInput): CliInvocation;

export function runCliProcess(
  invocation: CliInvocation,
  signal: AbortSignal,
  onEvent: (event: PlaylistBridgeEvent) => void,
): Promise<ProcessResult>;
```

## Complete cross-step signature registry

Phase P0.04 copies the following registry verbatim into `docs/build/symbol-contracts.yaml`. These signatures are authoritative for every symbol consumed by a later group. The controller rejects a dispatch when its symbol is absent or when its task envelope differs from this registry.

```yaml
registry_version: 6
rules:
  unknown_fields: reject
  datetimes: timezone-aware UTC
  provider_payloads_cross_boundary: false
  raw_credentials_in_arguments: false
  pure_symbols_have_no_io: true
  dispatch_contracts_must_equal_registry: true
  every_registry_symbol_has_owning_dispatch: true
  repeated_symbols_have_one_owner: true
  signature_changes_require_supersedes: true
  source_plan_step_set_equals_manifest: true
  embedded_registry_equals_external_registry: true
  test_only_dispatches_target_no_production_files: true
  composition_root_builders_required_by_cli: true
symbols:
  credential_key_name:
    file: runtime/src/playlist_bridge/credentials/store.py
    signature: '(service: SourceService | DestinationService, profile_name: str) -> str'
    errors:
    - ValueError
    side_effects: []
  CredentialCorruptionError:
    file: runtime/src/playlist_bridge/credentials/store.py
    signature: 'CredentialCorruptionError(service: str, profile_name: str, safe_message: str)'
    errors: []
    side_effects: []
  KeyringCacheHandler:
    file: runtime/src/playlist_bridge/credentials/store.py
    signature: 'KeyringCacheHandler(service: str, profile_name: str, store: CredentialStore)'
    errors:
    - CredentialCorruptionError
    side_effects:
    - os_keychain_read
    - os_keychain_write
    - os_keychain_delete
  create_spotify_pkce_manager:
    file: runtime/src/playlist_bridge/auth/spotify.py
    signature: '(settings: SpotifyOAuthSettings, cache_handler: KeyringCacheHandler, open_browser: bool = True) -> SpotifyOAuth'
    errors:
    - ValueError
    side_effects: []
  authenticate_spotify_profile:
    file: runtime/src/playlist_bridge/auth/spotify.py
    signature: '(profile_name: str, settings: SpotifyOAuthSettings, profiles: AccountProfileRepository, credentials: CredentialStore, open_browser: bool = True) -> AccountProfile'
    errors:
    - AuthenticationRequired
    - PermissionDenied
    - InvalidProviderResponse
    side_effects:
    - official_oauth_browser
    - os_keychain_write
    - sqlite_profile_write
  load_google_client_config:
    file: runtime/src/playlist_bridge/auth/youtube.py
    signature: '(client_secret_path: Path) -> GoogleOAuthSettings'
    errors:
    - ValueError
    - FileNotFoundError
    side_effects:
    - filesystem_read
  serialize_google_credentials:
    file: runtime/src/playlist_bridge/auth/youtube.py
    signature: '(credentials: Credentials) -> str'
    errors:
    - CredentialCorruptionError
    side_effects: []
  deserialize_google_credentials:
    file: runtime/src/playlist_bridge/auth/youtube.py
    signature: '(serialized: str, scopes: Sequence[str]) -> Credentials'
    errors:
    - CredentialCorruptionError
    side_effects: []
  authenticate_youtube_profile:
    file: runtime/src/playlist_bridge/auth/youtube.py
    signature: '(profile_name: str, settings: GoogleOAuthSettings, profiles: AccountProfileRepository, credentials: CredentialStore, open_browser: bool = True) -> AccountProfile'
    errors:
    - AuthenticationRequired
    - PermissionDenied
    - InvalidProviderResponse
    side_effects:
    - official_oauth_browser
    - os_keychain_write
    - sqlite_profile_write
  refresh_google_credentials:
    file: runtime/src/playlist_bridge/auth/youtube.py
    signature: '(profile_name: str, credentials: CredentialStore, request: Request) -> Credentials'
    errors:
    - AuthenticationRequired
    - TemporaryProviderFailure
    - CredentialCorruptionError
    side_effects:
    - provider_network
    - os_keychain_write
  get_auth_status:
    file: runtime/src/playlist_bridge/auth/status.py
    signature: '(service: SourceService | DestinationService, profile_name: str, profiles: AccountProfileRepository, credentials: CredentialStore) -> AuthStatus'
    errors:
    - CredentialCorruptionError
    side_effects:
    - os_keychain_read
    - sqlite_read
  parse_youtube_playlist_id:
    file: runtime/src/playlist_bridge/providers/youtube.py
    signature: '(url: str) -> str'
    errors:
    - ValueError
    side_effects: []
  fetch_youtube_playlist_metadata:
    file: runtime/src/playlist_bridge/providers/youtube.py
    signature: '(client: YouTubeResource, playlist_id: str) -> SourcePlaylistMetadata'
    errors:
    - AuthenticationRequired
    - PermissionDenied
    - ProviderNotFound
    - RateLimited
    - InvalidProviderResponse
    - TemporaryProviderFailure
    side_effects:
    - provider_network
  fetch_youtube_playlist_item_page:
    file: runtime/src/playlist_bridge/providers/youtube.py
    signature: '(client: YouTubeResource, playlist_id: str, page_token: str | None) -> YouTubePlaylistItemPage'
    errors:
    - AuthenticationRequired
    - PermissionDenied
    - ProviderNotFound
    - RateLimited
    - InvalidProviderResponse
    - TemporaryProviderFailure
    side_effects:
    - provider_network
  iter_youtube_playlist_items:
    file: runtime/src/playlist_bridge/providers/youtube.py
    signature: '(client: YouTubeResource, playlist_id: str, cancel: CancellationToken) -> Iterator[YouTubePlaylistItem]'
    errors:
    - AuthenticationRequired
    - PermissionDenied
    - ProviderNotFound
    - RateLimited
    - InvalidProviderResponse
    - TemporaryProviderFailure
    - CancellationRequested
    side_effects:
    - provider_network
  unique_video_ids:
    file: runtime/src/playlist_bridge/providers/youtube.py
    signature: '(items: Sequence[YouTubePlaylistItem]) -> list[str]'
    errors: []
    side_effects: []
  fetch_youtube_video_metadata:
    file: runtime/src/playlist_bridge/providers/youtube.py
    signature: '(client: YouTubeResource, video_ids: Sequence[str], cancel: CancellationToken) -> dict[str, YouTubeVideoMetadata]'
    errors:
    - AuthenticationRequired
    - PermissionDenied
    - RateLimited
    - InvalidProviderResponse
    - TemporaryProviderFailure
    - CancellationRequested
    side_effects:
    - provider_network
  YouTubeSourceAdapter.load_playlist:
    file: runtime/src/playlist_bridge/providers/youtube.py
    signature: '(self, reference: PlaylistReference, *, cancel: CancellationToken) -> LoadedSourcePlaylist'
    errors:
    - AuthenticationRequired
    - PermissionDenied
    - ProviderNotFound
    - RateLimited
    - InvalidProviderResponse
    - TemporaryProviderFailure
    - CancellationRequested
    side_effects:
    - provider_network
  normalize_unicode_text:
    file: runtime/src/playlist_bridge/matching/normalize.py
    signature: '(value: str) -> str'
    errors: []
    side_effects: []
  comparison_text:
    file: runtime/src/playlist_bridge/matching/normalize.py
    signature: '(value: str) -> str'
    errors: []
    side_effects: []
  remove_bracketed_noise:
    file: runtime/src/playlist_bridge/matching/normalize.py
    signature: '(value: str, removable_phrases: Collection[str] = REMOVABLE_NOISE_PHRASES) -> str'
    errors: []
    side_effects: []
  extract_version_tokens:
    file: runtime/src/playlist_bridge/matching/normalize.py
    signature: '(value: str) -> tuple[str, ...]'
    errors: []
    side_effects: []
  detect_unwanted_version_flags:
    file: runtime/src/playlist_bridge/matching/normalize.py
    signature: '(title: str, artist_hints: Sequence[str]) -> tuple[str, ...]'
    errors: []
    side_effects: []
  classify_source_item:
    file: runtime/src/playlist_bridge/matching/normalize.py
    signature: '(track: SourceTrack) -> str'
    errors: []
    side_effects: []
  SpotifyOAuthSettings:
    file: runtime/src/playlist_bridge/settings.py
    signature: 'SpotifyOAuthSettings(client_id: str, redirect_uri: str, scopes: tuple[str, ...])'
    errors:
    - ValueError
    side_effects: []
  GoogleOAuthSettings:
    file: runtime/src/playlist_bridge/settings.py
    signature: 'GoogleOAuthSettings(client_secret_path: Path, scopes: tuple[str, ...], redirect_host: str, redirect_port: int)'
    errors:
    - ValueError
    side_effects: []
  SourceAdapter:
    file: runtime/src/playlist_bridge/providers/youtube.py
    signature: 'Protocol.load_playlist(reference: PlaylistReference, *, cancel: CancellationToken) -> LoadedSourcePlaylist'
    errors:
    - AuthenticationRequired
    - PermissionDenied
    - ProviderNotFound
    - RateLimited
    - InvalidProviderResponse
    - TemporaryProviderFailure
    - CancellationRequested
    side_effects:
    - provider_network
  map_youtube_error:
    file: runtime/src/playlist_bridge/providers/youtube.py
    signature: '(error: HttpError, operation: str) -> ProviderError'
    errors: []
    side_effects: []
  REMOVABLE_NOISE_PHRASES:
    file: runtime/src/playlist_bridge/matching/normalize.py
    signature: Final[frozenset[str]]
    errors: []
    side_effects: []
  SpotifyAdapter:
    file: runtime/src/playlist_bridge/providers/spotify.py
    signature: Protocol.search_tracks(...); create_playlist(...); add_items(...); replace_items(...); read_items(...)
    errors:
    - AuthenticationRequired
    - PermissionDenied
    - ProviderNotFound
    - RateLimited
    - InvalidProviderResponse
    - TemporaryProviderFailure
    - CancellationRequested
    side_effects:
    - provider_network
    - destination_write
  map_spotify_error:
    file: runtime/src/playlist_bridge/providers/spotify.py
    signature: '(error: SpotifyException, operation: str) -> ProviderError'
    errors: []
    side_effects: []
  AuthenticatedSpotifyAdapter:
    file: runtime/src/playlist_bridge/providers/spotify.py
    signature: 'AuthenticatedSpotifyAdapter(client: Spotify)'
    errors: []
    side_effects: []
  MATCH_POLICY_THRESHOLDS:
    file: runtime/src/playlist_bridge/matching/scoring.py
    signature: Final[Mapping[MatchPolicy, PolicyThresholds]]
    errors: []
    side_effects: []
  JsonlEventEmitter:
    file: runtime/src/playlist_bridge/jobs/runner.py
    signature: 'JsonlEventEmitter(stream: TextIO)'
    errors:
    - OSError
    side_effects:
    - stream_write
    - stream_flush
  load_source_stage:
    file: runtime/src/playlist_bridge/jobs/runner.py
    signature: '(job_id: str, request: TransferRequest, dependencies: RuntimeDependencies, emit: EventEmitter, cancel: CancellationToken, lease_token: str) -> LoadedSourcePlaylist'
    errors:
    - JobNotFoundError
    - LeaseLostError
    - AuthenticationRequired
    - PermissionDenied
    - ProviderNotFound
    - RateLimited
    - InvalidProviderResponse
    - TemporaryProviderFailure
    - CancellationRequested
    side_effects:
    - sqlite_read
    - sqlite_write
    - provider_network
  match_one_stage:
    file: runtime/src/playlist_bridge/jobs/runner.py
    signature: '(job_id: str, dependencies: RuntimeDependencies, emit: EventEmitter, cancel: CancellationToken, lease_token: str) -> MatchDecision | None'
    errors:
    - JobNotFoundError
    - LeaseLostError
    - AuthenticationRequired
    - PermissionDenied
    - RateLimited
    - InvalidProviderResponse
    - TemporaryProviderFailure
    - CancellationRequested
    side_effects:
    - sqlite_read
    - sqlite_write
    - provider_network
  run_match_loop:
    file: runtime/src/playlist_bridge/jobs/runner.py
    signature: '(job_id: str, dependencies: RuntimeDependencies, emit: EventEmitter, cancel: CancellationToken, lease_token: str) -> list[MatchDecision]'
    errors:
    - JobNotFoundError
    - LeaseLostError
    - AuthenticationRequired
    - PermissionDenied
    - RateLimited
    - InvalidProviderResponse
    - TemporaryProviderFailure
    - CancellationRequested
    side_effects:
    - sqlite_read
    - sqlite_write
    - provider_network
  complete_dry_run:
    file: runtime/src/playlist_bridge/jobs/runner.py
    signature: '(job_id: str, request: TransferRequest, dependencies: RuntimeDependencies, emit: EventEmitter, lease_token: str) -> TransferResult'
    errors:
    - JobNotFoundError
    - LeaseLostError
    - OSError
    side_effects:
    - sqlite_read
    - sqlite_write
    - filesystem_write
  resolve_destination:
    file: runtime/src/playlist_bridge/jobs/runner.py
    signature: '(request: TransferRequest, adapter: SpotifyAdapter, cancel: CancellationToken) -> DestinationPlaylist'
    errors:
    - ValueError
    - AuthenticationRequired
    - PermissionDenied
    - ProviderNotFound
    - RateLimited
    - InvalidProviderResponse
    - TemporaryProviderFailure
    - CancellationRequested
    side_effects:
    - provider_network
    - destination_create
  DestinationWritePlan:
    file: runtime/src/playlist_bridge/jobs/runner.py
    signature: 'DestinationWritePlan(playlist_id: str, mode: TransferMode, ordered_uris: tuple[str, ...], batches: tuple[WriteBatch, ...])'
    errors:
    - ValueError
    side_effects: []
  reconcile_pending_batch:
    file: runtime/src/playlist_bridge/jobs/runner.py
    signature: '(plan: DestinationWritePlan, batch_index: int, adapter: SpotifyAdapter, cancel: CancellationToken) -> ReconciliationResult'
    errors:
    - AuthenticationRequired
    - PermissionDenied
    - ProviderNotFound
    - RateLimited
    - InvalidProviderResponse
    - TemporaryProviderFailure
    - CancellationRequested
    side_effects:
    - provider_network
  execute_write_plan:
    file: runtime/src/playlist_bridge/jobs/runner.py
    signature: '(job_id: str, plan: DestinationWritePlan, dependencies: RuntimeDependencies, emit: EventEmitter, cancel: CancellationToken, lease_token: str) -> DestinationPlaylist'
    errors:
    - LeaseLostError
    - AuthenticationRequired
    - PermissionDenied
    - ProviderNotFound
    - RateLimited
    - InvalidProviderResponse
    - TemporaryProviderFailure
    - CancellationRequested
    side_effects:
    - sqlite_read
    - sqlite_write
    - provider_network
    - destination_write
  CancellationController:
    file: runtime/src/playlist_bridge/jobs/cancellation.py
    signature: CancellationController()
    errors:
    - CancellationRequested
    side_effects:
    - in_memory_state
  install_signal_handlers:
    file: runtime/src/playlist_bridge/jobs/cancellation.py
    signature: '(controller: CancellationController) -> Callable[[], None]'
    errors: []
    side_effects:
    - process_signal_handler_install
  handle_job_failure:
    file: runtime/src/playlist_bridge/jobs/runner.py
    signature: '(job_id: str, error: Exception, dependencies: RuntimeDependencies, emit: EventEmitter, lease_token: str | None) -> TransferResult'
    errors:
    - LeaseLostError
    - OSError
    side_effects:
    - sqlite_write
    - filesystem_write
    - stream_write
  ExitCode:
    file: runtime/src/playlist_bridge/cli.py
    signature: IntEnum(success=0, validation=2, auth=3, provider=4, review_required=5, busy=6, cancelled=130, internal=70)
    errors: []
    side_effects: []
  configure_output_streams:
    file: runtime/src/playlist_bridge/cli.py
    signature: '(machine_readable: bool) -> OutputStreams'
    errors: []
    side_effects:
    - process_stream_configuration
  normalize_source_track:
    file: runtime/src/playlist_bridge/matching/normalize.py
    signature: '(track: SourceTrack) -> NormalizedTrackHint'
    errors:
    - ValueError
    side_effects: []
  source_fingerprint:
    file: runtime/src/playlist_bridge/matching/normalize.py
    signature: '(hint: NormalizedTrackHint) -> str'
    errors: []
    side_effects: []
  build_spotify_queries:
    file: runtime/src/playlist_bridge/matching/normalize.py
    signature: '(hint: NormalizedTrackHint, config: MatchingConfig) -> list[str]'
    errors: []
    side_effects: []
  search_spotify_query:
    file: runtime/src/playlist_bridge/providers/spotify.py
    signature: '(client: Spotify, query: str, market: str | None, limit: int) -> list[SpotifyCandidate]'
    errors:
    - AuthenticationRequired
    - PermissionDenied
    - ProviderNotFound
    - RateLimited
    - InvalidProviderResponse
    - TemporaryProviderFailure
    side_effects:
    - provider_network
  search_spotify_candidates:
    file: runtime/src/playlist_bridge/providers/spotify.py
    signature: '(adapter: SpotifyAdapter, queries: Sequence[str], market: str | None, config: MatchingConfig, cancel: CancellationToken) -> list[SpotifyCandidate]'
    errors:
    - AuthenticationRequired
    - PermissionDenied
    - RateLimited
    - InvalidProviderResponse
    - TemporaryProviderFailure
    - CancellationRequested
    side_effects:
    - provider_network
  get_spotify_identity:
    file: runtime/src/playlist_bridge/providers/spotify.py
    signature: '(client: Spotify) -> ProviderIdentity'
    errors:
    - AuthenticationRequired
    - PermissionDenied
    - RateLimited
    - InvalidProviderResponse
    - TemporaryProviderFailure
    side_effects:
    - provider_network
  list_owned_spotify_playlists:
    file: runtime/src/playlist_bridge/providers/spotify.py
    signature: '(client: Spotify, owner_id: str, cancel: CancellationToken) -> list[DestinationPlaylist]'
    errors:
    - AuthenticationRequired
    - PermissionDenied
    - RateLimited
    - InvalidProviderResponse
    - TemporaryProviderFailure
    - CancellationRequested
    side_effects:
    - provider_network
  find_owned_playlist_by_name:
    file: runtime/src/playlist_bridge/providers/spotify.py
    signature: '(playlists: Sequence[DestinationPlaylist], owner_id: str, name: str) -> DestinationPlaylist | None'
    errors: []
    side_effects: []
  create_spotify_playlist:
    file: runtime/src/playlist_bridge/providers/spotify.py
    signature: '(client: Spotify, owner_id: str, name: str, description: str, public: bool) -> DestinationPlaylist'
    errors:
    - AuthenticationRequired
    - PermissionDenied
    - RateLimited
    - InvalidProviderResponse
    - TemporaryProviderFailure
    side_effects:
    - provider_network
    - destination_create
  chunk_uris:
    file: runtime/src/playlist_bridge/providers/spotify.py
    signature: '(uris: Sequence[str], batch_size: int) -> list[tuple[str, ...]]'
    errors:
    - ValueError
    side_effects: []
  add_uri_batch:
    file: runtime/src/playlist_bridge/providers/spotify.py
    signature: '(client: Spotify, playlist_id: str, uris: Sequence[str]) -> str'
    errors:
    - AuthenticationRequired
    - PermissionDenied
    - ProviderNotFound
    - RateLimited
    - InvalidProviderResponse
    - TemporaryProviderFailure
    side_effects:
    - provider_network
    - destination_write
  add_all_uri_batches:
    file: runtime/src/playlist_bridge/providers/spotify.py
    signature: '(adapter: SpotifyAdapter, playlist_id: str, uris: Sequence[str], batch_size: int, cancel: CancellationToken) -> list[str]'
    errors:
    - AuthenticationRequired
    - PermissionDenied
    - ProviderNotFound
    - RateLimited
    - InvalidProviderResponse
    - TemporaryProviderFailure
    - CancellationRequested
    side_effects:
    - provider_network
    - destination_write
  read_spotify_playlist_items:
    file: runtime/src/playlist_bridge/providers/spotify.py
    signature: '(client: Spotify, playlist_id: str, cancel: CancellationToken) -> list[str | None]'
    errors:
    - AuthenticationRequired
    - PermissionDenied
    - ProviderNotFound
    - RateLimited
    - InvalidProviderResponse
    - TemporaryProviderFailure
    - CancellationRequested
    side_effects:
    - provider_network
  replace_playlist_items:
    file: runtime/src/playlist_bridge/providers/spotify.py
    signature: '(adapter: SpotifyAdapter, playlist_id: str, uris: Sequence[str], batch_size: int, cancel: CancellationToken) -> list[str]'
    errors:
    - AuthenticationRequired
    - PermissionDenied
    - ProviderNotFound
    - RateLimited
    - InvalidProviderResponse
    - TemporaryProviderFailure
    - CancellationRequested
    side_effects:
    - provider_network
    - destination_write
  matching_config_v1:
    file: runtime/src/playlist_bridge/matching/scoring.py
    signature: () -> MatchingConfig
    errors: []
    side_effects: []
  title_similarity:
    file: runtime/src/playlist_bridge/matching/scoring.py
    signature: '(hint: NormalizedTrackHint, candidate_title: str) -> float'
    errors: []
    side_effects: []
  artist_similarity:
    file: runtime/src/playlist_bridge/matching/scoring.py
    signature: '(artist_hints: Sequence[str], candidate_artists: Sequence[str]) -> float'
    errors: []
    side_effects: []
  version_agreement_score:
    file: runtime/src/playlist_bridge/matching/scoring.py
    signature: '(source_tokens: Sequence[str], candidate_title: str) -> tuple[float, tuple[str, ...]]'
    errors: []
    side_effects: []
  unwanted_version_penalty:
    file: runtime/src/playlist_bridge/matching/scoring.py
    signature: '(source_flags: Sequence[str], candidate_title: str, candidate_artists: Sequence[str], config: MatchingConfig) -> tuple[float, tuple[str, ...]]'
    errors: []
    side_effects: []
  explicit_state_score:
    file: runtime/src/playlist_bridge/matching/scoring.py
    signature: '(source_evidence: bool | None, candidate_explicit: bool, config: MatchingConfig) -> tuple[float, tuple[str, ...]]'
    errors: []
    side_effects: []
  score_candidate:
    file: runtime/src/playlist_bridge/matching/scoring.py
    signature: '(hint: NormalizedTrackHint, candidate: SpotifyCandidate, config: MatchingConfig) -> MatchScore'
    errors: []
    side_effects: []
  rank_candidates:
    file: runtime/src/playlist_bridge/matching/scoring.py
    signature: '(hint: NormalizedTrackHint, candidates: Sequence[SpotifyCandidate], config: MatchingConfig, alternative_limit: int) -> list[tuple[SpotifyCandidate, MatchScore]]'
    errors:
    - ValueError
    side_effects: []
  decide_match:
    file: runtime/src/playlist_bridge/matching/scoring.py
    signature: '(source_item_id: str, ranked: Sequence[tuple[SpotifyCandidate, MatchScore]], policy: MatchPolicy, config: MatchingConfig) -> MatchDecision'
    errors: []
    side_effects: []
  resolve_manual_correction:
    file: runtime/src/playlist_bridge/matching/matcher.py
    signature: '(fingerprint: str, corrections: ManualCorrectionRepository) -> ManualResolution | None'
    errors: []
    side_effects:
    - sqlite_read
  resolve_cached_match:
    file: runtime/src/playlist_bridge/matching/matcher.py
    signature: '(fingerprint: str, policy: MatchPolicy, now: datetime, config: MatchingConfig, cache: MatchCacheRepository) -> CachedResolution | None'
    errors: []
    side_effects:
    - sqlite_read
  match_source_track:
    file: runtime/src/playlist_bridge/matching/matcher.py
    signature: '(track: SourceTrack, policy: MatchPolicy, market: str | None, dependencies: MatcherDependencies, cancel: CancellationToken) -> MatchDecision'
    errors:
    - AuthenticationRequired
    - PermissionDenied
    - RateLimited
    - InvalidProviderResponse
    - TemporaryProviderFailure
    - CancellationRequested
    side_effects:
    - sqlite_read
    - sqlite_write
    - provider_network
  cache_accepted_match:
    file: runtime/src/playlist_bridge/matching/matcher.py
    signature: '(fingerprint: str, decision: MatchDecision, now: datetime, cache: MatchCacheRepository) -> None'
    errors: []
    side_effects:
    - sqlite_write
  apply_manual_review:
    file: runtime/src/playlist_bridge/matching/matcher.py
    signature: '(job_id: str, source_item_id: str, action: ReviewAction, spotify_id: str | None, repositories: ReviewRepositories) -> MatchDecision'
    errors:
    - ValueError
    - JobNotFoundError
    side_effects:
    - sqlite_read
    - sqlite_write
  new_job_id:
    file: runtime/src/playlist_bridge/jobs/runner.py
    signature: () -> str
    errors: []
    side_effects:
    - secure_random
  create_transfer_job:
    file: runtime/src/playlist_bridge/jobs/runner.py
    signature: '(request: TransferRequest, jobs: JobRepository, now: datetime) -> str'
    errors: []
    side_effects:
    - sqlite_write
  calculate_transfer_counts:
    file: runtime/src/playlist_bridge/jobs/runner.py
    signature: '(tracks: Sequence[SourceTrack], decisions: Sequence[MatchDecision]) -> TransferCounts'
    errors: []
    side_effects: []
  accepted_uris_in_source_order:
    file: runtime/src/playlist_bridge/jobs/runner.py
    signature: '(tracks: Sequence[SourceTrack], decisions: Sequence[MatchDecision]) -> list[str]'
    errors:
    - ValueError
    side_effects: []
  write_batch_key:
    file: runtime/src/playlist_bridge/jobs/runner.py
    signature: '(job_id: str, playlist_id: str, batch_index: int, uris: Sequence[str]) -> str'
    errors: []
    side_effects: []
  save_write_checkpoint:
    file: runtime/src/playlist_bridge/jobs/runner.py
    signature: '(job_id: str, plan: DestinationWritePlan, batch_index: int, snapshot_id: str | None, lease_token: str, repositories: RunnerRepositories) -> None'
    errors:
    - LeaseLostError
    side_effects:
    - sqlite_write
  compare_destination_items:
    file: runtime/src/playlist_bridge/jobs/runner.py
    signature: '(expected: Sequence[str], actual: Sequence[str | None]) -> VerificationResult'
    errors: []
    side_effects: []
  verify_destination:
    file: runtime/src/playlist_bridge/jobs/runner.py
    signature: '(playlist_id: str, expected: Sequence[str], adapter: SpotifyAdapter, cancel: CancellationToken) -> VerificationResult'
    errors:
    - AuthenticationRequired
    - PermissionDenied
    - ProviderNotFound
    - RateLimited
    - InvalidProviderResponse
    - TemporaryProviderFailure
    - CancellationRequested
    side_effects:
    - provider_network
  write_json_report:
    file: runtime/src/playlist_bridge/jobs/reports.py
    signature: '(result: TransferResult, destination: DestinationPlaylist | None, verification: VerificationResult | None, report_path: Path) -> Path'
    errors:
    - OSError
    side_effects:
    - filesystem_write
  write_review_csv:
    file: runtime/src/playlist_bridge/jobs/reports.py
    signature: '(rows: Sequence[ReviewReportRow], report_path: Path) -> Path'
    errors:
    - OSError
    side_effects:
    - filesystem_write
  RuntimeDependencies:
    file: runtime/src/playlist_bridge/jobs/runner.py
    signature: 'RuntimeDependencies(jobs: JobRepository, tracks: SourceTrackRepository, decisions: MatchDecisionRepository, match_cache: MatchCacheRepository, corrections: ManualCorrectionRepository, source: SourceAdapter, spotify: SpotifyAdapter, matching_config:
      MatchingConfig, clock: Clock, lease_owner_id: str, report_path_factory: ReportPathFactory)'
    errors:
    - ValueError
    side_effects: []
  run_transfer:
    file: runtime/src/playlist_bridge/jobs/runner.py
    signature: '(request: TransferRequest, *, dependencies: RuntimeDependencies, emit: EventEmitter, cancel: CancellationToken) -> TransferResult'
    errors:
    - JobBusyError
    - LeaseLostError
    - AuthenticationRequired
    - PermissionDenied
    - ProviderNotFound
    - RateLimited
    - InvalidProviderResponse
    - TemporaryProviderFailure
    - CancellationRequested
    - OSError
    side_effects:
    - sqlite_read
    - sqlite_write
    - provider_network
    - destination_write
    - filesystem_write
  resume_transfer:
    file: runtime/src/playlist_bridge/jobs/runner.py
    signature: '(job_id: str, *, allow_failed: bool, allow_cancelled: bool, dependencies: RuntimeDependencies, emit: EventEmitter, cancel: CancellationToken) -> TransferResult'
    errors:
    - JobNotFoundError
    - JobBusyError
    - LeaseLostError
    - CancellationRequested
    side_effects:
    - sqlite_read
    - sqlite_write
    - provider_network
    - destination_write
    - filesystem_write
  rerun_unresolved_reviews:
    file: runtime/src/playlist_bridge/jobs/runner.py
    signature: '(job_id: str, *, dependencies: RuntimeDependencies, emit: EventEmitter, cancel: CancellationToken) -> TransferResult'
    errors:
    - JobNotFoundError
    - JobBusyError
    - LeaseLostError
    - CancellationRequested
    side_effects:
    - sqlite_read
    - sqlite_write
    - provider_network
    - destination_write
    - filesystem_write
  locatePlaylistBridgeExecutable:
    file: extension/process.ts
    signature: '(configuredPath?: string) => Promise<string>'
    errors:
    - ExecutableNotFoundError
    side_effects:
    - filesystem_read
  buildCliInvocation:
    file: extension/process.ts
    signature: '(input: TypedToolInput) => CliInvocation'
    errors:
    - InputValidationError
    side_effects: []
  runCliProcess:
    file: extension/process.ts
    signature: '(invocation: CliInvocation, signal: AbortSignal, onEvent: (event: PlaylistBridgeEvent) => void) => Promise<ProcessResult>'
    errors:
    - ProcessSpawnError
    - ProcessProtocolError
    side_effects:
    - child_process_spawn
    - filesystem_report_write
  JsonlEventParser:
    file: extension/jsonl.ts
    signature: 'JsonlEventParser(onEvent: (event: PlaylistBridgeEvent) => void)'
    errors:
    - ProcessProtocolError
    side_effects: []
  BoundedProcessOutput:
    file: extension/process.ts
    signature: 'BoundedProcessOutput(maxBytes: number, reportPath: string)'
    errors:
    - OSError
    side_effects:
    - filesystem_report_write
  confirmDestructiveTransfer:
    file: extension/index.ts
    signature: '(input: PlaylistTransferInput, context: ToolContext) => Promise<boolean>'
    errors: []
    side_effects:
    - user_confirmation_ui
  renderToolCall:
    file: extension/render.ts
    signature: '(name: PlaylistToolName, input: unknown) => Renderable'
    errors: []
    side_effects: []
  renderToolResult:
    file: extension/render.ts
    signature: '(name: PlaylistToolName, result: unknown) => Renderable'
    errors: []
    side_effects: []
  PolicyThresholds:
    file: runtime/src/playlist_bridge/domain/models.py
    signature: 'PolicyThresholds(auto_accept_score: float, minimum_runner_up_gap: float, review_floor: float)'
    errors:
    - ValueError
    side_effects: []
  MatchingConfig:
    file: runtime/src/playlist_bridge/domain/models.py
    signature: 'MatchingConfig(schema_version: Literal[1], title_weight: float, artist_weight: float, duration_weight: float, version_weight: float, explicit_weight: float, unwanted_version_penalty: float, version_contradiction_penalty: float, explicit_mismatch_penalty:
      float, duration_full_credit_floor_ms: int, duration_full_credit_ratio: float, duration_zero_credit_floor_ms: int, duration_zero_credit_ratio: float, max_queries_per_track: int, results_per_query: int, max_unique_candidates: int, cache_freshness_days: int,
      policy_thresholds: dict[MatchPolicy, PolicyThresholds])'
    errors:
    - ValueError
    side_effects: []
  AuthStatus:
    file: runtime/src/playlist_bridge/auth/status.py
    signature: 'AuthStatus(service: SourceService | DestinationService, profile_name: str, state: Literal["authenticated", "missing", "expired_refreshable", "invalid"], provider_user_id: str | None, display_name: str | None, safe_message: str | None)'
    errors:
    - ValueError
    side_effects: []
  probe_spotify_auth_status:
    file: runtime/src/playlist_bridge/auth/status.py
    signature: '(profile_name: str, profiles: AccountProfileRepository, credentials: CredentialStore) -> AuthStatus'
    errors:
    - CredentialCorruptionError
    side_effects:
    - os_keychain_read
    - sqlite_read
  probe_youtube_auth_status:
    file: runtime/src/playlist_bridge/auth/status.py
    signature: '(profile_name: str, profiles: AccountProfileRepository, credentials: CredentialStore) -> AuthStatus'
    errors:
    - CredentialCorruptionError
    side_effects:
    - os_keychain_read
    - sqlite_read
  get_requested_auth_statuses:
    file: runtime/src/playlist_bridge/auth/status.py
    signature: '(requests: Sequence[tuple[SourceService | DestinationService, str]], profiles: AccountProfileRepository, credentials: CredentialStore) -> list[AuthStatus]'
    errors:
    - CredentialCorruptionError
    side_effects:
    - os_keychain_read
    - sqlite_read
  update_job_checkpoint:
    file: runtime/src/playlist_bridge/persistence/repositories.py
    signature: '(session: Session, job_id: str, checkpoint_fields: Mapping[str, Any], updated_at: datetime, *, lease: JobLease) -> JobRecord'
    errors:
    - JobNotFoundError
    - LeaseLostError
    side_effects:
    - sqlite_read
    - sqlite_write
  CredentialStore:
    file: runtime/src/playlist_bridge/ports.py
    signature: 'Protocol.save(service: SourceService | DestinationService, profile_name: str, token_payload: Mapping[str, Any]) -> None; load(service: SourceService | DestinationService, profile_name: str) -> dict[str, Any] | None; delete(service: SourceService
      | DestinationService, profile_name: str) -> bool'
    errors:
    - CredentialCorruptionError
    - KeyringError
    side_effects:
    - os_keychain_read
    - os_keychain_write
    - os_keychain_delete
  AccountProfileRepository:
    file: runtime/src/playlist_bridge/ports.py
    signature: 'Protocol.save(profile: AccountProfile) -> AccountProfile; get(service: SourceService | DestinationService, profile_name: str) -> AccountProfile | None; list(service: SourceService | DestinationService | None = None) -> list[AccountProfile]'
    errors:
    - IntegrityError
    side_effects:
    - sqlite_read
    - sqlite_write
  JobRepository:
    file: runtime/src/playlist_bridge/ports.py
    signature: 'Protocol.create(request: TransferRequest, job_id: str, created_at: datetime) -> JobRecord; get(job_id: str) -> JobRecord | None; update_state(job_id: str, status: JobStatus, updated_at: datetime) -> JobRecord; update_checkpoint(job_id: str, checkpoint_fields:
      Mapping[str, Any], updated_at: datetime, *, lease: JobLease) -> JobRecord; record_error(job_id: str, safe_code: str, safe_message: str, updated_at: datetime) -> JobRecord; list_recent(limit: int = 20) -> list[JobRecord]; acquire_lease(job_id: str, owner_id:
      str, now: datetime, lease_duration: timedelta, current_token: str | None = None) -> JobLease; heartbeat_lease(lease: JobLease, now: datetime, lease_duration: timedelta) -> JobLease; release_lease(lease: JobLease, now: datetime) -> bool'
    errors:
    - JobNotFoundError
    - JobLeaseBusyError
    - LeaseLostError
    - IntegrityError
    - ValueError
    side_effects:
    - sqlite_read
    - sqlite_write
    - secure_random_token_generation
  SourceTrackRepository:
    file: runtime/src/playlist_bridge/ports.py
    signature: 'Protocol.replace_for_job(job_id: str, tracks: Sequence[SourceTrack]) -> int; list_ordered(job_id: str) -> list[SourceTrack]; get(job_id: str, source_item_id: str) -> SourceTrack | None'
    errors:
    - JobNotFoundError
    - IntegrityError
    side_effects:
    - sqlite_read
    - sqlite_write
  MatchDecisionRepository:
    file: runtime/src/playlist_bridge/ports.py
    signature: 'Protocol.upsert(job_id: str, decision: MatchDecision) -> MatchDecision; unresolved(job_id: str) -> list[MatchDecision]'
    errors:
    - JobNotFoundError
    - IntegrityError
    side_effects:
    - sqlite_read
    - sqlite_write
  MatchCacheRepository:
    file: runtime/src/playlist_bridge/ports.py
    signature: 'Protocol.get(fingerprint: str) -> MatchCacheEntry | None; upsert(entry: MatchCacheEntry) -> MatchCacheEntry'
    errors:
    - IntegrityError
    side_effects:
    - sqlite_read
    - sqlite_write
  ManualCorrectionRepository:
    file: runtime/src/playlist_bridge/ports.py
    signature: 'Protocol.get(fingerprint: str) -> ManualCorrection | None; upsert(correction: ManualCorrection) -> ManualCorrection'
    errors:
    - IntegrityError
    side_effects:
    - sqlite_read
    - sqlite_write
  Clock:
    file: runtime/src/playlist_bridge/ports.py
    signature: Callable[[], datetime]
    errors: []
    side_effects: []
  ReportPathFactory:
    file: runtime/src/playlist_bridge/ports.py
    signature: Callable[[str, str], Path]
    errors: []
    side_effects: []
  RunnerRepositories:
    file: runtime/src/playlist_bridge/ports.py
    signature: 'RunnerRepositories(jobs: JobRepository, tracks: SourceTrackRepository, decisions: MatchDecisionRepository)'
    errors:
    - ValueError
    side_effects: []
  ReviewRepositories:
    file: runtime/src/playlist_bridge/ports.py
    signature: 'ReviewRepositories(jobs: JobRepository, tracks: SourceTrackRepository, decisions: MatchDecisionRepository, corrections: ManualCorrectionRepository)'
    errors:
    - ValueError
    side_effects: []
  MatcherDependencies:
    file: runtime/src/playlist_bridge/ports.py
    signature: 'MatcherDependencies(spotify: SpotifyAdapter, decisions: MatchDecisionRepository, match_cache: MatchCacheRepository, corrections: ManualCorrectionRepository, matching_config: MatchingConfig, clock: Clock)'
    errors:
    - ValueError
    side_effects: []
  KeyringCredentialStore:
    file: runtime/src/playlist_bridge/credentials/store.py
    signature: 'KeyringCredentialStore(backend: KeyringBackend)'
    errors:
    - KeyringError
    - CredentialCorruptionError
    side_effects:
    - os_keychain_read
    - os_keychain_write
    - os_keychain_delete
  SqlAlchemyAccountProfileRepository:
    file: runtime/src/playlist_bridge/persistence/repositories.py
    signature: 'SqlAlchemyAccountProfileRepository(session_factory: sessionmaker[Session])'
    errors:
    - IntegrityError
    side_effects:
    - sqlite_read
    - sqlite_write
  SqlAlchemyJobRepository:
    file: runtime/src/playlist_bridge/persistence/repositories.py
    signature: 'SqlAlchemyJobRepository(session_factory: sessionmaker[Session])'
    errors:
    - JobNotFoundError
    - JobLeaseBusyError
    - LeaseLostError
    - IntegrityError
    - ValueError
    side_effects:
    - sqlite_read
    - sqlite_write
    - secure_random_token_generation
  SqlAlchemySourceTrackRepository:
    file: runtime/src/playlist_bridge/persistence/repositories.py
    signature: 'SqlAlchemySourceTrackRepository(session_factory: sessionmaker[Session])'
    errors:
    - JobNotFoundError
    - IntegrityError
    side_effects:
    - sqlite_read
    - sqlite_write
  SqlAlchemyMatchDecisionRepository:
    file: runtime/src/playlist_bridge/persistence/repositories.py
    signature: 'SqlAlchemyMatchDecisionRepository(session_factory: sessionmaker[Session])'
    errors:
    - JobNotFoundError
    - IntegrityError
    side_effects:
    - sqlite_read
    - sqlite_write
  SqlAlchemyMatchCacheRepository:
    file: runtime/src/playlist_bridge/persistence/repositories.py
    signature: 'SqlAlchemyMatchCacheRepository(session_factory: sessionmaker[Session])'
    errors:
    - IntegrityError
    side_effects:
    - sqlite_read
    - sqlite_write
  SqlAlchemyManualCorrectionRepository:
    file: runtime/src/playlist_bridge/persistence/repositories.py
    signature: 'SqlAlchemyManualCorrectionRepository(session_factory: sessionmaker[Session])'
    errors:
    - IntegrityError
    side_effects:
    - sqlite_read
    - sqlite_write
  ApplicationState:
    file: runtime/src/playlist_bridge/bootstrap.py
    signature: 'ApplicationState(engine: Engine, session_factory: sessionmaker[Session], credentials: CredentialStore, profiles: AccountProfileRepository, jobs: JobRepository, tracks: SourceTrackRepository, decisions: MatchDecisionRepository, match_cache: MatchCacheRepository,
      corrections: ManualCorrectionRepository)'
    errors:
    - ValueError
    side_effects: []
  initialize_application_state:
    file: runtime/src/playlist_bridge/bootstrap.py
    signature: '(*, database_file: Path | None = None, keyring_backend: KeyringBackend | None = None) -> ApplicationState'
    errors:
    - OSError
    - SQLAlchemyError
    - MigrationError
    - KeyringError
    side_effects:
    - filesystem_directory_create
    - sqlite_open
    - sqlite_migration
    - database_backup
  AuthDependencies:
    file: runtime/src/playlist_bridge/bootstrap.py
    signature: 'AuthDependencies(profiles: AccountProfileRepository, credentials: CredentialStore)'
    errors:
    - ValueError
    side_effects: []
  build_auth_dependencies:
    file: runtime/src/playlist_bridge/bootstrap.py
    signature: '(state: ApplicationState | None = None) -> AuthDependencies'
    errors:
    - OSError
    - SQLAlchemyError
    - MigrationError
    - KeyringError
    side_effects:
    - filesystem_directory_create
    - sqlite_open
    - sqlite_migration
  SourceDependencies:
    file: runtime/src/playlist_bridge/bootstrap.py
    signature: 'SourceDependencies(source: SourceAdapter, profiles: AccountProfileRepository, credentials: CredentialStore)'
    errors:
    - ValueError
    side_effects: []
  build_source_dependencies:
    file: runtime/src/playlist_bridge/bootstrap.py
    signature: '(source_profile: str, *, state: ApplicationState | None = None) -> SourceDependencies'
    errors:
    - AuthenticationRequired
    - CredentialCorruptionError
    - InvalidProviderResponse
    - OSError
    - SQLAlchemyError
    - MigrationError
    side_effects:
    - filesystem_directory_create
    - sqlite_open
    - sqlite_migration
    - sqlite_read
    - os_keychain_read
    - provider_network
  build_runtime_dependencies:
    file: runtime/src/playlist_bridge/bootstrap.py
    signature: '(source_profile: str, spotify_profile: str, *, state: ApplicationState | None = None, market: str | None = None) -> RuntimeDependencies'
    errors:
    - AuthenticationRequired
    - CredentialCorruptionError
    - PermissionDenied
    - InvalidProviderResponse
    - TemporaryProviderFailure
    - OSError
    - SQLAlchemyError
    - MigrationError
    side_effects:
    - filesystem_directory_create
    - sqlite_open
    - sqlite_migration
    - sqlite_read
    - os_keychain_read
    - os_keychain_write
    - provider_network
    - secure_random
  build_runtime_dependencies_for_job:
    file: runtime/src/playlist_bridge/bootstrap.py
    signature: '(job_id: str, *, state: ApplicationState | None = None, market: str | None = None) -> RuntimeDependencies'
    errors:
    - JobNotFoundError
    - AuthenticationRequired
    - CredentialCorruptionError
    - PermissionDenied
    - InvalidProviderResponse
    - TemporaryProviderFailure
    - OSError
    - SQLAlchemyError
    - MigrationError
    side_effects:
    - filesystem_directory_create
    - sqlite_open
    - sqlite_migration
    - sqlite_read
    - os_keychain_read
    - os_keychain_write
    - provider_network
    - secure_random
  PlaylistToolName:
    file: extension/types.ts
    signature: type PlaylistToolName = "playlist_auth" | "playlist_transfer" | "playlist_review"
    errors: []
    side_effects: []
  PlaylistAuthInput:
    file: extension/types.ts
    signature: 'type PlaylistAuthInput = { action: "login" | "status" | "logout"; service: "youtube" | "spotify"; profile: string; clientSecretPath?: string }'
    errors: []
    side_effects: []
  PlaylistTransferInput:
    file: extension/types.ts
    signature: 'type PlaylistTransferInput = { sourceUrl: string; sourceProfile: string; spotifyProfile: string; destinationName?: string; mode?: "dry_run" | "create" | "merge" | "replace"; policy?: "strict" | "balanced" | "loose"; visibility?: "private" | "public";
      jobId?: string }'
    errors: []
    side_effects: []
  PlaylistReviewListInput:
    file: extension/types.ts
    signature: 'type PlaylistReviewListInput = { action: "list"; jobId: string }'
    errors: []
    side_effects: []
  PlaylistReviewApplyInput:
    file: extension/types.ts
    signature: 'type PlaylistReviewApplyInput = { action: "apply"; jobId: string; sourceItemId: string; spotifyTrackId?: string; skip?: boolean }'
    errors: []
    side_effects: []
  PlaylistReviewInput:
    file: extension/types.ts
    signature: type PlaylistReviewInput = PlaylistReviewListInput | PlaylistReviewApplyInput
    errors: []
    side_effects: []
  TypedToolInput:
    file: extension/types.ts
    signature: type TypedToolInput = PlaylistAuthInput | PlaylistTransferInput | PlaylistReviewInput
    errors: []
    side_effects: []
  PlaylistBridgeEvent:
    file: extension/types.ts
    signature: 'type PlaylistBridgeEvent = { schemaVersion: 1; type: string; jobId?: string; payload: Record<string, unknown> }'
    errors: []
    side_effects: []
  PlaylistAuthResult:
    file: extension/types.ts
    signature: 'type PlaylistAuthResult = { service: "youtube" | "spotify"; profile: string; state: string; safeMessage?: string }'
    errors: []
    side_effects: []
  PlaylistTransferResult:
    file: extension/types.ts
    signature: 'type PlaylistTransferResult = { jobId: string; status: string; counts: Record<string, number>; destinationId?: string; reportPaths: string[] }'
    errors: []
    side_effects: []
  PlaylistReviewResult:
    file: extension/types.ts
    signature: 'type PlaylistReviewResult = { jobId: string; unresolved: unknown[]; applied?: boolean }'
    errors: []
    side_effects: []
  CliInvocation:
    file: extension/types.ts
    signature: 'type CliInvocation = { executable: string; args: string[]; cwd: string; env: NodeJS.ProcessEnv }'
    errors: []
    side_effects: []
  ProcessResult:
    file: extension/types.ts
    signature: 'type ProcessResult = { exitCode: number; events: PlaylistBridgeEvent[]; stderrReportPath?: string }'
    errors: []
    side_effects: []
  ExtensionDependencies:
    file: extension/types.ts
    signature: 'type ExtensionDependencies = { buildInvocation: (input: TypedToolInput) => Promise<CliInvocation> | CliInvocation; runProcess: (invocation: CliInvocation, signal: AbortSignal, onEvent: (event: PlaylistBridgeEvent) => void) => Promise<ProcessResult>
      }'
    errors: []
    side_effects: []
  TransferRequest:
    file: runtime/src/playlist_bridge/domain/models.py
    signature: 'TransferRequest(source_url: str, source_profile: str, spotify_profile: str, destination_name: str, mode: TransferMode = TransferMode.dry_run, match_policy: MatchPolicy = MatchPolicy.balanced, public: bool = False)'
    errors:
    - ValueError
    side_effects: []
  JobQueryDependencies:
    file: runtime/src/playlist_bridge/bootstrap.py
    signature: 'JobQueryDependencies(jobs: JobRepository)'
    errors:
    - ValueError
    side_effects: []
  build_job_query_dependencies:
    file: runtime/src/playlist_bridge/bootstrap.py
    signature: '(state: ApplicationState | None = None) -> JobQueryDependencies'
    errors:
    - OSError
    - SQLAlchemyError
    - MigrationError
    - KeyringError
    side_effects:
    - filesystem_directory_create
    - sqlite_open
    - sqlite_migration
  build_review_dependencies:
    file: runtime/src/playlist_bridge/bootstrap.py
    signature: '(state: ApplicationState | None = None) -> ReviewRepositories'
    errors:
    - OSError
    - SQLAlchemyError
    - MigrationError
    - KeyringError
    side_effects:
    - filesystem_directory_create
    - sqlite_open
    - sqlite_migration
  jobs_list:
    file: runtime/src/playlist_bridge/cli.py
    signature: '(limit: int = 20, output: OutputMode = OutputMode.human) -> None'
    errors:
    - ValueError
    - OSError
    - SQLAlchemyError
    - MigrationError
    side_effects:
    - filesystem_directory_create
    - sqlite_open
    - sqlite_migration
    - sqlite_read
    - stdout_write
    - stderr_write
  load_job_for_cli:
    file: runtime/src/playlist_bridge/cli.py
    signature: '(job_id: str, dependencies: JobQueryDependencies) -> JobRecord'
    errors:
    - JobNotFoundError
    side_effects:
    - sqlite_read
  load_unresolved_review_decisions:
    file: runtime/src/playlist_bridge/cli.py
    signature: '(job_id: str, repositories: ReviewRepositories) -> list[MatchDecision]'
    errors:
    - JobNotFoundError
    side_effects:
    - sqlite_read
  apply_manual_review_correction:
    file: runtime/src/playlist_bridge/cli.py
    signature: '(job_id: str, source_item_id: str, spotify_track_id: str | None, skip: bool, repositories: ReviewRepositories) -> MatchDecision'
    errors:
    - ValueError
    - JobNotFoundError
    side_effects:
    - sqlite_read
    - sqlite_write
```

Symbols used only within one micro-step may remain private. Any symbol referenced by a later group, a test fixture contract, the CLI, or the Pi extension must be added to this registry before its producing step is dispatchable.

## Persistence, migration, transaction, and error policy

- `alembic` owns schema revisions. A fresh database and an upgraded database must both reach the same head revision.
- Before upgrading a non-empty SQLite database, copy it to a timestamped backup in the data directory. Never delete the backup automatically.
- Read repository methods never commit.
- A public mutation repository method owns exactly one transaction unless it receives an explicit unit-of-work/session supplied by an orchestration operation.
- Multi-row inserts, decision replacement, checkpoint updates, lease validation, and lease heartbeat changes are atomic.
- The jobs table contains `lease_owner`, `lease_token_hash`, `lease_expires_at`, `lease_heartbeat_at`, and integer `row_version` fields.
- Only one non-expired writer lease may exist per job. A stale lease may be replaced with a compare-and-swap update.
- A process that does not hold the current lease token may read a job but may not update checkpoints, write destination batches, or change terminal state.
- Provider response shapes do not escape provider modules.
- Provider failures are translated to typed safe errors before reaching orchestration.
- Tracebacks and raw provider payloads go only to diagnostic files/stderr after redaction; JSON/JSONL results contain typed safe summaries.

## Labeled matcher benchmark gate

The benchmark corpus contains at least `50` sanitized, manually labeled source/candidate sets, including at least `10` hard negatives and examples of remix, live, remaster, cover, karaoke, duplicate title, uncertain artist, unavailable, and non-track items. At least `10` cases must be correctly eligible for automatic acceptance under the labels; otherwise the precision gate is inconclusive and therefore fails.

Use these exact integer counts:

- `all_cases`: every labeled case.
- `auto_matches`: cases the matcher automatically accepts.
- `correct_auto_matches`: automatically accepted cases whose selected Spotify ID equals the labeled ID.
- `incorrect_auto_matches`: automatically accepted cases with the wrong selected ID or a label requiring no automatic match.
- `unsafe_cases`: cases labeled ambiguous, unmatched, unavailable, non-track, or otherwise “must not auto-match.”
- `unsafe_cases_rejected`: unsafe cases that are not automatically accepted.
- `eligible_positive_cases`: cases labeled with a specific Spotify ID and marked eligible for automatic acceptance.
- `correctly_auto_matched_positive_cases`: eligible positive cases automatically accepted with that exact ID.

Calculate the metrics exactly as follows:

```text
auto_match_precision = correct_auto_matches / auto_matches
unsafe_rejection_recall = unsafe_cases_rejected / unsafe_cases
false_confident_match_rate = incorrect_auto_matches / all_cases
auto_match_coverage = auto_matches / all_cases
eligible_positive_recall = correctly_auto_matched_positive_cases / eligible_positive_cases
```

A zero denominator fails the affected required metric rather than being treated as `1.0`. Required gates on the frozen defaults are:

- `auto_matches >= 10`.
- `auto_match_precision >= 0.98`.
- `unsafe_rejection_recall >= 0.95`.
- `false_confident_match_rate <= 0.02`.
- Auto-match coverage and eligible-positive recall are reported but have no minimum; safety takes priority over coverage.

A failure blocks writing modes and requires a reviewed plan/configuration revision followed by rerunning Groups 105–115 and every downstream gate.

## Milestone gates

- **Gate A — Foundation:** Groups 001–038 pass; a clean database can be initialized, upgraded to head, and protected by a tested job lease.
- **Gate B — Offline matching:** Groups 056–115 and 182 pass; sanitized provider fixtures produce deterministic decisions and satisfy the matcher benchmark.
- **Gate C — Fake end to end:** Groups 116–140 and 189 pass with fake adapters; create, interruption, reconciliation, resume, verification, reports, and cancellation succeed without network access.
- **Gate D — CLI and Pi integration:** Groups 141–181 and 190 pass; the frozen install, complete verification command, CLI integration suite, extension unit suite, and Pi load smoke test succeed.
- **Gate E — Live release acceptance:** Groups 183–188 pass from a clean installation using only the user’s explicit provider authorization.

## Fixed architecture

```text
Pi natural-language request
  -> typed Pi tool
  -> TypeScript extension spawns fixed executable with shell=false
  -> Python playlist-bridge CLI
  -> YouTube source adapter
  -> deterministic normalizer and matcher
  -> Spotify destination adapter
  -> SQLite checkpoints, reports, and verification
```

## Expected library set

**Python runtime:** `typer`, `pydantic`, `platformdirs`, `spotipy`, `google-api-python-client`, `google-auth`, `google-auth-oauthlib`, `keyring`, `SQLAlchemy`, `alembic`, `rapidfuzz`, `tenacity`, and `isodate`.

**Python development:** `pytest`, `pytest-cov`, `hypothesis`, `ruff`, `mypy`, `build`, and `uv` for the frozen development/CI lockfile.

**Pi extension:** `@earendil-works/pi-coding-agent`, `typebox`, TypeScript, Node built-ins, an npm lockfile consumed with `npm ci`, and optionally `@earendil-works/pi-tui`.

## Definition of done

- A user can authenticate named YouTube and Spotify profiles through browser-based OAuth.
- `playlist-bridge transfer ... --mode dry_run` reads and matches a playlist without writing.
- Create mode produces a Spotify playlist in source order.
- Ambiguous, unavailable, and non-track items are reported rather than silently guessed.
- Interrupted transfers resume without duplicate writes.
- The destination is read back and verified.
- Pi exposes typed auth, transfer, and review tools.
- Unit and contract tests require no live accounts.
- Live acceptance succeeds from a clean installation.
- Database upgrades are versioned, backed up, and migration-tested.
- Concurrent processes cannot write or resume the same job simultaneously.
- Python and Node dependencies install reproducibly from committed lockfiles.
- The frozen matching policy passes the labeled precision and unsafe-case benchmark gates.
- Production CLI commands construct dependencies through `bootstrap.py` rather than accepting sessions, credentials, or prebuilt bundles.
- Every TypeScript process/tool boundary imports its named types from `extension/types.ts`.
- User-facing documentation states that version one is YouTube-to-Spotify only and does not provide ytmusicapi library/liked-song features.
- Browser automation is absent from playlist operations; browser use is limited to official OAuth pages.
- The spotDL audit is pinned, attributed, and adds no downloader or FFmpeg runtime dependency.

## Required completion report for each micro-step

- **Step ID:** the exact `NNN.NN` identifier.
- **Changed files:** only files changed for this step.
- **Verification:** the exact command or deterministic check run.
- **Result:** pass or fail, including the relevant assertion/output.
- **Deferred work:** explicitly state that later micro-steps were not implemented.

## Phase 1 — Repository and executable skeleton

Create a runnable, testable Python CLI and the directory that will later contain the Pi extension.

### Group 001: Create the repository tree

**Source dependency:** None

**Expected libraries:** No runtime library; filesystem only

**Original requirement:** Create `runtime/src/playlist_bridge`, `runtime/tests`, `extension`, `fixtures`, and `docs` directories.

#### Step 001.01: Create runtime source directory

**Depends on:** None

**Implement:** Create only `runtime/src/playlist_bridge`.

**Acceptance:** The directory exists.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 001.02: Create runtime test directory

**Depends on:** Step 001.01

**Implement:** Create only `runtime/tests`.

**Acceptance:** The directory exists.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 001.03: Create extension directory

**Depends on:** Step 001.02

**Implement:** Create only `extension`.

**Acceptance:** The directory exists.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 001.04: Create fixture directory

**Depends on:** Step 001.03

**Implement:** Create only `fixtures`.

**Acceptance:** The directory exists.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 001.05: Create documentation directory

**Depends on:** Step 001.04

**Implement:** Create only `docs`.

**Acceptance:** The directory exists and no credential or token file was created.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 002: Create the Python project manifest

**Source dependency:** Step 001

**Expected libraries:** `hatchling` as build backend

**Original requirement:** Create `runtime/pyproject.toml` with package name `playlist-bridge`, Python `>=3.12`, and a console script named `playlist-bridge` pointing to `playlist_bridge.cli:app`.

#### Step 002.01: Create `runtime/pyproject.toml`

**Depends on:** Groups 001

**Implement:** Create a valid TOML project file using `hatchling` as the build backend.

**Acceptance:** A TOML parser can read the file.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 002.02: Set Python package metadata

**Depends on:** Step 002.01

**Implement:** Set package name `playlist-bridge` and Python requirement `>=3.12`.

**Acceptance:** The parsed project metadata contains the exact name and Python requirement.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 002.03: Register the console script

**Depends on:** Step 002.02

**Implement:** Add console script `playlist-bridge = playlist_bridge.cli:app`.

**Acceptance:** The parsed script table contains the exact entry point.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 002.04: Verify build discovery

**Depends on:** Step 002.03

**Implement:** Run the build discovery check after dependencies are installed. Do not add application behavior.

**Acceptance:** `python -m build` discovers the project.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 003: Declare runtime dependencies

**Source dependency:** Step 002

**Expected libraries:** `typer`, `pydantic`, `platformdirs`, `spotipy`, `google-api-python-client`, `google-auth`, `google-auth-oauthlib`, `keyring`, `SQLAlchemy`, `alembic`, `rapidfuzz`, `tenacity`, `isodate`

**Original requirement:** Add the listed libraries to the runtime dependency section without writing application code.

#### Step 003.01: Implement declare runtime dependencies

**Depends on:** Groups 002

**Implement:** Add the listed runtime libraries, including `alembic`, without writing application code.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 003.02: Test declare runtime dependencies

**Depends on:** Step 003.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: The project environment installs without dependency-resolution errors.

**Acceptance:** The project environment installs without dependency-resolution errors.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 004: Declare development dependencies and Python lockfile

**Source dependency:** Step 002

**Expected libraries:** `pytest`, `pytest-cov`, `hypothesis`, `ruff`, `mypy`, `build`, `uv`

**Original requirement:** Add the quality/test tools and commit a reproducible `runtime/uv.lock` used in frozen mode by development and CI.

#### Step 004.01: Declare development dependencies

**Depends on:** Groups 002

**Implement:** Add a development dependency group containing `pytest`, `pytest-cov`, `hypothesis`, `ruff`, `mypy`, and `build`; document `uv` as the lock/sync tool.

**Acceptance:** The development dependency group parses and every named command resolves after synchronization.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 004.02: Test development dependency resolution

**Depends on:** Step 004.01

**Implement:** Synchronize a clean development environment and resolve every development command.

**Acceptance:** Every development command can be invoked from the synchronized environment.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 004.03: Generate `runtime/uv.lock`

**Depends on:** Step 004.02

**Implement:** Generate the Python lockfile from `runtime/pyproject.toml` without changing application code.

**Acceptance:** `runtime/uv.lock` exists and records a solution compatible with Python `>=3.12`.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 004.04: Verify frozen Python synchronization

**Depends on:** Step 004.03

**Implement:** Create a clean environment and synchronize using the committed lockfile in frozen mode.

**Acceptance:** Frozen synchronization succeeds and produces no lockfile diff.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 005: Create the package initializer

**Source dependency:** Steps 002–004

**Expected libraries:** Python standard library

**Original requirement:** Create `playlist_bridge/__init__.py` and expose a string constant named `__version__`.

#### Step 005.01: Implement package initializer

**Depends on:** Groups 002–004

**Implement:** Create `playlist_bridge/__init__.py` and expose a string constant named `__version__`.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 005.02: Test package initializer

**Depends on:** Step 005.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Importing `playlist_bridge` returns a non-empty version string.

**Acceptance:** Importing `playlist_bridge` returns a non-empty version string.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 006: Create the empty Typer application

**Source dependency:** Step 005

**Expected libraries:** `typer`

**Original requirement:** Create `playlist_bridge/cli.py` with one `Typer` application and a `version` command.

#### Step 006.01: Implement empty typer application

**Depends on:** Groups 005

**Implement:** Create `playlist_bridge/cli.py` with one `Typer` application and a `version` command.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 006.02: Test empty typer application

**Depends on:** Step 006.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: `playlist-bridge version` exits with code 0 and prints the package version.

**Acceptance:** `playlist-bridge version` exits with code 0 and prints the package version.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 007: Create a CLI smoke test

**Source dependency:** Step 006

**Expected libraries:** `pytest`, `typer.testing.CliRunner`

**Original requirement:** Write one test that invokes the `version` command.

#### Step 007.01: Add a cli smoke test

**Depends on:** Groups 006

**Implement:** Write one test that invokes the `version` command.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 007.02: Run a cli smoke test

**Depends on:** Step 007.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: The test asserts exit code 0 and the expected version text.

**Acceptance:** The test asserts exit code 0 and the expected version text.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 008: Create the root ignore file

**Source dependency:** Step 001

**Expected libraries:** No library

**Original requirement:** Ignore virtual environments, Python caches, SQLite databases, reports, OAuth client-secret files, token exports, Node modules, and build artifacts.

#### Step 008.01: Ignore Python local artifacts

**Depends on:** Groups 001

**Implement:** Add ignore rules for virtual environments and Python caches.

**Acceptance:** A sample virtual environment and cache file do not appear in `git status`.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 008.02: Ignore application state

**Depends on:** Step 008.01

**Implement:** Add ignore rules for SQLite databases and generated reports.

**Acceptance:** A sample database and report do not appear in `git status`.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 008.03: Ignore credential-like files

**Depends on:** Step 008.02

**Implement:** Add ignore rules for OAuth client-secret files and token exports.

**Acceptance:** Deliberately created sample credential filenames do not appear in `git status`.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 008.04: Ignore Node and build artifacts

**Depends on:** Step 008.03

**Implement:** Add ignore rules for `node_modules` and Python/Node build output.

**Acceptance:** Sample dependency and build directories do not appear in `git status`.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 009: Create quality-tool configuration

**Source dependency:** Steps 002–007

**Expected libraries:** `ruff`, `mypy`, `pytest`

**Original requirement:** Add minimal Ruff, mypy, and pytest settings to `pyproject.toml`; enable strict enough typing to reject untyped public functions.

#### Step 009.01: Configure Ruff

**Depends on:** Groups 002–007

**Implement:** Add the minimal Ruff configuration to `runtime/pyproject.toml`.

**Acceptance:** `ruff check` starts successfully on the scaffold.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 009.02: Configure mypy

**Depends on:** Step 009.01

**Implement:** Add mypy configuration that rejects untyped public functions.

**Acceptance:** `mypy` starts successfully and rejects a deliberately untyped public function.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 009.03: Configure pytest

**Depends on:** Step 009.02

**Implement:** Add minimal pytest discovery and test-path settings.

**Acceptance:** `pytest` discovers the scaffold test suite.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 010: Create the first verification script

**Source dependency:** Step 009

**Expected libraries:** POSIX shell, Python tooling

**Original requirement:** Create `scripts/verify-runtime.sh` that runs Ruff, mypy, and pytest in that order and stops on the first failure.

#### Step 010.01: Create verification script shell

**Depends on:** Groups 009

**Implement:** Create `scripts/verify-runtime.sh` with a POSIX shebang and fail-fast shell settings.

**Acceptance:** The script is executable and passes a shell syntax check.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 010.02: Add Ruff command

**Depends on:** Step 010.01

**Implement:** Run Ruff as the first verification command.

**Acceptance:** A Ruff failure stops the script before later commands.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 010.03: Add mypy command

**Depends on:** Step 010.02

**Implement:** Run mypy after Ruff succeeds.

**Acceptance:** A mypy failure stops the script before pytest.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 010.04: Add pytest command

**Depends on:** Step 010.03

**Implement:** Run pytest after Ruff and mypy succeed.

**Acceptance:** The script exits 0 on the clean scaffold.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 010.05: Verify fail-fast behavior

**Depends on:** Step 010.04

**Implement:** Temporarily run the script against a deliberate failing test or equivalent isolated fixture. Revert the deliberate failure afterward.

**Acceptance:** The script exits nonzero on the deliberate failure.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

## Phase 2 — Application paths, configuration, and domain types

Define stable typed contracts before any provider-specific code.

### Group 011: Create application path helpers

**Source dependency:** Step 010

**Expected libraries:** `platformdirs`, `pathlib`

**Original requirement:** Implement functions returning the config, data, cache, jobs, reports, and database paths for `playlist-bridge`.

#### Step 011.01: Implement `config_dir`

**Depends on:** Groups 010

**Implement:** Return the platform-specific configuration directory for `playlist-bridge`.

**Acceptance:** `config_dir` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 011.02: Test `config_dir`

**Depends on:** Step 011.01

**Implement:** Add one focused test for `config_dir`. The returned path is beneath the platform config base.

**Acceptance:** The returned path is beneath the platform config base.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 011.03: Implement `data_dir`

**Depends on:** Step 011.02

**Implement:** Return the platform-specific data directory for `playlist-bridge`.

**Acceptance:** `data_dir` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 011.04: Test `data_dir`

**Depends on:** Step 011.03

**Implement:** Add one focused test for `data_dir`. The returned path is beneath the platform data base.

**Acceptance:** The returned path is beneath the platform data base.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 011.05: Implement `cache_dir`

**Depends on:** Step 011.04

**Implement:** Return the platform-specific cache directory for `playlist-bridge`.

**Acceptance:** `cache_dir` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 011.06: Test `cache_dir`

**Depends on:** Step 011.05

**Implement:** Add one focused test for `cache_dir`. The returned path is beneath the platform cache base.

**Acceptance:** The returned path is beneath the platform cache base.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 011.07: Implement `jobs_dir`

**Depends on:** Step 011.06

**Implement:** Return the jobs directory beneath the application data directory.

**Acceptance:** `jobs_dir` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 011.08: Test `jobs_dir`

**Depends on:** Step 011.07

**Implement:** Add one focused test for `jobs_dir`. The returned path is beneath `data_dir()`.

**Acceptance:** The returned path is beneath `data_dir()`.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 011.09: Implement `reports_dir`

**Depends on:** Step 011.08

**Implement:** Return the reports directory beneath the application data directory.

**Acceptance:** `reports_dir` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 011.10: Test `reports_dir`

**Depends on:** Step 011.09

**Implement:** Add one focused test for `reports_dir`. The returned path is beneath `data_dir()`.

**Acceptance:** The returned path is beneath `data_dir()`.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 011.11: Implement `database_path`

**Depends on:** Step 011.10

**Implement:** Return the SQLite database file path beneath the application data directory.

**Acceptance:** `database_path` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 011.12: Test `database_path`

**Depends on:** Step 011.11

**Implement:** Add one focused test for `database_path`. The returned file path is beneath `data_dir()`.

**Acceptance:** The returned file path is beneath `data_dir()`.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 012: Create the directory initializer

**Source dependency:** Step 011

**Expected libraries:** `pathlib`

**Original requirement:** Implement `ensure_app_directories()` to create only the directories returned by the path helpers.

#### Step 012.01: Implement directory initializer

**Depends on:** Groups 011

**Implement:** Implement `ensure_app_directories()` to create only the directories returned by the path helpers.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 012.02: Test directory initializer

**Depends on:** Step 012.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Calling the function twice succeeds and leaves all required directories present.

**Acceptance:** Calling the function twice succeeds and leaves all required directories present.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 013: Define service enums

**Source dependency:** Step 005

**Expected libraries:** `enum`

**Original requirement:** Define `SourceService` with `youtube` and `DestinationService` with `spotify`; treat standard and music.youtube.com playlist URLs as the same YouTube source adapter.

#### Step 013.01: Define `SourceService`

**Depends on:** Groups 005

**Implement:** Define a string enum containing only lowercase `youtube`.

**Acceptance:** Pydantic parses and serializes `youtube`.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 013.02: Define `DestinationService`

**Depends on:** Step 013.01

**Implement:** Define a string enum containing only lowercase `spotify`.

**Acceptance:** Pydantic parses and serializes `spotify`.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 013.03: Test YouTube URL adapter equivalence

**Depends on:** Step 013.02

**Implement:** Add a focused test proving standard YouTube and `music.youtube.com` playlist URLs select the same source service.

**Acceptance:** Both URL forms resolve to the YouTube source adapter.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 014: Define transfer-policy enums

**Source dependency:** Step 013

**Expected libraries:** `enum`

**Original requirement:** Define `MatchPolicy` (`strict`, `balanced`, `loose`) and `TransferMode` (`dry_run`, `create`, `merge`, `replace`).

#### Step 014.01: Define `MatchPolicy`

**Depends on:** Groups 013

**Implement:** Define string values `strict`, `balanced`, and `loose`.

**Acceptance:** Pydantic accepts each exact lowercase value and rejects an unknown value.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 014.02: Define `TransferMode`

**Depends on:** Step 014.01

**Implement:** Define string values `dry_run`, `create`, `merge`, and `replace`.

**Acceptance:** Pydantic accepts each exact value and rejects an unknown value.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 015: Define job-state enums

**Source dependency:** Step 013

**Expected libraries:** `enum`

**Original requirement:** Define `JobStatus` and `TrackStatus` values covering pending, reading, matching, review, writing, verifying, completed, failed, and cancelled states.

#### Step 015.01: Define `JobStatus`

**Depends on:** Groups 013

**Implement:** Define the required job lifecycle states: pending, reading, matching, review, writing, verifying, completed, failed, and cancelled.

**Acceptance:** Every documented job state parses from its lowercase string.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 015.02: Define `TrackStatus`

**Depends on:** Step 015.01

**Implement:** Define track-level states needed for pending, matching, review, accepted, unavailable, skipped, unmatched, and failed outcomes, using only states already implied by the parent plan.

**Acceptance:** Every declared track state parses from its lowercase string.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 015.03: Define terminal job-state check

**Depends on:** Step 015.02

**Implement:** Implement one small helper or constant set identifying completed, failed, and cancelled as terminal.

**Acceptance:** The helper returns true only for completed, failed, and cancelled.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 016: Define the account-profile model

**Source dependency:** Steps 013, 015

**Expected libraries:** `pydantic`

**Original requirement:** Create `AccountProfile` with profile name, service, optional provider user ID, optional display name, and timestamps; do not include access or refresh tokens.

#### Step 016.01: Implement account-profile model

**Depends on:** Groups 013, 015

**Implement:** Create `AccountProfile` with profile name, service, optional provider user ID, optional display name, and timestamps; do not include access or refresh tokens.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 016.02: Test account-profile model

**Depends on:** Step 016.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: The model rejects an empty profile name and serializes without credential fields.

**Acceptance:** The model rejects an empty profile name and serializes without credential fields.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 017: Define the playlist-reference model

**Source dependency:** Step 013

**Expected libraries:** `pydantic`, `pydantic.HttpUrl`

**Original requirement:** Create `PlaylistReference` with original URL, provider playlist ID, service, and optional title.

#### Step 017.01: Implement playlist-reference model

**Depends on:** Groups 013

**Implement:** Create `PlaylistReference` with original URL, provider playlist ID, service, and optional title.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 017.02: Test playlist-reference model

**Depends on:** Step 017.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Invalid URLs and blank IDs fail validation.

**Acceptance:** Invalid URLs and blank IDs fail validation.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 018: Define the source-track model

**Source dependency:** Steps 013, 015

**Expected libraries:** `pydantic`

**Original requirement:** Create `SourceTrack` with source item ID, video ID, position, raw title, channel title, duration in milliseconds, availability state, and optional normalized metadata.

#### Step 018.01: Implement source-track model

**Depends on:** Groups 013, 015

**Implement:** Create `SourceTrack` with source item ID, video ID, position, raw title, channel title, duration in milliseconds, availability state, and optional normalized metadata.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 018.02: Test source-track model

**Depends on:** Step 018.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Position cannot be negative and duration cannot be below zero.

**Acceptance:** Position cannot be negative and duration cannot be below zero.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 019: Define the Spotify-candidate model

**Source dependency:** Step 013

**Expected libraries:** `pydantic`

**Original requirement:** Create `SpotifyCandidate` with track ID, URI, title, artist names, album, duration, explicit flag, optional ISRC, and market availability.

#### Step 019.01: Implement spotify-candidate model

**Depends on:** Groups 013

**Implement:** Create `SpotifyCandidate` with track ID, URI, title, artist names, album, duration, explicit flag, optional ISRC, and market availability.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 019.02: Test spotify-candidate model

**Depends on:** Step 019.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: A candidate without a Spotify URI is rejected.

**Acceptance:** A candidate without a Spotify URI is rejected.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 020: Define the match-score model

**Source dependency:** Steps 018–019

**Expected libraries:** `pydantic`

**Original requirement:** Create `MatchScore` with component scores, penalties, total score, and explanatory reasons.

#### Step 020.01: Implement match-score model

**Depends on:** Groups 018–019

**Implement:** Create `MatchScore` with component scores, penalties, total score, and explanatory reasons.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 020.02: Test match-score model

**Depends on:** Step 020.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Every score is constrained to a documented numeric range.

**Acceptance:** Every score is constrained to a documented numeric range.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 021: Define the match-decision model

**Source dependency:** Steps 018–020

**Expected libraries:** `pydantic`

**Original requirement:** Create `MatchDecision` with source item ID, status, selected candidate, ranked alternatives, score, and reason.

#### Step 021.01: Implement match-decision model

**Depends on:** Groups 018–020

**Implement:** Create `MatchDecision` with source item ID, status, selected candidate, ranked alternatives, score, and reason.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 021.02: Test match-decision model

**Depends on:** Step 021.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: A matched decision must contain a selected candidate; an unmatched decision must not.

**Acceptance:** A matched decision must contain a selected candidate; an unmatched decision must not.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 022: Define transfer-request and result models

**Source dependency:** Steps 014, 016–021

**Expected libraries:** `pydantic`

**Original requirement:** Create all domain models crossing provider, matcher, runner, report, CLI, and extension boundaries, including transfer, destination, verification, source-playlist, normalized-hint, and matching-configuration contracts.

#### Step 022.01: Define `TransferRequest`

**Depends on:** Groups 014, 016–021

**Implement:** Define exactly these fields and no aliases: `source_url: str`, `source_profile: str`, `spotify_profile: str`, `destination_name: str`, `mode: TransferMode = TransferMode.dry_run`, `match_policy: MatchPolicy = MatchPolicy.balanced`, and `public: bool = False`. Reject blank profile/destination values and unknown fields.

**Acceptance:** A request using the seven exact field names round-trips; deprecated or invented aliases such as `destination_profile`, `policy`, or `visibility` are rejected at the Python model boundary.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 022.02: Define `TransferResult`

**Depends on:** Step 022.01

**Implement:** Create `TransferResult` with counts, destination ID, report paths, and the request/result metadata required by the parent requirement.

**Acceptance:** A valid result can be constructed and serialized.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 022.03: Test transfer model round trip

**Depends on:** Step 022.02

**Implement:** Serialize and deserialize one request and one result.

**Acceptance:** Round-trip JSON serialization reproduces the same model values.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 022.04: Define `DestinationPlaylist`

**Depends on:** Step 022.03

**Implement:** Create a provider-neutral destination model with playlist ID, name, owner ID, visibility, optional snapshot ID, and optional external URL; include no credentials or raw provider payload.

**Acceptance:** A Spotify-created playlist maps into the model and round-trips through JSON.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 022.05: Define `VerificationResult`

**Depends on:** Step 022.04

**Implement:** Create a verification model containing exact-match state plus missing, extra, reordered, and unavailable/null position details.

**Acceptance:** Exact and mismatch examples validate without using untyped dictionaries.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 022.06: Test destination and verification model round trips

**Depends on:** Step 022.05

**Implement:** Serialize and deserialize one destination model, one exact verification result, and one mismatch result.

**Acceptance:** All values reproduce exactly and no credential-shaped field is accepted.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 022.07: Define `SourcePlaylistMetadata`

**Depends on:** Step 022.06

**Implement:** Define the exact frozen fields for playlist reference, description, privacy status, owner channel ID/title, and nonnegative item count. Reject unknown fields and raw provider payloads.

**Acceptance:** A YouTube metadata fixture maps into the model and invalid negative counts or unknown payload fields fail validation.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 022.08: Define `LoadedSourcePlaylist`

**Depends on:** Step 022.07

**Implement:** Define the exact frozen fields `metadata: SourcePlaylistMetadata` and `tracks: list[SourceTrack]`; validate strict ascending source positions.

**Acceptance:** Ordered tracks validate and duplicate, descending, or negative positions fail.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 022.09: Define `NormalizedTrackHint`

**Depends on:** Step 022.08

**Implement:** Define the exact frozen fields for source item ID, normalized title, ordered artist hints, sorted unique version tokens, sorted unique unwanted flags, optional duration, classification, and optional explicit evidence.

**Acceptance:** Round-trip serialization preserves deterministic tuple order and rejects duplicate or unsorted token/flag collections.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 022.10: Define `PolicyThresholds` and `MatchingConfig`

**Depends on:** Step 022.09

**Implement:** Define the exact fields in the frozen cross-boundary model contract, including schema version 1, all scoring/search/cache values, and thresholds for every `MatchPolicy`.

**Acceptance:** `matching_config_v1()` can populate the model exactly and missing, duplicate, unknown, negative, or incomplete policy values fail validation.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 022.11: Test all cross-boundary model contracts

**Depends on:** Step 022.10

**Implement:** Add focused construction, round-trip, unknown-field rejection, ordering, and frozen-default tests for `SourcePlaylistMetadata`, `LoadedSourcePlaylist`, `NormalizedTrackHint`, `PolicyThresholds`, and `MatchingConfig`.

**Acceptance:** All five contracts match the frozen field definitions and no test uses an untyped dictionary across a provider, matcher, runner, CLI, or extension boundary.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 023: Define JSONL event models

**Source dependency:** Steps 015, 022

**Expected libraries:** `pydantic`, discriminated unions

**Original requirement:** Define event types for job start, source progress, match progress, review required, write progress, verification progress, failure, cancellation, and completion.

#### Step 023.01: Define job start event model

**Depends on:** Groups 015, 022

**Implement:** Define only the discriminated Pydantic model for the `job start` JSONL event, including a literal `type` field and only fields required by that event.

**Acceptance:** One valid event instance serializes with the expected `type` value.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 023.02: Define source progress event model

**Depends on:** Step 023.01

**Implement:** Define only the discriminated Pydantic model for the `source progress` JSONL event, including a literal `type` field and only fields required by that event.

**Acceptance:** One valid event instance serializes with the expected `type` value.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 023.03: Define match progress event model

**Depends on:** Step 023.02

**Implement:** Define only the discriminated Pydantic model for the `match progress` JSONL event, including a literal `type` field and only fields required by that event.

**Acceptance:** One valid event instance serializes with the expected `type` value.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 023.04: Define review required event model

**Depends on:** Step 023.03

**Implement:** Define only the discriminated Pydantic model for the `review required` JSONL event, including a literal `type` field and only fields required by that event.

**Acceptance:** One valid event instance serializes with the expected `type` value.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 023.05: Define write progress event model

**Depends on:** Step 023.04

**Implement:** Define only the discriminated Pydantic model for the `write progress` JSONL event, including a literal `type` field and only fields required by that event.

**Acceptance:** One valid event instance serializes with the expected `type` value.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 023.06: Define verification progress event model

**Depends on:** Step 023.05

**Implement:** Define only the discriminated Pydantic model for the `verification progress` JSONL event, including a literal `type` field and only fields required by that event.

**Acceptance:** One valid event instance serializes with the expected `type` value.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 023.07: Define failure event model

**Depends on:** Step 023.06

**Implement:** Define only the discriminated Pydantic model for the `failure` JSONL event, including a literal `type` field and only fields required by that event.

**Acceptance:** One valid event instance serializes with the expected `type` value.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 023.08: Define cancellation event model

**Depends on:** Step 023.07

**Implement:** Define only the discriminated Pydantic model for the `cancellation` JSONL event, including a literal `type` field and only fields required by that event.

**Acceptance:** One valid event instance serializes with the expected `type` value.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 023.09: Define completion event model

**Depends on:** Step 023.08

**Implement:** Define only the discriminated Pydantic model for the `completion` JSONL event, including a literal `type` field and only fields required by that event.

**Acceptance:** One valid event instance serializes with the expected `type` value.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 023.10: Define the JSONL event union

**Depends on:** Step 023.09

**Implement:** Create one discriminated union containing every event model from this group.

**Acceptance:** Pydantic can validate every event through the union.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 023.11: Test event dispatch by `type`

**Depends on:** Step 023.10

**Implement:** Add one parameterized parser test covering every event `type`.

**Acceptance:** The parser selects the correct event model for every `type` field.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 024: Create domain-model fixture tests

**Source dependency:** Steps 016–023

**Expected libraries:** `pytest`

**Original requirement:** Add compact fixtures for one ordinary song, one unavailable video, one Spotify candidate, and one ambiguous match.

#### Step 024.01: Add ordinary song fixture

**Depends on:** Groups 016–023

**Implement:** Create one compact ordinary-song fixture.

**Acceptance:** The fixture validates and serializes.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 024.02: Add unavailable video fixture

**Depends on:** Step 024.01

**Implement:** Create one unavailable-video fixture.

**Acceptance:** The fixture validates and serializes.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 024.03: Add Spotify candidate fixture

**Depends on:** Step 024.02

**Implement:** Create one Spotify-candidate fixture.

**Acceptance:** The fixture validates and serializes.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 024.04: Add ambiguous match fixture

**Depends on:** Step 024.03

**Implement:** Create one ambiguous-match fixture with ranked alternatives.

**Acceptance:** The fixture validates and serializes.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

## Phase 3 — Persistent storage

Add resumable local state without storing provider tokens in the database.

### Group 025: Create the SQLAlchemy engine factory

**Source dependency:** Steps 011–012

**Expected libraries:** `SQLAlchemy`, `sqlite3`

**Original requirement:** Implement `create_engine_for_path(path)` with SQLite foreign keys enabled and a bounded connection configuration.

#### Step 025.01: Implement sqlalchemy engine factory

**Depends on:** Groups 011–012

**Implement:** Implement `create_engine_for_path(path)` with SQLite foreign keys enabled and a bounded connection configuration.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 025.02: Test sqlalchemy engine factory

**Depends on:** Step 025.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: A test opens a temporary database and confirms `PRAGMA foreign_keys` is enabled.

**Acceptance:** A test opens a temporary database and confirms `PRAGMA foreign_keys` is enabled.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 026: Create the declarative base

**Source dependency:** Step 025

**Expected libraries:** `SQLAlchemy ORM`

**Original requirement:** Create a single declarative base class used by all persistence models.

#### Step 026.01: Implement declarative base

**Depends on:** Groups 025

**Implement:** Create a single declarative base class used by all persistence models.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 026.02: Test declarative base

**Depends on:** Step 026.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Importing the persistence package exposes exactly one base metadata object.

**Acceptance:** Importing the persistence package exposes exactly one base metadata object.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 027: Create the account-profile table

**Source dependency:** Steps 016, 026

**Expected libraries:** `SQLAlchemy ORM`

**Original requirement:** Store profile name, service, provider user ID, display name, and timestamps; add a unique constraint on service plus profile name.

#### Step 027.01: Implement account-profile table

**Depends on:** Groups 016, 026

**Implement:** Store profile name, service, provider user ID, display name, and timestamps; add a unique constraint on service plus profile name.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 027.02: Test account-profile table

**Depends on:** Step 027.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Inserting the same service/profile pair twice raises an integrity error.

**Acceptance:** Inserting the same service/profile pair twice raises an integrity error.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 028: Create the jobs table

**Source dependency:** Steps 015, 022, 026

**Expected libraries:** `SQLAlchemy ORM`

**Original requirement:** Store job request/state/checkpoints plus the fields required for optimistic concurrency and a single-writer job lease.

#### Step 028.01: Implement core jobs table fields

**Depends on:** Groups 015, 022, 026

**Implement:** Store job ID, request JSON, state, source/destination IDs, checkpoint counters, timestamps, and last safe error.

**Acceptance:** The model imports and a job row can be created with pending state.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 028.02: Test core jobs table round trip

**Depends on:** Step 028.01

**Implement:** Create and reload one job row.

**Acceptance:** The request, state, checkpoint values, and UTC timestamps round-trip unchanged.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 028.03: Add job lease and row-version fields

**Depends on:** Step 028.02

**Implement:** Add nullable `lease_owner`, `lease_token_hash`, `lease_expires_at`, `lease_heartbeat_at`, and nonnegative integer `row_version` fields with an index supporting active-lease lookup.

**Acceptance:** A row without a lease validates, and a leased row preserves timezone-aware UTC expiry/heartbeat values.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 028.04: Test job lease field constraints

**Depends on:** Step 028.03

**Implement:** Add focused persistence tests for lease-field nullability, UTC values, row-version default, and indexed lookup.

**Acceptance:** Invalid negative row versions fail and active lease fields reload exactly.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 029: Create the source-tracks table

**Source dependency:** Steps 018, 028

**Expected libraries:** `SQLAlchemy ORM`

**Original requirement:** Store each source item keyed by job ID and source item ID, including source position and normalized fields.

#### Step 029.01: Implement source-tracks table

**Depends on:** Groups 018, 028

**Implement:** Store each source item keyed by job ID and source item ID, including source position and normalized fields.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 029.02: Test source-tracks table

**Depends on:** Step 029.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: A unique constraint prevents duplicate source items within one job.

**Acceptance:** A unique constraint prevents duplicate source items within one job.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 030: Create the match-decisions table

**Source dependency:** Steps 021, 029

**Expected libraries:** `SQLAlchemy ORM`

**Original requirement:** Store selected Spotify ID, score JSON, decision status, and reviewed flag for each job track.

#### Step 030.01: Implement match-decisions table

**Depends on:** Groups 021, 029

**Implement:** Store selected Spotify ID, score JSON, decision status, and reviewed flag for each job track.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 030.02: Test match-decisions table

**Depends on:** Step 030.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: A decision can be replaced atomically without creating a duplicate row.

**Acceptance:** A decision can be replaced atomically without creating a duplicate row.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 031: Create the match-cache table

**Source dependency:** Steps 020–021, 026

**Expected libraries:** `SQLAlchemy ORM`

**Original requirement:** Store a canonical source fingerprint, Spotify ID, confidence, origin, and last verification timestamp.

#### Step 031.01: Implement match-cache table

**Depends on:** Groups 020–021, 026

**Implement:** Store a canonical source fingerprint, Spotify ID, confidence, origin, and last verification timestamp.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 031.02: Test match-cache table

**Depends on:** Step 031.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: The fingerprint is unique and supports an indexed lookup.

**Acceptance:** The fingerprint is unique and supports an indexed lookup.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 032: Create the manual-corrections table

**Source dependency:** Steps 020–021, 026

**Expected libraries:** `SQLAlchemy ORM`

**Original requirement:** Store explicit source fingerprint to Spotify ID or explicit skip decisions.

#### Step 032.01: Implement manual-corrections table

**Depends on:** Groups 020–021, 026

**Implement:** Store explicit source fingerprint to Spotify ID or explicit skip decisions.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 032.02: Test manual-corrections table

**Depends on:** Step 032.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: A newer correction replaces the prior correction for the same fingerprint.

**Acceptance:** A newer correction replaces the prior correction for the same fingerprint.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 033: Create schema initialization and migrations

**Source dependency:** Steps 026–032

**Expected libraries:** `SQLAlchemy`, `alembic`, `pathlib`, `shutil`

**Original requirement:** Initialize a fresh schema and upgrade existing SQLite databases through versioned, backup-protected migrations.

#### Step 033.01: Implement fresh schema initializer

**Depends on:** Groups 026–032

**Implement:** Implement `initialize_schema(engine)` for a new empty database using the single metadata object.

**Acceptance:** The function imports and creates no tables outside the declared metadata.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 033.02: Test fresh schema initialization

**Depends on:** Step 033.01

**Implement:** Initialize a temporary empty database and inspect its tables.

**Acceptance:** Every expected application table exists exactly once.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 033.03: Configure Alembic revision ownership

**Depends on:** Step 033.02

**Implement:** Add Alembic configuration and migration environment owned by `playlist_bridge.persistence`; use the same model metadata and a deterministic SQLite URL supplied at runtime.

**Acceptance:** Alembic can load metadata and report one head revision without importing CLI code.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 033.04: Create the initial schema migration

**Depends on:** Step 033.03

**Implement:** Create the initial migration containing every table, constraint, index, and job-lease field from Groups 027–032.

**Acceptance:** Applying the migration to an empty database produces the same inspected schema as `initialize_schema`.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 033.05: Implement backup-protected `upgrade_schema`

**Depends on:** Step 033.04

**Implement:** Implement `upgrade_schema(engine, database_file)` to create a timestamped backup for a non-empty database and then upgrade to Alembic head; do not delete backups.

**Acceptance:** A non-empty database creates one backup before migration and reaches head revision.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 033.06: Add migration idempotence and parity tests

**Depends on:** Step 033.05

**Implement:** Test fresh upgrade, repeated upgrade, backup behavior, and schema parity between initialization and migration paths.

**Acceptance:** Repeated upgrade is a no-op, the database remains readable, and both paths have identical tables, constraints, and indexes.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 034: Create the account-profile repository

**Source dependency:** Steps 027, 033

**Expected libraries:** `SQLAlchemy Session`

**Original requirement:** Implement `save_profile`, `get_profile`, and `list_profiles` without credential handling.

#### Step 034.01: Implement `save_profile`

**Depends on:** Groups 027, 033

**Implement:** Implement profile create/update persistence without accepting or storing credentials.

**Acceptance:** `save_profile` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 034.02: Test `save_profile`

**Depends on:** Step 034.01

**Implement:** Add one focused test for `save_profile`. Tests cover create and update.

**Acceptance:** Tests cover create and update.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 034.03: Implement `get_profile`

**Depends on:** Step 034.02

**Implement:** Return one profile by service and profile name, or the repository missing result.

**Acceptance:** `get_profile` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 034.04: Test `get_profile`

**Depends on:** Step 034.03

**Implement:** Add one focused test for `get_profile`. A missing lookup is handled explicitly.

**Acceptance:** A missing lookup is handled explicitly.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 034.05: Implement `list_profiles`

**Depends on:** Step 034.04

**Implement:** Return profiles in the documented stable sorted order.

**Acceptance:** `list_profiles` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 034.06: Test `list_profiles`

**Depends on:** Step 034.05

**Implement:** Add one focused test for `list_profiles`. A listing test confirms sort order.

**Acceptance:** A listing test confirms sort order.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 035: Create the job repository

**Source dependency:** Steps 028, 033

**Expected libraries:** `SQLAlchemy Session`

**Original requirement:** Implement core job persistence plus compare-and-swap writer leases, lease heartbeats, lease-validated checkpoints, stale takeover, and release.

#### Step 035.01: Implement `create_job`

**Depends on:** Groups 028, 033

**Implement:** Create one job row and commit one transaction.

**Acceptance:** `create_job` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 035.02: Test `create_job`

**Depends on:** Step 035.01

**Implement:** Add one focused test for `create_job`. The created job reloads with the initial state.

**Acceptance:** The created job reloads with the initial state.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 035.03: Implement `get_job`

**Depends on:** Step 035.02

**Implement:** Load one job by ID without mutating it.

**Acceptance:** `get_job` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 035.04: Test `get_job`

**Depends on:** Step 035.03

**Implement:** Add one focused test for `get_job`. Existing and missing job lookups are distinct.

**Acceptance:** Existing and missing job lookups are distinct.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 035.05: Implement `update_job_state`

**Depends on:** Step 035.04

**Implement:** Update only job state and related timestamp in one transaction.

**Acceptance:** `update_job_state` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 035.06: Test `update_job_state`

**Depends on:** Step 035.05

**Implement:** Add one focused test for `update_job_state`. Reloaded state equals the requested state.

**Acceptance:** Reloaded state equals the requested state.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 035.07: Implement `update_job_checkpoint`

**Depends on:** Step 035.06

**Implement:** Update only documented checkpoint fields in one transaction.

**Acceptance:** `update_job_checkpoint` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 035.08: Test `update_job_checkpoint`

**Depends on:** Step 035.07

**Implement:** Add one focused test for `update_job_checkpoint`. Reloaded checkpoints equal the supplied values.

**Acceptance:** Reloaded checkpoints equal the supplied values.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 035.09: Implement `record_job_error`

**Depends on:** Step 035.08

**Implement:** Store one safe error summary without credential text.

**Acceptance:** `record_job_error` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 035.10: Test `record_job_error`

**Depends on:** Step 035.09

**Implement:** Add one focused test for `record_job_error`. Reloaded error matches the safe summary.

**Acceptance:** Reloaded error matches the safe summary.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 035.11: Implement `list_recent_jobs`

**Depends on:** Step 035.10

**Implement:** Return recent jobs in deterministic recency order.

**Acceptance:** `list_recent_jobs` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 035.12: Test `list_recent_jobs`

**Depends on:** Step 035.11

**Implement:** Add one focused test for `list_recent_jobs`. A listing test confirms order and limit handling.

**Acceptance:** A listing test confirms order and limit handling.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 035.13: Implement `acquire_job_lease`

**Depends on:** Step 035.12

**Implement:** Atomically acquire a 90-second writer lease using a random secret token, store only its hash, and increment `row_version`; acquisition succeeds only when no unexpired lease exists or the caller already owns the matching lease.

**Acceptance:** The method returns a typed lease handle containing the plaintext token once and commits exactly one compare-and-swap transaction.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 035.14: Test `acquire_job_lease`

**Depends on:** Step 035.13

**Implement:** Test first acquisition, reentrant acquisition with the current token, and rejection of a second owner while the lease is live.

**Acceptance:** Exactly one owner can hold the live lease.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 035.15: Implement `heartbeat_job_lease`

**Depends on:** Step 035.14

**Implement:** Extend lease expiry by 90 seconds only when job ID, owner, token hash, and expected row version match; update heartbeat time and increment row version in one transaction.

**Acceptance:** A stale token or row version cannot extend the lease.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 035.16: Test `heartbeat_job_lease`

**Depends on:** Step 035.15

**Implement:** Test successful heartbeat, token mismatch, owner mismatch, and optimistic-version mismatch.

**Acceptance:** Only the current lease holder advances heartbeat, expiry, and row version.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 035.17: Implement lease-validated checkpoint update

**Depends on:** Step 035.16

**Implement:** Require the active lease token and expected row version in `update_job_checkpoint`; validate and write the checkpoint atomically.

**Acceptance:** A process without the current lease cannot advance any checkpoint.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 035.18: Test lease-validated checkpoint update

**Depends on:** Step 035.17

**Implement:** Test valid checkpoint update and rejection after token replacement or lease expiry.

**Acceptance:** No rejected attempt changes checkpoint counters or destination snapshot data.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 035.19: Implement `release_job_lease`

**Depends on:** Step 035.18

**Implement:** Clear lease fields only for the current owner/token pair and increment row version in one transaction; releasing an already absent lease is an explicit no-op result.

**Acceptance:** A different owner cannot release the lease.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 035.20: Test stale-lease takeover and release

**Depends on:** Step 035.19

**Implement:** Advance a fake clock beyond expiry, acquire with a new owner, prove the old token cannot checkpoint or release, and release with the new token.

**Acceptance:** Stale takeover is deterministic and leaves no active lease after valid release.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 036: Create the track and decision repositories

**Source dependency:** Steps 029–030, 033

**Expected libraries:** `SQLAlchemy Session`

**Original requirement:** Implement bulk source-track insertion, ordered retrieval, decision upsert, and unresolved-decision retrieval.

#### Step 036.01: Implement `bulk_insert_source_tracks`

**Depends on:** Groups 029–030, 033

**Implement:** Insert an ordered collection of source tracks for one job in one transaction.

**Acceptance:** `bulk_insert_source_tracks` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 036.02: Test `bulk_insert_source_tracks`

**Depends on:** Step 036.01

**Implement:** Add one focused test for `bulk_insert_source_tracks`. The inserted row count matches the input count.

**Acceptance:** The inserted row count matches the input count.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 036.03: Implement `get_source_tracks_ordered`

**Depends on:** Step 036.02

**Implement:** Return source tracks ordered by source position.

**Acceptance:** `get_source_tracks_ordered` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 036.04: Test `get_source_tracks_ordered`

**Depends on:** Step 036.03

**Implement:** Add one focused test for `get_source_tracks_ordered`. Retrieved tracks remain ordered by source position.

**Acceptance:** Retrieved tracks remain ordered by source position.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 036.05: Implement `upsert_match_decision`

**Depends on:** Step 036.04

**Implement:** Insert or replace one decision without creating a duplicate row.

**Acceptance:** `upsert_match_decision` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 036.06: Test `upsert_match_decision`

**Depends on:** Step 036.05

**Implement:** Add one focused test for `upsert_match_decision`. A second write replaces the first decision.

**Acceptance:** A second write replaces the first decision.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 036.07: Implement `get_unresolved_decisions`

**Depends on:** Step 036.06

**Implement:** Return only unresolved decisions in source order.

**Acceptance:** `get_unresolved_decisions` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 036.08: Test `get_unresolved_decisions`

**Depends on:** Step 036.07

**Implement:** Add one focused test for `get_unresolved_decisions`. Accepted and skipped decisions are excluded.

**Acceptance:** Accepted and skipped decisions are excluded.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 037: Create cache and correction repositories

**Source dependency:** Steps 031–033

**Expected libraries:** `SQLAlchemy Session`

**Original requirement:** Implement lookup and upsert methods for automatic matches and manual corrections.

#### Step 037.01: Implement `lookup_match_cache`

**Depends on:** Groups 031–033

**Implement:** Look up one automatic match by canonical fingerprint.

**Acceptance:** `lookup_match_cache` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 037.02: Test `lookup_match_cache`

**Depends on:** Step 037.01

**Implement:** Add one focused test for `lookup_match_cache`. A missing fingerprint returns no entry.

**Acceptance:** A missing fingerprint returns no entry.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 037.03: Implement `upsert_match_cache`

**Depends on:** Step 037.02

**Implement:** Insert or update one automatic cache entry.

**Acceptance:** `upsert_match_cache` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 037.04: Test `upsert_match_cache`

**Depends on:** Step 037.03

**Implement:** Add one focused test for `upsert_match_cache`. A second write replaces the prior entry.

**Acceptance:** A second write replaces the prior entry.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 037.05: Implement `lookup_manual_correction`

**Depends on:** Step 037.04

**Implement:** Look up one manual Spotify ID or explicit skip by fingerprint.

**Acceptance:** `lookup_manual_correction` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 037.06: Test `lookup_manual_correction`

**Depends on:** Step 037.05

**Implement:** Add one focused test for `lookup_manual_correction`. A stored skip is distinguishable from no correction.

**Acceptance:** A stored skip is distinguishable from no correction.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 037.07: Implement `upsert_manual_correction`

**Depends on:** Step 037.06

**Implement:** Insert or replace one manual correction.

**Acceptance:** `upsert_manual_correction` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 037.08: Test `upsert_manual_correction`

**Depends on:** Step 037.07

**Implement:** Add one focused test for `upsert_manual_correction`. A newer correction replaces the prior correction.

**Acceptance:** A newer correction replaces the prior correction.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 037.09: Implement `resolve_correction_then_cache`

**Depends on:** Step 037.08

**Implement:** Implement one small resolver that checks manual correction before automatic cache.

**Acceptance:** `resolve_correction_then_cache` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 037.10: Test `resolve_correction_then_cache`

**Depends on:** Step 037.09

**Implement:** Add one focused test for `resolve_correction_then_cache`. Manual corrections are returned before automatic cache entries for the same fingerprint.

**Acceptance:** Manual corrections are returned before automatic cache entries for the same fingerprint.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 038: Add storage transaction and concurrency tests

**Source dependency:** Steps 034–037

**Expected libraries:** `pytest`, `SQLAlchemy`, deterministic fake clock

**Original requirement:** Prove rollback atomicity, exclusive live job leases, stale takeover, and rejection of stale checkpoint writers.

#### Step 038.01: Add multi-row rollback test

**Depends on:** Groups 034–037

**Implement:** Force an exception during one multi-row repository operation.

**Acceptance:** The test imports and reaches the deliberate exception path.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 038.02: Verify rollback leaves no partial rows

**Depends on:** Step 038.01

**Implement:** Reload all affected tables after rollback.

**Acceptance:** Every affected row count remains unchanged.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 038.03: Add simultaneous lease-acquisition test

**Depends on:** Step 038.02

**Implement:** Attempt lease acquisition from two independent sessions against the same job using a synchronization barrier.

**Acceptance:** Exactly one transaction acquires the live lease and the loser receives the typed busy result.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 038.04: Add expired-lease takeover test

**Depends on:** Step 038.03

**Implement:** Use a fake clock to expire the first lease and acquire with a second owner.

**Acceptance:** The second owner succeeds only after expiry and row version increases monotonically.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 038.05: Add stale-writer checkpoint rejection test

**Depends on:** Step 038.04

**Implement:** Attempt a checkpoint update with the old lease token after takeover.

**Acceptance:** The stale writer changes no checkpoint, snapshot, state, or error field.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

## Phase 4 — Credential storage and provider authentication

Authenticate through provider OAuth pages while keeping refresh tokens in the operating-system keychain.

### Group 039: Create credential key naming

**Source dependency:** Steps 013, 016

**Expected libraries:** `hashlib`, Python standard library

**Original requirement:** Implement a deterministic key name from service plus profile name and a fixed keyring service name.

#### Step 039.01: Implement credential key naming

**Depends on:** Groups 013, 016

**Implement:** Implement a deterministic key name from service plus profile name and a fixed keyring service name.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 039.02: Test credential key naming

**Depends on:** Step 039.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: The same inputs return the same key and distinct services return distinct keys.

**Acceptance:** The same inputs return the same key and distinct services return distinct keys.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 040: Create the keyring token store

**Source dependency:** Step 039

**Expected libraries:** `keyring`

**Original requirement:** Implement `save_token`, `load_token`, and `delete_token` for JSON token payloads.

#### Step 040.01: Implement `save_token`

**Depends on:** Groups 039

**Implement:** Serialize and save one JSON token payload through the injected keyring backend.

**Acceptance:** `save_token` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 040.02: Test `save_token`

**Depends on:** Step 040.01

**Implement:** Add one focused test for `save_token`. A fake keyring contains the saved payload.

**Acceptance:** A fake keyring contains the saved payload.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 040.03: Implement `load_token`

**Depends on:** Step 040.02

**Implement:** Load and deserialize one JSON token payload through the injected keyring backend.

**Acceptance:** `load_token` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 040.04: Test `load_token`

**Depends on:** Step 040.03

**Implement:** Add one focused test for `load_token`. A new token-store instance reads the prior fake-keyring payload.

**Acceptance:** A new token-store instance reads the prior fake-keyring payload.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 040.05: Implement `delete_token`

**Depends on:** Step 040.04

**Implement:** Delete one named token from the injected keyring backend.

**Acceptance:** `delete_token` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 040.06: Test `delete_token`

**Depends on:** Step 040.05

**Implement:** Add one focused test for `delete_token`. Loading after deletion returns the documented missing result.

**Acceptance:** Loading after deletion returns the documented missing result.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 041: Reject malformed stored tokens

**Source dependency:** Step 040

**Expected libraries:** `pydantic`, `keyring`

**Original requirement:** Validate token JSON before returning it and raise a typed credential-corruption error when invalid.

#### Step 041.01: Implement malformed stored tokens

**Depends on:** Groups 040

**Implement:** Validate token JSON before returning it and raise a typed credential-corruption error when invalid.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 041.02: Test malformed stored tokens

**Depends on:** Step 041.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Malformed JSON and missing required fields produce the typed error.

**Acceptance:** Malformed JSON and missing required fields produce the typed error.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 042: Create a Spotipy keyring cache handler

**Source dependency:** Steps 040–041

**Expected libraries:** `spotipy`, `keyring`

**Original requirement:** Subclass Spotipy's cache-handler interface and delegate reads/writes to the keyring token store.

#### Step 042.01: Implement a spotipy keyring cache handler

**Depends on:** Groups 040–041 and Step 189.02

**Implement:** Subclass Spotipy's cache-handler interface and delegate reads/writes to the keyring token store.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 042.02: Test a spotipy keyring cache handler

**Depends on:** Step 042.01 and Step 189.02

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Spotipy token data survives a new cache-handler instance in the fake keyring test.

**Acceptance:** Spotipy token data survives a new cache-handler instance in the fake keyring test.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 043: Create Spotify OAuth settings

**Source dependency:** Steps 011, 016, 042

**Expected libraries:** `pydantic`, `os.environ`, `pathlib`

**Original requirement:** Load Spotify client ID, redirect URI, and scopes from environment or config; never accept a client secret for the desktop flow.

#### Step 043.01: Define Spotify OAuth settings model

**Depends on:** Groups 011, 016, 042

**Implement:** Create a typed settings model for client ID, redirect URI, and scopes. Do not include a client-secret field.

**Acceptance:** The model has no client-secret field.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 043.02: Load Spotify settings from environment

**Depends on:** Step 043.01

**Implement:** Load each Spotify setting from the documented environment names.

**Acceptance:** A test constructs settings from environment values.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 043.03: Load Spotify settings from config

**Depends on:** Step 043.02

**Implement:** Load each Spotify setting from the documented config source when environment values are absent.

**Acceptance:** A test constructs settings from config values.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 043.04: Reject missing Spotify client ID

**Depends on:** Step 043.03

**Implement:** Raise a clear configuration error naming the missing client ID setting.

**Acceptance:** The missing-client-ID test contains the required setting name.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 044: Create the Spotify PKCE manager

**Source dependency:** Steps 042–043

**Expected libraries:** `spotipy.SpotifyPKCE`

**Original requirement:** Build a PKCE auth manager using the configured client ID, loopback redirect URI, scopes, and keyring cache handler.

#### Step 044.01: Implement spotify pkce manager

**Depends on:** Groups 042–043

**Implement:** Build a PKCE auth manager using the configured client ID, loopback redirect URI, scopes, and keyring cache handler.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 044.02: Test spotify pkce manager

**Depends on:** Step 044.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: A unit test inspects the manager configuration without opening a browser.

**Acceptance:** A unit test inspects the manager configuration without opening a browser.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 045: Create the Spotify interactive-auth function

**Source dependency:** Step 044

**Expected libraries:** `spotipy`, `webbrowser`

**Original requirement:** Implement a function that triggers authorization, receives the loopback callback, refreshes if needed, and returns token metadata.

#### Step 045.01: Start Spotify authorization

**Depends on:** Groups 044 and Step 189.02

**Implement:** Implement the call that obtains or opens the PKCE authorization URL using the configured manager. Do not automate password entry.

**Acceptance:** A mocked call reaches the authorization-start operation without exposing token text.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 045.02: Receive Spotify loopback callback

**Depends on:** Step 045.01 and Step 189.02

**Implement:** Implement callback handling that passes the returned authorization data to Spotipy.

**Acceptance:** A mocked callback is consumed exactly once.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 045.03: Persist Spotify token metadata

**Depends on:** Step 045.02 and Step 189.02

**Implement:** Persist the resulting token through the existing cache handler and return only safe metadata.

**Acceptance:** The fake keyring receives the token and the returned value contains no access or refresh token.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 045.04: Refresh Spotify token when required

**Depends on:** Step 045.03 and Step 189.02

**Implement:** Use the auth manager refresh path when the cached token is expired and refreshable.

**Acceptance:** A mocked expired token is refreshed once.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 046: Create the Spotify authenticated client factory

**Source dependency:** Steps 043–045

**Expected libraries:** `spotipy`

**Original requirement:** Return a Spotify client only when a valid token is available; otherwise raise `AuthenticationRequired` with the profile name.

#### Step 046.01: Load Spotify token for a profile

**Depends on:** Groups 043–045 and Step 189.02

**Implement:** Load token state through the existing cache handler for the selected profile.

**Acceptance:** The valid-token branch performs no interactive authorization.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 046.02: Create Spotify client from valid token

**Depends on:** Step 046.01 and Step 189.02

**Implement:** Return a Spotipy client configured with the valid auth manager.

**Acceptance:** The returned object uses the expected auth manager.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 046.03: Handle expired refreshable Spotify token

**Depends on:** Step 046.02 and Step 189.02

**Implement:** Refresh an expired token before returning the client.

**Acceptance:** The refreshable branch returns a client after one refresh.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 046.04: Raise missing-authentication error

**Depends on:** Step 046.03 and Step 189.02

**Implement:** Raise `AuthenticationRequired` containing the profile name when no valid token exists.

**Acceptance:** The missing-token test receives the expected typed error and profile name.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 047: Create Google client-secret loading

**Source dependency:** Steps 011, 016, 039

**Expected libraries:** `google-auth-oauthlib`, `pydantic`

**Original requirement:** Load an installed-application OAuth client JSON path from config and validate that the file exists.

#### Step 047.01: Implement google client-secret loading

**Depends on:** Groups 011, 016, 039

**Implement:** Load an installed-application OAuth client JSON path from config and validate that the file exists.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 047.02: Test google client-secret loading

**Depends on:** Step 047.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: A missing or web-application client file produces a targeted configuration error.

**Acceptance:** A missing or web-application client file produces a targeted configuration error.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 048: Create Google credential serialization

**Source dependency:** Steps 040, 047

**Expected libraries:** `google.oauth2.credentials`, `keyring`

**Original requirement:** Convert Google credentials to and from a minimal JSON payload suitable for keyring storage.

#### Step 048.01: Serialize Google credentials

**Depends on:** Groups 040, 047

**Implement:** Convert Google credentials into the minimal JSON fields required by the parent plan.

**Acceptance:** The payload contains refresh token, token URI, client ID, client secret, and scopes.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 048.02: Deserialize Google credentials

**Depends on:** Step 048.01

**Implement:** Construct Google credentials from the stored minimal JSON payload.

**Acceptance:** Deserialization returns credentials with the same required fields.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 048.03: Test Google credential round trip

**Depends on:** Step 048.02

**Implement:** Add one round-trip test using fake credential values only.

**Acceptance:** The round trip preserves refresh token, token URI, client ID, client secret, and scopes.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 049: Create the Google interactive-auth function

**Source dependency:** Steps 047–048

**Expected libraries:** `google-auth-oauthlib.flow.InstalledAppFlow`

**Original requirement:** Run the local-server flow for YouTube read scopes and save the resulting credentials to keyring.

#### Step 049.01: Implement google interactive-auth function

**Depends on:** Groups 047–048 and Step 189.02

**Implement:** Run the local-server flow for YouTube read scopes and save the resulting credentials to keyring.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 049.02: Test google interactive-auth function

**Depends on:** Step 049.01 and Step 189.02

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: A mocked flow stores credentials and returns an account-authenticated result.

**Acceptance:** A mocked flow stores credentials and returns an account-authenticated result.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 050: Create Google credential refresh

**Source dependency:** Steps 048–049

**Expected libraries:** `google.auth.transport.requests.Request`

**Original requirement:** Refresh expired credentials that contain a refresh token and persist the refreshed payload.

#### Step 050.01: Implement google credential refresh

**Depends on:** Groups 048–049 and Step 189.02

**Implement:** Refresh expired credentials that contain a refresh token and persist the refreshed payload.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 050.02: Test google credential refresh

**Depends on:** Step 050.01 and Step 189.02

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: A mocked refresh changes the access token and writes the new payload once.

**Acceptance:** A mocked refresh changes the access token and writes the new payload once.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 051: Create the YouTube service factory

**Source dependency:** Steps 049–050

**Expected libraries:** `google-api-python-client`

**Original requirement:** Build a YouTube Data API v3 service from valid credentials and raise `AuthenticationRequired` otherwise.

#### Step 051.01: Implement youtube service factory

**Depends on:** Groups 049–050 and Step 189.02

**Implement:** Build a YouTube Data API v3 service from valid credentials and raise `AuthenticationRequired` otherwise.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 051.02: Test youtube service factory

**Depends on:** Step 051.01 and Step 189.02

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: The factory passes credentials and disables discovery-cache writes.

**Acceptance:** The factory passes credentials and disables discovery-cache writes.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 052: Create account identity probes

**Source dependency:** Steps 046, 051

**Expected libraries:** `spotipy`, `google-api-python-client`

**Original requirement:** Implement one small function per provider that returns the authenticated provider user ID and display name.

#### Step 052.01: Implement `probe_spotify_identity`

**Depends on:** Groups 046, 051

**Implement:** Call the current-user endpoint and return provider user ID and display name only.

**Acceptance:** `probe_spotify_identity` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 052.02: Test `probe_spotify_identity`

**Depends on:** Step 052.01

**Implement:** Add one focused test for `probe_spotify_identity`. The result maps into `AccountProfile` without tokens.

**Acceptance:** The result maps into `AccountProfile` without tokens.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 052.03: Implement `probe_youtube_identity`

**Depends on:** Step 052.02

**Implement:** Call the authenticated YouTube identity endpoint and return provider user ID and display name only.

**Acceptance:** `probe_youtube_identity` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 052.04: Test `probe_youtube_identity`

**Depends on:** Step 052.03

**Implement:** Add one focused test for `probe_youtube_identity`. The result maps into `AccountProfile` without tokens.

**Acceptance:** The result maps into `AccountProfile` without tokens.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 053: Create auth-status aggregation

**Source dependency:** Steps 034, 046, 051–052

**Expected libraries:** `pydantic`, provider client factories

**Original requirement:** Return authenticated, missing, expired-refreshable, or invalid for each requested profile.

#### Step 053.01: Define authentication status result

**Depends on:** Groups 034, 046, 051–052

**Implement:** Create `AuthStatus` in `auth/status.py` with authenticated, missing, expired-refreshable, and invalid states.

**Acceptance:** Every status value serializes.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 053.02: Aggregate Spotify profile status

**Depends on:** Step 053.01 and Step 189.02

**Implement:** Implement `probe_spotify_auth_status` in the shared status module. Inspect Spotify credentials without opening a browser and return one typed status.

**Acceptance:** All four status branches are testable with fakes.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 053.03: Aggregate YouTube profile status

**Depends on:** Step 053.02 and Step 189.02

**Implement:** Implement `probe_youtube_auth_status` in the shared status module. Inspect YouTube credentials without opening a browser and return one typed status.

**Acceptance:** All four status branches are testable with fakes.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 053.04: Aggregate requested profiles

**Depends on:** Step 053.03 and Step 189.02

**Implement:** Implement the sole public `get_auth_status` dispatcher and `get_requested_auth_statuses` aggregator in `auth/status.py`; route to provider probes without triggering interactive auth.

**Acceptance:** Status checking never opens a browser.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 054: Create logout operations

**Source dependency:** Steps 034, 040, 053

**Expected libraries:** `keyring`, persistence repositories

**Original requirement:** Delete the selected provider token while retaining non-secret profile metadata.

#### Step 054.01: Implement `logout_spotify_profile`

**Depends on:** Groups 034, 040, 053 and Step 189.02

**Implement:** Delete only the selected Spotify token and retain profile metadata.

**Acceptance:** `logout_spotify_profile` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 054.02: Test `logout_spotify_profile`

**Depends on:** Step 054.01 and Step 189.02

**Implement:** Add one focused test for `logout_spotify_profile`. Status becomes missing and the profile row remains.

**Acceptance:** Status becomes missing and the profile row remains.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 054.03: Implement `logout_youtube_profile`

**Depends on:** Step 054.02 and Step 189.02

**Implement:** Delete only the selected YouTube token and retain profile metadata.

**Acceptance:** `logout_youtube_profile` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 054.04: Test `logout_youtube_profile`

**Depends on:** Step 054.03 and Step 189.02

**Implement:** Add one focused test for `logout_youtube_profile`. Status becomes missing and the profile row remains.

**Acceptance:** Status becomes missing and the profile row remains.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 055: Add authentication command tests

**Source dependency:** Steps 045–054

**Expected libraries:** `pytest`, mocks

**Original requirement:** Test Spotify auth, YouTube auth, status, and logout through fake provider flows.

#### Step 055.01: Add Spotify auth command test

**Depends on:** Groups 045–054

**Implement:** Use fake Spotipy authorization and fake keyring storage.

**Acceptance:** The command succeeds without network I/O or opening a real browser.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 055.02: Add YouTube auth command test

**Depends on:** Step 055.01

**Implement:** Use a fake InstalledAppFlow and fake keyring storage.

**Acceptance:** The command succeeds without network I/O or opening a real browser.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 055.03: Add auth status command test

**Depends on:** Step 055.02

**Implement:** Exercise authenticated, missing, refreshable, and invalid status output.

**Acceptance:** The command performs no interactive auth.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 055.04: Add logout command test

**Depends on:** Step 055.03

**Implement:** Exercise token deletion while retaining profile metadata.

**Acceptance:** The fake keyring entry is removed and the profile row remains.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

## Phase 5 — YouTube playlist source adapter

Read a user's YouTube playlist into ordered, provider-neutral source-track records.

### Group 056: Create provider error types

**Source dependency:** Step 013

**Expected libraries:** Python standard library

**Original requirement:** Define typed errors for authentication required, permission denied, not found, rate limited, invalid response, and temporary provider failure.

#### Step 056.01: Define provider error base

**Depends on:** Groups 013

**Implement:** Define one base provider error containing service, operation, and a safe user-facing message.

**Acceptance:** The base error stores only the documented safe fields.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 056.02: Define `AuthenticationRequired`

**Depends on:** Step 056.01

**Implement:** Define `AuthenticationRequired` as one typed subclass of the provider error base.

**Acceptance:** An instance contains service, operation, and a safe message.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 056.03: Define `PermissionDenied`

**Depends on:** Step 056.02

**Implement:** Define `PermissionDenied` as one typed subclass of the provider error base.

**Acceptance:** An instance contains service, operation, and a safe message.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 056.04: Define `ProviderNotFound`

**Depends on:** Step 056.03

**Implement:** Define `ProviderNotFound` as one typed subclass of the provider error base.

**Acceptance:** An instance contains service, operation, and a safe message.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 056.05: Define `RateLimited`

**Depends on:** Step 056.04

**Implement:** Define `RateLimited` as one typed subclass of the provider error base.

**Acceptance:** An instance contains service, operation, and a safe message.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 056.06: Define `InvalidProviderResponse`

**Depends on:** Step 056.05

**Implement:** Define `InvalidProviderResponse` as one typed subclass of the provider error base.

**Acceptance:** An instance contains service, operation, and a safe message.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 056.07: Define `TemporaryProviderFailure`

**Depends on:** Step 056.06

**Implement:** Define `TemporaryProviderFailure` as one typed subclass of the provider error base.

**Acceptance:** An instance contains service, operation, and a safe message.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 057: Implement YouTube playlist-ID parsing

**Source dependency:** Steps 017, 056

**Expected libraries:** `urllib.parse`, regular expressions

**Original requirement:** Extract a playlist ID from standard YouTube and YouTube Music playlist URLs while rejecting video-only URLs without a list parameter.

#### Step 057.01: Implement youtube playlist-id parsing

**Depends on:** Groups 017, 056

**Implement:** Extract a playlist ID from standard YouTube and YouTube Music playlist URLs while rejecting video-only URLs without a list parameter.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 057.02: Test youtube playlist-id parsing

**Depends on:** Step 057.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Parameterized tests cover valid, malformed, extra-query, and shortened URLs.

**Acceptance:** Parameterized tests cover valid, malformed, extra-query, and shortened URLs.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 058: Define the source-adapter protocol

**Source dependency:** Steps 017–018, 022

**Expected libraries:** `typing.Protocol`

**Original requirement:** Define methods for playlist metadata, item-page retrieval, and complete ordered playlist loading.

#### Step 058.01: Define playlist-metadata protocol method

**Depends on:** Groups 017–018, 022

**Implement:** Add the source-adapter method signature for playlist metadata lookup returning `SourcePlaylistMetadata`.

**Acceptance:** A fake adapter can implement the signature.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 058.02: Define item-page protocol method

**Depends on:** Step 058.01

**Implement:** Add the source-adapter method signature for retrieving one item page.

**Acceptance:** A fake adapter can implement the signature.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 058.03: Define complete-load protocol method

**Depends on:** Step 058.02

**Implement:** Add `load_playlist(reference: PlaylistReference, *, cancel: CancellationToken) -> LoadedSourcePlaylist`.

**Acceptance:** A fake adapter can implement the signature.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 058.04: Add source-adapter type-check fixture

**Depends on:** Step 058.03

**Implement:** Create one minimal fake adapter and include it in static type checking.

**Acceptance:** The fake adapter satisfies the protocol.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 059: Fetch YouTube playlist metadata

**Source dependency:** Steps 022, 051, 057–058

**Expected libraries:** `google-api-python-client`

**Original requirement:** Call the playlist-list endpoint for one playlist ID and map title, description, privacy status, owner channel, and item count.

#### Step 059.01: Implement youtube playlist metadata

**Depends on:** Groups 022, 051, 057–058

**Implement:** Call the playlist-list endpoint for one playlist ID and map title, description, privacy status, owner channel, and item count into `SourcePlaylistMetadata`.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 059.02: Test youtube playlist metadata

**Depends on:** Step 059.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: A fixture response maps to the internal playlist metadata model.

**Acceptance:** A fixture response maps exactly to `SourcePlaylistMetadata` and no raw provider field crosses the adapter boundary.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 060: Map YouTube API errors

**Source dependency:** Steps 056, 059

**Expected libraries:** `googleapiclient.errors.HttpError`

**Original requirement:** Translate expected status/reason combinations into the provider error types.

#### Step 060.01: Add YouTube 401 mapping test

**Depends on:** Groups 056, 059

**Implement:** Map an HTTP 401 fixture to authentication required.

**Acceptance:** The typed error has service and operation.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 060.02: Add YouTube 403 mapping test

**Depends on:** Step 060.01

**Implement:** Map expected permission/quota reason fixtures to the correct typed error.

**Acceptance:** The reason-specific mapping is deterministic.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 060.03: Add YouTube 404 mapping test

**Depends on:** Step 060.02

**Implement:** Map an HTTP 404 fixture to provider not found.

**Acceptance:** The typed error has a safe message.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 060.04: Add YouTube 429 mapping test

**Depends on:** Step 060.03

**Implement:** Map an HTTP 429 fixture to rate limited and preserve retry metadata when present.

**Acceptance:** Retry metadata is preserved.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 060.05: Add YouTube 5xx mapping test

**Depends on:** Step 060.04

**Implement:** Map an HTTP 5xx fixture to temporary provider failure.

**Acceptance:** The typed error is marked retryable by type.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 061: Fetch one playlist-item page

**Source dependency:** Steps 051, 057, 060

**Expected libraries:** `google-api-python-client`

**Original requirement:** Request snippet, content details, status, page token, and at most 50 items for one page.

#### Step 061.01: Implement one playlist-item page

**Depends on:** Groups 051, 057, 060

**Implement:** Request snippet, content details, status, page token, and at most 50 items for one page.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 061.02: Test one playlist-item page

**Depends on:** Step 061.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: The function returns items and the next-page token without mutating order.

**Acceptance:** The function returns items and the next-page token without mutating order.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 062: Paginate all playlist items

**Source dependency:** Step 061

**Expected libraries:** Python iterator/generator

**Original requirement:** Implement a generator that repeatedly calls the one-page function until no next-page token remains.

#### Step 062.01: Implement paginate all playlist items

**Depends on:** Groups 061

**Implement:** Implement a generator that repeatedly calls the one-page function until no next-page token remains.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 062.02: Test paginate all playlist items

**Depends on:** Step 062.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: A three-page fixture yields every item exactly once.

**Acceptance:** A three-page fixture yields every item exactly once.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 063: Represent unavailable playlist items

**Source dependency:** Steps 018, 061–062

**Expected libraries:** `pydantic`

**Original requirement:** Map deleted, private, or missing videos into `SourceTrack` records with availability state and preserved source position.

#### Step 063.01: Map deleted YouTube item

**Depends on:** Groups 018, 061–062

**Implement:** Map a deleted playlist item into `SourceTrack` with deleted availability and preserved position.

**Acceptance:** The deleted item remains in output.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 063.02: Map private YouTube item

**Depends on:** Step 063.01

**Implement:** Map a private playlist item into `SourceTrack` with private availability and preserved position.

**Acceptance:** The private item remains in output.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 063.03: Map missing-video YouTube item

**Depends on:** Step 063.02

**Implement:** Map an item without usable video metadata into an unavailable `SourceTrack`.

**Acceptance:** The missing-video item remains in output.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 064: Collect video IDs for metadata enrichment

**Source dependency:** Steps 018, 063

**Expected libraries:** Python standard library

**Original requirement:** Implement a function returning unique available video IDs in stable first-seen order.

#### Step 064.01: Implement video ids for metadata enrichment

**Depends on:** Groups 018, 063

**Implement:** Implement a function returning unique available video IDs in stable first-seen order.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 064.02: Test video ids for metadata enrichment

**Depends on:** Step 064.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Duplicate videos produce one lookup ID while their playlist items remain separate.

**Acceptance:** Duplicate videos produce one lookup ID while their playlist items remain separate.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 065: Fetch video metadata in batches

**Source dependency:** Steps 051, 060, 064

**Expected libraries:** `google-api-python-client`

**Original requirement:** Call the videos-list endpoint in batches of at most 50 video IDs and return snippet plus content details by video ID.

#### Step 065.01: Chunk YouTube video IDs

**Depends on:** Groups 051, 060, 064

**Implement:** Split unique video IDs into legal request-sized batches.

**Acceptance:** Concatenating the batches reproduces the original ID order.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 065.02: Fetch one video metadata batch

**Depends on:** Step 065.01

**Implement:** Call the videos-list endpoint for exactly one batch and return snippet/content-details data keyed by video ID.

**Acceptance:** A fixture request returns the expected dictionary.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 065.03: Merge video metadata batches

**Depends on:** Step 065.02

**Implement:** Iterate batches and merge each dictionary without losing IDs.

**Acceptance:** A fixture larger than one batch produces one merged dictionary.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 066: Parse ISO-8601 video durations

**Source dependency:** Step 003

**Expected libraries:** `isodate`

**Original requirement:** Convert YouTube duration strings to integer milliseconds and return `None` for unavailable duration.

#### Step 066.01: Implement iso-8601 video durations

**Depends on:** Groups 003

**Implement:** Convert YouTube duration strings to integer milliseconds and return `None` for unavailable duration.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 066.02: Test iso-8601 video durations

**Depends on:** Step 066.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Tests cover seconds, minutes, hours, live streams, and malformed values.

**Acceptance:** Tests cover seconds, minutes, hours, live streams, and malformed values.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 067: Map enriched items to source tracks

**Source dependency:** Steps 063–066

**Expected libraries:** `pydantic`

**Original requirement:** Combine playlist item data and video metadata into ordered `SourceTrack` values.

#### Step 067.01: Implement enriched items to source tracks

**Depends on:** Groups 063–066

**Implement:** Combine playlist item data and video metadata into ordered `SourceTrack` values.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 067.02: Test enriched items to source tracks

**Depends on:** Step 067.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: The output count equals the playlist-item count and positions are unchanged.

**Acceptance:** The output count equals the playlist-item count and positions are unchanged.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 068: Implement complete playlist loading

**Source dependency:** Steps 022, 058–067

**Expected libraries:** Source-adapter protocol implementation

**Original requirement:** Compose metadata lookup, pagination, enrichment, and mapping into one adapter method.

#### Step 068.01: Implement complete playlist loading

**Depends on:** Groups 022, 058–067

**Implement:** Compose metadata lookup, pagination, enrichment, and mapping into one adapter method returning `LoadedSourcePlaylist`.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 068.02: Test complete playlist loading

**Depends on:** Step 068.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: An adapter contract test returns metadata plus ordered tracks using only mocked responses.

**Acceptance:** An adapter contract test returns one `LoadedSourcePlaylist` with exact metadata and strictly ordered tracks using only mocked responses.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 069: Add a YouTube fixture corpus

**Source dependency:** Steps 060–068

**Expected libraries:** JSON fixtures

**Original requirement:** Add fixtures for official audio, official video, user upload, remix, live recording, full DJ mix, deleted item, private item, and duplicate item.

#### Step 069.01: Add YouTube official audio fixture

**Depends on:** Groups 060–068

**Implement:** Add one sanitized deterministic JSON fixture representing a YouTube official audio.

**Acceptance:** The fixture loads deterministically and contains no credential material.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 069.02: Add YouTube official video fixture

**Depends on:** Step 069.01

**Implement:** Add one sanitized deterministic JSON fixture representing a YouTube official video.

**Acceptance:** The fixture loads deterministically and contains no credential material.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 069.03: Add YouTube user upload fixture

**Depends on:** Step 069.02

**Implement:** Add one sanitized deterministic JSON fixture representing a YouTube user upload.

**Acceptance:** The fixture loads deterministically and contains no credential material.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 069.04: Add YouTube remix fixture

**Depends on:** Step 069.03

**Implement:** Add one sanitized deterministic JSON fixture representing a YouTube remix.

**Acceptance:** The fixture loads deterministically and contains no credential material.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 069.05: Add YouTube live recording fixture

**Depends on:** Step 069.04

**Implement:** Add one sanitized deterministic JSON fixture representing a YouTube live recording.

**Acceptance:** The fixture loads deterministically and contains no credential material.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 069.06: Add YouTube full DJ mix fixture

**Depends on:** Step 069.05

**Implement:** Add one sanitized deterministic JSON fixture representing a YouTube full DJ mix.

**Acceptance:** The fixture loads deterministically and contains no credential material.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 069.07: Add YouTube deleted item fixture

**Depends on:** Step 069.06

**Implement:** Add one sanitized deterministic JSON fixture representing a YouTube deleted item.

**Acceptance:** The fixture loads deterministically and contains no credential material.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 069.08: Add YouTube private item fixture

**Depends on:** Step 069.07

**Implement:** Add one sanitized deterministic JSON fixture representing a YouTube private item.

**Acceptance:** The fixture loads deterministically and contains no credential material.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 069.09: Add YouTube duplicate item fixture

**Depends on:** Step 069.08

**Implement:** Add one sanitized deterministic JSON fixture representing a YouTube duplicate item.

**Acceptance:** The fixture loads deterministically and contains no credential material.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

## Phase 6 — Track-title normalization and source classification

Turn noisy YouTube metadata into deterministic search hints without using an LLM.

### Group 070: Create Unicode text normalization

**Source dependency:** Steps 018, 069

**Expected libraries:** `unicodedata`

**Original requirement:** Implement normalization of Unicode width, whitespace, smart quotes, dash variants, and repeated separators while preserving non-Latin text.

#### Step 070.01: Normalize Unicode width

**Depends on:** Groups 018, 069

**Implement:** Normalize compatible Unicode width variants while preserving non-Latin text.

**Acceptance:** Applying the function twice does not change the result.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 070.02: Normalize whitespace

**Depends on:** Step 070.01

**Implement:** Collapse or standardize whitespace as required by the parent plan.

**Acceptance:** Equivalent whitespace variants normalize equally.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 070.03: Normalize smart quotes

**Depends on:** Step 070.02

**Implement:** Map smart quote variants to the selected canonical form.

**Acceptance:** Quote variants normalize equally.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 070.04: Normalize dash variants

**Depends on:** Step 070.03

**Implement:** Map dash variants to the selected canonical form.

**Acceptance:** Dash variants normalize equally.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 070.05: Normalize repeated separators

**Depends on:** Step 070.04

**Implement:** Collapse repeated separators without removing meaningful characters.

**Acceptance:** Repeated separators produce the expected canonical form.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 070.06: Add Unicode normalization property test

**Depends on:** Step 070.05

**Implement:** Use Hypothesis to prove idempotence and crash resistance while preserving non-Latin input.

**Acceptance:** The property test passes for generated Unicode strings.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 071: Create casefolded comparison text

**Source dependency:** Step 070

**Expected libraries:** Python standard library

**Original requirement:** Implement a comparison-only form using Unicode casefolding without changing the display value.

#### Step 071.01: Implement casefolded comparison text

**Depends on:** Groups 070

**Implement:** Implement a comparison-only form using Unicode casefolding without changing the display value.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 071.02: Test casefolded comparison text

**Depends on:** Step 071.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Equivalent capitalization variants produce equal comparison text.

**Acceptance:** Equivalent capitalization variants produce equal comparison text.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 072: Define removable noise phrases

**Source dependency:** Step 070

**Expected libraries:** Static data only

**Original requirement:** Create a reviewed list containing phrases such as official video, official audio, lyrics, HD, HQ, visualizer, and label-upload decorations.

#### Step 072.01: Define removable media-label phrases

**Depends on:** Groups 070

**Implement:** Create the reviewed static set for official video, official audio, lyrics, HD, HQ, visualizer, and label-upload decorations.

**Acceptance:** Every listed removable phrase is present exactly once.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 072.02: Define meaningful version terms separately

**Depends on:** Step 072.01

**Implement:** Create or reference a separate set for meaningful version terms that must not be treated as removable noise.

**Acceptance:** A test proves remix/live/remaster terms are not in the removable set.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 073: Remove bracketed noise segments

**Source dependency:** Steps 071–072

**Expected libraries:** `re`

**Original requirement:** Remove bracketed segments only when they consist entirely of removable noise phrases.

#### Step 073.01: Implement remove bracketed noise segments

**Depends on:** Groups 071–072

**Implement:** Remove bracketed segments only when they consist entirely of removable noise phrases.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 073.02: Test remove bracketed noise segments

**Depends on:** Step 073.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: A remix name in brackets is retained while `[Official Video]` is removed.

**Acceptance:** A remix name in brackets is retained while `[Official Video]` is removed.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 074: Extract meaningful version tokens

**Source dependency:** Steps 070, 073

**Expected libraries:** `re`, static vocabularies

**Original requirement:** Extract remix, mix, edit, remaster, live, instrumental, acoustic, dub, clean, and explicit qualifiers.

#### Step 074.01: Implement extract meaningful version tokens

**Depends on:** Groups 070, 073

**Implement:** Extract remix, mix, edit, remaster, live, instrumental, acoustic, dub, clean, and explicit qualifiers.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 074.02: Test extract meaningful version tokens

**Depends on:** Step 074.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Tests preserve the original token text and a normalized token category.

**Acceptance:** Tests preserve the original token text and a normalized token category.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 075: Detect unwanted-version indicators

**Source dependency:** Steps 070, 073

**Expected libraries:** `re`, static vocabularies

**Original requirement:** Detect karaoke, cover, tribute, nightcore, sped-up, slowed, reverb, reaction, tutorial, and performance indicators.

#### Step 075.01: Implement unwanted-version indicators

**Depends on:** Groups 070, 073

**Implement:** Detect karaoke, cover, tribute, nightcore, sped-up, slowed, reverb, reaction, tutorial, and performance indicators.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 075.02: Test unwanted-version indicators

**Depends on:** Step 075.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Each fixture produces the expected flag set.

**Acceptance:** Each fixture produces the expected flag set.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 076: Split common artist-title formats

**Source dependency:** Steps 070, 074

**Expected libraries:** `re`

**Original requirement:** Parse `Artist - Title`, `Artist – Title`, and carefully delimited alternatives into candidate artist and title parts.

#### Step 076.01: Implement split common artist-title formats

**Depends on:** Groups 070, 074

**Implement:** Parse `Artist - Title`, `Artist – Title`, and carefully delimited alternatives into candidate artist and title parts.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 076.02: Test split common artist-title formats

**Depends on:** Step 076.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Titles containing legitimate internal hyphens are not split at every hyphen.

**Acceptance:** Titles containing legitimate internal hyphens are not split at every hyphen.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 077: Use channel title as an artist hint

**Source dependency:** Steps 070, 075

**Expected libraries:** Python standard library

**Original requirement:** Create a lower-priority artist hint after removing channel suffixes such as `- Topic` and `VEVO`.

#### Step 077.01: Implement channel title as an artist hint

**Depends on:** Groups 070, 075

**Implement:** Create a lower-priority artist hint after removing channel suffixes such as `- Topic` and `VEVO`.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 077.02: Test channel title as an artist hint

**Depends on:** Step 077.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: A topic channel yields the artist name; a generic uploader is marked low confidence.

**Acceptance:** A topic channel yields the artist name; a generic uploader is marked low confidence.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 078: Detect non-track source items

**Source dependency:** Steps 066, 073–076

**Expected libraries:** `re`, duration thresholds

**Original requirement:** Classify likely full mixes, interviews, podcasts, tutorials, compilations, and albums using title flags plus duration.

#### Step 078.01: Implement non-track source items

**Depends on:** Groups 066, 073–076

**Implement:** Classify likely full mixes, interviews, podcasts, tutorials, compilations, and albums using title flags plus duration.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 078.02: Test non-track source items

**Depends on:** Step 078.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: The fixture corpus marks the expected items as non-track without excluding ordinary long tracks automatically.

**Acceptance:** The fixture corpus marks the expected items as non-track without excluding ordinary long tracks automatically.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 079: Create canonical search hints

**Source dependency:** Steps 022, 070–078

**Expected libraries:** `pydantic`

**Original requirement:** Implement `normalize_source_track(track)` to populate the already-defined frozen `NormalizedTrackHint` contract.

#### Step 079.01: Implement canonical search hints

**Depends on:** Groups 022, 070–078

**Implement:** Implement `normalize_source_track(track)` and populate every frozen `NormalizedTrackHint` field without adding alternate hint models.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 079.02: Test canonical search hints

**Depends on:** Step 079.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Every available source track produces exactly one hint.

**Acceptance:** Every available source track produces exactly one hint.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 080: Create the source fingerprint

**Source dependency:** Step 079

**Expected libraries:** `hashlib`, canonical JSON

**Original requirement:** Serialize stable normalized fields as canonical sorted-key JSON and hash with SHA-256 while excluding mutable playlist position and job ID.

#### Step 080.01: Implement source fingerprint

**Depends on:** Groups 079

**Implement:** Serialize stable normalized fields as canonical sorted-key JSON and hash with SHA-256 while excluding mutable playlist position and job ID.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 080.02: Test source fingerprint

**Depends on:** Step 080.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: The same video metadata in two playlists produces the same fingerprint.

**Acceptance:** The same video metadata in two playlists produces the same fingerprint.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 081: Create Spotify search queries

**Source dependency:** Step 079

**Expected libraries:** Python standard library

**Original requirement:** Generate a short ordered list of queries from strongest artist/title evidence to title-only fallback.

#### Step 081.01: Implement spotify search queries

**Depends on:** Groups 079

**Implement:** Generate a short ordered list of queries from strongest artist/title evidence to title-only fallback.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 081.02: Test spotify search queries

**Depends on:** Step 081.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Duplicate query strings are removed while preserving order.

**Acceptance:** Duplicate query strings are removed while preserving order.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 082: Add normalization regression tests

**Source dependency:** Steps 070–081

**Expected libraries:** `pytest`, `hypothesis`

**Original requirement:** Create parameterized tests for the fixture corpus and property tests for idempotence, whitespace stability, and crash resistance.

#### Step 082.01: Add normalization fixture regression test

**Depends on:** Groups 070–081

**Implement:** Parameterize the fixture corpus and assert expected normalized values.

**Acceptance:** All fixture expectations pass.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 082.02: Add normalization idempotence property test

**Depends on:** Step 082.01

**Implement:** Generate Unicode strings and compare one versus two normalization passes.

**Acceptance:** Normalization is idempotent.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 082.03: Add whitespace stability property test

**Depends on:** Step 082.02

**Implement:** Generate whitespace variants around the same tokens.

**Acceptance:** Equivalent whitespace variants normalize equally.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 082.04: Add normalization crash-resistance property test

**Depends on:** Step 082.03

**Implement:** Generate arbitrary Unicode input.

**Acceptance:** No generated input raises an unhandled exception.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

## Phase 7 — Spotify search and playlist adapter

Search Spotify candidates and write verified destination playlists.

### Group 083: Define the Spotify-adapter protocol

**Source dependency:** Steps 019, 046

**Expected libraries:** `typing.Protocol`

**Original requirement:** Define methods for identity, track search, playlist creation, item addition, playlist retrieval, and user-playlist listing.

#### Step 083.01: Define Spotify identity method

**Depends on:** Groups 019, 046

**Implement:** Add the adapter protocol method for authenticated-user identity.

**Acceptance:** A fake adapter implements the method.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 083.02: Define Spotify track-search method

**Depends on:** Step 083.01

**Implement:** Add the adapter protocol method for track search.

**Acceptance:** A fake adapter implements the method.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 083.03: Define Spotify playlist-create method

**Depends on:** Step 083.02

**Implement:** Add the adapter protocol method for playlist creation.

**Acceptance:** A fake adapter implements the method.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 083.04: Define Spotify item-add method

**Depends on:** Step 083.03

**Implement:** Add the adapter protocol method for adding ordered items.

**Acceptance:** A fake adapter implements the method.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 083.05: Define Spotify playlist-read method

**Depends on:** Step 083.04

**Implement:** Add the adapter protocol method for reading ordered playlist items.

**Acceptance:** A fake adapter implements the method.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 083.06: Define Spotify user-playlist-list method

**Depends on:** Step 083.05

**Implement:** Add the adapter protocol method for listing the authenticated user’s playlists.

**Acceptance:** A fake adapter implements the method.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 083.07: Add Spotify-adapter type-check fixture

**Depends on:** Step 083.06

**Implement:** Create one minimal fake adapter and include it in static type checking.

**Acceptance:** The fake adapter satisfies the protocol.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 084: Map Spotify API exceptions

**Source dependency:** Steps 056, 083

**Expected libraries:** `spotipy.exceptions.SpotifyException`

**Original requirement:** Translate authentication, permission, not found, rate limit, and server errors into provider errors.

#### Step 084.01: Add Spotify authentication error mapping test

**Depends on:** Groups 056, 083

**Implement:** Map the relevant Spotify exception to authentication required.

**Acceptance:** The typed error contains service and operation.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 084.02: Add Spotify permission error mapping test

**Depends on:** Step 084.01

**Implement:** Map the relevant Spotify exception to permission denied.

**Acceptance:** The typed error contains a safe message.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 084.03: Add Spotify not-found error mapping test

**Depends on:** Step 084.02

**Implement:** Map the relevant Spotify exception to provider not found.

**Acceptance:** The typed error is deterministic.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 084.04: Add Spotify rate-limit error mapping test

**Depends on:** Step 084.03

**Implement:** Map rate limiting and preserve retry-after data.

**Acceptance:** Retry-after data is preserved.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 084.05: Add Spotify server error mapping test

**Depends on:** Step 084.04

**Implement:** Map retryable server failures to temporary provider failure.

**Acceptance:** The typed error is retryable by type.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 084.06: Add Spotify invalid-response mapping test

**Depends on:** Step 084.05

**Implement:** Map malformed successful responses to invalid provider response.

**Acceptance:** No partial domain object is returned.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 085: Create the authenticated Spotify adapter

**Source dependency:** Steps 046, 083–084

**Expected libraries:** `spotipy`

**Original requirement:** Wrap a Spotipy client from the existing authenticated client factory.

#### Step 085.01: Implement authenticated spotify adapter

**Depends on:** Groups 046, 083–084

**Implement:** Wrap a Spotipy client from the existing authenticated client factory.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 085.02: Test authenticated spotify adapter

**Depends on:** Step 085.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Constructing the adapter performs no network request.

**Acceptance:** Constructing the adapter performs no network request.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 086: Search one Spotify query

**Source dependency:** Steps 084–085

**Expected libraries:** `spotipy`

**Original requirement:** Search only track items for one query and market, requesting exactly 10 candidates unless a stricter adapter limit is configured, and return the raw result page.

#### Step 086.01: Implement search one spotify query

**Depends on:** Groups 084–085

**Implement:** Search only track items for one query and market, requesting exactly 10 candidates unless a stricter adapter limit is configured, and return the raw result page.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 086.02: Test search one spotify query

**Depends on:** Step 086.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: The call uses an explicit small candidate limit and returns no non-track items.

**Acceptance:** The call uses an explicit small candidate limit and returns no non-track items.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 087: Map a Spotify track result

**Source dependency:** Steps 019, 084, 086

**Expected libraries:** `pydantic`

**Original requirement:** Convert a raw Spotify track object into `SpotifyCandidate` including artists, duration, explicit state, ISRC, URI, and availability.

#### Step 087.01: Implement a spotify track result

**Depends on:** Groups 019, 084, 086

**Implement:** Convert a raw Spotify track object into `SpotifyCandidate` including artists, duration, explicit state, ISRC, URI, and availability.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 087.02: Test a spotify track result

**Depends on:** Step 087.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Malformed entries produce a typed invalid-response error rather than a partial candidate.

**Acceptance:** Malformed entries produce a typed invalid-response error rather than a partial candidate.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 088: Search multiple fallback queries

**Source dependency:** Steps 081, 085–087

**Expected libraries:** Python standard library

**Original requirement:** Call at most 4 queries in order, merge candidates by Spotify track ID, and stop after 25 unique candidates.

#### Step 088.01: Execute fallback queries in order

**Depends on:** Groups 081, 085–087

**Implement:** Call the ordered query list sequentially using the one-query search function.

**Acceptance:** A fake records calls in the exact query order.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 088.02: Merge candidates by Spotify track ID

**Depends on:** Step 088.01

**Implement:** Deduplicate returned candidates by track ID while retaining the earliest query rank.

**Acceptance:** Repeated candidates appear once with the earliest rank.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 088.03: Stop at maximum candidate count

**Depends on:** Step 088.02

**Implement:** Stop issuing or collecting results when 25 unique candidates are retained or 4 queries have been issued.

**Acceptance:** The output never exceeds the configured maximum.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 089: Get the authenticated Spotify user

**Source dependency:** Step 085

**Expected libraries:** `spotipy`

**Original requirement:** Return provider user ID and display name from the current-user endpoint.

#### Step 089.01: Implement get the authenticated spotify user

**Depends on:** Groups 085

**Implement:** Return provider user ID and display name from the current-user endpoint.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 089.02: Test get the authenticated spotify user

**Depends on:** Step 089.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: The adapter maps absent display name to a safe fallback.

**Acceptance:** The adapter maps absent display name to a safe fallback.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 090: List the user's playlists

**Source dependency:** Steps 084–085

**Expected libraries:** `spotipy`

**Original requirement:** Paginate the current user's playlists and return ID, name, owner ID, snapshot ID, and visibility.

#### Step 090.01: Implement list the user's playlists

**Depends on:** Groups 084–085

**Implement:** Paginate the current user's playlists and return ID, name, owner ID, snapshot ID, and visibility.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 090.02: Test list the user's playlists

**Depends on:** Step 090.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: A multi-page fixture yields every playlist once.

**Acceptance:** A multi-page fixture yields every playlist once.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 091: Find a destination playlist by exact name

**Source dependency:** Steps 070, 089–090

**Expected libraries:** Python standard library

**Original requirement:** Search only playlists owned by the authenticated user and compare names exactly after Unicode normalization.

#### Step 091.01: Implement find a destination playlist by exact name

**Depends on:** Groups 070, 089–090

**Implement:** Search only playlists owned by the authenticated user and compare names exactly after Unicode normalization.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 091.02: Test find a destination playlist by exact name

**Depends on:** Step 091.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Zero, one, and multiple exact matches produce explicit outcomes.

**Acceptance:** Zero, one, and multiple exact matches produce explicit outcomes.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 092: Create a Spotify playlist

**Source dependency:** Steps 085, 089

**Expected libraries:** `spotipy`

**Original requirement:** Create a playlist for the authenticated user with name, description, and public/private value.

#### Step 092.01: Implement a spotify playlist

**Depends on:** Groups 085, 089

**Implement:** Create a playlist for the authenticated user with name, description, and public/private value.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 092.02: Test a spotify playlist

**Depends on:** Step 092.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: The result maps into the destination-playlist model.

**Acceptance:** The result maps into the destination-playlist model.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 093: Chunk Spotify URIs

**Source dependency:** Step 003

**Expected libraries:** Python standard library

**Original requirement:** Split an ordered URI sequence into batches no larger than 100 URIs and never larger than the adapter/provider maximum.

#### Step 093.01: Implement chunk spotify uris

**Depends on:** Groups 003

**Implement:** Split an ordered URI sequence into batches no larger than 100 URIs and never larger than the adapter/provider maximum.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 093.02: Test chunk spotify uris

**Depends on:** Step 093.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Property tests prove concatenating chunks reproduces the original sequence.

**Acceptance:** Property tests prove concatenating chunks reproduces the original sequence.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 094: Add one URI batch

**Source dependency:** Steps 083, 085, 092–093

**Expected libraries:** `spotipy`

**Original requirement:** Add one ordered batch to a destination playlist and return its new snapshot ID.

#### Step 094.01: Implement one uri batch

**Depends on:** Groups 083, 085, 092–093

**Implement:** Add one ordered batch to a destination playlist and return its new snapshot ID.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 094.02: Test one uri batch

**Depends on:** Step 094.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: An empty batch is rejected before any API call.

**Acceptance:** An empty batch is rejected before any API call.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 095: Add all URI batches

**Source dependency:** Steps 093–094

**Expected libraries:** Python standard library

**Original requirement:** Iterate through batches, emit progress after each successful batch, and stop immediately on failure.

#### Step 095.01: Implement all uri batches

**Depends on:** Groups 093–094

**Implement:** Iterate through batches, emit progress after each successful batch, and stop immediately on failure.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 095.02: Test all uri batches

**Depends on:** Step 095.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: A fake adapter confirms batch order and checkpoint callbacks.

**Acceptance:** A fake adapter confirms batch order and checkpoint callbacks.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 096: Read destination playlist items

**Source dependency:** Steps 084–085

**Expected libraries:** `spotipy`

**Original requirement:** Paginate track items and return ordered Spotify URIs plus unavailable/null positions.

#### Step 096.01: Implement read destination playlist items

**Depends on:** Groups 084–085

**Implement:** Paginate track items and return ordered Spotify URIs plus unavailable/null positions.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 096.02: Test read destination playlist items

**Depends on:** Step 096.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: The returned position count matches the provider item count.

**Acceptance:** The returned position count matches the provider item count.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 097: Create playlist replacement primitives

**Source dependency:** Steps 093–095

**Expected libraries:** `spotipy`

**Original requirement:** Implement replace-first-batch followed by append-remaining-batches as a separate adapter method.

#### Step 097.01: Implement playlist replacement primitives

**Depends on:** Groups 093–095

**Implement:** Implement replace-first-batch followed by append-remaining-batches as a separate adapter method.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 097.02: Test playlist replacement primitives

**Depends on:** Step 097.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: A fake adapter confirms that replacement never runs in create or merge mode.

**Acceptance:** A fake adapter confirms that replacement never runs in create or merge mode.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 098: Add Spotify adapter contract tests

**Source dependency:** Steps 083–097

**Expected libraries:** `pytest`, fake/mocked Spotipy client

**Original requirement:** Test search, mapping, user playlists, create, append, replace, pagination, and error mapping.

#### Step 098.01: Add Spotify search contract test

**Depends on:** Groups 083–097

**Implement:** Test one-query search arguments and track-only results.

**Acceptance:** The adapter uses the expected query, market, and limit.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 098.02: Add Spotify mapping contract test

**Depends on:** Step 098.01

**Implement:** Test raw-track to `SpotifyCandidate` mapping and malformed-response failure.

**Acceptance:** All consumed fields are mapped.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 098.03: Add Spotify identity contract test

**Depends on:** Step 098.02

**Implement:** Test authenticated-user mapping.

**Acceptance:** Missing display name uses the safe fallback.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 098.04: Add Spotify playlist-list contract test

**Depends on:** Step 098.03

**Implement:** Test pagination and stable unique output.

**Acceptance:** Every playlist is returned once.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 098.05: Add Spotify create contract test

**Depends on:** Step 098.04

**Implement:** Test create arguments and destination mapping.

**Acceptance:** The created model contains the provider ID.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 098.06: Add Spotify append contract test

**Depends on:** Step 098.05

**Implement:** Test one-batch and all-batch order.

**Acceptance:** URI order is preserved.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 098.07: Add Spotify replace contract test

**Depends on:** Step 098.06

**Implement:** Test replace-first then append-remaining behavior.

**Acceptance:** Replace is used only by replace mode.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 098.08: Add Spotify error contract test

**Depends on:** Step 098.07

**Implement:** Test provider exception translation.

**Acceptance:** Every expected exception maps to the typed error.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

## Phase 8 — Deterministic candidate matching

Rank Spotify search results, use cached decisions, and route uncertain tracks to review.

### Group 099: Implement title similarity

**Source dependency:** Steps 019, 079

**Expected libraries:** `rapidfuzz.fuzz`

**Original requirement:** Return a normalized score comparing source title hints with a Spotify title.

#### Step 099.01: Implement title similarity

**Depends on:** Groups 019, 079

**Implement:** Return a normalized score comparing source title hints with a Spotify title.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 099.02: Test title similarity

**Depends on:** Step 099.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Exact normalized titles score higher than partial-token matches.

**Acceptance:** Exact normalized titles score higher than partial-token matches.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 100: Implement artist similarity

**Source dependency:** Steps 019, 079

**Expected libraries:** `rapidfuzz.fuzz`

**Original requirement:** Compare all source artist hints against all candidate artists and return the best explained score.

#### Step 100.01: Implement artist similarity

**Depends on:** Groups 019, 079

**Implement:** Compare all source artist hints against all candidate artists and return the best explained score.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 100.02: Test artist similarity

**Depends on:** Step 100.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Artist order and `feat.` formatting do not cause a false mismatch.

**Acceptance:** Artist order and `feat.` formatting do not cause a false mismatch.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 101: Implement duration similarity

**Source dependency:** Steps 018–019

**Expected libraries:** Python standard library

**Original requirement:** Return full credit when delta is at most `max(2500 ms, 2%)`, decline linearly to zero at `max(15000 ms, 10%)`, and remain neutral when either duration is absent.

#### Step 101.01: Implement duration similarity

**Depends on:** Groups 018–019

**Implement:** Return full credit when delta is at most `max(2500 ms, 2%)`, decline linearly to zero at `max(15000 ms, 10%)`, and remain neutral when either duration is absent.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 101.02: Test duration similarity

**Depends on:** Step 101.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Boundary tests cover exact, near, far, and missing durations.

**Acceptance:** Boundary tests cover exact, near, far, and missing durations.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 102: Implement version agreement scoring

**Source dependency:** Steps 019, 074, 079

**Expected libraries:** Static vocabularies

**Original requirement:** Reward matching meaningful version categories and penalize contradictions such as live versus studio or remix-name disagreement.

#### Step 102.01: Implement version agreement scoring

**Depends on:** Groups 019, 074, 079

**Implement:** Reward matching meaningful version categories and penalize contradictions such as live versus studio or remix-name disagreement.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 102.02: Test version agreement scoring

**Depends on:** Step 102.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: The score explanation names every agreement and contradiction.

**Acceptance:** The score explanation names every agreement and contradiction.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 103: Implement unwanted-version penalties

**Source dependency:** Steps 019, 075, 079

**Expected libraries:** Static vocabularies

**Original requirement:** Penalize candidate titles or artist names that indicate cover, karaoke, tribute, sped-up, slowed, or nightcore when the source does not.

#### Step 103.01: Implement unwanted-version penalties

**Depends on:** Groups 019, 075, 079

**Implement:** Penalize candidate titles or artist names that indicate cover, karaoke, tribute, sped-up, slowed, or nightcore when the source does not.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 103.02: Test unwanted-version penalties

**Depends on:** Step 103.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Each unwanted class has an independent regression test.

**Acceptance:** Each unwanted class has an independent regression test.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 104: Implement explicit-state handling

**Source dependency:** Steps 019, 079

**Expected libraries:** Python standard library

**Original requirement:** Apply a small configurable penalty when source evidence and candidate explicit state conflict; remain neutral when source evidence is absent.

#### Step 104.01: Implement explicit-state handling

**Depends on:** Groups 019, 079

**Implement:** Apply a small configurable penalty when source evidence and candidate explicit state conflict; remain neutral when source evidence is absent.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 104.02: Test explicit-state handling

**Depends on:** Step 104.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: The score never rejects a candidate solely because source evidence is unknown.

**Acceptance:** The score never rejects a candidate solely because source evidence is unknown.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 105: Implement aggregate scoring

**Source dependency:** Steps 020, 022, 099–104

**Expected libraries:** `pydantic`

**Original requirement:** Combine title, artist, duration, version, explicit, and penalty components into one bounded `MatchScore` with reasons.

#### Step 105.01: Define aggregate score weights

**Depends on:** Groups 020, 022, 099–104

**Implement:** Implement `matching_config_v1()` by constructing the frozen `MatchingConfig` exactly once with positive weights title=40, artist=30, duration=15, version=10, explicit=5; penalties unwanted=30, version contradiction=20, explicit mismatch=3; and every frozen search, cache, duration, and policy value. Do not duplicate these literals in another production module.

**Acceptance:** The returned model equals the canonical version-one configuration fixture, the positive component weights sum to exactly 100, and scanning production code finds no second source of frozen numeric defaults.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 105.02: Combine positive score components

**Depends on:** Step 105.01

**Implement:** Implement the arithmetic that combines title, artist, duration, version, and explicit components.

**Acceptance:** A focused test matches a hand-calculated example.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 105.03: Apply aggregate penalties

**Depends on:** Step 105.02

**Implement:** Subtract the documented penalty components without changing individual component records.

**Acceptance:** Adding a penalty cannot raise the total.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 105.04: Clamp and explain aggregate score

**Depends on:** Step 105.03

**Implement:** Clamp the total to the documented range and construct `MatchScore` with component values and reasons.

**Acceptance:** The result stays within bounds and preserves reasons.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 106: Create policy thresholds

**Source dependency:** Steps 014, 022, 105

**Expected libraries:** `pydantic` configuration

**Original requirement:** Define acceptance, ambiguity, and rejection thresholds for strict, balanced, and loose policies.

#### Step 106.01: Define strict policy thresholds

**Depends on:** Groups 014, 022, 105

**Implement:** Read the strict `PolicyThresholds` from `matching_config_v1()` and expose it through `MATCH_POLICY_THRESHOLDS`; do not create a second threshold literal source.

**Acceptance:** The strict configuration validates.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 106.02: Define balanced policy thresholds

**Depends on:** Step 106.01

**Implement:** Read the balanced `PolicyThresholds` from `matching_config_v1()` and expose it through `MATCH_POLICY_THRESHOLDS`; do not create a second threshold literal source.

**Acceptance:** The balanced configuration validates.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 106.03: Define loose policy thresholds

**Depends on:** Step 106.02

**Implement:** Read the loose `PolicyThresholds` from `matching_config_v1()` and expose it through `MATCH_POLICY_THRESHOLDS`; do not create a second threshold literal source.

**Acceptance:** The loose configuration validates.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 106.04: Test policy ordering invariant

**Depends on:** Step 106.03

**Implement:** Add one invariant test comparing strict, balanced, and loose acceptance behavior.

**Acceptance:** Strict never accepts a score that balanced rejects, and balanced never accepts a score that loose rejects.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 107: Rank candidate lists

**Source dependency:** Steps 105–106

**Expected libraries:** Python standard library

**Original requirement:** Score each candidate, sort descending with deterministic tie breakers, and retain a configured number of alternatives.

#### Step 107.01: Score every candidate

**Depends on:** Groups 105–106

**Implement:** Apply the aggregate scorer to each candidate exactly once.

**Acceptance:** A fake scorer records one call per candidate.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 107.02: Sort candidates by total score

**Depends on:** Step 107.01

**Implement:** Sort descending by total score.

**Acceptance:** Higher scores appear first.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 107.03: Add deterministic tie breakers

**Depends on:** Step 107.02

**Implement:** Add stable tie breakers using existing candidate fields only.

**Acceptance:** Repeated runs produce identical order for ties.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 107.04: Limit ranked alternatives

**Depends on:** Step 107.03

**Implement:** Retain only the configured number of alternatives.

**Acceptance:** The output length respects the limit.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 108: Decide matched, ambiguous, or unmatched

**Source dependency:** Steps 021, 106–107

**Expected libraries:** `pydantic`

**Original requirement:** Use top score, runner-up gap, and policy thresholds to create a `MatchDecision`.

#### Step 108.01: Handle no-candidate decision

**Depends on:** Groups 021, 106–107

**Implement:** Return unmatched when the candidate list is empty.

**Acceptance:** The decision has no selected candidate.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 108.02: Handle weak top-result decision

**Depends on:** Step 108.01

**Implement:** Return unmatched when the top score is below the policy threshold.

**Acceptance:** The decision has no selected candidate.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 108.03: Handle close-tie decision

**Depends on:** Step 108.02

**Implement:** Return ambiguous when the top two scores are too close under the selected policy.

**Acceptance:** The decision preserves ranked alternatives.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 108.04: Handle confident-match decision

**Depends on:** Step 108.03

**Implement:** Return matched when the top score and runner-up gap satisfy policy thresholds.

**Acceptance:** The decision contains the selected candidate.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 109: Apply manual corrections first

**Source dependency:** Steps 037, 080, 108

**Expected libraries:** Correction repository

**Original requirement:** Return a manual Spotify ID or explicit skip before consulting cache or provider search.

#### Step 109.01: Implement manual corrections first

**Depends on:** Groups 037, 080, 108 and Step 189.04

**Implement:** Return a manual Spotify ID or explicit skip before consulting cache or provider search.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 109.02: Test manual corrections first

**Depends on:** Step 109.01 and Step 189.04

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: No search call occurs when a correction exists.

**Acceptance:** No search call occurs when a correction exists.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 110: Apply verified match cache second

**Source dependency:** Steps 037, 080, 106

**Expected libraries:** Cache repository

**Original requirement:** Return a cached match only when it meets the selected policy auto-accept score and was verified within the previous 30 days.

#### Step 110.01: Implement verified match cache second

**Depends on:** Groups 037, 080, 106 and Step 189.04

**Implement:** Return a cached match only when it meets the selected policy auto-accept score and was verified within the previous 30 days.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 110.02: Test verified match cache second

**Depends on:** Step 110.01 and Step 189.04

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: A stale or weak cache entry falls through to provider search.

**Acceptance:** A stale or weak cache entry falls through to provider search.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 111: Create the single-track matcher

**Source dependency:** Steps 036, 079–081, 088, 108–110

**Expected libraries:** Spotify adapter, normalization, repositories

**Original requirement:** For one source track: normalize, classify, check correction, check cache, search, rank, decide, persist, and return one decision.

#### Step 111.01: Normalize one source track

**Depends on:** Groups 036, 079–081, 088, 108–110 and Step 189.04

**Implement:** Convert one source track into its canonical normalized hint.

**Acceptance:** The normalizer is called once.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 111.02: Classify one source track

**Depends on:** Step 111.01 and Step 189.04

**Implement:** Apply non-track classification and stop with the documented non-track decision when applicable.

**Acceptance:** A non-track input performs no Spotify search.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 111.03: Check manual correction

**Depends on:** Step 111.02 and Step 189.04

**Implement:** Look up the source fingerprint in manual corrections and return the explicit match or skip when found.

**Acceptance:** A correction prevents cache and provider search calls.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 111.04: Check verified match cache

**Depends on:** Step 111.03 and Step 189.04

**Implement:** Look up an eligible verified cache entry when no correction exists.

**Acceptance:** A valid cache hit prevents provider search.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 111.05: Search Spotify candidates

**Depends on:** Step 111.04 and Step 189.04

**Implement:** Generate ordered queries and call the Spotify adapter when no prior decision exists.

**Acceptance:** The adapter receives queries in order.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 111.06: Rank Spotify candidates

**Depends on:** Step 111.05 and Step 189.04

**Implement:** Run deterministic candidate ranking.

**Acceptance:** The ranked output is deterministic.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 111.07: Create match decision

**Depends on:** Step 111.06 and Step 189.04

**Implement:** Apply policy thresholds to produce matched, ambiguous, or unmatched.

**Acceptance:** Each branch returns a valid `MatchDecision`.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 111.08: Persist match decision

**Depends on:** Step 111.07 and Step 189.04

**Implement:** Upsert the one-track decision and cache only eligible accepted automatic matches.

**Acceptance:** The persisted decision reloads with the same status.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 112: Persist accepted automatic matches

**Source dependency:** Steps 037, 080, 108, 111

**Expected libraries:** Cache repository

**Original requirement:** Write only confident automatic matches to the match cache with score and verification timestamp.

#### Step 112.01: Implement accepted automatic matches

**Depends on:** Groups 037, 080, 108, 111 and Step 189.04

**Implement:** Write only confident automatic matches to the match cache with score and verification timestamp.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 112.02: Test accepted automatic matches

**Depends on:** Step 112.01 and Step 189.04

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Ambiguous and unmatched decisions do not enter the automatic cache.

**Acceptance:** Ambiguous and unmatched decisions do not enter the automatic cache.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 113: Create a manual-review update function

**Source dependency:** Steps 036–037, 080, 108

**Expected libraries:** Decision and correction repositories

**Original requirement:** Load the source track through `repositories.tracks.get(job_id, source_item_id)`, normalize it, compute `source_fingerprint`, save the Spotify-ID or skip correction under that fingerprint, and update the job decision as reviewed.

#### Step 113.01: Implement a manual-review update function

**Depends on:** Groups 036–037, 080, 108 and Step 189.04

**Implement:** Load the source track through `repositories.tracks.get(job_id, source_item_id)`, normalize it, compute `source_fingerprint`, save the Spotify-ID or skip correction under that fingerprint, and update the job decision as reviewed.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 113.02: Test a manual-review update function

**Depends on:** Step 113.01 and Step 189.04

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: The updated decision is marked reviewed; the persisted correction key equals the computed source fingerprint; the next matcher run resolves the correction before cache/search.

**Acceptance:** The updated decision is marked reviewed; the persisted correction key equals the computed source fingerprint; the next matcher run resolves the correction before cache/search.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 114: Add matching property tests

**Source dependency:** Steps 099–113

**Expected libraries:** `hypothesis`

**Original requirement:** Test score bounds, deterministic ranking, normalization invariance, and that adding an unwanted penalty cannot raise a score.

#### Step 114.01: Add score-bounds property test

**Depends on:** Groups 099–113

**Implement:** Generate valid component values and aggregate them.

**Acceptance:** Every aggregate score stays within bounds.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 114.02: Add deterministic-ranking property test

**Depends on:** Step 114.01

**Implement:** Generate candidate lists and rank them twice.

**Acceptance:** Both rankings are identical.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 114.03: Add normalization-invariance property test

**Depends on:** Step 114.02

**Implement:** Generate equivalent normalized source variants.

**Acceptance:** Equivalent normalized inputs produce equivalent comparison behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 114.04: Add penalty-monotonicity property test

**Depends on:** Step 114.03

**Implement:** Generate a base score and an additional unwanted penalty.

**Acceptance:** Adding an unwanted penalty never raises the score.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 115: Add matching regression corpus

**Source dependency:** Steps 069, 098, 106, 111, 114

**Expected libraries:** `pytest`, JSON fixtures

**Original requirement:** Add regression cases and a labeled safety benchmark that validates the frozen automatic-match policy before any write mode is accepted.

#### Step 115.01: Add official audio matching regression case

**Depends on:** Groups 069, 098, 106, 111, 114

**Implement:** Add one sanitized fixture case for `official audio` with expected status and expected Spotify ID or explicit no-selection.

**Acceptance:** The single case passes deterministically.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 115.02: Add official video matching regression case

**Depends on:** Step 115.01

**Implement:** Add one sanitized fixture case for `official video` with expected status and expected Spotify ID or explicit no-selection.

**Acceptance:** The single case passes deterministically.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 115.03: Add remix matching regression case

**Depends on:** Step 115.02

**Implement:** Add one sanitized fixture case for `remix` with expected status and expected Spotify ID or explicit no-selection.

**Acceptance:** The single case passes deterministically.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 115.04: Add live matching regression case

**Depends on:** Step 115.03

**Implement:** Add one sanitized fixture case for `live` with expected status and expected Spotify ID or explicit no-selection.

**Acceptance:** The single case passes deterministically.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 115.05: Add remaster matching regression case

**Depends on:** Step 115.04

**Implement:** Add one sanitized fixture case for `remaster` with expected status and expected Spotify ID or explicit no-selection.

**Acceptance:** The single case passes deterministically.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 115.06: Add cover matching regression case

**Depends on:** Step 115.05

**Implement:** Add one sanitized fixture case for `cover` with expected status and expected Spotify ID or explicit no-selection.

**Acceptance:** The single case passes deterministically.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 115.07: Add karaoke matching regression case

**Depends on:** Step 115.06

**Implement:** Add one sanitized fixture case for `karaoke` with expected status and expected Spotify ID or explicit no-selection.

**Acceptance:** The single case passes deterministically.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 115.08: Add duplicate title matching regression case

**Depends on:** Step 115.07

**Implement:** Add one sanitized fixture case for `duplicate title` with expected status and expected Spotify ID or explicit no-selection.

**Acceptance:** The single case passes deterministically.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 115.09: Add uncertain artist matching regression case

**Depends on:** Step 115.08

**Implement:** Add one sanitized fixture case for `uncertain artist` with expected status and expected Spotify ID or explicit no-selection.

**Acceptance:** The single case passes deterministically.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 115.10: Create labeled benchmark manifest

**Depends on:** Step 115.09

**Implement:** Create a sanitized benchmark manifest containing at least 50 manually labeled source/candidate sets, including at least 10 hard negatives and all required version/non-track categories.

**Acceptance:** Every case has a stable ID, expected auto-match/ambiguous/unmatched class, and expected selected Spotify ID or explicit no-selection.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 115.11: Compute matcher benchmark metrics

**Depends on:** Step 115.10

**Implement:** Run the frozen matching configuration over the manifest and calculate the exact integer counts and formulas defined in the labeled matcher benchmark gate: auto-match precision, unsafe-rejection recall, false confident-match rate, auto-match coverage, and eligible-positive recall. Treat every zero denominator as a failed required metric.

**Acceptance:** Repeated runs produce identical counts and metrics, every numerator/denominator is present in the report, and at least 10 cases are automatically accepted.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 115.12: Enforce matcher safety thresholds

**Depends on:** Step 115.11

**Implement:** Fail the test suite when fewer than 10 cases are automatically accepted, auto-match precision is below 0.98, unsafe-rejection recall is below 0.95, false confident-match rate exceeds 0.02, or a required denominator is zero.

**Acceptance:** A deliberately mislabeled confident false match causes the gate to fail.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 115.13: Write benchmark report

**Depends on:** Step 115.12

**Implement:** Write a deterministic JSON benchmark report containing configuration version, corpus hash, confusion counts, required metrics, and reported auto-match coverage.

**Acceptance:** The report validates, contains no provider credentials or personal account data, and changes when the corpus or matching config changes.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

## Phase 9 — Resumable transfer job runner

Compose the adapters and matcher into a deterministic, restartable transfer.

### Group 116: Create job IDs

**Source dependency:** Step 022

**Expected libraries:** `uuid`

**Original requirement:** Implement one job-ID generator and validate IDs when loading jobs.

#### Step 116.01: Implement job ids

**Depends on:** Groups 022

**Implement:** Implement one job-ID generator and validate IDs when loading jobs.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 116.02: Test job ids

**Depends on:** Step 116.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Generated IDs are unique across a large test sample and safe in filenames.

**Acceptance:** Generated IDs are unique across a large test sample and safe in filenames.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 117: Create a job from a transfer request

**Source dependency:** Steps 035, 116

**Expected libraries:** Job repository

**Original requirement:** Persist the request and initial pending state before any provider call.

#### Step 117.01: Implement a job from a transfer request

**Depends on:** Groups 035, 116 and Step 189.04

**Implement:** Persist the request and initial pending state before any provider call.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 117.02: Test a job from a transfer request

**Depends on:** Step 117.01 and Step 189.04

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: A failed later provider call still leaves a recoverable job record.

**Acceptance:** A failed later provider call still leaves a recoverable job record.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 118: Create event-emitter and cancellation interfaces

**Source dependency:** Step 023

**Expected libraries:** `typing.Protocol`, Pydantic event models

**Original requirement:** Define validated event emission and a read-only cancellation contract before orchestration stages consume either interface.

#### Step 118.01: Define `EventEmitter`

**Depends on:** Groups 023

**Implement:** Define one synchronous callback accepting only the discriminated `JobEvent` union.

**Acceptance:** Static typing rejects a callback invocation containing a non-event object.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 118.02: Test recording event emitter

**Depends on:** Step 118.01

**Implement:** Add a recording emitter fake that stores validated events in call order.

**Acceptance:** The fake captures the exact event sequence without serializing or logging.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 118.03: Define `CancellationToken`

**Depends on:** Step 118.02

**Implement:** Define the read-only protocol with `is_cancelled()` and `raise_if_cancelled()`; orchestration code must not receive direct mutation access.

**Acceptance:** A fake token satisfies static typing and a consumer cannot call a mutation method through the protocol.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 118.04: Test cancellation token fake

**Depends on:** Step 118.03

**Implement:** Add deterministic active and cancelled token fakes.

**Acceptance:** The active token returns normally and the cancelled token raises the typed cancellation error.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 119: Create the JSONL event emitter

**Source dependency:** Steps 023, 118

**Expected libraries:** `json`, `sys.stdout`

**Original requirement:** Serialize one event per line to a supplied text stream and flush after each event.

#### Step 119.01: Implement jsonl event emitter

**Depends on:** Groups 023, 118

**Implement:** Serialize one event per line to a supplied text stream and flush after each event.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 119.02: Test jsonl event emitter

**Depends on:** Step 119.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Every emitted line parses as one JSON object and no log text is mixed into stdout.

**Acceptance:** Every emitted line parses as one JSON object and no log text is mixed into stdout.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 120: Create the source-loading stage

**Source dependency:** Steps 035–036, 068, 118–119

**Expected libraries:** YouTube adapter, repositories

**Original requirement:** Update job state, load the source playlist, persist ordered tracks, and checkpoint the source count.

#### Step 120.01: Enter source-reading state

**Depends on:** Groups 035–036, 068, 118–119

**Implement:** Update the job state to reading before a provider call and emit the corresponding event.

**Acceptance:** Reloaded job state is reading.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 120.02: Load source playlist

**Depends on:** Step 120.01

**Implement:** Call the YouTube adapter complete-load method once.

**Acceptance:** The adapter result contains metadata and ordered tracks.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 120.03: Persist ordered source tracks

**Depends on:** Step 120.02

**Implement:** Bulk insert the loaded source tracks idempotently.

**Acceptance:** Rerunning does not duplicate tracks.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 120.04: Checkpoint source count

**Depends on:** Step 120.03

**Implement:** Persist the source item count and emit source completion progress.

**Acceptance:** The checkpoint equals the persisted track count.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 121: Create the per-track matching stage

**Source dependency:** Steps 036, 111, 115, 118–119

**Expected libraries:** Single-track matcher, repositories

**Original requirement:** Process exactly one unresolved track, persist its decision, increment the checkpoint, and emit one progress event.

#### Step 121.01: Load next unresolved track

**Depends on:** Groups 036, 111, 115, 118–119

**Implement:** Retrieve exactly one unresolved track in source order.

**Acceptance:** The first unresolved source position is selected.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 121.02: Match one unresolved track

**Depends on:** Step 121.01

**Implement:** Call the single-track matcher for the selected track.

**Acceptance:** The matcher is called exactly once.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 121.03: Persist one match decision

**Depends on:** Step 121.02

**Implement:** Upsert the returned decision in its own transaction.

**Acceptance:** A forced later exception does not remove the decision.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 121.04: Increment match checkpoint

**Depends on:** Step 121.03

**Implement:** Increment the persisted completed-match counter after the decision commit.

**Acceptance:** The checkpoint increases by one.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 121.05: Emit one match-progress event

**Depends on:** Step 121.04

**Implement:** Emit one validated progress event for the completed track.

**Acceptance:** The recording emitter captures exactly one new event.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 122: Create the match-loop stage

**Source dependency:** Steps 036, 118, 121

**Expected libraries:** Python standard library

**Original requirement:** Iterate unresolved tracks in source order and call the per-track stage until complete or cancelled.

#### Step 122.01: Iterate unresolved tracks in order

**Depends on:** Groups 036, 118, 121

**Implement:** Loop by repeatedly requesting the next unresolved track rather than using an in-memory index.

**Acceptance:** Processing order follows source position.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 122.02: Resume from persisted decisions

**Depends on:** Step 122.01

**Implement:** On restart, begin with the first unresolved persisted track.

**Acceptance:** Resume does not reprocess accepted tracks.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 122.03: Stop match loop on cancellation

**Depends on:** Step 122.02

**Implement:** Check the cancellation signal between tracks and exit through the documented cancellation path.

**Acceptance:** Cancellation stops before the next matcher call.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 122.04: Finish match loop when empty

**Depends on:** Step 122.03

**Implement:** Exit normally when no unresolved tracks remain.

**Acceptance:** The loop performs no extra repository query after completion beyond the terminating lookup.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 123: Create transfer-count calculation

**Source dependency:** Step 036

**Expected libraries:** Python standard library

**Original requirement:** Calculate matched, ambiguous, unmatched, unavailable, skipped, and non-track counts from persisted decisions.

#### Step 123.01: Implement transfer-count calculation

**Depends on:** Groups 036

**Implement:** Calculate matched, ambiguous, unmatched, unavailable, skipped, and non-track counts from persisted decisions.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 123.02: Test transfer-count calculation

**Depends on:** Step 123.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Counts sum to the source item count.

**Acceptance:** Counts sum to the source item count.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 124: Create dry-run completion

**Source dependency:** Steps 014, 035, 118–119, 123

**Expected libraries:** Job repository, report writer

**Original requirement:** For dry-run mode, stop before destination creation and mark the job review-required or completed according to unresolved counts.

#### Step 124.01: Block destination writes in dry-run mode

**Depends on:** Groups 014, 035, 118–119, 123

**Implement:** Return from the write path before playlist resolution or mutation.

**Acceptance:** No Spotify write method is called.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 124.02: Compute dry-run terminal state

**Depends on:** Step 124.01

**Implement:** Choose review-required when unresolved decisions exist; otherwise choose completed.

**Acceptance:** The stored state matches unresolved counts.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 124.03: Write dry-run reports

**Depends on:** Step 124.02

**Implement:** Generate the final dry-run report artifacts using persisted decisions.

**Acceptance:** The report paths exist and contain no destination mutation.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 125: Create destination-resolution logic

**Source dependency:** Steps 035, 089–092

**Expected libraries:** Spotify adapter, job repository

**Original requirement:** Resolve create, merge, or replace behavior using the destination name and any stored destination ID.

#### Step 125.01: Resolve create-mode destination

**Depends on:** Groups 035, 089–092

**Implement:** For create mode, ensure the plan creates a new playlist and does not silently reuse an existing exact-name playlist.

**Acceptance:** The create branch has an explicit outcome.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 125.02: Resolve merge-mode destination

**Depends on:** Step 125.01

**Implement:** For merge mode, select exactly one owned exact-name playlist or fail safely.

**Acceptance:** Zero and multiple matches produce explicit outcomes.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 125.03: Resolve replace-mode destination

**Depends on:** Step 125.02

**Implement:** For replace mode, select exactly one owned exact-name playlist or a stored destination ID, preserving the explicit replace mode.

**Acceptance:** The replace branch never runs without explicit replace mode.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 125.04: Reuse stored destination ID safely

**Depends on:** Step 125.03

**Implement:** When a job already has a destination ID, verify and reuse it according to the parent behavior.

**Acceptance:** Resume does not create a second destination.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 126: Create ordered accepted URI extraction

**Source dependency:** Step 036

**Expected libraries:** Repositories

**Original requirement:** Return accepted Spotify URIs in source position order while excluding unavailable, skipped, ambiguous, and unmatched items.

#### Step 126.01: Implement ordered accepted uri extraction

**Depends on:** Groups 036

**Implement:** Return accepted Spotify URIs in source position order while excluding unavailable, skipped, ambiguous, and unmatched items.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 126.02: Test ordered accepted uri extraction

**Depends on:** Step 126.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Duplicate source items remain duplicated unless a later explicit deduplication option is enabled.

**Acceptance:** Duplicate source items remain duplicated unless a later explicit deduplication option is enabled.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 127: Create destination write plan

**Source dependency:** Steps 014, 093, 125–126

**Expected libraries:** `pydantic`

**Original requirement:** Represent destination ID, mode, existing URI prefix, batches, expected final URI order, and starting checkpoint.

#### Step 127.01: Implement destination write plan

**Depends on:** Groups 014, 093, 125–126

**Implement:** Represent destination ID, mode, existing URI prefix, batches, expected final URI order, and starting checkpoint.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 127.02: Test destination write plan

**Depends on:** Step 127.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: The plan is serializable and contains no credentials.

**Acceptance:** The plan is serializable and contains no credentials.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 128: Create idempotent batch keys

**Source dependency:** Step 127

**Expected libraries:** `hashlib`

**Original requirement:** Hash canonical job ID, destination ID, batch index, and ordered URI list with SHA-256 to identify a write batch.

#### Step 128.01: Implement idempotent batch keys

**Depends on:** Groups 127

**Implement:** Hash canonical job ID, destination ID, batch index, and ordered URI list with SHA-256 to identify a write batch.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 128.02: Test idempotent batch keys

**Depends on:** Step 128.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: The same batch has the same key and reordered URIs change the key.

**Acceptance:** The same batch has the same key and reordered URIs change the key.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 129: Persist write checkpoints

**Source dependency:** Steps 035, 128

**Expected libraries:** Job repository

**Original requirement:** Record completed batch index, destination snapshot ID, and idempotent batch key after each successful write.

#### Step 129.01: Implement write checkpoints

**Depends on:** Groups 035, 128 and Step 189.04

**Implement:** Record completed batch index, destination snapshot ID, and idempotent batch key after each successful write.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 129.02: Test write checkpoints

**Depends on:** Step 129.01 and Step 189.04

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: A crash before checkpoint leaves the prior checkpoint unchanged.

**Acceptance:** A crash before checkpoint leaves the prior checkpoint unchanged.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 130: Reconcile uncertain prior writes

**Source dependency:** Steps 096, 127–129

**Expected libraries:** Spotify adapter, repositories

**Original requirement:** Before retrying an uncheckpointed batch, read destination items and determine whether the intended ordered batch is already present.

#### Step 130.01: Read destination before uncertain retry

**Depends on:** Groups 096, 127–129

**Implement:** Read the ordered destination items when the prior write may have succeeded without a checkpoint.

**Acceptance:** The adapter read occurs before any retry write.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 130.02: Locate intended batch in destination sequence

**Depends on:** Step 130.01

**Implement:** Compare the intended ordered batch at the expected position.

**Acceptance:** Exact ordered presence is detected.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 130.03: Mark already-applied batch reconciled

**Depends on:** Step 130.02

**Implement:** Advance the checkpoint without rewriting when the batch is already present.

**Acceptance:** No duplicate add call occurs.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 130.04: Retry missing batch

**Depends on:** Step 130.03

**Implement:** Leave the batch pending for normal execution when it is not present.

**Acceptance:** A missing batch is not skipped.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 131: Execute destination batches

**Source dependency:** Steps 084, 093–095, 097, 118–119, 127–130

**Expected libraries:** Spotify adapter, `tenacity` for temporary retries

**Original requirement:** Write planned batches in order, check cancellation between batches, retry temporary errors for at most 4 total attempts using provider Retry-After or 1/2/4-second fallback delays, and checkpoint each success.

#### Step 131.01: Define temporary retry policy

**Depends on:** Groups 084, 093–095, 097, 118–119, 127–130

**Implement:** Configure `tenacity` to retry only typed temporary provider failures and rate limits.

**Acceptance:** Permanent errors are excluded from retry.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 131.02: Honor provider retry timing

**Depends on:** Step 131.01

**Implement:** Use provider retry-after timing when present.

**Acceptance:** A fake rate limit waits according to supplied retry metadata.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 131.03: Write one planned batch

**Depends on:** Step 131.02

**Implement:** Call the correct append or replace primitive for the current plan and batch index.

**Acceptance:** The adapter receives the exact ordered URI batch.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 131.04: Checkpoint successful batch

**Depends on:** Step 131.03

**Implement:** Persist batch index, snapshot ID, and idempotent key immediately after success.

**Acceptance:** The checkpoint reloads with the successful batch data.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 131.05: Check cancellation between batches

**Depends on:** Step 131.04

**Implement:** Stop before starting the next batch when cancellation is set.

**Acceptance:** No later batch call occurs.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 131.06: Stop immediately on permanent error

**Depends on:** Step 131.05

**Implement:** Propagate the typed permanent error to the job boundary.

**Acceptance:** No later batch or checkpoint is performed.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 132: Create verification comparison

**Source dependency:** Steps 096, 126–127

**Expected libraries:** Python standard library

**Original requirement:** Compare expected and actual destination URI sequences and report missing, extra, reordered, and unavailable positions.

#### Step 132.01: Detect exact verification match

**Depends on:** Groups 096, 126–127

**Implement:** Return an exact-match result when expected and actual URI sequences are identical.

**Acceptance:** The exact fixture reports no mismatches.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 132.02: Detect missing destination items

**Depends on:** Step 132.01

**Implement:** Report expected positions absent from the actual sequence.

**Acceptance:** The missing-item fixture reports the correct positions.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 132.03: Detect extra destination items

**Depends on:** Step 132.02

**Implement:** Report actual positions not expected by the plan.

**Acceptance:** The extra-item fixture reports the correct positions.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 132.04: Detect reordered destination items

**Depends on:** Step 132.03

**Implement:** Report order differences for the same items.

**Acceptance:** The reorder fixture is not misclassified as exact.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 132.05: Detect unavailable/null positions

**Depends on:** Step 132.04

**Implement:** Report provider null or unavailable entries without crashing.

**Acceptance:** The unavailable fixture preserves destination position.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 133: Create destination verification stage

**Source dependency:** Steps 035, 096, 118–119, 127, 132

**Expected libraries:** Spotify adapter, job repository

**Original requirement:** Read the destination after writing, run comparison, save verification status, and emit verification events.

#### Step 133.01: Enter destination-verification state

**Depends on:** Groups 035, 096, 118–119, 127, 132

**Implement:** Persist verifying state and emit verification-start progress.

**Acceptance:** The job reloads in verifying state.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 133.02: Read final destination items

**Depends on:** Step 133.01

**Implement:** Call the Spotify adapter playlist-read method after writes finish.

**Acceptance:** The ordered actual URI list is captured.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 133.03: Compare expected and actual destination

**Depends on:** Step 133.02

**Implement:** Run the verification comparison using the persisted write plan.

**Acceptance:** The comparison result is deterministic.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 133.04: Persist verification result

**Depends on:** Step 133.03

**Implement:** Store verification success or detailed mismatch information.

**Acceptance:** The stored result reloads unchanged.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 133.05: Emit verification completion event

**Depends on:** Step 133.04

**Implement:** Emit success or mismatch progress using the validated event model.

**Acceptance:** A recording emitter receives the expected event.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 133.06: Prevent completed status on mismatch

**Depends on:** Step 133.05

**Implement:** Return the verification-failure path when comparison is not exact.

**Acceptance:** A mismatch produces a report and never marks the job completed.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 134: Create cancellation handling

**Source dependency:** Steps 035, 062, 088, 118–119, 122, 131

**Expected libraries:** `signal`, `threading.Event`

**Original requirement:** Check cancellation before source pages, each track, each search query, and each destination batch; persist cancelled status.

#### Step 134.01: Create cancellation event

**Depends on:** Groups 035, 062, 088, 118–119, 122, 131

**Implement:** Create the shared `threading.Event` or equivalent cancellation state.

**Acceptance:** The event begins unset and can be set safely.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 134.02: Register graceful signal handlers

**Depends on:** Step 134.01

**Implement:** Register supported process signals to set the cancellation event without doing provider work inside the handler.

**Acceptance:** A fake signal handler sets the event.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 134.03: Check cancellation before source pages

**Depends on:** Step 134.02

**Implement:** Add a cancellation boundary before each source-page request.

**Acceptance:** Cancellation prevents the next source-page request.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 134.04: Check cancellation before tracks and queries

**Depends on:** Step 134.03

**Implement:** Add cancellation boundaries before each track and each search query.

**Acceptance:** Cancellation prevents the next matcher/search call.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 134.05: Check cancellation before destination batches

**Depends on:** Step 134.04

**Implement:** Add a cancellation boundary before each write batch.

**Acceptance:** Cancellation prevents the next write call.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 134.06: Persist cancelled status

**Depends on:** Step 134.05

**Implement:** At the job boundary, store cancelled state and emit cancellation output.

**Acceptance:** A cancelled job resumes safely from prior checkpoints.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 135: Create failure handling

**Source dependency:** Steps 035, 056, 118–134

**Expected libraries:** Provider errors, job repository

**Original requirement:** Catch typed operational errors at the job boundary, store a safe error summary, emit a failure event, and return a non-secret result.

#### Step 135.01: Catch typed operational errors

**Depends on:** Groups 035, 056, 118–134

**Implement:** Catch only documented typed operational errors at the top-level job boundary.

**Acceptance:** An expected provider error does not escape as an unhandled exception.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 135.02: Create safe error summary

**Depends on:** Step 135.01

**Implement:** Convert the typed error into a non-secret user-facing summary.

**Acceptance:** Credential-like fixture values are absent.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 135.03: Persist failed state and error

**Depends on:** Step 135.02

**Implement:** Store failed state and the safe summary.

**Acceptance:** The job reloads as failed with the same summary.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 135.04: Emit failure event

**Depends on:** Step 135.03

**Implement:** Emit one validated failure event to the selected emitter.

**Acceptance:** JSONL stdout contains only the event object.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 135.05: Route traceback to diagnostics

**Depends on:** Step 135.04

**Implement:** Write traceback details only to stderr or the diagnostic log/report.

**Acceptance:** Traceback text never appears in JSONL stdout.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 135.06: Return non-secret failure result

**Depends on:** Step 135.05

**Implement:** Return the documented failure result and exit mapping inputs.

**Acceptance:** The result contains no token or OAuth code.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 136: Create final JSON report

**Source dependency:** Steps 022–023, 036, 123, 132–133, 135

**Expected libraries:** `json`, `pathlib`, Pydantic

**Original requirement:** Write request, playlist metadata, counts, every decision, destination information, verification result, and timestamps.

#### Step 136.01: Create final report path

**Depends on:** Groups 022–023, 036, 123, 132–133, 135

**Implement:** Choose the deterministic JSON report path under the reports directory.

**Acceptance:** The path is beneath the reports directory and safe for the job ID.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 136.02: Write request and playlist metadata

**Depends on:** Step 136.01

**Implement:** Add the transfer request and source playlist metadata sections.

**Acceptance:** Both sections validate against their schemas.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 136.03: Write counts and decisions

**Depends on:** Step 136.02

**Implement:** Add every transfer count and every persisted match decision.

**Acceptance:** The decision count equals the source item count.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 136.04: Write destination and verification data

**Depends on:** Step 136.03

**Implement:** Add destination identifiers, write-plan summary, and verification result.

**Acceptance:** The report contains the final verification status.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 136.05: Write timestamps and report references

**Depends on:** Step 136.04

**Implement:** Add lifecycle timestamps and paths to related artifacts.

**Acceptance:** All documented timestamps and report paths are present.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 136.06: Validate and redact final JSON report

**Depends on:** Step 136.05

**Implement:** Validate the document against the result-related schemas and scan for credential fields.

**Acceptance:** The report validates and contains no tokens.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 137: Create review CSV report

**Source dependency:** Steps 021, 036, 105, 108

**Expected libraries:** `csv`

**Original requirement:** Write one row for each ambiguous or unmatched source item with source metadata, candidate IDs, scores, and reason.

#### Step 137.01: Implement review csv report

**Depends on:** Groups 021, 036, 105, 108

**Implement:** Write one row for each ambiguous or unmatched source item with source metadata, candidate IDs, scores, and reason.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 137.02: Test review csv report

**Depends on:** Step 137.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: The CSV opens with stable columns and Unicode content intact.

**Acceptance:** The CSV opens with stable columns and Unicode content intact.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 138: Create the top-level run function

**Source dependency:** Steps 022, 117, 120–137

**Expected libraries:** All runtime components

**Original requirement:** Define the typed runtime dependency bundle, acquire a single-writer lease, and compose all existing stages without duplicating provider, matching, or batching logic.

#### Step 138.01: Define `RuntimeDependencies`

**Depends on:** Groups 022, 117, 120–137 and Step 189.04

**Implement:** Define a typed dataclass containing the job/track/cache repositories, source and Spotify adapters, matching configuration, UTC clock, lease owner ID, and report-path factory required by `run_transfer`; include no provider credentials directly.

**Acceptance:** A fake dependency bundle type-checks and can be constructed entirely from fake adapters/repositories.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 138.02: Create or load job at run start

**Depends on:** Step 138.01

**Implement:** Persist a new job before provider work, or load the requested existing job.

**Acceptance:** A later failure still leaves a recoverable job record.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 138.03: Acquire the job writer lease

**Depends on:** Step 138.02

**Implement:** Acquire the job lease before reading source pages, matching, or destination mutation; return a typed busy result when another live owner exists.

**Acceptance:** A second runner for the same job performs no provider call or checkpoint write.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 138.04: Run source-loading stage

**Depends on:** Step 138.03

**Implement:** Invoke the source-loading stage only when its persisted checkpoint is incomplete and heartbeat the lease at the documented interval.

**Acceptance:** A resumed completed source stage is not repeated and heartbeat uses the current lease token.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 138.05: Run matching stage

**Depends on:** Step 138.04

**Implement:** Invoke the resumable match loop until complete, review-required, failed, or cancelled; heartbeat the lease between bounded units of work.

**Acceptance:** Accepted tracks are not reprocessed and a lost lease stops before the next track.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 138.06: Apply dry-run branch

**Depends on:** Step 138.05

**Implement:** Stop before destination mutation when transfer mode is dry run.

**Acceptance:** No Spotify write method is called.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 138.07: Run destination planning and writing

**Depends on:** Step 138.06

**Implement:** Resolve the destination, create a write plan, reconcile uncertain writes, and execute pending batches by calling the existing stage functions only.

**Acceptance:** The top-level function contains no duplicate track matching or provider batching algorithm.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 138.08: Run destination verification

**Depends on:** Step 138.07

**Implement:** Invoke the verification stage after writing.

**Acceptance:** A mismatch prevents completed status.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 138.09: Generate reports and terminal state

**Depends on:** Step 138.08

**Implement:** Generate reports, persist the final state under the active lease, emit completion/review/failure/cancellation result, and return `TransferResult`.

**Acceptance:** The fake end-to-end test observes the expected event sequence and terminal state.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 138.10: Release the job lease in `finally`

**Depends on:** Step 138.09

**Implement:** Release the current lease in a `finally` boundary after success, review stop, failure, or cancellation; do not mask the original result if release reports an already-lost lease.

**Acceptance:** Every terminal path leaves no owned live lease, and another runner can subsequently acquire the job.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 139: Create the resume function

**Source dependency:** Steps 035, 117, 138

**Expected libraries:** Job repository, top-level runner

**Original requirement:** Load a non-terminal job by ID and re-enter the top-level runner from persisted state.

#### Step 139.01: Load job for resume

**Depends on:** Groups 035, 117, 138

**Implement:** Load the job by validated ID and return a distinct missing-job outcome when absent.

**Acceptance:** An unknown ID is handled explicitly.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 139.02: Return completed job without work

**Depends on:** Step 139.01

**Implement:** Return the existing result for a completed job without provider calls.

**Acceptance:** No provider write occurs.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 139.03: Resume non-terminal job

**Depends on:** Step 139.02

**Implement:** Pass a non-terminal job back into the top-level runner using persisted checkpoints.

**Acceptance:** Work begins at the first incomplete stage.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 139.04: Gate failed-job resume

**Depends on:** Step 139.03

**Implement:** Require the explicit resume flag before re-entering a failed job.

**Acceptance:** A missing flag blocks provider calls.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 139.05: Gate cancelled-job resume

**Depends on:** Step 139.04

**Implement:** Require the explicit resume flag before re-entering a cancelled job.

**Acceptance:** A missing flag blocks provider calls.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 140: Create unresolved-review rerun

**Source dependency:** Steps 113, 121–123, 127, 136, 138–139

**Expected libraries:** Repositories, single-track matcher

**Original requirement:** After corrections are applied, rematch only ambiguous and unmatched tracks and regenerate the write plan.

#### Step 140.01: Select unresolved reviewed tracks

**Depends on:** Groups 113, 121–123, 127, 136, 138–139

**Implement:** Retrieve only ambiguous and unmatched decisions eligible for rerun.

**Acceptance:** Accepted decisions are excluded.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 140.02: Apply stored manual corrections

**Depends on:** Step 140.01

**Implement:** Ensure newly stored corrections are visible to the matcher.

**Acceptance:** A corrected track returns the manual choice without search.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 140.03: Rematch unresolved tracks only

**Depends on:** Step 140.02

**Implement:** Call the single-track matcher for the selected unresolved tracks.

**Acceptance:** Previously accepted decisions remain unchanged.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 140.04: Regenerate counts and write plan

**Depends on:** Step 140.03

**Implement:** Recalculate transfer counts and create a fresh destination write plan from current accepted decisions.

**Acceptance:** The new plan reflects corrections.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

## Phase 10 — User-facing CLI

Expose deterministic commands that a person or Pi extension can invoke.

### Group 189: Define ports and the production composition root

**Source dependency:** Steps 016, 025–042, 057–140

**Expected libraries:** `typing.Protocol`, SQLAlchemy, keyring, provider factories, existing adapters

**Original requirement:** Define the missing dependency ports, concrete keyring/SQLAlchemy adapters, and production composition builders that wire the real CLI to application state and provider adapters without exposing sessions or raw credentials.

#### Step 189.01: Define `CredentialStore`

**Depends on:** Groups 013, 016, 039–041

**Implement:** Define the service-neutral credential protocol with typed save, load, and delete operations; it must not expose a concrete keyring backend.

**Acceptance:** A fake in-memory store satisfies the protocol and malformed payload errors remain typed.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 189.02: Define `AccountProfileRepository`

**Depends on:** Step 189.01 and Group 016

**Implement:** Define save, get, and list operations over `AccountProfile` without exposing SQLAlchemy sessions.

**Acceptance:** A fake repository satisfies the protocol and returns typed domain profiles.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 189.03: Define persistence repository protocols

**Depends on:** Steps 189.01–189.02 and Groups 027–037

**Implement:** Define service-neutral job, source-track, decision, match-cache, and correction repository protocols whose method signatures wrap the existing session functions. `SourceTrackRepository` must include `get(job_id, source_item_id)` for fingerprint-based review corrections.

**Acceptance:** Fake repositories satisfy every protocol without exposing a SQLAlchemy session to orchestration.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 189.04: Define supporting dependency contracts

**Depends on:** Step 189.03 and Groups 111, 117–140

**Implement:** Define `Clock`, `ReportPathFactory`, `RunnerRepositories`, `ReviewRepositories`, and `MatcherDependencies` with exact typed fields. `ReviewRepositories` must include `tracks: SourceTrackRepository`.

**Acceptance:** All previously referenced dependency names resolve from one owned module and type-check.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 189.05: Implement `KeyringCredentialStore`

**Depends on:** Steps 040–042 and 189.01

**Implement:** Implement the credential protocol with a supplied keyring backend by delegating to `save_token`, `load_token`, and `delete_token`; do not duplicate serialization or key naming.

**Acceptance:** A fake backend proves save/load/delete behavior, corruption mapping, and absence of SQLite or plaintext token storage.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 189.06: Implement `SqlAlchemyAccountProfileRepository`

**Depends on:** Steps 034.01–034.06 and 189.02

**Implement:** Implement the profile port by opening short-lived sessions and delegating to save/get/list profile functions.

**Acceptance:** Each method closes its session, commits only mutations, and returns domain profiles.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 189.07: Implement `SqlAlchemyJobRepository`

**Depends on:** Step 189.06 and Steps 035.01–035.20

**Implement:** Implement job creation, lookup, state/checkpoint/error updates, recent listing, and lease lifecycle through the existing session functions.

**Acceptance:** Lease tokens and compare-and-swap behavior remain unchanged; orchestration receives no Session object.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 189.08: Implement `SqlAlchemySourceTrackRepository`

**Depends on:** Step 189.07 and Steps 034.03–034.04

**Implement:** Implement ordered source-track replacement, ordered listing, and exact `(job_id, source_item_id)` lookup through short-lived sessions.

**Acceptance:** A rollback fixture leaves no partial track rows; ordered results preserve source position; exact lookup returns the source track or `None` without exposing a Session.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 189.09: Implement `SqlAlchemyMatchDecisionRepository`

**Depends on:** Step 189.08 and Group 036

**Implement:** Implement decision upsert and unresolved-decision lookup using the existing transaction functions.

**Acceptance:** Repeated upserts replace one decision atomically and unresolved results remain deterministic.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 189.10: Implement `SqlAlchemyMatchCacheRepository`

**Depends on:** Step 189.09 and Group 037

**Implement:** Implement verified match-cache get/upsert behavior through short-lived sessions.

**Acceptance:** Cache freshness data and selected Spotify identity round-trip unchanged.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 189.11: Implement `SqlAlchemyManualCorrectionRepository`

**Depends on:** Step 189.10 and Group 037

**Implement:** Implement manual-correction get/upsert behavior through short-lived sessions.

**Acceptance:** Manual corrections remain authoritative over automatic cache entries.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 189.12: Define `ApplicationState`

**Depends on:** Steps 189.05–189.11

**Implement:** Define an immutable typed bundle containing the engine, session factory, concrete credential store, and every repository port required by auth, matching, review, and runner code.

**Acceptance:** A complete fake or temporary-database state can be constructed without provider clients.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 189.13: Implement `initialize_application_state`

**Depends on:** Step 189.12 and Groups 011–012, 025–033

**Implement:** Create application directories, open the selected SQLite database, run backup-protected migrations, construct the keyring adapter and every SQLAlchemy repository adapter, then return `ApplicationState`.

**Acceptance:** A fresh and upgraded temporary database reach migration head; initialization is idempotent and never opens a provider browser.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 189.14: Define `AuthDependencies`

**Depends on:** Step 189.13

**Implement:** Define the minimal profile-repository and credential-store bundle used by authentication commands.

**Acceptance:** The bundle contains no provider token payload and accepts fake ports.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 189.15: Implement local dependency builders

**Depends on:** Step 189.14

**Implement:** Initialize or accept `ApplicationState`; implement `build_auth_dependencies`, `build_job_query_dependencies`, and `build_review_dependencies`. The job builder returns only the job repository. The review builder returns jobs, tracks, decisions, and corrections. Neither local builder opens provider clients or reads tokens.

**Acceptance:** Auth, jobs, and review command tests construct production dependencies without passing sessions, keyring backends, or unexplained dependency objects through the CLI.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 189.16: Define `SourceDependencies`

**Depends on:** Step 189.15 and Group 058

**Implement:** Define the authenticated source adapter plus auth ports required by inspect commands.

**Acceptance:** The bundle contains no Spotify client and can use a fake source adapter.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 189.17: Implement `build_source_dependencies`

**Depends on:** Step 189.16 and Groups 047–051, 057–068

**Implement:** Load the named YouTube profile and keychain credentials, refresh when required, create the official YouTube client, wrap it in `YouTubeSourceAdapter`, and return `SourceDependencies`.

**Acceptance:** Missing or revoked credentials produce typed auth errors; no Spotify call or browser playlist automation occurs.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 189.18: Implement `build_runtime_dependencies`

**Depends on:** Steps 138.01 and 189.13–189.17 plus Groups 043–051, 083–098, 105

**Implement:** Load both named profiles and keychain credentials, refresh credentials when required, create official provider clients/adapters, use the concrete repositories and `matching_config_v1`, create a UTC clock, lease-owner ID, and report-path factory, and return `RuntimeDependencies`.

**Acceptance:** A temporary-state test constructs the full bundle with fake provider factories; missing auth fails before any destination write.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 189.19: Implement `build_runtime_dependencies_for_job`

**Depends on:** Step 189.18 and Group 035

**Implement:** Load the job from `ApplicationState.jobs`, read its stored source and Spotify profile aliases, and delegate to `build_runtime_dependencies`.

**Acceptance:** Unknown jobs fail before provider access; resumed jobs use the same named profiles and concrete repositories as their original run.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 189.20: Test the production composition root

**Depends on:** Step 189.19

**Implement:** Using a temporary SQLite database, fake keyring backend, and fake provider client factories, call the auth, jobs, review, source, runtime, and resume builders and then invoke a dry-run transfer through the same dependency path used by the CLI.

**Acceptance:** The test reaches the runner, lists and shows the recorded job through `build_job_query_dependencies`, loads review repositories including source tracks, returns reports, performs no destination write in dry run, and exposes no Session or token payload at the CLI boundary.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 141: Create the `auth spotify` command

**Source dependency:** Steps 034, 045, 052, 153

**Expected libraries:** `typer`, Spotify auth function

**Original requirement:** Accept a profile name, run interactive Spotify auth, save profile identity, and print a safe success message.

#### Step 141.01: Declare `auth spotify` command signature

**Depends on:** Groups 034, 045, 052, 153

**Implement:** Accept a profile name

**Acceptance:** Typer help shows the documented arguments and options.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 141.02: Implement `auth spotify` command behavior

**Depends on:** Step 141.01 and Step 189.15

**Implement:** Call `build_auth_dependencies()`, then pass its profile repository and credential store to the Spotify interactive-auth function with the requested profile name.

**Acceptance:** A fake composition builder is called once and its ports receive the expected profile and OAuth settings.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 141.03: Implement `auth spotify` output and errors

**Depends on:** Step 141.02

**Implement:** Format the documented human/JSON success output and map typed failures without exposing secrets.

**Acceptance:** Output is deterministic and diagnostics use stderr.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 141.04: Test `auth spotify` command

**Depends on:** Step 141.03

**Implement:** Add focused `CliRunner` tests for the command. The command never prints access or refresh tokens.

**Acceptance:** The command never prints access or refresh tokens.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 142: Create the `auth youtube` command

**Source dependency:** Steps 034, 047–052, 153

**Expected libraries:** `typer`, Google auth function

**Original requirement:** Accept a profile name and client-secret path, run interactive Google auth, save profile identity, and print success.

#### Step 142.01: Declare `auth youtube` command signature

**Depends on:** Groups 034, 047–052, 153

**Implement:** Accept a profile name and client-secret path

**Acceptance:** Typer help shows the documented arguments and options.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 142.02: Implement `auth youtube` command behavior

**Depends on:** Step 142.01 and Step 189.15

**Implement:** Call `build_auth_dependencies()`, load the Google settings from the client-secret path, and pass the resulting auth ports to the Google interactive-auth function.

**Acceptance:** A fake composition builder is called once and its ports receive the expected profile and Google settings.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 142.03: Implement `auth youtube` output and errors

**Depends on:** Step 142.02

**Implement:** Format the documented human/JSON success output and map typed failures without exposing secrets.

**Acceptance:** Output is deterministic and diagnostics use stderr.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 142.04: Test `auth youtube` command

**Depends on:** Step 142.03

**Implement:** Add focused `CliRunner` tests for the command. A failed callback exits nonzero with a concise error.

**Acceptance:** A failed callback exits nonzero with a concise error.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 143: Create the `auth status` command

**Source dependency:** Steps 034, 053, 153

**Expected libraries:** `typer`

**Original requirement:** Show all profiles or one selected profile in human-readable or JSON form.

#### Step 143.01: Declare `auth status` command signature

**Depends on:** Groups 034, 053, 153

**Implement:** Accept optional service/profile selection

**Acceptance:** Typer help shows the documented arguments and options.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 143.02: Implement `auth status` command behavior

**Depends on:** Step 143.01 and Step 189.15

**Implement:** Call `build_auth_dependencies()` and pass its ports to auth-status aggregation without interactive auth.

**Acceptance:** A fake dependency receives the expected arguments.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 143.03: Implement `auth status` output and errors

**Depends on:** Step 143.02

**Implement:** Format the documented human/JSON success output and map typed failures without exposing secrets.

**Acceptance:** Output is deterministic and diagnostics use stderr.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 143.04: Test `auth status` command

**Depends on:** Step 143.03

**Implement:** Add focused `CliRunner` tests for the command. Status mode performs no interactive auth.

**Acceptance:** Status mode performs no interactive auth.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 144: Create the `auth logout` command

**Source dependency:** Steps 034, 054, 153

**Expected libraries:** `typer`

**Original requirement:** Delete one profile token after explicit confirmation unless `--yes` is supplied.

#### Step 144.01: Declare `auth logout` command signature

**Depends on:** Groups 034, 054, 153

**Implement:** Accept service/profile and `--yes`; otherwise request explicit confirmation before logout..

**Acceptance:** Typer help shows the documented arguments and options.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 144.02: Implement `auth logout` command behavior

**Depends on:** Step 144.01 and Step 189.15

**Implement:** Accept service/profile and `--yes`; otherwise request explicit confirmation before logout.

**Acceptance:** A fake dependency receives the expected arguments.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 144.03: Implement `auth logout` output and errors

**Depends on:** Step 144.02

**Implement:** Format the documented human/JSON success output and map typed failures without exposing secrets.

**Acceptance:** Output is deterministic and diagnostics use stderr.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 144.04: Test `auth logout` command

**Depends on:** Step 144.03

**Implement:** Add focused `CliRunner` tests for the command. The command reports the retained non-secret profile record.

**Acceptance:** The command reports the retained non-secret profile record.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 145: Create the `inspect youtube` command

**Source dependency:** Steps 057–068, 153

**Expected libraries:** `typer`, YouTube adapter

**Original requirement:** Load playlist metadata and print item counts plus a bounded sample without matching or Spotify access.

#### Step 145.01: Declare `inspect youtube` command signature

**Depends on:** Groups 057–068, 153

**Implement:** Accept a YouTube URL/profile.

**Acceptance:** Typer help shows the documented arguments and options.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 145.02: Implement `inspect youtube` command behavior

**Depends on:** Step 145.01 and Step 189.17

**Implement:** Call `build_source_dependencies(source_profile)`, then load playlist metadata and a bounded item sample through its `SourceAdapter` without Spotify access.

**Acceptance:** A fake dependency receives the expected arguments.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 145.03: Implement `inspect youtube` output and errors

**Depends on:** Step 145.02

**Implement:** Format the documented human/JSON success output and map typed failures without exposing secrets.

**Acceptance:** Output is deterministic and diagnostics use stderr.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 145.04: Test `inspect youtube` command

**Depends on:** Step 145.03

**Implement:** Add focused `CliRunner` tests for the command. The command performs no matching or Spotify call.

**Acceptance:** The command performs no matching or Spotify call.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 146: Create the `transfer` command arguments

**Source dependency:** Steps 014, 022, 153

**Expected libraries:** `typer`, Pydantic

**Original requirement:** Accept source URL, source profile, destination profile, destination name, mode, match policy, visibility, output mode, and optional job ID.

#### Step 146.01: Add transfer source arguments

**Depends on:** Groups 014, 022, 153

**Implement:** Add source URL and source-profile parameters to the `transfer` command.

**Acceptance:** Typer help and parsing expose both values.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 146.02: Add transfer destination arguments

**Depends on:** Step 146.01

**Implement:** Add destination profile and destination name parameters.

**Acceptance:** Typer help and parsing expose both values.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 146.03: Add transfer mode and policy options

**Depends on:** Step 146.02

**Implement:** Add typed transfer mode and match-policy options.

**Acceptance:** Invalid enum values are rejected before provider calls.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 146.04: Add visibility and output options

**Depends on:** Step 146.03

**Implement:** Add visibility and machine/human output options.

**Acceptance:** Each documented output mode parses.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 146.05: Add optional transfer job ID

**Depends on:** Step 146.04

**Implement:** Add the optional job-ID parameter using the existing validator.

**Acceptance:** An invalid job ID is rejected before provider calls.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 147: Connect `transfer` to the job runner

**Source dependency:** Steps 138, 146, 153–154

**Expected libraries:** `typer`, job runner

**Original requirement:** Construct `TransferRequest`, choose JSONL or human event emitter, invoke the top-level runner, and return mapped exit codes.

#### Step 147.01: Construct `TransferRequest` in CLI

**Depends on:** Groups 138, 146, 153–154

**Implement:** Construct `TransferRequest` using only the frozen names: `source_url=source_url`, `source_profile=source_profile`, `spotify_profile=spotify_profile`, `destination_name=destination_name`, `mode=mode`, `match_policy=policy`, and `public=public`. Do not pass output mode or job ID into the request model.

**Acceptance:** A fake runner receives a request with exactly the seven frozen fields; CLI `policy` maps to `match_policy`, and visibility maps to `public` without extra aliases.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 147.02: Select transfer event emitter

**Depends on:** Step 147.01

**Implement:** Choose JSONL or human emitter from the output option.

**Acceptance:** JSONL mode selects the JSONL emitter.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 147.03: Invoke top-level transfer runner

**Depends on:** Step 147.02 and Step 189.18

**Implement:** Call `build_runtime_dependencies(request.source_profile, request.spotify_profile)` exactly once, then call the top-level run function exactly once with the returned bundle.

**Acceptance:** The fake composition builder and fake runner are each called once; no dependency object is accepted as a CLI argument.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 147.04: Map transfer result to exit code

**Depends on:** Step 147.03

**Implement:** Translate the typed result into the stable CLI exit code.

**Acceptance:** Each result category maps to the documented code.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 148: Create the `resume` command

**Source dependency:** Steps 139, 146, 153–154

**Expected libraries:** `typer`, job runner

**Original requirement:** Accept a job ID and resume flag, invoke the resume function, and preserve JSONL output behavior.

#### Step 148.01: Declare `resume` command signature

**Depends on:** Groups 139, 146, 153–154

**Implement:** Accept a validated job ID, explicit resume flag, and output mode.

**Acceptance:** Typer help shows the arguments.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 148.02: Invoke resume function

**Depends on:** Step 148.01 and Step 189.19

**Implement:** Call `build_runtime_dependencies_for_job(job_id)` and pass the resulting bundle plus parsed flags to the resume function.

**Acceptance:** The fake job composition builder and resume function receive exact values, and no dependency object is accepted from command input.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 148.03: Preserve JSONL behavior in resume

**Depends on:** Step 148.02

**Implement:** Use the JSONL emitter and stdout rules when requested.

**Acceptance:** Every stdout line parses as JSON.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 148.04: Map resume outcomes to exit codes

**Depends on:** Step 148.03

**Implement:** Return distinct codes for unknown, terminal, blocked, and resumed outcomes.

**Acceptance:** Unknown and terminal job IDs receive distinct exit codes.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 149: Create the `jobs list` command

**Source dependency:** Steps 035, 153

**Expected libraries:** `typer`, job repository

**Original requirement:** Print recent jobs with ID, state, source title, destination name, counts, and updated time.

#### Step 149.01: Load recent jobs for CLI

**Depends on:** Groups 035, 153

**Implement:** Call `build_job_query_dependencies()` and then `dependencies.jobs.list_recent(limit)`; no Session or repository object is accepted as a CLI parameter.

**Acceptance:** The repository receives the exact limit.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 149.02: Render human jobs list

**Depends on:** Step 149.01

**Implement:** Print ID, state, source title, destination name, counts, and updated time in stable columns.

**Acceptance:** The human output contains all required fields.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 149.03: Render JSON jobs list

**Depends on:** Step 149.02

**Implement:** Define and emit one stable JSON schema for recent jobs.

**Acceptance:** The JSON output parses and matches the schema.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 150: Create the `jobs show` command

**Source dependency:** Steps 035, 123, 136–137, 153

**Expected libraries:** `typer`, repositories

**Original requirement:** Print one job request, checkpoints, counts, reports, and safe error details.

#### Step 150.01: Load one job for CLI

**Depends on:** Groups 035, 123, 136–137, 153

**Implement:** Call `build_job_query_dependencies()`, pass the returned bundle to `load_job_for_cli`, and load the requested job plus related persisted summaries; return the typed not-found error when absent.

**Acceptance:** The missing-job outcome is explicit.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 150.02: Render job request and checkpoints

**Depends on:** Step 150.01

**Implement:** Print the stored request and checkpoint fields.

**Acceptance:** The displayed values match persistence.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 150.03: Render job counts and reports

**Depends on:** Step 150.02

**Implement:** Print counts and report paths.

**Acceptance:** Every existing report path is included.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 150.04: Render safe job error details

**Depends on:** Step 150.03

**Implement:** Print only the safe stored error summary.

**Acceptance:** No credential material appears.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 151: Create the `review list` command

**Source dependency:** Steps 036, 108, 137, 153

**Expected libraries:** `typer`, repositories

**Original requirement:** Show unresolved tracks and ranked alternatives for a job.

#### Step 151.01: Load unresolved review decisions

**Depends on:** Groups 036, 108, 137, 153

**Implement:** Call `build_review_dependencies()`, then retrieve unresolved decisions and their source tracks/ranked alternatives for the job through the returned repositories.

**Acceptance:** Only unresolved items are returned.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 151.02: Render one review item

**Depends on:** Step 151.01 and Step 189.13

**Implement:** Format source metadata, alternatives, scores, and reasons for one item.

**Acceptance:** The output contains the required decision context.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 151.03: Render review list in source order

**Depends on:** Step 151.02

**Implement:** Apply the one-item renderer to all unresolved items in source position order.

**Acceptance:** Results are ordered by source position.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 152: Create the `review apply` command

**Source dependency:** Steps 113, 153

**Expected libraries:** `typer`, manual-review function

**Original requirement:** Accept job ID, source item ID, and either Spotify track ID or skip; save the correction.

#### Step 152.01: Declare `review apply` arguments

**Depends on:** Groups 113, 153

**Implement:** Accept job ID, source item ID, optional Spotify track ID, and explicit skip option.

**Acceptance:** Typer help shows all values.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 152.02: Validate review choice exclusivity

**Depends on:** Step 152.01

**Implement:** Reject neither-choice and both-choice inputs before repository writes.

**Acceptance:** The fake repository sees no call for invalid combinations.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 152.03: Apply manual review correction

**Depends on:** Step 152.02 and Step 189.04 and Step 189.13

**Implement:** Call `build_review_dependencies()`, then call the manual-review update function with the validated choice. The function must load the source track and persist the correction by `source_fingerprint`, not by mutable playlist position or raw title.

**Acceptance:** The correction is saved and the decision is marked reviewed.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 153: Create CLI exit-code constants

**Source dependency:** Steps 015, 022, 056, 135

**Expected libraries:** Python standard library

**Original requirement:** Define stable codes for success, review required, authentication required, invalid input, provider failure, verification failure, and cancellation.

#### Step 153.01: Implement cli exit-code constants

**Depends on:** Groups 015, 022, 056, 135

**Implement:** Define stable codes for success, review required, authentication required, invalid input, provider failure, verification failure, and cancellation.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 153.02: Test cli exit-code constants

**Depends on:** Step 153.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Command tests assert the correct code for each typed result.

**Acceptance:** Command tests assert the correct code for each typed result.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 154: Separate stdout and stderr

**Source dependency:** Steps 119, 153

**Expected libraries:** `logging`, `typer`

**Original requirement:** Reserve stdout for selected machine-readable output and send diagnostics to stderr.

#### Step 154.01: Implement stdout and stderr

**Depends on:** Groups 119, 153

**Implement:** Reserve stdout for selected machine-readable output and send diagnostics to stderr.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 154.02: Test stdout and stderr

**Depends on:** Step 154.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: A JSONL test parses every stdout line even when warnings are emitted.

**Acceptance:** A JSONL test parses every stdout line even when warnings are emitted.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 155: Add CLI integration tests

**Source dependency:** Steps 141–154

**Expected libraries:** `pytest`, `CliRunner`, fake adapters

**Original requirement:** Cover auth status, inspect, dry run, successful transfer, review required, resume, and provider failure.

#### Step 155.01: Add auth-status CLI integration test

**Depends on:** Groups 141–154

**Implement:** Run `auth status` with fake credential state.

**Acceptance:** The expected human and JSON outputs pass.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 155.02: Add inspect CLI integration test

**Depends on:** Step 155.01

**Implement:** Run `inspect youtube` with a fake YouTube adapter.

**Acceptance:** No matching or Spotify dependency is called.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 155.03: Add dry-run CLI integration test

**Depends on:** Step 155.02

**Implement:** Run a complete fake dry run.

**Acceptance:** No destination write occurs.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 155.04: Add successful-transfer CLI integration test

**Depends on:** Step 155.03

**Implement:** Run a complete fake create transfer.

**Acceptance:** The command exits success with report paths.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 155.05: Add review-required CLI integration test

**Depends on:** Step 155.04

**Implement:** Return ambiguous decisions from the fake runner.

**Acceptance:** The command exits with review-required code.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 155.06: Add resume CLI integration test

**Depends on:** Step 155.05

**Implement:** Resume a fake interrupted job.

**Acceptance:** The persisted checkpoint is respected.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 155.07: Add provider-failure CLI integration test

**Depends on:** Step 155.06

**Implement:** Raise a typed fake provider failure.

**Acceptance:** The command returns the provider-failure code and safe stderr.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

## Phase 11 — Pi extension

Wrap the CLI in typed Pi tools without allowing arbitrary shell execution.

### Group 190: Define TypeScript boundary types

**Source dependency:** Steps 023, 156–157

**Expected libraries:** TypeScript, TypeBox test fixtures

**Original requirement:** Own every Pi-extension tool input, result, event, invocation, process-result, and dependency type in one module before process and tool implementations consume them.

#### Step 190.01: Define tool input types

**Depends on:** Groups 014, 156–157

**Implement:** Define the tool-name discriminant and exact auth, transfer, review-list, review-apply, review-union, and overall typed-input union in `extension/types.ts`. `PlaylistAuthInput` includes required `action`; `PlaylistTransferInput` includes optional `visibility` and optional defaulted `mode`/`policy`.

**Acceptance:** Every supported variant narrows by its discriminant and unknown actions fail type checking.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 190.02: Define event, result, invocation, and dependency types

**Depends on:** Step 190.01 and Group 023

**Implement:** Define the JSONL event, auth/transfer/review result, `CliInvocation`, `ProcessResult`, and `ExtensionDependencies` types in the same module.

**Acceptance:** The public process signatures compile using only these named types.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 190.03: Test boundary-type and schema alignment

**Depends on:** Step 190.02

**Implement:** Add compile-time fixtures for every valid and invalid authoritative tool-input variant. These fixtures are consumed by the later schema dispatches; do not import schemas that have not been created yet.

**Acceptance:** Type checking passes, valid fixtures satisfy the exact input types, and invalid action/visibility fixtures are rejected by TypeScript. Runtime schema parity is verified when Steps 164.04 and 166.05 create the schemas.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 156: Create the extension package manifest and lockfile

**Source dependency:** Steps 001, 004

**Expected libraries:** `@earendil-works/pi-coding-agent`, `typebox`, TypeScript, npm lockfile

**Original requirement:** Create `extension/package.json`, scripts, and a committed `package-lock.json` verified with `npm ci`.

#### Step 156.01: Create extension package metadata

**Depends on:** Groups 001, 004

**Implement:** Create `extension/package.json` with package name, private/package settings, and supported module configuration.

**Acceptance:** `npm` parses the manifest.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 156.02: Declare extension runtime dependencies

**Depends on:** Step 156.01

**Implement:** Add Pi coding-agent and TypeBox runtime dependencies.

**Acceptance:** Dependency names and version constraints are present without unrelated packages.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 156.03: Declare extension development dependencies

**Depends on:** Step 156.02

**Implement:** Add TypeScript and the chosen test tooling.

**Acceptance:** The development dependency table parses.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 156.04: Add extension typecheck script

**Depends on:** Step 156.03

**Implement:** Add the package script for TypeScript type checking.

**Acceptance:** `npm run typecheck` resolves.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 156.05: Add extension test script

**Depends on:** Step 156.04

**Implement:** Add the package script for extension unit tests.

**Acceptance:** `npm test` resolves.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 156.06: Generate `extension/package-lock.json`

**Depends on:** Step 156.05

**Implement:** Generate and commit the npm lockfile from the manifest without editing generated entries manually.

**Acceptance:** The lockfile uses the current lockfile format and contains the declared direct dependencies.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 156.07: Verify clean `npm ci`

**Depends on:** Step 156.06

**Implement:** Remove the local dependency directory and install using `npm ci`.

**Acceptance:** Installation succeeds and produces no manifest or lockfile diff.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 157: Create the extension entry point

**Source dependency:** Step 156

**Expected libraries:** `@earendil-works/pi-coding-agent`

**Original requirement:** Export one default extension factory from `extension/index.ts`.

#### Step 157.01: Implement extension entry point

**Depends on:** Groups 156

**Implement:** Export one default extension factory from `extension/index.ts`.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 157.02: Test extension entry point

**Depends on:** Step 157.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Pi can load the extension with `-e` without registering tools yet.

**Acceptance:** Pi can load the extension with `-e` without registering tools yet.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 158: Locate the CLI executable

**Source dependency:** Steps 006, 156–157

**Expected libraries:** `node:fs`, `node:path`, `node:process`

**Original requirement:** Implement a deterministic lookup using explicit configuration first and known installation paths second; do not search arbitrary PATH entries silently.

#### Step 158.01: Read explicit CLI executable configuration

**Depends on:** Groups 006, 156–157 and Step 190.03

**Implement:** Return the configured executable path when present.

**Acceptance:** The configured-path test returns the exact path.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 158.02: Validate configured executable

**Depends on:** Step 158.01 and Step 190.03

**Implement:** Check that the configured path exists, is a file, and is executable.

**Acceptance:** A non-executable path produces the typed missing/unusable result.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 158.03: Check known installation paths

**Depends on:** Step 158.02 and Step 190.03

**Implement:** When no explicit path is configured, check only the documented known installation paths in deterministic order.

**Acceptance:** The first valid known path is returned.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 158.04: Reject silent arbitrary PATH search

**Depends on:** Step 158.03 and Step 190.03

**Implement:** Do not fall back to an unbounded PATH lookup.

**Acceptance:** A test places a fake binary only on PATH and confirms it is not selected.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 158.05: Handle missing executable

**Depends on:** Step 158.04 and Step 190.03

**Implement:** Return the documented actionable error when no valid path exists.

**Acceptance:** The missing-executable test contains the configuration hint.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 159: Build safe CLI argument arrays

**Source dependency:** Steps 146, 148–153

**Expected libraries:** TypeScript standard library

**Original requirement:** Implement pure functions mapping typed tool parameters to an executable plus argument array.

#### Step 159.01: Implement `build_auth_args`

**Depends on:** Groups 146, 148–153 and Step 190.03

**Implement:** Map the required auth `action`, provider, profile, and allowed client-secret path to the corresponding literal CLI subcommand argument array.

**Acceptance:** `build_auth_args` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 159.02: Test `build_auth_args`

**Depends on:** Step 159.01 and Step 190.03

**Implement:** Add one focused test for `build_auth_args`. Login/status/logout fixtures produce distinct literal arrays; invalid action/path combinations fail; no shell command string is returned.

**Acceptance:** Login/status/logout fixtures produce distinct literal arrays; invalid action/path combinations fail; no shell command string is returned.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 159.03: Implement `build_transfer_args`

**Depends on:** Step 159.02 and Step 190.03

**Implement:** Map typed transfer parameters to executable and literal arguments, applying defaults `mode=dry_run`, `policy=balanced`, and `visibility=private` when omitted. Translate visibility to the CLI public/private option without renaming the TypeScript field.

**Acceptance:** `build_transfer_args` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 159.04: Test `build_transfer_args`

**Depends on:** Step 159.03 and Step 190.03

**Implement:** Add one focused test for `build_transfer_args`. Replace mode and public visibility remain explicit arguments; omitted defaults produce dry-run, balanced, and private arguments.

**Acceptance:** Replace mode and public visibility remain explicit arguments; omitted defaults produce dry-run, balanced, and private arguments.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 159.05: Implement `build_review_args`

**Depends on:** Step 159.04 and Step 190.03

**Implement:** Map typed review parameters to executable and literal argument array.

**Acceptance:** `build_review_args` imports or type-checks and changes no unrelated behavior.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 159.06: Test `build_review_args`

**Depends on:** Step 159.05 and Step 190.03

**Implement:** Add one focused test for `build_review_args`. Track IDs and skip remain distinct literal arguments.

**Acceptance:** Track IDs and skip remain distinct literal arguments.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 159.07: Implement `buildCliInvocation`

**Depends on:** Step 159.06 and Step 190.03

**Implement:** Route the `TypedToolInput` union to `build_auth_args`, `build_transfer_args`, or `build_review_args`; resolve the executable and return the exact `CliInvocation` fields `executable`, `args`, `cwd`, and bounded `env`.

**Acceptance:** All three tool-input variants produce literal argument arrays, unknown input variants fail with `InputValidationError`, and no shell command string is produced.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 160: Spawn without a shell

**Source dependency:** Steps 158–159

**Expected libraries:** `node:child_process.spawn`

**Original requirement:** Implement a process runner with `shell: false`, bounded environment variables, separate stdout/stderr, and explicit working directory.

#### Step 160.01: Create bounded child environment

**Depends on:** Groups 158–159 and Step 190.03

**Implement:** Build the explicit child environment allowlist/overrides.

**Acceptance:** Unapproved parent variables are absent.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 160.02: Configure child working directory

**Depends on:** Step 160.01 and Step 190.03

**Implement:** Set the explicit working directory used by the runtime process.

**Acceptance:** A fake child observes the documented directory.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 160.03: Spawn with `shell: false`

**Depends on:** Step 160.02 and Step 190.03

**Implement:** Call `node:child_process.spawn` with the executable and argument array, setting `shell: false`.

**Acceptance:** Metacharacters remain literal arguments.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 160.04: Capture stdout separately

**Depends on:** Step 160.03 and Step 190.03

**Implement:** Expose or collect child stdout without mixing stderr.

**Acceptance:** A fake child’s stdout is captured exactly.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 160.05: Capture stderr separately

**Depends on:** Step 160.04 and Step 190.03

**Implement:** Expose or collect child stderr without mixing stdout.

**Acceptance:** A fake child’s stderr is captured exactly.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 160.06: Implement `runCliProcess`

**Depends on:** Step 160.05, Step 161.05, Step 162.05, Step 163.04, and Step 190.03

**Implement:** Call `spawnCli`; connect `JsonlEventParser`; capture bounded stdout/stderr; attach `AbortSignal` cancellation; await child completion; and return `ProcessResult` without duplicating the private helper logic.

**Acceptance:** A fixture child stream produces parsed events and bounded diagnostics, cancellation terminates the child, and the returned `ProcessResult` matches the frozen contract.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 161: Parse JSONL progress

**Source dependency:** Steps 023, 119, 153

**Expected libraries:** TypeScript, `JSON.parse`

**Original requirement:** Buffer partial stdout chunks, split complete lines, validate event type fields, and retain a trailing partial line.

#### Step 161.01: Buffer incoming stdout chunks

**Depends on:** Groups 023, 119, 153 and Step 190.03

**Implement:** Append each stdout chunk to an internal text buffer.

**Acceptance:** Partial data is retained.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 161.02: Split complete JSONL lines

**Depends on:** Step 161.01 and Step 190.03

**Implement:** Extract only newline-terminated records from the buffer.

**Acceptance:** Multiple lines in one chunk are emitted separately.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 161.03: Parse and validate event type

**Depends on:** Step 161.02 and Step 190.03

**Implement:** Parse each complete line and reject records without a supported `type`.

**Acceptance:** Valid events are returned and malformed events produce the typed parse error.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 161.04: Retain trailing partial line

**Depends on:** Step 161.03 and Step 190.03

**Implement:** Keep the final incomplete fragment for the next chunk.

**Acceptance:** A split event reconstructs after the next chunk.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 161.05: Flush final complete fragment

**Depends on:** Step 161.04 and Step 190.03

**Implement:** At process end, parse a final non-empty complete JSON object or return a clear trailing-data error.

**Acceptance:** Chunk-boundary tests reconstruct events correctly.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 162: Connect Pi cancellation

**Source dependency:** Steps 134, 160–161

**Expected libraries:** `AbortSignal`, Node child process

**Original requirement:** On abort, send a graceful termination signal, wait briefly, then force termination if required.

#### Step 162.01: Listen to Pi `AbortSignal`

**Depends on:** Groups 134, 160–161 and Step 190.03

**Implement:** Register one abort listener for the running child process.

**Acceptance:** Triggering abort starts cancellation once.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 162.02: Send graceful termination signal

**Depends on:** Step 162.01 and Step 190.03

**Implement:** Send the selected graceful signal when abort fires.

**Acceptance:** A fake child records the graceful signal.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 162.03: Wait bounded grace period

**Depends on:** Step 162.02 and Step 190.03

**Implement:** Wait only the documented bounded period for child exit.

**Acceptance:** The timer is cancellable when the child exits.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 162.04: Force terminate remaining child

**Depends on:** Step 162.03 and Step 190.03

**Implement:** Send the forceful termination signal only if the child remains alive after the grace period.

**Acceptance:** A stubborn test child exits.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 162.05: Verify no orphan process

**Depends on:** Step 162.04 and Step 190.03

**Implement:** Add a test that confirms the child is gone after cancellation.

**Acceptance:** No orphan remains.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 163: Bound and truncate process output

**Source dependency:** Steps 136–137, 160–161

**Expected libraries:** Pi truncation utilities

**Original requirement:** Keep at most 65536 bytes of progress/summary output in memory, write full diagnostics to a report file, and apply Pi's exported truncation helpers to returned text.

#### Step 163.01: Store bounded progress summaries

**Depends on:** Groups 136–137, 160–161 and Step 190.03

**Implement:** Keep only the compact progress state required for Pi updates.

**Acceptance:** Memory usage does not grow with every raw output line.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 163.02: Write full diagnostics to report file

**Depends on:** Step 163.01 and Step 190.03

**Implement:** Stream or append full diagnostic output to the documented report path.

**Acceptance:** The report contains the untruncated diagnostics.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 163.03: Apply Pi truncation helper

**Depends on:** Step 163.02 and Step 190.03

**Implement:** Apply Pi’s exported truncation utility to returned text.

**Acceptance:** Oversized text returns a truncation notice.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 163.04: Return valid diagnostic report path

**Depends on:** Step 163.03 and Step 190.03

**Implement:** Include the report path whenever returned text was truncated.

**Acceptance:** The path exists and is readable.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 164: Define the `playlist_auth` tool schema

**Source dependency:** Steps 013, 141–142, 156–157

**Expected libraries:** `typebox`

**Original requirement:** Accept service and profile name, plus optional Google client-secret path; reject unknown services and blank profile names.

#### Step 164.01: Define `playlist_auth` service field

**Depends on:** Groups 013, 141–142, 156–157 and Step 190.03

**Implement:** Add required `action` (`login`, `status`, or `logout`) and required `service` (`youtube` or `spotify`) fields exactly matching `PlaylistAuthInput`.

**Acceptance:** Missing/unknown actions and unknown services are rejected; valid action/service pairs type-check.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 164.02: Define `playlist_auth` profile field

**Depends on:** Step 164.01 and Step 190.03

**Implement:** Add the required non-blank profile-name field.

**Acceptance:** Blank profile names are rejected.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 164.03: Define optional Google client-secret path

**Depends on:** Step 164.02 and Step 190.03

**Implement:** Add the optional path field used only for YouTube auth.

**Acceptance:** Valid YouTube input accepts the path.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 164.04: Add cross-field auth schema validation

**Depends on:** Step 164.03 and Step 190.03

**Implement:** Reject provider/action/path combinations not allowed by the parent plan: `clientSecretPath` is permitted only for YouTube `login`; status/logout and Spotify reject it.

**Acceptance:** Missing or unknown auth actions fail; Spotify and non-login actions do not require or consume a Google path. Focused schema tests accept every valid `PlaylistAuthInput` fixture and reject the invalid fixtures from Step 190.03.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 165: Implement the `playlist_auth` tool

**Source dependency:** Steps 141–144, 160–164

**Expected libraries:** Pi `registerTool`, process runner

**Original requirement:** Run the corresponding CLI auth command, stream a waiting-for-browser update, and return safe account identity results.

#### Step 165.01: Map auth tool input to CLI args

**Depends on:** Groups 141–144, 160–164 and Step 190.03

**Implement:** Use the safe argument builder for the requested action and provider: login maps to provider auth, status maps to auth status, and logout maps to provider logout using literal arguments.

**Acceptance:** The expected literal argument array is produced.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 165.02: Launch auth CLI process

**Depends on:** Step 165.01 and Step 190.03

**Implement:** Run the process through the shell-free runner.

**Acceptance:** No arbitrary shell string is constructed.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 165.03: Stream waiting-for-browser update

**Depends on:** Step 165.02 and Step 190.03

**Implement:** Send one bounded Pi update only while a `login` action is waiting for official provider browser authorization; status and logout never emit a browser-wait update.

**Acceptance:** The fake context records the update.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 165.04: Parse safe account identity result

**Depends on:** Step 165.03 and Step 190.03

**Implement:** Return provider user ID/display name and status only.

**Acceptance:** No token field is returned.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 165.05: Redact child auth output

**Depends on:** Step 165.04 and Step 190.03

**Implement:** Apply token/code redaction to all returned child text.

**Acceptance:** Token fixture strings do not appear in the tool result.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 166: Define the `playlist_transfer` tool schema

**Source dependency:** Steps 014, 146, 156–157

**Expected libraries:** `typebox`, Pi `StringEnum` if needed

**Original requirement:** Accept source URL, account profiles, destination name, mode, policy, and visibility with conservative defaults.

#### Step 166.01: Define transfer source fields

**Depends on:** Groups 014, 146, 156–157 and Step 190.03

**Implement:** Add source URL and source-profile fields.

**Acceptance:** Valid values pass schema validation.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 166.02: Define transfer destination fields

**Depends on:** Step 166.01 and Step 190.03

**Implement:** Add destination profile and destination name fields.

**Acceptance:** Blank destination names are rejected.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 166.03: Define explicit transfer mode

**Depends on:** Step 166.02 and Step 190.03

**Implement:** Add optional typed `dry_run`, `create`, `merge`, and `replace` values; omission is normalized to `dry_run` before CLI argument construction.

**Acceptance:** All four modes type-check; omission is represented and later normalized to `dry_run`.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 166.04: Define match policy field

**Depends on:** Step 166.03 and Step 190.03

**Implement:** Add optional typed strict/balanced/loose policy; omission is normalized to `balanced` before CLI argument construction.

**Acceptance:** Unknown values are rejected; omission is represented and later normalized to `balanced`.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 166.05: Define visibility field

**Depends on:** Step 166.04 and Step 190.03

**Implement:** Add optional typed `private`/`public` visibility exactly matching `PlaylistTransferInput`; omission is normalized to `private` before CLI argument construction.

**Acceptance:** Valid public/private values pass, invalid visibility fails, and omission deterministically produces private destination arguments. Focused schema tests accept every valid `PlaylistTransferInput` fixture and reject the invalid fixtures from Step 190.03.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 167: Implement transfer confirmation rules

**Source dependency:** Steps 127, 130, 160, 166

**Expected libraries:** Pi `ctx.ui.confirm`

**Original requirement:** Require user confirmation for replace mode and for resuming a failed write after uncertain provider state.

#### Step 167.01: Confirm replace mode

**Depends on:** Groups 127, 130, 160, 166 and Step 190.03

**Implement:** Before process launch, request Pi UI confirmation when mode is replace.

**Acceptance:** Cancelling confirmation prevents process launch.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 167.02: Confirm uncertain failed-write resume

**Depends on:** Step 167.01 and Step 190.03

**Implement:** Before resuming a failed write with uncertain provider state, request Pi UI confirmation.

**Acceptance:** Cancelling confirmation prevents process launch.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 167.03: Bypass confirmation for safe modes

**Depends on:** Step 167.02 and Step 190.03

**Implement:** Do not request these confirmations for dry run, create, or ordinary merge/resume states.

**Acceptance:** A safe-mode test launches directly.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 168: Implement the `playlist_transfer` tool

**Source dependency:** Steps 147–148, 160–163, 166–167

**Expected libraries:** Pi `registerTool`, process runner

**Original requirement:** Spawn the CLI in JSONL mode, convert events into bounded `onUpdate` progress, and return final counts plus report paths.

#### Step 168.01: Build transfer CLI invocation

**Depends on:** Groups 147–148, 160–163, 166–167 and Step 190.03

**Implement:** Map validated tool input to the JSONL transfer command arguments.

**Acceptance:** The argument array contains explicit mode and policy.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 168.02: Spawn transfer CLI

**Depends on:** Step 168.01 and Step 190.03

**Implement:** Launch the child through the shell-free process runner.

**Acceptance:** The child is launched exactly once.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 168.03: Convert events to bounded Pi updates

**Depends on:** Step 168.02 and Step 190.03

**Implement:** Map parsed JSONL progress events into compact `onUpdate` calls.

**Acceptance:** A fixture stream produces the expected update sequence.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 168.04: Map final event and exit status

**Depends on:** Step 168.03 and Step 190.03

**Implement:** Build the typed tool result from final counts, review status, report paths, and process exit.

**Acceptance:** The result matches the fixture final event.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 169: Handle missing authentication

**Source dependency:** Steps 046, 051, 153, 165, 168

**Expected libraries:** Typed CLI exit codes

**Original requirement:** Recognize authentication-required results and return a direct instruction to call `playlist_auth` for the missing profile.

#### Step 169.01: Implement handle missing authentication

**Depends on:** Groups 046, 051, 153, 165, 168 and Step 190.03

**Implement:** Recognize authentication-required results and return a direct instruction to call `playlist_auth` for the missing profile.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 169.02: Test handle missing authentication

**Depends on:** Step 169.01 and Step 190.03

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: The transfer tool never attempts to collect passwords.

**Acceptance:** The transfer tool never attempts to collect passwords.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 170: Define and implement `playlist_review`

**Source dependency:** Steps 151–152, 156–163

**Expected libraries:** `typebox`, Pi `registerTool`

**Original requirement:** Support list and apply actions by invoking the corresponding deterministic CLI commands.

#### Step 170.01: Define `playlist_review` action schema

**Depends on:** Groups 151–152, 156–163 and Step 190.03

**Implement:** Define typed `list` and `apply` actions plus shared job ID.

**Acceptance:** Unknown actions are rejected.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 170.02: Define review-apply choice fields

**Depends on:** Step 170.01 and Step 190.03

**Implement:** Add source item ID, optional Spotify track ID, and explicit skip for apply.

**Acceptance:** The schema rejects both-choice and neither-choice apply requests.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 170.03: Implement review list action

**Depends on:** Step 170.02 and Step 190.03

**Implement:** Invoke the deterministic CLI `review list` command and return bounded results.

**Acceptance:** The exact literal argument array is used.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 170.04: Implement review apply action

**Depends on:** Step 170.03 and Step 190.03

**Implement:** Invoke the deterministic CLI `review apply` command with exactly one validated choice.

**Acceptance:** The exact literal argument array is used.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 171: Add concise tool prompt guidance

**Source dependency:** Steps 164–170

**Expected libraries:** Pi tool metadata

**Original requirement:** Describe when Pi should use auth, transfer, and review tools and state that individual track operations must not be improvised through shell commands.

#### Step 171.01: Implement concise tool prompt guidance

**Depends on:** Groups 164–170 and Step 190.03

**Implement:** Describe when Pi should use auth, transfer, and review tools and state that individual track operations must not be improvised through shell commands.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 171.02: Test concise tool prompt guidance

**Depends on:** Step 171.01 and Step 190.03

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: The guidance names each tool explicitly.

**Acceptance:** The guidance names each tool explicitly.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 172: Add custom call/result rendering

**Source dependency:** Steps 161, 163–170

**Expected libraries:** `@earendil-works/pi-tui` optional

**Original requirement:** Render source, destination, progress counts, review status, and report path without displaying raw JSON unless expanded.

#### Step 172.01: Implement custom call/result rendering

**Depends on:** Groups 161, 163–170 and Step 190.03

**Implement:** Render source, destination, progress counts, review status, and report path without displaying raw JSON unless expanded.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 172.02: Test custom call/result rendering

**Depends on:** Step 172.01 and Step 190.03

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: Collapsed rendering remains under a few terminal lines.

**Acceptance:** Collapsed rendering remains under a few terminal lines.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 173: Add extension unit tests

**Source dependency:** Steps 158–172

**Expected libraries:** `node:test`, TypeScript

**Original requirement:** Test argument building, executable lookup, JSONL chunk parsing, cancellation, confirmation blocking, redaction, and final result mapping.

#### Step 173.01: Add argument-building unit test

**Depends on:** Groups 158–172 and Step 190.03

**Implement:** Test auth, transfer, and review argument arrays.

**Acceptance:** No output is a shell command string.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 173.02: Add executable-lookup unit test

**Depends on:** Step 173.01 and Step 190.03

**Implement:** Test configured, known-path, missing, and non-executable cases.

**Acceptance:** Lookup behavior is deterministic.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 173.03: Add JSONL chunk parser unit test

**Depends on:** Step 173.02 and Step 190.03

**Implement:** Test split lines, multiple lines, malformed lines, and trailing fragments.

**Acceptance:** Events reconstruct correctly.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 173.04: Add cancellation unit test

**Depends on:** Step 173.03 and Step 190.03

**Implement:** Test graceful then forced child termination.

**Acceptance:** No orphan remains.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 173.05: Add confirmation blocking unit test

**Depends on:** Step 173.04 and Step 190.03

**Implement:** Test replace and uncertain-resume cancellation.

**Acceptance:** Cancelled confirmation prevents launch.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 173.06: Add redaction unit test

**Depends on:** Step 173.05 and Step 190.03

**Implement:** Test token and OAuth-code fixture removal.

**Acceptance:** Sensitive fixture strings are absent.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 173.07: Add final-result mapping unit test

**Depends on:** Step 173.06 and Step 190.03

**Implement:** Test final event and exit-code mapping.

**Acceptance:** The typed result contains counts and report paths.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 174: Add a Pi loading smoke test

**Source dependency:** Steps 157, 164–170, 173

**Expected libraries:** Pi CLI

**Original requirement:** Create a script that loads the extension and verifies the three tool names are registered. The script accepts `PI_EXTENSION_PATH` to load an unpacked release artifact and defaults to the source extension path only when the variable is absent.

#### Step 174.01: Add pi loading smoke test

**Depends on:** Groups 157, 164–170, 173

**Implement:** Create a script that loads the extension and verifies the three tool names are registered. Accept `PI_EXTENSION_PATH` as an explicit extension directory override; when absent, use the source extension directory.

**Acceptance:** The changed artifact imports, compiles, parses, or loads successfully. Do not add unrelated behavior or edit unrelated modules.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 174.02: Run pi loading smoke test

**Depends on:** Step 174.01

**Implement:** Add or run one focused automated test or deterministic verification check for this requirement: The script exits 0 in the local Pi harness.

**Acceptance:** The script exits 0 in the local Pi harness.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

## Phase 12 — Packaging, documentation, and live acceptance

Make the tool installable and prove the complete path with the user's own accounts.

### Group 175: Create the skill file

**Source dependency:** Steps 164–166, 168, 170–171

**Expected libraries:** Markdown; Pi skills mechanism

**Original requirement:** Write `SKILL.md` explaining that Pi must call the registered tools, must not handle tokens, and must preserve explicit transfer modes.

#### Step 175.01: Document auth tool usage

**Depends on:** Groups 164–166, 168, 170–171

**Implement:** In `SKILL.md`, state when Pi must call `playlist_auth`.

**Acceptance:** A reviewer can identify the auth tool from the section alone.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 175.02: Document transfer tool usage

**Depends on:** Step 175.01

**Implement:** State when Pi must call `playlist_transfer` and preserve explicit transfer modes.

**Acceptance:** Dry run, create, merge, and replace are named.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 175.03: Document review tool usage

**Depends on:** Step 175.02

**Implement:** State when Pi must call `playlist_review`.

**Acceptance:** List and apply actions are named.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 175.04: Document credential boundary

**Depends on:** Step 175.03

**Implement:** State that Pi must not request, store, or display provider tokens/passwords.

**Acceptance:** The prohibition is explicit.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 175.05: Document no improvised track shell work

**Depends on:** Step 175.04

**Implement:** State that track-level actions must go through deterministic registered tools, not improvised shell commands.

**Acceptance:** The rule is explicit.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 175.06: Document version-one direction and service scope

**Depends on:** Step 175.05

**Implement:** State that the registered workflow supports YouTube and YouTube Music playlist URLs as YouTube sources and Spotify as the only destination; do not imply Spotify-to-YouTube or bidirectional synchronization.

**Acceptance:** The skill describes the product as a YouTube-to-Spotify bridge and names reverse-direction adapters as deferred.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 175.07: Document browser-automation boundary

**Depends on:** Step 175.06

**Implement:** State that browser use is limited to official OAuth pages and that all playlist operations must use deterministic APIs through registered tools.

**Acceptance:** OAuth browser interaction is allowed while browser scraping, browser playlist mutation, and automated password entry are explicitly prohibited.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 176: Create the runtime README

**Source dependency:** Steps 141–155, 164–175

**Expected libraries:** Markdown

**Original requirement:** Document the YouTube-to-Spotify version-one scope, installation, provider app setup, environment/config values, authentication, dry-run, transfer, review, resume, reports, deferred adapters, and upstream matcher attribution.

#### Step 176.01: Document runtime installation

**Depends on:** Groups 141–155, 164–175

**Implement:** Add installation commands that match the release/install scripts.

**Acceptance:** Every command exists and is testable.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 176.02: Document provider application setup

**Depends on:** Step 176.01

**Implement:** Add Spotify and Google application setup requirements from the parent plan.

**Acceptance:** Required redirect/client configuration is named.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 176.03: Document configuration values

**Depends on:** Step 176.02

**Implement:** List environment/config values and placeholder examples.

**Acceptance:** No real credential-like value appears.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 176.04: Document authentication commands

**Depends on:** Step 176.03

**Implement:** Add Spotify auth, YouTube auth, status, and logout examples.

**Acceptance:** Every command exists in CLI tests.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 176.05: Document inspect and dry-run commands

**Depends on:** Step 176.04

**Implement:** Add playlist inspection and dry-run examples.

**Acceptance:** Every command exists in CLI tests.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 176.06: Document transfer modes

**Depends on:** Step 176.05

**Implement:** Add create, merge, and explicit replace examples.

**Acceptance:** Every command exists in CLI tests.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 176.07: Document review workflow

**Depends on:** Step 176.06

**Implement:** Add review list/apply and rerun examples.

**Acceptance:** Every command exists in CLI tests.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 176.08: Document resume workflow

**Depends on:** Step 176.07

**Implement:** Add job listing/showing and resume examples.

**Acceptance:** Every command exists in CLI tests.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 176.09: Document reports

**Depends on:** Step 176.08

**Implement:** Explain JSON, JSONL, CSV, and diagnostic report locations and contents.

**Acceptance:** The documented paths match application path helpers.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 176.10: Document intentional version-one scope

**Depends on:** Step 176.09

**Implement:** Add the four version-one scope decisions verbatim: official YouTube API for both playlist URL domains, YouTube-to-Spotify only, local RapidFuzz matcher, and browser use only for OAuth.

**Acceptance:** The README neither advertises ytmusicapi library features nor implies bidirectional or browser-automated playlist operations.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 176.11: Document deferred adapters

**Depends on:** Step 176.10

**Implement:** Add the post-v1 source and destination adapter tree and state that each requires a new plan version and isolated contract.

**Acceptance:** YouTube Music library/liked songs, Spotify source, regular YouTube destination, and YouTube Music destination are clearly marked deferred.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 176.12: Document spotDL audit and attribution

**Depends on:** Step 176.11

**Implement:** Link `docs/research/spotdl-matcher-audit.md`, identify any reproduced or ported MIT-licensed behavior/tests and attribution, or explicitly record that nothing was ported. State that spotDL, downloading, and FFmpeg are not runtime dependencies.

**Acceptance:** Every adopted upstream behavior has a source revision and attribution record, and dependency manifests contain no prohibited downloader/media dependency.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 177: Create the security model

**Source dependency:** Steps 039–055, 134, 153–154, 160, 162–163, 165, 167–170

**Expected libraries:** Markdown

**Original requirement:** Document keychain storage, local database contents, OAuth browser flow, no password collection, output redaction, extension permissions, and threat boundaries.

#### Step 177.01: Document keychain storage

**Depends on:** Groups 039–055, 134, 153–154, 160, 162–163, 165, 167–170

**Implement:** Explain which provider credential material is stored in the OS keychain.

**Acceptance:** The document does not claim tokens are stored in SQLite.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 177.02: Document local database contents

**Depends on:** Step 177.01

**Implement:** List non-secret profile, job, track, decision, cache, correction, and checkpoint data.

**Acceptance:** Credential fields are explicitly excluded.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 177.03: Document OAuth browser flow

**Depends on:** Step 177.02

**Implement:** Explain that interaction is limited to official provider authorization pages; playlist reads, writes, matching, and verification use APIs only.

**Acceptance:** Password automation, browser scraping, and browser-based playlist mutation are explicitly excluded.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 177.04: Document output redaction

**Depends on:** Step 177.03

**Implement:** Explain stdout/stderr/report redaction boundaries.

**Acceptance:** Token and OAuth-code redaction is named.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 177.05: Document extension permissions

**Depends on:** Step 177.04

**Implement:** List executable spawning, filesystem/report, browser-auth, and cancellation permissions used by the extension.

**Acceptance:** Arbitrary shell execution is explicitly excluded.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 177.06: Document threat boundaries

**Depends on:** Step 177.05

**Implement:** State local-device, provider-account, malicious-playlist-metadata, and compromised-dependency boundaries supported by the source plan.

**Acceptance:** Unsupported guarantees are not added.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 177.07: Document provider revocation

**Depends on:** Step 177.06

**Implement:** Explain how to revoke Spotify and Google/YouTube authorizations and what local cleanup does.

**Acceptance:** Both provider revocation paths are named.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 178: Create configuration examples

**Source dependency:** Steps 043, 047, 146, 156, 176

**Expected libraries:** TOML or environment example

**Original requirement:** Provide placeholder-only examples for Spotify client ID, Google client-secret path, database path override, and executable path.

#### Step 178.01: Add Spotify client-ID placeholder

**Depends on:** Groups 043, 047, 146, 156, 176

**Implement:** Provide a clearly fake Spotify client-ID example.

**Acceptance:** No real credential-like string is committed.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 178.02: Add Google client-secret-path placeholder

**Depends on:** Step 178.01

**Implement:** Provide a path placeholder only, not client-secret contents.

**Acceptance:** The example contains no secret JSON.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 178.03: Add database-path override placeholder

**Depends on:** Step 178.02

**Implement:** Provide a clearly local placeholder path.

**Acceptance:** The example parses.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 178.04: Add CLI executable-path placeholder

**Depends on:** Step 178.03

**Implement:** Provide a clearly local placeholder path for the Pi extension.

**Acceptance:** The example parses.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 179: Create the installation script

**Source dependency:** Steps 002–006, 156, 175–178

**Expected libraries:** POSIX shell, Python build tools, npm

**Original requirement:** Build and install the Python package into an isolated environment, install extension dependencies, and print the extension path to add to Pi.

#### Step 179.01: Create isolated runtime environment

**Depends on:** Groups 002–006, 156, 175–178

**Implement:** Create or reuse the documented isolated Python environment.

**Acceptance:** Running twice selects the same environment safely.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 179.02: Build and install Python package

**Depends on:** Step 179.01

**Implement:** Synchronize/install the runtime from `runtime/uv.lock` in frozen mode, then build/install the package into the isolated environment.

**Acceptance:** `playlist-bridge version` runs from the environment.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 179.03: Install extension dependencies

**Depends on:** Step 179.02

**Implement:** Run `npm ci` in `extension`; do not use an unlocked install command.

**Acceptance:** Extension dependencies resolve.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 179.04: Print Pi extension path

**Depends on:** Step 179.03

**Implement:** Print the exact extension path the user should add to Pi.

**Acceptance:** The path exists.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 179.05: Verify install idempotence

**Depends on:** Step 179.04

**Implement:** Run the installer twice using fake/local configuration.

**Acceptance:** The second run succeeds and does not overwrite credentials.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 180: Create the uninstall script

**Source dependency:** Step 179

**Expected libraries:** POSIX shell

**Original requirement:** Remove installed code while leaving user data and keychain credentials unless explicit purge flags are supplied.

#### Step 180.01: Remove installed runtime code

**Depends on:** Groups 179

**Implement:** Remove the installed Python runtime and generated executable links only.

**Acceptance:** Default uninstall removes code.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 180.02: Remove installed extension code

**Depends on:** Step 180.01

**Implement:** Remove installed extension dependencies/artifacts according to the package layout.

**Acceptance:** Default uninstall removes extension code.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 180.03: Preserve user data by default

**Depends on:** Step 180.02

**Implement:** Do not remove database, reports, or configuration without purge flags.

**Acceptance:** Default uninstall preserves reports and database.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 180.04: Preserve keychain credentials by default

**Depends on:** Step 180.03

**Implement:** Do not delete provider tokens without the explicit credential-purge flag.

**Acceptance:** Default uninstall leaves fake keyring entries.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 180.05: Implement explicit purge flags

**Depends on:** Step 180.04

**Implement:** Add separate explicit flags for local data and keychain credential purge.

**Acceptance:** Each flag affects only its documented target.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 181: Create the full verification script

**Source dependency:** Steps 010, 155, 173–174

**Expected libraries:** Ruff, mypy, pytest/pytest-cov, uv, npm, extension tests, Pi smoke test

**Original requirement:** Verify frozen dependencies, Python quality/tests/coverage, extension quality/tests, Pi loading, and plan DAG integrity in one fail-fast command.

#### Step 181.01: Verify frozen Python lockfile

**Depends on:** Groups 010, 155, 173–174

**Implement:** Add a frozen Python synchronization/check before running quality tools.

**Acceptance:** A stale `uv.lock` stops the script before linting.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 181.02: Run Python lint verification

**Depends on:** Step 181.01

**Implement:** Run Ruff after the lockfile check.

**Acceptance:** A lint failure stops the script.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 181.03: Run Python type verification

**Depends on:** Step 181.02

**Implement:** Run mypy after linting.

**Acceptance:** A type failure stops the script.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 181.04: Run Python tests with coverage

**Depends on:** Step 181.03

**Implement:** Run unit, property, contract, integration-with-fakes, migration, and concurrency tests with branch coverage enabled.

**Acceptance:** A test failure stops the script.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 181.05: Enforce 85-percent coverage gate

**Depends on:** Step 181.04

**Implement:** Fail when total branch-aware coverage is below 85%.

**Acceptance:** A deliberate isolated coverage drop below 85% fails.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 181.06: Verify npm lockfile with `npm ci`

**Depends on:** Step 181.05

**Implement:** Install extension dependencies using `npm ci` and reject a manifest/lock mismatch.

**Acceptance:** A stale `package-lock.json` stops the script.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 181.07: Run extension type checking

**Depends on:** Step 181.06

**Implement:** Run the extension TypeScript typecheck command.

**Acceptance:** A type failure stops the script.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 181.08: Run extension unit tests

**Depends on:** Step 181.07

**Implement:** Run the extension test command.

**Acceptance:** A test failure stops the script.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 181.09: Run Pi extension load smoke test

**Depends on:** Step 181.08

**Implement:** Run the Pi extension loading smoke test.

**Acceptance:** The expected tool names register and the process exits zero.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 181.10: Validate build-plan dependency graph

**Depends on:** Step 181.09

**Implement:** Implement and run `python3 scripts/validate-build-plan.py docs/build/pi-playlist-bridge-plan.md docs/build/symbol-contracts.yaml` from the repository root. Validate plan version, exact controller paths, group/step IDs, dependency references/ranges, duplicate IDs, self-dependencies, cycles, task-envelope resolvability, registry coverage for every cross-step symbol, and registry/plan hash consistency.

**Acceptance:** Unknown references, duplicate IDs, self-dependencies, cycles, missing contract records, renamed/missing controller inputs, or hash mismatches fail; the exact canonical command passes.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 181.11: Execute the full verification script

**Depends on:** Step 181.10

**Implement:** Run `bash scripts/verify-all.sh` from the repository root and retain its stage output.

**Acceptance:** The command exits zero and every declared verification stage executes.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 181.12: Add fail-fast mutation verification

**Depends on:** Step 181.11

**Implement:** Create the shell harness and pytest contract test. Each mutation runs in an isolated temporary repository copy and is removed afterward.

**Acceptance:** All eight mutations fail at the expected stage, later stages do not run, the source checkout is unchanged, and the clean pipeline still passes.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 182: Add provider contract fixtures

**Source dependency:** Steps 069, 098

**Expected libraries:** Sanitized JSON

**Original requirement:** Store sanitized YouTube and Spotify response fixtures matching every field consumed by adapters.

#### Step 182.01: Add sanitized YouTube contract fixtures

**Depends on:** Groups 069, 098

**Implement:** Store sanitized YouTube responses for every field consumed by the YouTube adapter.

**Acceptance:** No credential or personal account value appears.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 182.02: Add sanitized Spotify contract fixtures

**Depends on:** Step 182.01

**Implement:** Store sanitized Spotify responses for every field consumed by the Spotify adapter.

**Acceptance:** No credential or personal account value appears.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 182.03: Add consumed-field schema test

**Depends on:** Step 182.02

**Implement:** Validate fixtures against the adapter’s explicitly consumed field contract.

**Acceptance:** The schema test passes for all fixtures.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 182.04: Fail on newly unrepresented consumed field

**Depends on:** Step 182.03

**Implement:** Add a test mechanism that fails when adapter code declares a consumed field absent from fixtures.

**Acceptance:** A deliberate isolated new field causes the test to fail.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 183: Add a dry-run live checklist

**Source dependency:** Steps 138, 141–143, 145–147, 155, 182

**Expected libraries:** Markdown

**Original requirement:** Define a manual test using one small owned YouTube playlist and no Spotify writes.

#### Step 183.01: Define dry-run live prerequisites

**Depends on:** Groups 138, 141–143, 145–147, 155, 182

**Implement:** Specify one small owned YouTube playlist, authenticated profiles, and a no-write expectation.

**Acceptance:** The checklist has explicit prerequisites.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 183.02: Record source inspection results

**Depends on:** Step 183.01

**Implement:** Record playlist identity and source item count.

**Acceptance:** The checklist includes the observed count.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 183.03: Record match decisions

**Depends on:** Step 183.02

**Implement:** Record matched, ambiguous, unavailable, skipped, and non-track outcomes.

**Acceptance:** Every source item has an explicit outcome.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 183.04: Verify no destination mutation

**Depends on:** Step 183.03

**Implement:** Check that no Spotify playlist was created or changed.

**Acceptance:** The checklist records absence of destination mutation.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 184: Add a write live checklist

**Source dependency:** Steps 131–136, 138, 147–148, 155, 182

**Expected libraries:** Markdown

**Original requirement:** Define a manual create-mode test using a temporary private Spotify playlist.

#### Step 184.01: Define write live prerequisites

**Depends on:** Groups 131–136, 138, 147–148, 155, 182

**Implement:** Specify one small owned YouTube playlist and a temporary private Spotify destination.

**Acceptance:** The checklist has explicit cleanup-safe prerequisites.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 184.02: Execute create-mode live transfer

**Depends on:** Step 184.01

**Implement:** Run create mode once using the documented CLI or Pi tool.

**Acceptance:** A destination playlist ID is recorded.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 184.03: Verify destination order and count

**Depends on:** Step 184.02

**Implement:** Compare source accepted order/count with destination items.

**Acceptance:** Order and count match the expected accepted sequence.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 184.04: Verify selected versions

**Depends on:** Step 184.03

**Implement:** Manually inspect the selected remix/live/remaster variants represented by the test playlist.

**Acceptance:** The checklist records the selected versions.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 184.05: Verify report contents

**Depends on:** Step 184.04

**Implement:** Inspect JSON and CSV/report outputs for counts and exceptions.

**Acceptance:** Required report sections are present.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 184.06: Verify resume does not duplicate writes

**Depends on:** Step 184.05

**Implement:** Interrupt at a controlled checkpoint, resume, and compare destination items.

**Acceptance:** No duplicate write is introduced.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 185: Add a review live checklist

**Source dependency:** Steps 109–115, 140, 151–152, 155, 182

**Expected libraries:** Markdown

**Original requirement:** Define a playlist containing at least one ambiguous, unavailable, remix, and non-song item, then exercise review apply and resume.

#### Step 185.01: Prepare ambiguous review item

**Depends on:** Groups 109–115, 140, 151–152, 155, 182

**Implement:** Include at least one source item expected to require manual match review.

**Acceptance:** The dry run reports it as ambiguous or unmatched.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 185.02: Prepare unavailable source item

**Depends on:** Step 185.01

**Implement:** Include at least one unavailable source item.

**Acceptance:** The item remains represented in reports.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 185.03: Prepare remix source item

**Depends on:** Step 185.02

**Implement:** Include at least one remix/version-sensitive source item.

**Acceptance:** The decision records version reasoning.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 185.04: Prepare non-song source item

**Depends on:** Step 185.03

**Implement:** Include at least one non-track item.

**Acceptance:** The item is classified explicitly.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 185.05: Apply manual review choice

**Depends on:** Step 185.04

**Implement:** Use review apply with a Spotify track ID or skip for the unresolved item.

**Acceptance:** The correction is persisted.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 185.06: Resume reviewed job

**Depends on:** Step 185.05

**Implement:** Resume or rerun unresolved review processing.

**Acceptance:** Only unresolved decisions are rematched.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 185.07: Verify final exception report

**Depends on:** Step 185.06

**Implement:** Inspect the final report for all prepared exception types.

**Acceptance:** Each exception is handled explicitly.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 186: Add credential-revocation acceptance

**Source dependency:** Steps 053–054, 141–144, 162, 165, 169

**Expected libraries:** Provider dashboards plus CLI status

**Original requirement:** Revoke each provider grant externally and verify the CLI reports authentication required without corrupting job data.

#### Step 186.01: Revoke Spotify provider grant

**Depends on:** Groups 053–054, 141–144, 162, 165, 169

**Implement:** Revoke the Spotify authorization externally for the test profile.

**Acceptance:** The grant is absent in the provider dashboard.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 186.02: Verify Spotify auth-required state

**Depends on:** Step 186.01

**Implement:** Run CLI status or a safe operation and observe authentication required.

**Acceptance:** Job data remains readable and uncorrupted.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 186.03: Reauthenticate Spotify profile

**Depends on:** Step 186.02

**Implement:** Authenticate again under the same profile name.

**Acceptance:** Access is restored without creating a new local profile.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 186.04: Revoke Google/YouTube provider grant

**Depends on:** Step 186.03

**Implement:** Revoke the Google/YouTube authorization externally for the test profile.

**Acceptance:** The grant is absent in the provider dashboard.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 186.05: Verify YouTube auth-required state

**Depends on:** Step 186.04

**Implement:** Run CLI status or a safe operation and observe authentication required.

**Acceptance:** Job data remains readable and uncorrupted.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 186.06: Reauthenticate YouTube profile

**Depends on:** Step 186.05

**Implement:** Authenticate again under the same profile name.

**Acceptance:** Access is restored without creating a new local profile.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 187: Create a release build

**Source dependency:** Steps 002–006, 156, 173–181

**Expected libraries:** `python -m build`, npm packaging or Git package

**Original requirement:** Build the Python wheel/source distribution and package the Pi extension with runtime dependencies declared correctly.

#### Step 187.01: Build Python wheel

**Depends on:** Groups 002–006, 156, 173–181

**Implement:** Run the Python wheel build.

**Acceptance:** A wheel artifact is produced.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 187.02: Build Python source distribution

**Depends on:** Step 187.01

**Implement:** Run the Python source-distribution build.

**Acceptance:** A source archive is produced.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 187.03: Package Pi extension

**Depends on:** Step 187.02

**Implement:** Create the extension release package with runtime dependencies declared correctly.

**Acceptance:** The package contains the compiled/source files required by the install method.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 187.04: Test clean release installation

**Depends on:** Step 187.03

**Implement:** Install the release artifacts in a clean environment or clean user account.

**Acceptance:** The runtime command and extension load successfully.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

### Group 188: Run the final end-to-end acceptance

**Source dependency:** Steps 141–155, 164–187

**Expected libraries:** All production libraries

**Original requirement:** From Pi, authenticate both accounts, request a YouTube-to-Spotify dry run, review uncertainty, execute create mode, verify destination, rerun, and inspect reports.

#### Step 188.01: Authenticate both accounts from Pi

**Depends on:** Groups 141–155, 164–187

**Implement:** Call the registered auth tool for the selected YouTube and Spotify profiles.

**Acceptance:** Both profiles report authenticated.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 188.02: Run Pi dry-run transfer

**Depends on:** Step 188.01

**Implement:** Request the owned YouTube playlist transfer in dry-run mode.

**Acceptance:** No destination write occurs and reports are returned.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 188.03: Review uncertainty from Pi

**Depends on:** Step 188.02

**Implement:** List unresolved decisions and apply explicit choices where needed.

**Acceptance:** Corrections are persisted.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 188.04: Run Pi create transfer

**Depends on:** Step 188.03

**Implement:** Execute create mode using the reviewed job/request.

**Acceptance:** A Spotify destination is created with accepted items.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 188.05: Verify destination from Pi result

**Depends on:** Step 188.04

**Implement:** Inspect the verification result and destination playlist.

**Acceptance:** Expected and actual URI order match.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 188.06: Rerun or resume the same transfer

**Depends on:** Step 188.05

**Implement:** Run the relevant repeat/resume path using persisted state.

**Acceptance:** No unintended duplicate writes occur.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.

#### Step 188.07: Inspect final reports

**Depends on:** Step 188.06

**Implement:** Open the returned JSON/CSV/diagnostic paths and compare counts, decisions, and verification.

**Acceptance:** Pi returns the verified playlist plus valid report paths.

**Stop after:** The acceptance check passes. Do not begin the next micro-step.
