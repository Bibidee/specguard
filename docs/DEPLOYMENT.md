# Deployment status

## Current v0.4.1 StudioNet deployment

- Source version: `0.4.1`
- Merged source commit: `8082a0a28d2f72650054f135a4ea6b5218cf0d1c`
- Network: GenLayer Studio Network (chain ID `61999`), CLI `genlayer@0.39.1`
- Contract: [`0xCbeD8bb09981a42347C87928d1dCd2A75552b8e8`](https://explorer-studio.genlayer.com/address/0xCbeD8bb09981a42347C87928d1dCd2A75552b8e8)
- Deployment transaction: [`0xd4f781f345ddd48c323ca4dc36f6c18ec1e01f3489365d1e4496b015dc4eae2e`](https://explorer-studio.genlayer.com/tx/0xd4f781f345ddd48c323ca4dc36f6c18ec1e01f3489365d1e4496b015dc4eae2e)
- Deployment result: `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS`
- Local source bytes: `52925`
- Deployed source bytes: `52925`
- Raw source SHA-256: `b40b6a205b8cc8683481d0e3d8086f6cb6c6f566163ed3ec773eca7dd1c577c2`
- Source parity: `gen_getContractCode` returned the same 52,925 bytes and
  matched byte-for-byte: **YES**.
- Local release gate: **49 tests passed**, 0 skipped, 0 failed; GenVM lint PASS,
  ABI/schema PASS, and preflight PASS.
- GitHub Actions: [39158223106](https://github.com/Bibidee/specguard/actions/runs/39158223106) completed successfully for this merged HEAD.
- `get_info()`: `name=SpecGuard`, `version=0.4.1`, `min_confidence=75`,
  `min_deposit_wei=1000000000000000`, `max_text_bytes=16000`,
  `max_image_bytes=2000000`, `max_cases_per_sponsor=64`, `max_challenges=3`.
- No funded guard, escrow, challenge, settlement, or other lifecycle write was
  executed during this deployment pass. The live transaction tables below are
  historical evidence for superseded releases.
- The source includes bounded multi-party challenge records, global evidence-ID
  collision checks, committed-origin corroboration, sponsor-only blocked
  refunds, and safe challenge deadline finalization.

## Historical v0.3.0 — verified; superseded by the v0.4.1 source

- Frozen contract-source commit: `d68374aa4ea41a4f685e23cdb66f9f978ce279c9`
- Fixture/documentation commit used for live artifacts: `23ec793d6dba5ddc65890fd448d2f72d961f8e27`
- Raw source SHA-256: `4bab5d8642ae98aa8a9196e4890b6a6d5acc9317664103a250ffead773ee6b36`
- Contract: [`0x79E1948E93a28F3B90001a2cB984566a0BF781C7`](https://explorer-studio.genlayer.com/address/0x79E1948E93a28F3B90001a2cB984566a0BF781C7)
- Deployment transaction: [`0x704484a21ea26daa000e9e523caef81f119680cd0b0e7e7599f3c827aa4682e4`](https://explorer-studio.genlayer.com/tx/0x704484a21ea26daa000e9e523caef81f119680cd0b0e7e7599f3c827aa4682e4)
- Deployment result: `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS`
- Source parity: `gen_getContractCode` returned 38,647 bytes; local source was
  also 38,647 bytes and matched byte-for-byte with the SHA-256 above.

### Live approved settlement

Guard `SG-LIVE-20261018-A` used a 0.001 GEN deposit, sponsor
`0x7afc209ad72153f6c8ae7b8055bfba6e7f4d5efc`, beneficiary
`0x7eb2a4b4e913df62eae807ef60509b3b7284c7fa`, and designated consumer
`0xf883bce8fcb120f714b147446342d7e4545bc988`. Its policy required two
declared authorities to corroborate criterion `C1`.

| Artifact | Immutable URL | SHA-256 |
| --- | --- | --- |
| Specification | `raw.githubusercontent.com/Bibidee/specguard/23ec793d6dba5ddc65890fd448d2f72d961f8e27/docs/live-fixtures/v0.3.0/specification.txt` | `0x108d49da462dd3250456a17519cee3cdc0f2653496c2d3ec5e5d041d499862fd` |
| Implementation | `raw.githubusercontent.com/Bibidee/specguard/23ec793d6dba5ddc65890fd448d2f72d961f8e27/docs/live-fixtures/v0.3.0/implementation.txt` | `0x6d43ea78e0f131fc2649cf17d633f42f435934dea788f49d4ac558089b249d5c` |
| Evidence EV1 | `raw.githubusercontent.com/Bibidee/specguard/23ec793d6dba5ddc65890fd448d2f72d961f8e27/docs/live-fixtures/v0.3.0/ci-record.txt` | `0x9641fed8b0c0e66b5f125b2725c8d08294207d036f2804dd01b48ffccd132bb2` |
| Evidence EV2 | `cdn.jsdelivr.net/gh/Bibidee/specguard@23ec793d6dba5ddc65890fd448d2f72d961f8e27/docs/live-fixtures/v0.3.0/audit-record.txt` | `0xee14ece14999cd96dfe723c71847eb02b9bf7a1dbe10b4ae5b513520504034fc` |

| Step | Transaction | Verified result |
| --- | --- | --- |
| Fund | [`0x3894cbf97e8589b265f7172eec77cf316260aa6c80dc49a28dc3787b5ceff662`](https://explorer-studio.genlayer.com/tx/0x3894cbf97e8589b265f7172eec77cf316260aa6c80dc49a28dc3787b5ceff662) | `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS`, 0.001 GEN credited |
| Accept | [`0xb58cc006dab6ca834d5c7b0a808ab2cd0c72e88be39e3e3f4463b2ed5b79f155`](https://explorer-studio.genlayer.com/tx/0xb58cc006dab6ca834d5c7b0a808ab2cd0c72e88be39e3e3f4463b2ed5b79f155) | `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS` |
| Submit | [`0x9a7e6a9a429f827011c0fbef192633711b99879218ad158ef6268366df1f9ac5`](https://explorer-studio.genlayer.com/tx/0x9a7e6a9a429f827011c0fbef192633711b99879218ad158ef6268366df1f9ac5) | `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS` |
| First review | [`0xf1461a29763356bbacb9e655f7ef50df4308ec6ca9a7eb40f7e8bb4e81d2b899`](https://explorer-studio.genlayer.com/tx/0xf1461a29763356bbacb9e655f7ef50df4308ec6ca9a7eb40f7e8bb4e81d2b899) | `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS`; safe `retryable / malformed_model_output` |
| Controlled review retry | [`0x180f93b46e28182da168f37a6181876bb66edb18ffbc7f10c533c3e9efce39d7`](https://explorer-studio.genlayer.com/tx/0x180f93b46e28182da168f37a6181876bb66edb18ffbc7f10c533c3e9efce39d7) | `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS`; `preliminary_approved`, confidence `100` |
| Finalize preliminary | [`0x16550a8ae178e689646aa5f545eea2196e1b9a563e0df406f5d80f8a131a7b5a`](https://explorer-studio.genlayer.com/tx/0x16550a8ae178e689646aa5f545eea2196e1b9a563e0df406f5d80f8a131a7b5a) | `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS`; `approved` after an unchallenged deadline |
| Settle | [`0xbe191925340264d5ba35b8384e763aacf5c2a1d2980d047e41b1969b62855d15`](https://explorer-studio.genlayer.com/tx/0xbe191925340264d5ba35b8384e763aacf5c2a1d2980d047e41b1969b62855d15) | `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS`; designated consumer settled 0.001 GEN |
| Child transfer | [`0x4a16cba604761b8d63202be10c219eb262146d3986b450a561024f8e51583f9a`](https://explorer-studio.genlayer.com/tx/0x4a16cba604761b8d63202be10c219eb262146d3986b450a561024f8e51583f9a) | `FINALIZED`, beneficiary credited `1000000000000000` wei with `value_credited: true` |

The historical final read reports `status: paid_beneficiary`,
`reason: paid_beneficiary`, `deposit: 0`, and
`settled_amount: 1000000000000000`. The evidence sources use two declared
authority labels for the controlled lifecycle proof; these labels do not prove
independent real-world publisher identity.

All sections below are historical and are retained only for the exact source
versions they describe. They are not current deployment evidence for v0.4.1.

## Historical v0.1.0 — superseded; do not use

The initial v0.1.0 deployment finalized on StudioNet at
`0x902fb7fDA76d914190C4F1afc2114afF5c4bb104` in transaction
`0x57d8bf632cc2933b9fb453b81e16dcadfc0d1a7f17258f7b80dbcba73c21f245`.
Its raw source was retrieved through `gen_getContractCode` and matched the
repository byte-for-byte (SHA-256
`9d89f8a840238ecc159e6930ede6a11bbbbdb01ec5497fa212118498c215aa7d`).

It is nevertheless **superseded and must not be used**. The first payable
`create_guard` call,
`0x7352bd249b9ea072bbc33e0550ccede7140dc9c480ad6fe8b1a53cce81fcb896`,
failed in StudioNet's event-emission primitive after value credit. No guard
record was created while `0.001 GEN` was credited to that v0.1.0 contract.
The v0.1.1 source removes the incompatible nonessential event emissions and
adds a regression test. It requires a fresh deployment and lifecycle proof
before any address can be treated as canonical.

## Historical v0.1.1 — superseded; do not use

- Source commit: `9b5ead31b50b9f77e8473ba05f68cda88dbeb6a0`
- Raw source SHA-256: `7ca2ef1c1d1d166c6672da8b518b3ae8fb71d4932e9cf4532a18ac6ce2df433b`
- Contract: `0x70968dd0354236e3Eae6eb6eb9Cd3C3C01A4D0f0`
- Deployment transaction: `0x9be4311bc42deecae8db75e30d790c1c6dca1e454e4a1163bd4f7a6dcf51a4e7`
- Deployment result: `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS`
- Source parity: retrieved with `gen_getContractCode`; local and deployed bytes
  both measured 21,296 bytes and SHA-256 matched byte-for-byte.

### Live conformance settlement

The committed public artifacts are pinned to Git commit
`d18bea08204c5f22a4ae723d9fb08411ff4dc9b4`:

- Specification: `specification.txt`, SHA-256
  `0x3f5f9f851c59ca98326b40923a4d3c86712b0443509dfa2d996875c6e88310c8`
- Implementation: `implementation.txt`, SHA-256
  `0x4850f97edefab6e62ef1e0046ce920dd69ff8f18317d8524b114538c3ee57ee2`
- Evidence: `evidence.txt`, SHA-256
  `0x7f686028f7f58c6612f9f8dee0b65d8cfbd27986a6634392b6c431d8bbce7ed6`

Guard `SG-LIVE-1792250172` used sponsor
`0x02b137dde85c7798f06665dc19449b8797882055`, beneficiary
`0x7eb2a4b4e913df62eae807ef60509b3b7284c7fa`, and designated consumer
`0xf883bce8fcb120f714b147446342d7e4545bc988`.

| Step | Transaction | Verified result |
| --- | --- | --- |
| Fund | `0x9dbe94b58e26f3153a1e99a1386204a65a0c6bdf090d8705a996cfd398066407` | `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS`, 0.001 GEN credited to this guard |
| Accept | `0xb659ca3ba449540e42e1be37ce213945e4e6e891efe7d6ea5e5b0fbfdded96f3` | `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS` |
| Submit | `0x9155e3b719ef6681689c267b96f88946d9fe6dc809bc44fa949e12892e78fb05` | `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS` |
| Review | `0x7fcd65c6cc0fb1f0aa1d500256c50aba4bf4bb55830c0d84cf41493db095284e` | `FINALIZED`, `MAJORITY_AGREE`, `approved`, confidence 92 |
| Settle | `0x26d07a772cd6e62c3d67214b07bdcc021620e890b4257a4251cf2336f82aa491` | `FINALIZED`, unanimous `MAJORITY_AGREE`, GenVM `SUCCESS` |
| Child transfer | `0x858e68adf170c88fc3041998bf03f1c3fff4a52146fb69eea77b6c9487c09568` | `FINALIZED`, recipient credited `1000000000000000` wei |

The canonical post-settlement read reports `status: paid_beneficiary`,
`reason: paid_beneficiary`, `deposit: 0`, and
`settled_amount: 1000000000000000`.

The v0.1.1 lifecycle above was valid for that source, but it is not the
canonical release. v0.2.1 later exposed a persisted-`Address` comparison
regression during a real role transition; v0.2.2 replaces it with canonical
address comparisons. No historical deployment should be used for new guards.

## Historical v0.2.1 — superseded; do not use

- Contract: `0xBDD3542C4BFA58455b75A03D59706538DA0B5543`

This address is retained only as historical context; it is not a current
deployment or source-parity claim.

Its real beneficiary-acceptance attempt exposed a persisted-`Address` runtime
comparison defect: the same EVM address could be represented by distinct
runtime objects and was rejected. The rejected write did not modify escrow
state. v0.2.2 corrected authorization comparisons using canonical address text
and is the only canonical release documented below.

## Historical v0.2.2 — verified; superseded

- Source commit: `f666b362a368906af151bb93822f3c55879b0f17`
- Raw source SHA-256: `54087ad83eb2e639193ae09278eb503b60592b92c23584266d168ebc2d67ed8c`
- Contract: [`0xD57061E923F6E8BD0BCB6a615551388D61bBE8aa`](https://explorer-studio.genlayer.com/address/0xD57061E923F6E8BD0BCB6a615551388D61bBE8aa)
- Deployment transaction: [`0x5e19c1d6f768902c94fd8756535b3835b3ecb110b9c8ff5fec39078ade574025`](https://explorer-studio.genlayer.com/tx/0x5e19c1d6f768902c94fd8756535b3835b3ecb110b9c8ff5fec39078ade574025)
- Deployment result: `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS`
- Source parity: `gen_getContractCode` returned 24,797 deployed bytes; they
  match the 24,797 local source bytes and SHA-256 byte-for-byte.
- `get_info()`: `SpecGuard`, version `0.2.2`, minimum confidence `75`, minimum
  deposit `1000000000000000` wei, maximum text bytes `16000`, maximum image
  bytes `2000000`, and maximum guards per sponsor `64`.

### Live approved settlement

The immutable public artifacts are pinned to Git commit
`d18bea08204c5f22a4ae723d9fb08411ff4dc9b4`:

- [Specification](https://raw.githubusercontent.com/Bibidee/specguard/d18bea08204c5f22a4ae723d9fb08411ff4dc9b4/docs/live-fixtures/v0.1.0/specification.txt): `0x3f5f9f851c59ca98326b40923a4d3c86712b0443509dfa2d996875c6e88310c8`
- [Implementation](https://raw.githubusercontent.com/Bibidee/specguard/d18bea08204c5f22a4ae723d9fb08411ff4dc9b4/docs/live-fixtures/v0.1.0/implementation.txt): `0x4850f97edefab6e62ef1e0046ce920dd69ff8f18317d8524b114538c3ee57ee2`
- [Evidence](https://raw.githubusercontent.com/Bibidee/specguard/d18bea08204c5f22a4ae723d9fb08411ff4dc9b4/docs/live-fixtures/v0.1.0/evidence.txt): `0x7f686028f7f58c6612f9f8dee0b65d8cfbd27986a6634392b6c431d8bbce7ed6`

Guard `SG-V022-LIVE-1792274655413` used sponsor
`0x02b137dde85c7798f06665dc19449b8797882055`, beneficiary
`0x7eb2a4b4e913df62eae807ef60509b3b7284c7fa`, and designated consumer
`0xf883bce8fcb120f714b147446342d7e4545bc988`.

| Step | Transaction | Verified result |
| --- | --- | --- |
| Fund | [`0x85ad9acbfeae56bb975138ea773d2b9058a257f0a6b28c50e18800eba93bf764`](https://explorer-studio.genlayer.com/tx/0x85ad9acbfeae56bb975138ea773d2b9058a257f0a6b28c50e18800eba93bf764) | `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS`, 0.001 GEN credited |
| Accept | [`0x0d3eb3689a00cbe521a7d44778640e7d64395edcaad85dceab51f497c6b60222`](https://explorer-studio.genlayer.com/tx/0x0d3eb3689a00cbe521a7d44778640e7d64395edcaad85dceab51f497c6b60222) | `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS` |
| Submit | [`0x6692527390a115c808c916fec7f3082250ab71476de16ec57723c3e06ca564e0`](https://explorer-studio.genlayer.com/tx/0x6692527390a115c808c916fec7f3082250ab71476de16ec57723c3e06ca564e0) | `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS`; canonical record preserved exact URLs and hashes |
| Review | [`0x9303d71e85f34a7a1a6ceef36c9a5f95b478d138f8956784cff6b9c2b7ab02cb`](https://explorer-studio.genlayer.com/tx/0x9303d71e85f34a7a1a6ceef36c9a5f95b478d138f8956784cff6b9c2b7ab02cb) | `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS`, `approved`, confidence `93` |
| Settle | [`0x09d21b12e1547c6bf2824acaa433ba920fb1f784991918aefc01a30d80dbb60f`](https://explorer-studio.genlayer.com/tx/0x09d21b12e1547c6bf2824acaa433ba920fb1f784991918aefc01a30d80dbb60f) | `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS`; 0.001 GEN dispatched to beneficiary |
| Child transfer | [`0x556714a9903b7a2742a0d00503bb63514252212ede001aeb5247d42462be1291`](https://explorer-studio.genlayer.com/tx/0x556714a9903b7a2742a0d00503bb63514252212ede001aeb5247d42462be1291) | `FINALIZED`, `value_credited: true`, beneficiary received `1000000000000000` wei |

The post-settlement canonical read reports `status: paid_beneficiary`,
`reason: paid_beneficiary`, `deposit: 0`, and
`settled_amount: 1000000000000000`.
