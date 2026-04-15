import puppeteer from "puppeteer";
import fs from "fs";

const browser = await puppeteer.launch({ headless: false, defaultViewport: null });
const page = await browser.newPage();
await page.goto("https://www.easylaw.ai/", { waitUntil: "networkidle2", timeout: 120000 });
await page.type("textarea[name='Query'], #comment2", "constitutional petition", { delay: 20 });
await Promise.all([
  page.waitForNavigation({ waitUntil: "networkidle2", timeout: 120000 }).catch(() => null),
  page.click("input#myBtn, input[type='submit'].btn-success")
]);
await page.waitForSelector("#myTable tbody tr form button[name='details']", { timeout: 60000 });

const firstBtn = await page.$("#myTable tbody tr form button[name='details']");
const detailsValue = await page.$eval("#myTable tbody tr form button[name='details']", el => el.value || "");
console.log("details token:", detailsValue);

const [newPage] = await Promise.all([
  new Promise(resolve => page.once('popup', resolve)),
  firstBtn.click()
]);

await newPage.bringToFront();
await newPage.waitForNavigation({ waitUntil: 'networkidle2', timeout: 120000 }).catch(() => null);
await new Promise(r => setTimeout(r, 5000));

const out = await newPage.evaluate(() => {
  const links = Array.from(document.querySelectorAll('a')).map(a => ({
    text: (a.innerText || '').trim().slice(0, 140),
    hrefAttr: a.getAttribute('href') || '',
    href: a.href || '',
    cls: a.className || ''
  }));
  const forms = Array.from(document.querySelectorAll('form')).map(f => ({
    action: f.getAttribute('action') || '',
    method: f.getAttribute('method') || '',
    target: f.getAttribute('target') || '',
    html: f.outerHTML.slice(0, 500)
  }));
  const buttons = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"]')).map(b => ({
    text: (b.innerText || b.value || '').trim().slice(0, 120),
    name: b.getAttribute('name') || '',
    value: b.getAttribute('value') || '',
    id: b.id || '',
    cls: b.className || ''
  }));
  const iframes = Array.from(document.querySelectorAll('iframe')).map(i => ({ src: i.src, id: i.id || '', cls: i.className || '' }));
  return {
    url: location.href,
    title: document.title,
    textSample: (document.body.innerText || '').slice(0, 7000),
    links: links.slice(0, 400),
    forms,
    buttons,
    iframes
  };
});

fs.writeFileSync('easylaw_case_probe.json', JSON.stringify(out, null, 2));
await newPage.screenshot({ path: 'easylaw_case_probe.png', fullPage: true });
await browser.close();
console.log('WROTE easylaw_case_probe.json and easylaw_case_probe.png');
