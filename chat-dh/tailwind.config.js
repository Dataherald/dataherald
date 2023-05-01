/** @type {import('tailwindcss').Config} */

const COLORS = {
  primary: "#3931D8",
  secondary: "#24205E",
  ["secondary-dark"]: "#1c1c1c",
};

const COLOR_CONFIG = {
  primary: COLORS.primary,
  secondary: COLORS.secondary,
  ["secondary-dark"]: COLORS["secondary-dark"],
};

module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      backgroundColor: COLOR_CONFIG,
      borderColor: COLOR_CONFIG,
      textColor: COLOR_CONFIG,
      backgroundImage: (theme) => ({
        "progress-gradient": "linear-gradient(to right, #3931D8, #C6C7F8)",
      }),
    },
  },
  plugins: [],
};
