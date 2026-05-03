import { execFileSync } from "node:child_process";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const fetchScript = join(here, "fetch-models.mjs");
const rawPath = join(here, "available_models.raw.json");
const templatePath = join(here, "available-models.template.json");
const overridesPath = join(here, "available-models.md");
const jsonlPath = join(here, "available_models.copilot.jsonl");

function inferProvider(modelId) {
  if (modelId.startsWith("claude-")) {
    return "anthropic";
  }
  if (modelId.startsWith("gpt-") || modelId.startsWith("o")) {
    return "openai";
  }
  return "unknown";
}

function normalizeModelId(raw) {
  return raw.trim().toLowerCase().replace(/\s+/g, "-");
}

function parseMultiplier(raw) {
  const cleaned = raw.trim().replace(/x$/i, "");
  const value = Number.parseFloat(cleaned);
  if (Number.isNaN(value)) {
    throw new Error(`invalid multiplier: ${raw}`);
  }
  return value;
}

function parseTier(raw) {
  return raw.trim().toLowerCase().replace(/\s+tier$/i, "");
}

function parseRecommended(parts) {
  return parts.some((part) => /\b(recommended|recomended|preferred)\b/i.test(part));
}

function parseOverridesMarkdown(text) {
  const overrides = new Map();
  for (const line of text.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) {
      continue;
    }
    const parts = trimmed.split(",").map((part) => part.trim()).filter(Boolean);
    if (parts.length < 3) {
      continue;
    }
    const modelId = normalizeModelId(parts[0]);
    overrides.set(modelId, {
      token_cost_multiplier: parseMultiplier(parts[1]),
      tier: parseTier(parts[2]),
      recomended: parseRecommended(parts.slice(3)),
    });
  }
  return overrides;
}

function fetchRawModels() {
  const stdout = execFileSync("node", [fetchScript], {
    cwd: here,
    env: process.env,
    encoding: "utf8",
    maxBuffer: 8 * 1024 * 1024,
  });
  return JSON.parse(stdout);
}

function buildTemplate(rawModels, overrides) {
  return rawModels
    .filter((model) => model.id !== "auto")
    .map((model) => {
      const modelId = String(model.id);
      const override = overrides.get(modelId) || {};
      return {
        model_id: modelId,
        name: model.name ?? modelId,
        provider: inferProvider(modelId),
        tier: override.tier ?? null,
        token_cost_multiplier: override.token_cost_multiplier ?? model.multiplier ?? null,
        recomended: override.recomended ?? false,
      };
    });
}

function buildJsonl(rawModels, overrides) {
  return (
    rawModels
      .filter((model) => model.id !== "auto")
      .map((model) => {
        const modelId = String(model.id);
        const override = overrides.get(modelId) || {};
        return {
          model_id: modelId,
          name: model.name ?? modelId,
          provider: inferProvider(modelId),
          tier: override.tier ?? null,
          token_cost_multiplier: override.token_cost_multiplier ?? model.multiplier ?? null,
          recomended: override.recomended ?? false,
          supports: model.supports ?? {},
          limits: model.limits ?? {},
          policy_state: model.policy?.state ?? null,
          supported_reasoning_efforts: model.supportedReasoningEfforts ?? null,
          default_reasoning_effort: model.defaultReasoningEffort ?? null,
        };
      })
      .map((row) => JSON.stringify(row))
      .join("\n") + "\n"
  );
}

function main() {
  mkdirSync(here, { recursive: true });
  const rawModels = fetchRawModels();
  writeFileSync(rawPath, `${JSON.stringify(rawModels, null, 2)}\n`, "utf8");

  const overridesText = readFileSync(overridesPath, "utf8");
  const overrides = parseOverridesMarkdown(overridesText);

  const template = buildTemplate(rawModels, overrides);
  writeFileSync(templatePath, `${JSON.stringify(template, null, 2)}\n`, "utf8");

  const jsonl = buildJsonl(rawModels, overrides);
  writeFileSync(jsonlPath, jsonl, "utf8");

  process.stdout.write(
    [
      `raw_saved=${rawPath}`,
      `template_saved=${templatePath}`,
      `jsonl_saved=${jsonlPath}`,
      `model_count=${template.length}`,
    ].join("\n") + "\n",
  );
}

main();
