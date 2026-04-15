import puppeteer from "puppeteer";
import fs from "fs";

const browser = await puppeteer.launch({ headless: false, defaultViewport: null });
const page = await browser.newPage();
await page.goto("https://www.easylaw.ai/", { waitUntil: "networkidle2", timeout: 120000 });
await page.waitForSelector("textarea[name='Query'], #comment2", { timeout: 20000 });
await page.type("textarea[name='Query'], #comment2", "constitutional petition", { delay: 20 });
await Promise.all([
  page.waitForNavigation({ waitUntil: "networkidle2", timeout: 120000 }).catch(() => null),
  page.click("input#myBtn, input[type='submit'].btn-success")
]);
await page.waitForSelector("table tbody tr td a", { timeout: 30000 });

const firstLinkSel = "table tbody tr td a";
const href = await page.$eval(firstLinkSel, a => a.href);
console.log("First href:", href);

await Promise.all([
  page.waitForNavigation({ waitUntil: "networkidle2", timeout: 120000 }).catch(() => null),
  page.click(firstLinkSel)
]);
await new Promise(r => setTimeout(r, 5000));

const out = await page.evaluate(() => {
  const links = Array.from(document.querySelectorAll("a")).map(a => ({ text: (a.innerText || "").trim().slice(0, 140), href: a.href, cls: a.className || "" }));
  const buttons = Array.from(document.querySelectorAll("button, input[type='button'], input[type='submit']")).map(b => ({
    tag: b.tagName.toLowerCase(),
    text: (b.innerText || b.value || "").trim().slice(0, 120),
    id: b.id || "",
    cls: b.className || "",
    onclick: b.getAttribute("onclick") || ""
  }));
  const iframes = Array.from(document.querySelectorAll("iframe")).map(f => ({ src: f.src, id: f.id || "", cls: f.className || "" }));
  return {
    url: location.href,
    title: document.title,
    textSample: document.body.innerText.slice(0, 5000),
    links: links.slice(0, 400),
    buttons,
    iframes
  };
});

fs.writeFileSync("easylaw_judgment_probe.json", JSON.stringify(out, null, 2));
await page.screenshot({ path: "easylaw_judgment_probe.png", fullPage: true });
await browser.close();
console.log("WROTE easylaw_judgment_probe.json and easylaw_judgment_probe.png");
