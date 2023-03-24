const path = require('path');
const config  = require('newsroom-core/webpack.config');

config.entry.login = path.resolve(__dirname, 'src', 'login.js');
config.entry.reset_password = path.resolve(__dirname, 'src', 'reset-password.js');

module.exports = config;
