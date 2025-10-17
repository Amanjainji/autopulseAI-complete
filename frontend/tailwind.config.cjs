/** @type {import('tailwindcss').Config} */
module.exports = {
	content: [
		"./index.html",
		"./src/**/*.{js,jsx,ts,tsx}",
	],
	theme: {
		extend: {
			colors: {
				graphite: "#0d0f12",
				card: "rgba(255,255,255,0.04)",
				accent: "#00b4ff",
			},
			fontFamily: {
				sans: ["Inter", "ui-sans-serif", "system-ui"],
			},
			borderColor: {
				subtle: "rgba(255,255,255,0.08)",
			}
		},
	},
	plugins: [],
}
