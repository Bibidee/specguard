# SpecGuard v0.4 security model (source not deployed)

## Trust boundary

The sponsor commits an acceptance policy before beneficiary acceptance. The
beneficiary cannot edit that policy after acceptance, and a challenge cannot
edit it at all. SHA-256 binds artifact bytes, not the real-world identity or
truthfulness of a publisher. An evidence `authority` is a policy label supplied
by the submitter; it is useful for preventing two sources from being counted as
independent, but it is not an identity credential.

## Threats and defenses

| Threat | Contract defense | Test coverage |
| --- | --- | --- |
| Artifact substitution | Hash before decode or visual review | hash mismatch and mirror tests |
| Two copies called independent | Distinct declared-authority **and committed-origin** threshold | false-independence and same-origin tests |
| Prompt injection | Artifacts are explicitly quoted untrusted data | malformed/injection tests |
| Favorable leader hides failure | Validators independently observe and compare criterion statuses | validator critical-failure test |
| Invalid/unreviewed challenge manufactures refund | Append-only challenge records; deadline finalization restores the original decision | invalid-hash, unavailable-source, abandoned-challenge tests |
| Challenge slot monopolization | Three bounded slots, one per eligible role, no early terminal transition | multi-challenger and early-resolution tests |
| Cross-manifest evidence shadowing | Global evidence-ID collision rejection and immutable source index | collision regression |
| Unsupported publisher authentication | `authenticated` policy mode is rejected until runtime attestation support exists | provenance policy test |
| Double payout or refund | Single debit-before-dispatch settlement path | one-shot settlement regression |
| Consumer abandonment | Beneficiary-only settlement after seven days | consumer timeout test |

## Native GEN transfers

The contract updates its ledger before a single external transfer dispatch.
Dispatch is asynchronous: a parent settlement is not evidence that a child
transfer credited the recipient. Integrators must verify the child receipt and
its `value_credited` field. The contract deliberately has no unsafe automatic
retry for ambiguous child transfers.

## URL and availability limits

HTTPS syntax checks reject credentials, local names, numeric IP literals, and
malformed hosts. They cannot prove DNS resolution safety, remote ownership, or
availability. Non-2xx, invalid, oversized, malformed, or unavailable artifacts
never approve a guard. Redirect visibility depends on the runtime; an exposed
redirect is rejected, while hidden runtime redirect behavior remains an external
platform assumption documented for deployment review. Declared authorities and
origins are corroboration metadata, not real-world identity proofs.
