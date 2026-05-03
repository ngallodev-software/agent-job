import { CopilotClient } from "@github/copilot-sdk";

async function main() {
  const argv = process.argv.slice(2);
  const tokenArgIndex = argv.findIndex((arg) => arg === "--token" || arg === "--github-token");
  const githubToken =
    tokenArgIndex >= 0 ? argv[tokenArgIndex + 1] : process.env.GITHUB_TOKEN || process.env.GH_TOKEN;

  const client = new CopilotClient();
  await client.start();

  try {
    let models;
    if (githubToken) {
      const response = await client.rpc.models.list({ auth: githubToken });
      models = response?.models;
    } else {
      try {
        models = await client.listModels();
      } catch {
        const response = await client.rpc.models.list();
        models = response?.models;
      }
    }

    const output = models.map((model) => ({
      id: model.id,
      name: model.name,
      multiplier:
        model.billing && typeof model.billing.multiplier === "number" ? model.billing.multiplier : 1,
      supports: model.capabilities?.supports ?? {},
      limits: model.capabilities?.limits ?? {},
      policy: model.policy ?? null,
      supportedReasoningEfforts: model.supportedReasoningEfforts ?? null,
      defaultReasoningEffort: model.defaultReasoningEffort ?? null,
    }));

    console.log(JSON.stringify(output, null, 2));
  } catch (error) {
    console.error(JSON.stringify({ error: String(error && (error.message || error)) }));
    process.exit(2);
  } finally {
    await client.stop();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
