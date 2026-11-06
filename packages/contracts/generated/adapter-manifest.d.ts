/* Generated from JSON Schema. Do not edit manually. */

export interface AdapterManifest {
  id: string;
  version: string;
  contract_version: "1.0.0";
  status: "planned" | "experimental" | "supported" | "disabled";
  capabilities: string[];
  supported_os: ("windows" | "macos" | "linux")[];
  runtime: string;
  network: "none" | "optional" | "required";
  determinism: "deterministic" | "seeded" | "nondeterministic" | "unknown";
  license: {
    code: string;
    models: string;
    review_status: "not_reviewed" | "reviewed" | "restricted";
  };
  requirements?: {
    [k: string]: unknown;
  };
  documentation_url?: string;
}
