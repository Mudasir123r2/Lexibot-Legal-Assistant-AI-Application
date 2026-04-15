const fs = require('fs');
const cheerio = require('cheerio');
const html = fs.readFileSync('pls_dashboard.html', 'utf8');
const $ = cheerio.load(html);
console.log($('form').html());
