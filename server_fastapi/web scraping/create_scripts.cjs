const fs = require('fs');
const path = require('path');

const content = fs.readFileSync('D:\\\\scraping\\\\easylaw_scraper.js', 'utf8');

const categories = [
    'bail-matters', 'civil-law', 'family-law', 'constitutional-matters',
    'service-employment-law', 'banking-finance', 'taxation-law',
    'anti-corruption-nab', 'anti-terrorism', 'rent-cases', 'land-revenue',
    'company-corporate-law', 'intellectual-property', 'election-law',
    'environmental-law', 'consumer-protection', 'immigration-foreigners',
    'military-armed-forces'
];

for (const cat of categories) {
    let newContent = content.replace(
        "const KEYWORDS = CATEGORY_PATTERNS['criminal-law'];",
        `const KEYWORDS = CATEGORY_PATTERNS['${cat}'];`
    );
    newContent = newContent.replace(
        "const STATE_FILE = path.resolve('D:\\\\scraping\\\\easylaw_state.json');",
        `const STATE_FILE = path.resolve('D:\\\\scraping\\\\easylaw_state_${cat}.json');`
    );
    fs.writeFileSync(`D:\\\\scraping\\\\easylaw_scraper_${cat}.js`, newContent);
    console.log(`Created easylaw_scraper_${cat}.js`);
}
