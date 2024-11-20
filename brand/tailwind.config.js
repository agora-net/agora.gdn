/** @type {import('tailwindcss').Config} */
module.exports = {
	content: ["../**/*.{html,js,css,svg}", "!../**/node_modules"],
	theme: {
		extend: {},
		fontFamily: {
			sans: ["Figtree", "sans-serif"],
		},
	},
	plugins: [require("daisyui")],
	daisyui: {
		themes: [
			{
				light: {
					...require("daisyui/src/theming/themes").light,
					primary: "#fc8b37",
					secondary: "#000932",
					"secondary-content": "#f8f9fa",
				},
			},
			{
				dark: {
					...require("daisyui/src/theming/themes").dark,
					primary: "#fc8b37",
					secondary: "#000932",
					"secondary-content": "#f8f9fa",
				},
			},
		],
	},
};
