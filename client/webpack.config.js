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
const defines = Object.fromEntries(
  KEYS.map((k) => [
    `process.env.${k}`,
    JSON.stringify(process.env[k] ?? parsed[k]),
  ]),
);

config.entry.home_js = [
  config.entry.home_js,
  "./assets/auth/pr-manager-sso.ts",
];
config.entry.firebase_login_js = "./assets/auth/firebase/login.ts";

config.plugins = [...(config.plugins || []), new webpack.DefinePlugin(defines)];

module.exports = config;
