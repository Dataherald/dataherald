/** @type {import('tailwindcss').Config} */

const primaryColor = "#1C1C1C";

module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      backgroundColor: {
        primary: primaryColor,
      },
      borderColor: {
        primary: primaryColor,
      },
      textColor: {
        primary: primaryColor,
      },
    },
  },
  plugins: [],
};
