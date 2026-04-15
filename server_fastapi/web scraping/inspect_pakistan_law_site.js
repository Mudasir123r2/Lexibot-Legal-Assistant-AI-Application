/**
 * Pakistan Law Site - Page Structure Inspector
 * This diagnostic script inspects the actual page HTML to find correct selectors
 */

import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const CREDENTIALS = {
  username: 'Sandr',
  password: 'Egohurt'
};

const BASE_URL = 'https://www.pakistanlawsite.com';
const LOGIN_URL = `${BASE_URL}/Login/MainPage`;
const MAIN_PAGE = `${BASE_URL}/Login/Check`;

const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function main() {
  let browser;
  
  try {
    console.log('🔍 Starting Page Structure Analysis...\n');
    
    browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    page.setDefaultTimeout(60000);
    
    // Step 1: Login
    console.log('🔐 Step 1: Logging in...');
    await page.goto(LOGIN_URL, { waitUntil: 'networkidle2' });
    
    // Fill login form  
    await page.waitForSelector('input[type="password"]', { timeout: 10000 });
    
    const userInput = await page.$('input[type="text"], input[type="email"], input[name*="User"], input[name*="Email"]');
    if (userInput) {
      await userInput.type(CREDENTIALS.username, { delay: 30 });
    }
    
    await page.type('input[type="password"]', CREDENTIALS.password, { delay: 30 });
    await page.click('button[type="submit"]');
    
    try {
      await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 });
    } catch (e) {
      console.log('⚠️ Navigation timeout, continuing...');
    }
    
    await wait(2000);
    const finalURL = page.url();
    console.log(`✅ After login, final URL: ${finalURL}\n`);
    
    // If still on MainPage after login, something went wrong - navigate to /Home or dashboard
    if (finalURL.includes('MainPage')) {
      console.log('⚠️ Still on MainPage after login attempt, looking for dashboard links...');
      const dashboardLinks = await page.evaluate(() => {
        const links = [];
        document.querySelectorAll('a[href], button').forEach(el => {
          const href = el.href || '';
          const text = (el.innerText || el.textContent || '').toLowerCase();
          if (href && (text.includes('home') || text.includes('dashboard') || text.includes('law') || text.includes('judgment') || href.includes('Home') || href.includes('home'))) {
            links.push({ text: el.innerText || el.textContent, href });
          }
        });
        return links;
      });
      
      console.log(`Found ${dashboardLinks.length} dashboard-related links`);
      dashboardLinks.forEach((link, i) => {
        if (i < 10) {
          console.log(`  ${i+1}. ${link.text} → ${link.href}`);
        }
      });
      
      // Try to click first meaningful link
      if (dashboardLinks.length > 0) {
        const firstLink = dashboardLinks.find(l => l.href && !l.href.includes('javascript'));
        if (firstLink) {
          console.log(`\nNavigating to: ${firstLink.href}`);
          await page.goto(firstLink.href, { waitUntil: 'networkidle2', timeout: 15000 }).catch(e => {
            console.log(`Could not navigate: ${e.message}`);
          });
        }
      }
    }
    
    console.log(`Final URL before analysis: ${page.url()}\n`);
    
    // Step 2: Navigate to Home/Dashboard 
    console.log('🔍 Step 2: Staying on MainPage to analyze...');
    // Don't navigate - analyze current page
    console.log(`✅ At: ${page.url()}\n`);
    
    // Step 3: Analyze page structure
    console.log('📋 Step 3: Analyzing page HTML...\n');
    
    const pageAnalysis = await page.evaluate(() => {
      const analysis = {
        title: document.title,
        formElements: {
          textInputs: [],
          buttons: [],
          selects: [],
          textareas: []
        },
        links: [],
        tables: [],
        divContainers: []
      };
      
      // Find all text input fields
      document.querySelectorAll('input[type="text"], input:not([type])').forEach((el, idx) => {
        if (idx < 20) {
          analysis.formElements.textInputs.push({
            id: el.id || `input_${idx}`,
            name: el.name,
            placeholder: el.placeholder,
            value: el.value,
            class: el.className
          });
        }
      });
      
      // Find all buttons
      document.querySelectorAll('button, input[type="submit"], a.btn').forEach((el, idx) => {
        if (idx < 15) {
          analysis.formElements.buttons.push({
            text: (el.innerText || '').substring(0, 50),
            id: el.id,
            name: el.name,
            class: el.className,
            type: el.type
          });
        }
      });
      
      // Find all select dropdowns
      document.querySelectorAll('select').forEach((el, idx) => {
        if (idx < 10) {
          analysis.formElements.selects.push({
            name: el.name,
            id: el.id,
            class: el.className,
            options: Array.from(el.options).slice(0, 5).map(o => o.text)
          });
        }
      });
      
      // Find tables and result containers
      document.querySelectorAll('table').forEach((el, idx) => {
        if (idx < 3) {
          analysis.tables.push({
            id: el.id,
            class: el.className,
            rows: el.querySelectorAll('tbody tr').length,
            cols: el.querySelectorAll('th').length
          });
        }
      });
      
      // Find divs with judgment/case/result related classes
      document.querySelectorAll('div[class*="judgment"], div[class*="case"], div[class*="result"], div[class*="item"]').forEach((el, idx) => {
        if (idx < 10) {
          analysis.divContainers.push({
            class: el.className,
            text: (el.innerText || '').substring(0, 100)
          });
        }
      });
      
      // Find all links that might be judgment/case related
      document.querySelectorAll('a').forEach((el, idx) => {
        const href = el.href || '';
        const text = el.innerText || '';
        if ((text.length > 0 && (text.toLowerCase().includes('judgment') || text.toLowerCase().includes('case') || text.toLowerCase().includes('download'))) || 
            (href.includes('judgment') || href.includes('case') || href.includes('download') || href.includes('pdf'))) {
          if (idx < 20) {
            analysis.links.push({
              text: text.substring(0, 80),
              href: href.substring(0, 200),
              target: el.target
            });
          }
        }
      });
      
      return analysis;
    });
    
    // Print detailed analysis
    console.log(`📄 Page Title: ${pageAnalysis.title}\n`);
    
    console.log('📝 Form Elements Found:');
    console.log(`   Text Inputs: ${pageAnalysis.formElements.textInputs.length}`);
    pageAnalysis.formElements.textInputs.forEach((input, i) => {
      console.log(`     ${i+1}. ID: "${input.id}", Name: "${input.name}", Placeholder: "${input.placeholder}"`);
    });
    
    console.log(`\n   Buttons: ${pageAnalysis.formElements.buttons.length}`);
    pageAnalysis.formElements.buttons.forEach((btn, i) => {
      console.log(`     ${i+1}. "${btn.text}" - ID: "${btn.id}", Name: "${btn.name}", Type: "${btn.type}"`);
    });
    
    console.log(`\n   Select Dropdowns: ${pageAnalysis.formElements.selects.length}`);
    pageAnalysis.formElements.selects.forEach((sel, i) => {
      console.log(`     ${i+1}. "${sel.name}" - Options: ${sel.options.join(', ')}`);
    });
    
    console.log(`\n📊 Tables Found: ${pageAnalysis.tables.length}`);
    pageAnalysis.tables.forEach((tbl, i) => {
      console.log(`     ${i+1}. ID: "${tbl.id}", Rows: ${tbl.rows}, Columns: ${tbl.cols}`);
    });
    
    console.log(`\n📦 Result Containers (div elements): ${pageAnalysis.divContainers.length}`);
    pageAnalysis.divContainers.forEach((div, i) => {
      console.log(`     ${i+1}. Class: "${div.class}"`);
    });
    
    console.log(`\n🔗 Links Found: ${pageAnalysis.links.length}`);
    pageAnalysis.links.forEach((link, i) => {
      if (i < 10) {
        console.log(`     ${i+1}. "${link.text}" → ${link.href}`);
      }
    });
    
    // Try to find search button and keyword field
    console.log('\n\n🔎 Step 4: Testing Search Interaction...');
    
    // Look for all form inputs on the page
    const allInputs = await page.$$('input');
    console.log(`\nTotal input fields on page: ${allInputs.length}`);
    
    for (let i = 0; i < Math.min(10, allInputs.length); i++) {
      const properties = await allInputs[i].evaluate(el => ({
        type: el.type,
        name: el.name,
        id: el.id,
        placeholder: el.placeholder,
        value: el.value,
        visible: el.offsetParent !== null
      }));
      console.log(`${i+1}. ${JSON.stringify(properties)}`);
    }
    
    // Look for all buttons
    const allButtons = await page.$$('button, input[type="submit"]');
    console.log(`\nTotal buttons on page: ${allButtons.length}`);
    
    for (let i = 0; i < Math.min(10, allButtons.length); i++) {
      const properties = await allButtons[i].evaluate(el => ({
        text: el.innerText.substring(0, 30),
        type: el.type,
        id: el.id,
        name: el.name,
        class: el.className
      }));
      console.log(`${i+1}. ${JSON.stringify(properties)}`);
    }
    
    // Try to interact with the page
    console.log('\n📝 Step 5: Testing form submission...');
    
    // Find text input and try to populate it
    const textInput = await page.$('input[type="text"]');
    if (textInput) {
      await textInput.type('law', { delay: 30 });
      console.log('✅ Typed "law" into text input');
    }
    
    // Find submit button and click it
    const submitBtn = await page.$('button[type="submit"]');
    if (submitBtn) {
      await submitBtn.click();
      console.log('✅ Clicked submit button');
      
      // Wait for results
      await wait(3000);
      
      // Check for results
      const results = await page.evaluate(() => {
        const items = [];
        document.querySelectorAll('tr, div[class*="result"], div[class*="item"], div[class*="case"], div[class*="judgment"]').forEach((el, idx) => {
          if (idx < 20) {
            const text = el.innerText?.substring(0, 200) || '';
            if (text.length > 10) {
              items.push(text);
            }
          }
        });
        return items;
      });
      
      console.log(`\n📊 Search Results Found: ${results.length}`);
      results.slice(0, 5).forEach((result, i) => {
        console.log(`\n  Result ${i+1}:`);
        console.log(`  ${result.substring(0, 150)}`);
      });
    } else {
      console.log('❌ Submit button not found');
    }
    
    // Save page HTML for analysis
    const html = await page.content();
    const htmlPath = path.join(__dirname, 'page_analysis.html');
    fs.writeFileSync(htmlPath, html);
    console.log(`\n✅ Page HTML saved to: ${htmlPath}`);
    
    await browser.close();
    console.log('\n✨ Analysis complete!');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    if (browser) await browser.close();
    process.exit(1);
  }
}

main();
