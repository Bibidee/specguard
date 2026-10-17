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
