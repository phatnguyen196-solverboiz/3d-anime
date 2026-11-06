import { readdir, writeFile, mkdir } from "node:fs/promises";
import { resolve } from "node:path";
import { compileFromFile } from "json-schema-to-typescript";

const schemaDir = resolve("packages/contracts/src/animeflow_contracts/schemas");
const outputDir = resolve("packages/contracts/generated");
await mkdir(outputDir, { recursive: true });
for (const name of (await readdir(schemaDir)).filter((item) => item.endsWith(".schema.json")).sort()) {
  const output = await compileFromFile(resolve(schemaDir, name), {
    bannerComment: "/* Generated from JSON Schema. Do not edit manually. */",
    style: { singleQuote: false, semi: true },
  });
  await writeFile(resolve(outputDir, name.replace(".schema.json", ".d.ts")), output);
}
