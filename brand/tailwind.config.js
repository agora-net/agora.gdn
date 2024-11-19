/** @type {import('tailwindcss').Config} */
module.exports = {
	content: ["../**/templates/*.{html,js,css,svg}", "!../**/node_modules"],
	theme: {
		extend: {},
	},
	plugins: [require("daisyui")],
};
