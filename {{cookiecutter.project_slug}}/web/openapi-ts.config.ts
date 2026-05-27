import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
  input: "",
  output: {
    path: "./src/shared/api/generated",
  },
  plugins: ["@hey-api/client-fetch", "@hey-api/sdk", "@hey-api/typescript"],
});
