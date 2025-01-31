import type { UserConfig } from "vite";

import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";

import fs from "node:fs";

export default {
	base: "/static/",
	server: {
		https: {
			key: fs.readFileSync("../../../certs/localhost.key"),
			cert: fs.readFileSync("../../../certs/localhost.crt"),
		},
	},
	build: {
		manifest: "manifest.json",
		outDir: "dist/",
		rollupOptions: {
			input: {
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
