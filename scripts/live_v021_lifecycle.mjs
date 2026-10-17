throw new Error("ARCHIVED: historical v0.2.1 transaction script disabled. It can access local keychain signers and submit funded writes. See docs/DEPLOYMENT.md; do not run.");

import { createHash } from "node:crypto";
import { createRequire } from "node:module";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
import { setTimeout as delay } from "node:timers/promises";

const cliRoot = join(process.env.APPDATA, "npm", "node_modules", "genlayer");
const cliRequire = createRequire(join(cliRoot, "package.json"));
const [{ createClient }, { studionet }, { privateKeyToAccount }] = await Promise.all([
  import(pathToFileURL(cliRequire.resolve("genlayer-js"))),
  import(pathToFileURL(cliRequire.resolve("genlayer-js/chains"))),
  import(pathToFileURL(cliRequire.resolve("viem/accounts"))),
]);
const keytar = cliRequire("keytar");

const address = "0xBDD3542C4BFA58455b75A03D59706538DA0B5543";
const accounts = {
  sponsor: "live-dave",
  beneficiary: "live-alice",
  consumer: "live-bob",
};
const endpoint = "https://studio.genlayer.com/api";
const fixtureCommit = "d18bea08204c5f22a4ae723d9fb08411ff4dc9b4";
const rawUrl = (name) => `https://raw.githubusercontent.com/Bibidee/specguard/${fixtureCommit}/docs/live-fixtures/v0.1.0/${name}`;
const mirrorUrl = (name) => `https://cdn.jsdelivr.net/gh/Bibidee/specguard@${fixtureCommit}/docs/live-fixtures/v0.1.0/${name}`;
const sha256 = (value) => `0x${createHash("sha256").update(value).digest("hex")}`;
const json = (value) => JSON.stringify(value, (_, item) => typeof item === "bigint" ? item.toString() : item);

const clientFor = async (name) => {
  const key = await keytar.getPassword("genlayer-cli", `account:${name}`);
  if (!key) throw new Error(`Unlocked CLI keychain signer unavailable for ${name}`);
  return createClient({ chain: studionet, endpoint, account: privateKeyToAccount(key) });
};
const waitForFinal = async (client, hash) => {
  for (let attempt = 0; attempt < 180; attempt += 1) {
    await delay(10_000);
    const transaction = await client.getTransaction({ hash });
    const status = transaction.statusName || transaction.status_name;
    if (["FINALIZED", "UNDETERMINED", "CANCELED"].includes(status)) return transaction;
  }
  throw new Error(`Timed out waiting for ${hash}`);
};
const execution = (transaction) => transaction.consensus_data?.leader_receipt?.[0]?.execution_result;
const write = async (client, step, functionName, args, value = 0n) => {
  const hash = await client.writeContract({
    address,
    functionName,
    args,
    value,
    consensusMaxRotations: 5,
  });
  const transaction = await waitForFinal(client, hash);
  const result = {
    step,
    functionName,
    hash,
    status: transaction.statusName || transaction.status_name,
    consensus: transaction.result_name || transaction.resultName,
    execution: execution(transaction),
  };
  console.log(json(result));
  if (result.status !== "FINALIZED" || result.execution !== "SUCCESS") {
    throw new Error(`${step} did not finalize with GenVM SUCCESS: ${json(result)}`);
  }
  return { hash, transaction, result };
};

const sponsor = await clientFor(accounts.sponsor);
const beneficiary = await clientFor(accounts.beneficiary);
const consumer = await clientFor(accounts.consumer);
const artifacts = {};
for (const [key, filename] of Object.entries({ specification: "specification.txt", implementation: "implementation.txt", evidence: "evidence.txt" })) {
  const url = rawUrl(filename);
  const response = await fetch(url, { redirect: "error" });
  if (!response.ok) throw new Error(`${filename} returned HTTP ${response.status}`);
  const bytes = Buffer.from(await response.arrayBuffer());
  new TextDecoder("utf-8", { fatal: true }).decode(bytes);
  artifacts[key] = { url, mirror: mirrorUrl(filename), hash: sha256(bytes), bytes: bytes.length };
  console.log(json({ step: "artifact_verified", key, url, hash: artifacts[key].hash, bytes: artifacts[key].bytes }));
}

const now = Math.floor(Date.now() / 1000);
const guardId = `SG-V021-LIVE-${Date.now()}`;
const brief = "The implementation must state exactly: Security regression tests passed.";
console.log(json({
  step: "parameters",
  chainId: studionet.id,
  contract: address,
  guardId,
  sponsor: sponsor.account.address,
  beneficiary: beneficiary.account.address,
  consumer: consumer.account.address,
  deliverBy: now + 7200,
  reviewWindow: 7200,
  brief,
  artifacts,
}));

const created = await write(sponsor, "create", "create_guard", [
  guardId,
  beneficiary.account.address,
  consumer.account.address,
  brief,
  artifacts.specification.url,
  artifacts.specification.hash,
  BigInt(now + 7200),
  7200n,
], 1_000_000_000_000_000n);
let state = await sponsor.readContract({ address, functionName: "get_guard", args: [guardId], transactionHashVariant: "latest-final" });
console.log(json({ step: "funded_guard", state }));
if (state.status !== "funded" || state.deposit !== 1_000_000_000_000_000n) throw new Error(`Unexpected funded guard: ${json(state)}`);

const accepted = await write(beneficiary, "accept", "accept_guard", [guardId]);
const mirrored = await write(beneficiary, "mirror", "set_spec_mirror", [guardId, artifacts.specification.mirror]);
const submitted = await write(beneficiary, "submit", "submit_implementation", [
  guardId,
  "text",
  artifacts.implementation.url,
  artifacts.implementation.hash,
  artifacts.evidence.url,
  artifacts.evidence.hash,
  "The committed implementation states the exact required security regression result, and the committed independent evidence confirms it.",
]);
state = await sponsor.readContract({ address, functionName: "get_guard", args: [guardId], transactionHashVariant: "latest-final" });
console.log(json({ step: "submitted_guard", state }));
if (state.status !== "submitted") throw new Error(`Guard was not submitted: ${json(state)}`);

const reviewed = await write(consumer, "review", "review", [guardId]);
state = await sponsor.readContract({ address, functionName: "get_guard", args: [guardId], transactionHashVariant: "latest-final" });
console.log(json({ step: "reviewed_guard", state }));
if (state.status !== "approved") {
  console.log(json({ step: "safe_stop", reason: "Live semantic review did not approve; no settlement sent", finalState: state }));
  process.exitCode = 2;
} else {
  const settled = await write(consumer, "settle", "settle_approved", [guardId]);
  state = await sponsor.readContract({ address, functionName: "get_guard", args: [guardId], transactionHashVariant: "latest-final" });
  console.log(json({
    step: "settled_guard",
    createTx: created.hash,
    acceptTx: accepted.hash,
    mirrorTx: mirrored.hash,
    submitTx: submitted.hash,
    reviewTx: reviewed.hash,
    settleTx: settled.hash,
    state,
  }));
  if (state.status !== "paid_beneficiary" || state.deposit !== 0n || state.settled_amount !== 1_000_000_000_000_000n) {
    throw new Error(`Unexpected post-settlement state: ${json(state)}`);
  }
}
