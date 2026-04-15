import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';

const DOWNLOAD_DIR = path.resolve('D:\\scraping\\easylaw_downloads');
if (!fs.existsSync(DOWNLOAD_DIR)) {
    fs.mkdirSync(DOWNLOAD_DIR, { recursive: true });
}

// Categories to search
const CATEGORY_PATTERNS = {
  'criminal-law': [
    'criminal', 'crl', 'murder', 'homicide', 'attempt to murder', 'theft', 'robbery', 'dacoity',
    'fraud', 'cheating', 'narcotics', 'cybercrime', 'assault', 'hurt case', 'kidnapping', 'abduction'
  ],
  'bail-matters': ['bail', 'pre-arrest bail', 'post-arrest bail', 'bail cancellation'],
  'civil-law': ['civil', 'property dispute', 'contract dispute', 'recovery of money', 'damages', 'compensation', 'specific performance'],
  'family-law': ['family', 'divorce', 'talaq', 'khula', 'child custody', 'maintenance', 'naqfa', 'guardianship', 'dowry'],
  'constitutional-matters': ['writ petition', 'fundamental rights', 'public interest litigation', 'constitutional'],
  'service-employment-law': ['job termination', 'promotion', 'transfer', 'pension dispute', 'service matter', 'employment'],
  'banking-finance': ['loan default', 'recovery suit', 'mortgage', 'banking', 'finance'],
  'taxation-law': ['income tax', 'sales tax', 'customs duty', 'taxation', 'tax'],
  'anti-corruption-nab': ['corruption', 'nab', 'assets beyond means', 'money laundering'],
  'anti-terrorism': ['terrorism', 'anti-terrorism', 'bomb blast', 'extremism'],
  'rent-cases': ['eviction', 'rent dispute', 'landlord', 'tenant', 'rent case'],
  'land-revenue': ['land ownership', 'agricultural land', 'revenue record', 'land dispute', 'revenue'],
  'company-corporate-law': ['company dispute', 'shareholder', 'secp', 'corporate'],
  'intellectual-property': ['trademark', 'copyright', 'patent', 'intellectual property', 'ip'],
  'election-law': ['election dispute', 'candidate eligibility', 'election'],
  'environmental-law': ['pollution', 'environmental protection', 'environmental'],
  'consumer-protection': ['consumer complaint', 'defective product', 'consumer protection'],
  'immigration-foreigners': ['visa issue', 'deportation', 'immigration', 'foreigner'],
  'military-armed-forces': ['court martial', 'armed forces', 'military'],
  'miscellaneous-other': ['contempt of court', 'execution petition', 'review petition', 'appeal']
};

const KEYWORDS = ['naqfa'];

const STATE_FILE = path.resolve('D:\\scraping\\easylaw_state.json');

function loadState() {
    if (fs.existsSync(STATE_FILE)) {
        try {
            return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
        } catch (e) {
            return { keywordIndex: 0, pageNum: 1 };
        }
    }
    return { keywordIndex: 0, pageNum: 1 };
}

function saveState(keywordIndex, pageNum) {
    fs.writeFileSync(STATE_FILE, JSON.stringify({ keywordIndex, pageNum }, null, 2));
}

async function run() {
    console.log('🚀 Starting EasyLaw Scraper...');
    
    const state = loadState();
    let startKeywordIndex = state.keywordIndex || 0;
    let startPageNum = state.pageNum || 1;
    
    console.log(`📌 Resuming from keyword index: ${startKeywordIndex}, page: ${startPageNum}`);

    // Launch browser (disabling headless temporarily to allow debugging or captcha solving if needed)
    const browser = await puppeteer.launch({ 
        headless: false, 
        defaultViewport: null,
        protocolTimeout: 600000 // Raise default Protocol Timeout on underlying CDPSession to 10 mins
    });

    const page = await browser.newPage();

    for (let k = startKeywordIndex; k < KEYWORDS.length; k++) {
        const keyword = KEYWORDS[k];
        console.log(`\n🔎 Searching for keyword: "${keyword}" (${k + 1}/${KEYWORDS.length})`);
        try {
            await page.goto("https://www.easylaw.ai/", { waitUntil: "networkidle2", timeout: 60000 });
            
            // Wait for and enter query
            await page.waitForSelector("textarea[name='Query'], #comment2", { timeout: 20000 });
            await page.evaluate(() => {
                const q = document.querySelector("textarea[name='Query'], #comment2");
                if (q) q.value = "";
            });
            await page.type("textarea[name='Query'], #comment2", keyword, { delay: 15 });
            
            // Submit the search form
            await Promise.all([
                page.waitForNavigation({ waitUntil: "networkidle2", timeout: 60000 }).catch(() => null),
                page.click("input#myBtn, input[type='submit'].btn-success")
            ]);
            
            let hasPages = true;
            let pageNum = 1;
            const MAX_PAGES = 50; // Getting as many as possible per category

            while (hasPages && pageNum <= MAX_PAGES) {
                // Determine if we need to fast-forward
                if (k === startKeywordIndex && pageNum < startPageNum) {
                    console.log(`⏩ Fast-forwarding past page ${pageNum}...`);
                    try {
                        await page.waitForSelector("a.paginate_button.next", { timeout: 15000 });
                    } catch(e) {}
                                    
                    const nextBtn = await page.$("a.paginate_button.next:not(.disabled)");
                    if (nextBtn) {
                        try {
                            const [resp] = await Promise.all([
                                // Usually updates via ajax but just in case
                                new Promise(r => setTimeout(r, 4000)),
                                nextBtn.click()
                            ]);
                            pageNum++;
                            continue;
                        } catch (e) {
                            console.log(`⚠️ Fast-forward click failed at page ${pageNum}:`, e.message);
                            break;
                        }
                    } else {
                        break;
                    }
                }
                
                // Save current state securely BEFORE pulling PDFs
                saveState(k, pageNum);

                console.log(`📑 Processing page ${pageNum} for "${keyword}"...`);
                
                // Wait for the results table to load
                try {
                    await page.waitForSelector("#myTable tbody tr form button[name='details']", { timeout: 15000 });
                } catch (e) {
                    console.log('⚠️ No results or table not found (might be end of results).');
                    break;
                }

                // Gather details IDs for the current page
                const buttonsInfo = await page.evaluate(() => {
                    return Array.from(document.querySelectorAll("#myTable tbody tr form button[name='details']")).map((btn, i) => ({
                        index: i,
                        val: btn.value
                    }));
                });

                console.log(`Found ${buttonsInfo.length} judgments on page ${pageNum}.`);

                const existingFiles = fs.readdirSync(DOWNLOAD_DIR);

                for (const info of buttonsInfo) {
                    // Check if already downloaded
                    if (existingFiles.some(f => f.includes(info.val))) {
                        console.log(`⏩ Skipping judgment ${info.val} (already downloaded)`);
                        continue;
                    }

                    console.log(`📥 Downloading judgment ${info.val}...`);
                    
                    try {
                        const btns = await page.$$("#myTable tbody tr form button[name='details']");
                        const targetBtn = btns[info.index];
                        if (!targetBtn) continue;

                        // Click the button which triggers a popup
                        const [newPage] = await Promise.all([
                            new Promise(resolve => page.once('popup', resolve)),
                            targetBtn.click()
                        ]);

                        if (newPage) {
                            await newPage.bringToFront();
                            await newPage.waitForNavigation({ waitUntil: 'networkidle2', timeout: 30000 }).catch(() => null);
                            await new Promise(r => setTimeout(r, 4000)); // wait for full render
                            
                            // Try to extract citation to make filename cleaner using textContent (much faster than innerText on huge documents to prevent callFunctionOn timeouts)
                            const citation = await newPage.evaluate(() => {
                                const match = document.body.textContent.match(/Journal\s+([^\n]+)/i);
                                return match ? match[1].trim().replace(/[^a-z0-9]/gi, '_') : '';
                            });

                            // Try checking the exact final filename, some instances exist with multiple IDs under the same namespace but we want absolute uniqueness
                            const pdfName = citation ? `EasyLaw_${citation}_${info.val}.pdf` : `EasyLaw_${info.val}.pdf`;
                            const finalPath = path.join(DOWNLOAD_DIR, pdfName);

                            if (fs.existsSync(finalPath)) {
                                console.log(`⏩ Already downloaded: ${pdfName}`);
                                await newPage.close();
                                await page.bringToFront();
                                continue;
                            }

                            // Save as PDF
                            // Use cdp to set protocol timeout heavily to prevent Runtime.callFunctionOn from failing mid-way on complex pages.
                            const client = await newPage.createCDPSession();
                            await client.send('Runtime.enable');
                            
                            await newPage.pdf({ 
                                path: finalPath, 
                                format: 'A4', 
                                printBackground: true, 
                                margin: { top: '0.4in', right: '0.4in', bottom: '0.4in', left: '0.4in' },
                                timeout: 120000 // Increase timeout drastically to 2 mins for generation
                            });
                            
                            console.log(`✅ Saved: ${pdfName}`);
                            
                            await newPage.close();
                            await page.bringToFront();
                        }
                    } catch (err) {
                        console.error(`❌ Error downloading ${info.val}: ${err.message}`);
                        // ensure we close any potentially stuck popups and keep the session clean
                        const pages = await browser.pages();
                        if (pages.length > 2) { // more than original + results page
                             await pages[pages.length - 1].close().catch(() => null);
                        }
                    }
                }

                // Check for Next page link
                const nextBtn = await page.$("a.paginate_button.next:not(.disabled)");
                if (nextBtn) {
                    try {
                        console.log('🔄 Moving to next page...');
                        await nextBtn.click();
                        // wait for DataTables to update the DOM via AJAX
                        await new Promise(r => setTimeout(r, 5000)); 
                        pageNum++;
                    } catch (e) {
                        console.log('⚠️ Failed to navigate to next page.');
                        hasPages = false;
                    }
                } else {
                    console.log('🔚 Reached the end of pagination for this query.');
                    hasPages = false;
                }
            }

            // Keyword done, reset for next keyword
            if (k === startKeywordIndex) {
                 startPageNum = 1; 
            }
            saveState(k + 1, 1);

        } catch (error) {
            console.error(`❌ Global error processing keyword "${keyword}":`, error.message);
        }
    }

    console.log('🎉 Scraping complete!');
    await browser.close();
}

run().catch(console.error);