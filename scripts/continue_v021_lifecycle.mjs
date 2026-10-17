throw new Error("ARCHIVED: historical v0.2.1 transaction script disabled. It can access local keychain signers and submit writes. See docs/DEPLOYMENT.md; do not run.");

import { createRequire } from "node:module";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
import { setTimeout as delay } from "node:timers/promises";

const guardId = process.argv[2];
if (!guardId) throw new Error("Usage: node scripts/continue_v021_lifecycle.mjs <guard-id>");
const contract = "0xBDD3542C4BFA58455b75A03D59706538DA0B5543";
const fixtureCommit = "d18bea08204c5f22a4ae723d9fb08411ff4dc9b4";
const root = "https://raw.githubusercontent.com/Bibidee/specguard";
const raw = (name) => `${root}/${fixtureCommit}/docs/live-fixtures/v0.1.0/${name}`;
const mirror = `https://cdn.jsdelivr.net/gh/Bibidee/specguard@${fixtureCommit}/docs/live-fixtures/v0.1.0/specification.txt`;
const hashes = {
  implementation: "0x4850f97edefab6e62ef1e0046ce920dd69ff8f18317d8524b114538c3ee57ee2",
  evidence: "0x7f686028f7f58c6612f9f8dee0b65d8cfbd27986a6634392b6c431d8bbce7ed6",
};
const cliRoot = join(process.env.APPDATA, "npm", "node_modules", "genlayer");
const cliRequire = createRequire(join(cliRoot, "package.json"));
const [{ createClient }, { studionet }, { privateKeyToAccount }] = await Promise.all([
  import(pathToFileURL(cliRequire.resolve("genlayer-js"))),
  import(pathToFileURL(cliRequire.resolve("genlayer-js/chains"))),
  import(pathToFileURL(cliRequire.resolve("viem/accounts"))),
]);
const keytar = cliRequire("keytar");
const json = (value) => JSON.stringify(value, (_, item) => typeof item === "bigint" ? item.toString() : item);
const clientFor = async (name) => {
  const key = await keytar.getPassword("genlayer-cli", `account:${name}`);
  if (!key) throw new Error(`Unlocked CLI keychain signer unavailable for ${name}`);
  return createClient({ chain: studionet, endpoint: "https://studio.genlayer.com/api", account: privateKeyToAccount(key) });
};
const sponsor = await clientFor("live-dave");
const beneficiary = await clientFor("live-alice");
const consumer = await clientFor("live-bob");
const wait = async (client, hash) => {
  for (let attempt = 0; attempt < 180; attempt += 1) {
    await delay(10_000);
    const transaction = await client.getTransaction({ hash });
    const status = transaction.statusName || transaction.status_name;
    if (["FINALIZED", "UNDETERMINED", "CANCELED"].includes(status)) return transaction;
  }
  throw new Error(`Timed out waiting for ${hash}`);
};
const write = async (client, step, functionName, args) => {
  const hash = await client.writeContract({ address: contract, functionName, args, consensusMaxRotations: 5 });
  const transaction = await wait(client, hash);
  const result = {
    step, hash, status: transaction.statusName || transaction.status_name,
    consensus: transaction.result_name || transaction.resultName,
    execution: transaction.consensus_data?.leader_receipt?.[0]?.execution_result,
  };
  console.log(json(result));
  if (result.status !== "FINALIZED" || result.execution !== "SUCCESS") throw new Error(`${step} failed: ${json(result)}`);
  return result;
};
const read = () => sponsor.readContract({ address: contract, functionName: "get_guard", args: [guardId], transactionHashVariant: "latest-final" });

let state = await read();
console.log(json({ step: "starting_state", state }));
if (state.status !== "funded") throw new Error(`Expected funded guard, found ${state.status}`);
if (state.beneficiary.toLowerCase() !== beneficiary.account.address.toLowerCase() || state.consumer.toLowerCase() !== consumer.account.address.toLowerCase()) {
  throw new Error("Stored roles do not match designated unlocked accounts");
}
const accepted = await write(beneficiary, "accept", "accept_guard", [guardId]);
const mirrored = await write(beneficiary, "mirror", "set_spec_mirror", [guardId, mirror]);
const submitted = await write(beneficiary, "submit", "submit_implementation", [
  guardId, "text", raw("implementation.txt"), hashes.implementation, raw("evidence.txt"), hashes.evidence,
  "The committed implementation states the exact required security regression result, and the committed independent evidence confirms it.",
]);
state = await read();
console.log(json({ step: "submitted_state", state }));
if (state.status !== "submitted") throw new Error(`Expected submitted guard, found ${state.status}`);
const reviewed = await write(consumer, "review", "review", [guardId]);
state = await read();
console.log(json({ step: "reviewed_state", state }));
if (state.status !== "approved") {
  console.log(json({ step: "safe_stop", reason: "semantic review did not approve; settlement withheld", finalState: state }));
  process.exitCode = 2;
} else {
  const settled = await write(consumer, "settle", "settle_approved", [guardId]);
  state = await read();
  console.log(json({ step: "final_state", accepted, mirrored, submitted, reviewed, settled, state }));
  if (state.status !== "paid_beneficiary" || BigInt(state.deposit) !== 0n || BigInt(state.settled_amount) !== 1_000_000_000_000_000n) {
    throw new Error(`Unexpected terminal state: ${json(state)}`);
  }
}
