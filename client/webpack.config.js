const config = require("newsroom-core/webpack.config");
const dotenv = require("dotenv");
const webpack = require("webpack");

const KEYS = [
  "AUTH0_DOMAIN",
  "AUTH0_CLIENT_ID",
  "AUTH0_REDIRECT_URI",
  "AUTH0_FIREBASE_CONNECTION",
];

const parsed = dotenv.config().parsed ?? {};
const env = KEYS.reduce((acc, key) => {
  if (parsed[key] !== undefined) {
    acc[key] = parsed[key];
  }
  return acc;
}, {});

config.entry.home_js = [
  config.entry.home_js,
  "./assets/auth/pr-manager-sso.ts",
];
config.entry.firebase_login_js = "./assets/auth/firebase/login.ts";

config.plugins = [
  ...(config.plugins || []),
  new webpack.DefinePlugin({
    "process.env": JSON.stringify(env),
  }),
];

module.exports = config;
