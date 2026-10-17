import fsd from "@feature-sliced/steiger-plugin";
import { defineConfig } from "steiger";

export default defineConfig([
	...fsd.configs.recommended,
	{
		// Keep generated modules in the public API rule's graph to check handwritten consumers.
		files: ["./src/shared/api/generated/**"],
		rules: {
			...Object.fromEntries(fsd.plugin.ruleDefinitions.map((rule) => [rule.name, "off"])),
			"fsd/no-public-api-sidestep": "error",
		},
	},
]);
