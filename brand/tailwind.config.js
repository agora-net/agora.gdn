/** @type {import('tailwindcss').Config} */

const defaultTheme = require("tailwindcss/defaultTheme");

module.exports = {
	content: ["../**/*.{html,js,css,svg}", "!./node_modules"],
	theme: {
		extend: {},
		fontFamily: {
			sans: ['"Figtree Variable"', ...defaultTheme.fontFamily.sans],
		},
	},
	plugins: [require("daisyui"), require("@tailwindcss/typography")],
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
