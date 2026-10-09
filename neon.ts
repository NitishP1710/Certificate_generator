import { defineConfig } from "@neon/config/v1";

export default defineConfig({
  preview: {
    buckets: {
      certificate: { access: "public_read" },
    },
  },
});
