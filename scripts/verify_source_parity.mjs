import crypto from "node:crypto";
import fs from "node:fs/promises";

const address = process.argv[2];
const deploymentTx = process.argv[3];
if (!address || !deploymentTx) {
  throw new Error("Usage: node scripts/verify_source_parity.mjs <address> <deployment-tx>");
}

const endpoint = "https://studio.genlayer.com/api";
const rpc = async (method, params) => {
  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ jsonrpc: "2.0", id: 1, method, params }),
  });
  if (!response.ok) throw new Error(`${method}: HTTP ${response.status}`);
  return response.json();
};

const finality = await rpc("gen_getTransactionStatus", [deploymentTx]);
if (finality.result !== "FINALIZED") {
  throw new Error(`Deployment is not FINALIZED: ${JSON.stringify(finality)}`);
}
let code = await rpc("gen_getContractCode", [{ address, status: "finalized" }]);
let retrieval = "finalized code query";
if (code.error) {
  code = await rpc("gen_getContractCode", [address]);
  retrieval = "legacy code query after finalized deployment proof";
}
if (code.error || typeof code.result !== "string") {
  throw new Error(`Source retrieval failed: ${JSON.stringify(code)}`);
}
const local = await fs.readFile("contracts/specguard.py");
const deployed = Buffer.from(code.result, "base64");
const sha256 = (value) => crypto.createHash("sha256").update(value).digest("hex");
const result = {
  address,
  deployment: "FINALIZED",
  retrieval,
  localBytes: local.length,
  deployedBytes: deployed.length,
  localSha256: sha256(local),
  deployedSha256: sha256(deployed),
  parity: local.equals(deployed),
};
console.log(JSON.stringify(result, null, 2));
if (!result.parity) process.exitCode = 1;
