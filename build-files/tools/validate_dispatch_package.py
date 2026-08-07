#!/usr/bin/env python3
from __future__ import annotations
import collections,json,re,sys,yaml
from pathlib import Path

def fail(msg):
    print("FAIL:",msg,file=sys.stderr); raise SystemExit(1)
root=Path(sys.argv[1] if len(sys.argv)>1 else ".")
m=json.loads((root/"manifests/execution-order.json").read_text())
ds=m["dispatches"]
regdoc=yaml.safe_load((root/"reference/symbol-contracts.yaml").read_text())
reg=regdoc["symbols"]
plan_path=root/"reference/pi-playlist-bridge-plan-v2.6.md"
plan=plan_path.read_text()
plan_steps=re.findall(r'^#### Step ([0-9]+\.[0-9]+):',plan,re.M)
if len(plan_steps)!=len(set(plan_steps)): fail('duplicate source-plan step headings')
manifest_steps=[s for d in ds for s in d['step_ids']]
if set(plan_steps)!=set(manifest_steps):
    fail(f"source/manifest step set mismatch missing_from_plan={sorted(set(manifest_steps)-set(plan_steps))} extra_in_plan={sorted(set(plan_steps)-set(manifest_steps))}")
# Embedded registry must parse exactly like the external registry.
match=re.search(r'## Complete cross-step signature registry.*?```yaml\n(.*?)\n```',plan,re.S)
if not match: fail('missing embedded registry')
embedded=yaml.safe_load(match.group(1))
if embedded!=regdoc: fail('embedded registry differs from reference/symbol-contracts.yaml')
if [d["sequence"] for d in ds] != list(range(1,len(ds)+1)): fail("non-contiguous sequence")
available=set(); seen_steps=[]; owners={}; occurrences={}; prior_contract={}
found_pi=found_full=found_mutation=found_packed=False
batches=collections.defaultdict(list)
production_prefixes=('runtime/src/','extension/index.ts','extension/process.ts','extension/schemas.ts','extension/jsonl.ts','extension/render.ts','extension/types.ts')
test_only_steps={'058.04','083.07','082.01','082.02','082.03','082.04','189.20','190.03'}
for d in ds:
    batches[(d["wave"],d["parallel_batch"])].append(d)
    p=root/d["file"]
    if not p.is_file(): fail(f"missing {d['file']}")
    text=p.read_text(); seen_steps += d["step_ids"]
    for q in d["prerequisite_dispatches"]:
        if q>=d["sequence"]: fail(f"late prerequisite {q} -> {d['sequence']}")
    missing=set(d["requires_capabilities"])-available
    if missing: fail(f"capabilities unavailable at {d['sequence']}: {sorted(missing)}")
    if set(d['step_ids']) & test_only_steps:
        bad=[t for t in d['target_files'] if t.startswith(production_prefixes)]
        if bad: fail(f"test-only production target at {d['sequence']}: {bad}")
    symbols=d.get("primary_symbols",[])
    if not symbols: fail(f"empty symbol envelope {d['sequence']}")
    for s in symbols:
        name=s.get("name"); kind=s.get("kind")
        if kind=="callable":
            sig=s.get("signature") or ""
            if "(" not in sig or not ("->" in sig or "=>" in sig): fail(f"untyped callable {d['sequence']} {name}")
        if name:
            cur=(s.get("signature"),tuple(s.get("errors",[])),tuple(s.get("side_effects",[])),s.get("owner_file"))
            if name in prior_contract and prior_contract[name][0] != cur:
                expected=f"{prior_contract[name][1]:04d}:{name}"
                if s.get("supersedes") != expected: fail(f"signature change without exact supersedes at {d['sequence']} {name}; expected {expected}")
            prior_contract[name]=(cur,d["sequence"])
        if name in reg:
            entry=reg[name]
            if s.get("signature")!=entry.get("signature"): fail(f"signature mismatch {d['sequence']} {name}")
            if s.get("errors",[])!=entry.get("errors",[]): fail(f"errors mismatch {d['sequence']} {name}")
            if s.get("side_effects",[])!=entry.get("side_effects",[]): fail(f"side effects mismatch {d['sequence']} {name}")
            if s.get("owner_file")!=entry.get("file"): fail(f"owner field mismatch {d['sequence']} {name}")
            if entry["file"] not in d["target_files"]: fail(f"registered owner not targeted {d['sequence']} {name}: {entry['file']}")
            occurrences.setdefault(name,[]).append(d["sequence"]); owners.setdefault(name,set()).add(s["owner_file"])
    names={s.get("name") for s in symbols if s.get("name")}
    for name in re.findall(r"## Original micro-step `[^`]+` — Define `([^`]+)`\s*\n",text):
        if name not in names: fail(f"Define step missing primary symbol {d['sequence']}: {name}")
    v=d["verification"]; joined="\n".join(v["commands"])
    if d["step_ids"]==["174.02"]: found_pi="bash scripts/verify-pi-extension.sh" in joined
    if d["step_ids"]==["181.11"]: found_full="bash scripts/verify-all.sh" in joined
    if d["step_ids"]==["181.12"]: found_mutation="test-verify-all-failfast.sh" in joined and "test_verify_all_pipeline.py" in joined
    if d["step_ids"]==["187.04"]: found_packed=all(x in joined for x in ["tar -xzf","PI_EXTENSION_PATH=","package.json"])
    available.update(d["produces_capabilities"])
for key,items in batches.items():
    target_owner={}
    for d in items:
        for target in d["target_files"]:
            if target in target_owner: fail(f"parallel target conflict wave/batch {key}: {target} in {target_owner[target]} and {d['sequence']}")
            target_owner[target]=d["sequence"]
if len(seen_steps)!=len(set(seen_steps)): fail("duplicate micro-step IDs")
if len(seen_steps)!=m["microstep_count"]: fail(f"manifest micro-step count mismatch {len(seen_steps)} != {m['microstep_count']}")
missing_symbols=sorted(set(reg)-set(occurrences))
if missing_symbols: fail(f"registry symbols without dispatch: {missing_symbols}")
for name,files in owners.items():
    if len(files)!=1: fail(f"repeated symbol has multiple owners {name}: {sorted(files)}")
if not all([found_pi,found_full,found_mutation,found_packed]): fail("future execution gates not scheduled")
# Composition root must be produced before the CLI consumers.
seq_by_step={sid:d['sequence'] for d in ds for sid in d['step_ids']}
for producer,consumer in [('189.15','141.02'),('189.15','142.02'),('189.15','149.01'),('189.15','150.01'),('189.15','151.01'),('189.15','152.03'),('189.17','145.02'),('189.18','147.03'),('189.19','148.02'),('190.03','159.07'),('190.03','160.06')]:
    if seq_by_step[producer]>=seq_by_step[consumer]: fail(f'composition/type producer not earlier: {producer} -> {consumer}')
# V4.2 implementation-freeze semantics.
expected_transfer='TransferRequest(source_url: str, source_profile: str, spotify_profile: str, destination_name: str, mode: TransferMode = TransferMode.dry_run, match_policy: MatchPolicy = MatchPolicy.balanced, public: bool = False)'
if reg.get('TransferRequest',{}).get('signature') != expected_transfer: fail('TransferRequest field contract is not frozen exactly')
expected_auth='type PlaylistAuthInput = { action: "login" | "status" | "logout"; service: "youtube" | "spotify"; profile: string; clientSecretPath?: string }'
expected_transfer_ts='type PlaylistTransferInput = { sourceUrl: string; sourceProfile: string; spotifyProfile: string; destinationName?: string; mode?: "dry_run" | "create" | "merge" | "replace"; policy?: "strict" | "balanced" | "loose"; visibility?: "private" | "public"; jobId?: string }'
if reg.get('PlaylistAuthInput',{}).get('signature') != expected_auth: fail('PlaylistAuthInput does not align with auth schema action')
if reg.get('PlaylistTransferInput',{}).get('signature') != expected_transfer_ts: fail('PlaylistTransferInput does not align with transfer schema visibility/defaults')
if 'required `action`' not in plan or '`visibility`' not in plan or 'invalid visibility' not in plan: fail('TypeBox schema alignment wording missing')
for sid in ['164.04','166.05']:
    d=next(x for x in ds if sid in x['step_ids'])
    if 'npm test -- test/schemas.test.ts' not in '\n'.join(d['verification']['commands']): fail(f'runtime schema parity test not scheduled at {sid}')
    if seq_by_step['190.03'] >= d['sequence']: fail(f'type fixtures not earlier than schema parity test {sid}')
if 'get(job_id: str, source_item_id: str) -> SourceTrack | None' not in reg['SourceTrackRepository']['signature']: fail('review cannot retrieve source track')
if 'tracks: SourceTrackRepository' not in reg['ReviewRepositories']['signature']: fail('ReviewRepositories lacks source tracks')
if reg['apply_manual_review']['side_effects'] != ['sqlite_read','sqlite_write']: fail('review fingerprint contract lacks read/write effects')
if 'compute `source_fingerprint`' not in plan or 'persist the correction by `source_fingerprint`' not in plan: fail('fingerprint-safe review wording missing')
for name in ['JobQueryDependencies','build_job_query_dependencies','build_review_dependencies']:
    if name not in reg: fail(f'missing composition-root symbol {name}')
for sid in ['149.01','150.01','151.01','152.03']:
    d=next(x for x in ds if sid in x['step_ids'])
    if 204 not in d['prerequisite_dispatches'] or 'local_query_composition_root' not in d['requires_capabilities']: fail(f'CLI composition root not wired for {sid}')
if '## Implementation freeze' not in plan or 'concrete contradiction, missing dependency, or impossible acceptance check' not in plan: fail('implementation freeze rule missing')
print(json.dumps({
  "status":"PASS","dispatches":len(ds),"microsteps":len(seen_steps),"waves":m["waves"],
  "all_prerequisites_earlier":True,"all_steps_once":True,"source_plan_step_set_match":"PASS",
  "embedded_registry_sync":"PASS","parallel_batch_target_conflicts":0,
  "registry_symbol_coverage":"PASS","registry_owner_mapping":"PASS","registry_contract_equality":"PASS",
  "duplicate_symbol_owner_conflicts":0,"signature_supersedes_validation":"PASS","unauthorized_signature_changes":0,
  "test_only_target_containment":"PASS","composition_root_scheduled":"PASS","job_review_composition_root":"PASS","typescript_boundary_types_scheduled":"PASS","transfer_request_fields_frozen":"PASS","typescript_typebox_alignment":"PASS","review_fingerprint_access":"PASS","implementation_freeze":"PASS",
  "pi_smoke_execution_scheduled":"PASS","full_verification_execution_scheduled":"PASS",
  "failfast_mutation_suite_scheduled":"PASS","packed_extension_smoke_scheduled":"PASS",
  "clean_room_capability_simulation":"PASS"
},indent=2))
