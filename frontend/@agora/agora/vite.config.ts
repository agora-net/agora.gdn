import type { UserConfig } from "vite";

import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";

import fs from "node:fs";

export default {
	base: "/static/",
	server: {
		https: {
			key: fs.readFileSync("/tmp/agora.key"),
			cert: fs.readFileSync("/tmp/agora.crt"),
		},
	},
	build: {
		manifest: "manifest.json",
		outDir: "dist/",
		rollupOptions: {
			input: {
				copyToClipboard: "src/clipboard.ts",
				tailwind: "src/tailwind.css",
				agora: "src/agora.ts",
			},
		},
		modulePreload: {
			polyfill: true,
		},
	},
	plugins: [react(), tailwindcss()],
} satisfies UserConfig;
