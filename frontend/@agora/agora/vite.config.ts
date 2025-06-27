import type { UserConfig } from "vite";

import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";

import fs from "node:fs";

const isDev = process.env.NODE_ENV === "development";

const https = isDev ? {
	key: fs.readFileSync("/tmp/agora.key"),
	cert: fs.readFileSync("/tmp/agora.crt"),
} : undefined;

export default {
	base: "/static/",
	server: {
		https,
	},
	build: {
		manifest: "manifest.json",
		outDir: "dist/",
		rollupOptions: {
			input: {
				copyToClipboard: "src/clipboard.ts",
				tailwind: "src/tailwind.css",
				agora: "src/agora.ts",
				newsletter: "src/newsletter.tsx",
			},
		},
		modulePreload: {
			polyfill: true,
		},
	},
	plugins: [react(), tailwindcss()],
} satisfies UserConfig;
