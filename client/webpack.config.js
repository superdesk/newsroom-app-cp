const config = require("newsroom-core/webpack.config");
const dotenv = require("dotenv");
const webpack = require("webpack");

config.entry.home_js = [
  config.entry.home_js,
  "./assets/auth/pr-manager-sso.ts",
];
config.entry.firebase_login_js = "./assets/auth/firebase/login.ts";

config.plugins = [
  ...(config.plugins || []),
  new webpack.DefinePlugin({
    "process.env": JSON.stringify(dotenv.config().parsed),
  }),
];

module.exports = config;
