const path = require('path');
const config  = require('newsroom-core/webpack.config');

config.entry.login = path.resolve(__dirname, 'src', 'login.ts');
config.entry.reset_password = path.resolve(__dirname, 'src', 'reset-password.ts');

// Override `newsroom_js` from core to use `./src/index.ts` instead
config.entry.newsroom_js = path.resolve(__dirname, 'src', 'index.ts');

module.exports = config;
