const config = {
  "bracketSameLine": true,
  "htmlWhitespaceSensitivity": "ignore",
  plugins:[
    require.resolve("prettier-plugin-jinja-template")
  ],
};

module.exports = config;
