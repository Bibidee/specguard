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
const key = await keytar.getPassword("genlayer-cli", "account:live-alice");
if (!key) throw new Error("Unlocked CLI keychain signer unavailable for live-alice");

const client = createClient({
  chain: studionet,
  endpoint: "https://studio.genlayer.com/api",
  account: privateKeyToAccount(key),
});
const hash = await client.writeContract({
  address: "0xD57061E923F6E8BD0BCB6a615551388D61bBE8aa",
  functionName: "submit_implementation",
  args: [
    "SG-V022-LIVE-1792274655413",
    "text",
    "https://raw.githubusercontent.com/Bibidee/specguard/d18bea08204c5f22a4ae723d9fb08411ff4dc9b4/docs/live-fixtures/v0.1.0/implementation.txt",
    "0x4850f97edefab6e62ef1e0046ce920dd69ff8f18317d8524b114538c3ee57ee2",
    "https://raw.githubusercontent.com/Bibidee/specguard/d18bea08204c5f22a4ae723d9fb08411ff4dc9b4/docs/live-fixtures/v0.1.0/evidence.txt",
    "0x7f686028f7f58c6612f9f8dee0b65d8cfbd27986a6634392b6c431d8bbce7ed6",
    "The committed implementation states the exact required security regression result, and the committed independent evidence confirms it.",
  ],
  consensusMaxRotations: 5,
});
console.log(JSON.stringify({ hash, signer: client.account.address }));
