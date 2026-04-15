const puppeteer = require('puppeteer');
const fs = require('fs');
const readline = require('readline');

async function run() {
  console.log('Launching browser...');
  const browser = await puppeteer.launch({
    headless: false,
    defaultViewport: null,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--start-maximized']
  });

  const page = await browser.newPage();

  try {
    console.log('Navigating to MainPage...');
    await page.goto('https://www.pakistanlawsite.com/Login/MainPage', { waitUntil: 'networkidle2' });

    console.log('\n======================================================');
    console.log('Browser opened! Please log in manually in the window.');
    console.log('Solve any multi-login issues or agreement checkboxes.');
    console.log('Once you are fully logged in and see the dashboard/search page,');
    console.log('press ENTER in this terminal to continue scraping.');
    console.log('======================================================\n');

    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    await new Promise(resolve => rl.question('Press ENTER here when ready...', resolve));
    rl.close();

    console.log('Starting scraping flow from Current URL:', page.url());
    
    // Save dashboard HTML to verify where we are
    const html = await page.content();
    fs.writeFileSync('pls_dashboard.html', html);
    console.log('Saved current HTML to pls_dashboard.html');

    const cookies = await page.cookies();
    fs.writeFileSync('cookies.json', JSON.stringify(cookies, null, 2));
    console.log('Navigating to PTCLMain...');
    await page.goto('https://www.pakistanlawsite.com/Login/FederalStatutes', { waitUntil: 'networkidle2' });
    fs.writeFileSync('pls_statutes.html', await page.content());
    console.log('Saved PTCLMain to pls_statutes.html');
    
  } catch (err) {
    console.error('Error:', err);
  } finally {
    // await browser.close();
  }
}

run();