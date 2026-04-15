const fs = require('fs');
const path = require('path');

const content = fs.readFileSync('D:\\\\scraping\\\\easylaw_scraper.js', 'utf8');

const keywords = ['child custody', 'maintenance', 'naqfa', 'guardianship', 'dowry'];

for (const kw of keywords) {
    const safeKw = kw.replace(/ /g, '-');
    
    // Replace the KEYWORDS definition
    let newContent = content.replace(
        /const KEYWORDS = CATEGORY_PATTERNS\['[^']+'\];/,
        `const KEYWORDS = ['${kw}'];`
    );
    
    // Replace the STATE_FILE definition
    newContent = newContent.replace(
        /const STATE_FILE = path\.resolve\('D:\\\\\\\\scraping\\\\\\\\easylaw_state\.json'\);/,
        `const STATE_FILE = path.resolve('D:\\\\\\\\scraping\\\\\\\\easylaw_state_${safeKw}.json');`
    );
    
    fs.writeFileSync(`D:\\\\scraping\\\\easylaw_scraper_${safeKw}.js`, newContent);
    console.log(`Created easylaw_scraper_${safeKw}.js`);
}
