import type { UserConfig } from "vite";

import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";

export default {
	base: "/static/",
	build: {
		manifest: "manifest.json",
		outDir: "dist/",
		rollupOptions: {
			input: {
				tailwind: "src/tailwind.css",
			},
		},
	},
	plugins: [react(), tailwindcss()],
} satisfies UserConfig;
