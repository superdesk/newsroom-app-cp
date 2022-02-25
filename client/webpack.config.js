const path = require('path');
const config  = require('newsroom-core/webpack.config');

config.entry.login = path.resolve(__dirname, 'src', 'login.js');

module.exports = config;
