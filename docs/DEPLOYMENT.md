# Deployment status

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

## Canonical v0.1.1 — verified

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

## v0.2.1 remediation candidate — not deployed

This repository also contains a post-v0.1.1 remediation candidate. It changes
storage and public methods, so it requires a fresh Studionet deployment and
new source-parity proof before any address may be called canonical. No existing
v0.1.1 guard or balance is modified by this candidate.
