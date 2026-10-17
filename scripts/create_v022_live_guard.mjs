throw new Error("ARCHIVED: completed v0.2.2 funded-guard script disabled. It can access a local keychain signer and submit a payable write. See docs/DEPLOYMENT.md; do not run.");

import { createHash } from "node:crypto";
import { createRequire } from "node:module";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const cliRoot = join(process.env.APPDATA, "npm", "node_modules", "genlayer");
const cliRequire = createRequire(join(cliRoot, "package.json"));
const [{ createClient }, { studionet }, { privateKeyToAccount }] = await Promise.all([
  import(pathToFileURL(cliRequire.resolve("genlayer-js"))),
  import(pathToFileURL(cliRequire.resolve("genlayer-js/chains"))),
  import(pathToFileURL(cliRequire.resolve("viem/accounts"))),
]);
const keytar = cliRequire("keytar");
const key = await keytar.getPassword("genlayer-cli", "account:live-dave");
if (!key) throw new Error("Unlocked CLI keychain signer unavailable for live-dave");
const client = createClient({ chain: studionet, endpoint: "https://studio.genlayer.com/api", account: privateKeyToAccount(key) });
const contract = "0xD57061E923F6E8BD0BCB6a615551388D61bBE8aa";
const fixtureCommit = "d18bea08204c5f22a4ae723d9fb08411ff4dc9b4";
const url = `https://raw.githubusercontent.com/Bibidee/specguard/${fixtureCommit}/docs/live-fixtures/v0.1.0/specification.txt`;
const expected = "0x3f5f9f851c59ca98326b40923a4d3c86712b0443509dfa2d996875c6e88310c8";
const response = await fetch(url, { redirect: "error" });
if (!response.ok) throw new Error(`Specification returned HTTP ${response.status}`);
const raw = Buffer.from(await response.arrayBuffer());
const actual = `0x${createHash("sha256").update(raw).digest("hex")}`;
if (actual !== expected) throw new Error("Specification raw-byte SHA-256 mismatch");
new TextDecoder("utf-8", { fatal: true }).decode(raw);
const guardId = `SG-V022-LIVE-${Date.now()}`;
const now = Math.floor(Date.now() / 1000);
const hash = await client.writeContract({
  address: contract,
  functionName: "create_guard",
  args: [
    guardId,
    "0x7eb2a4b4e913df62eae807ef60509b3b7284c7fa",
    "0xf883bce8fcb120f714b147446342d7e4545bc988",
    "The implementation must state exactly: Security regression tests passed.",
    url,
    actual,
    BigInt(now + 7200),
    7200n,
  ],
  value: 1_000_000_000_000_000n,
  consensusMaxRotations: 5,
});
console.log(JSON.stringify({ guardId, hash, contract, sponsor: client.account.address, specificationUrl: url, specificationHash: actual, deliverBy: now + 7200 }));
