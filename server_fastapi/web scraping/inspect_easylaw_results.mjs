import puppeteer from "puppeteer";
import fs from "fs";

const browser = await puppeteer.launch({ headless: false, defaultViewport: null });
const page = await browser.newPage();
await page.goto("https://www.easylaw.ai/", { waitUntil: "networkidle2", timeout: 120000 });
await page.waitForSelector("textarea[name='Query'], #comment2", { timeout: 20000 });

await page.evaluate(() => {
  const q = document.querySelector("textarea[name='Query'], #comment2");
  if (q) q.value = "";
});
await page.type("textarea[name='Query'], #comment2", "constitutional petition", { delay: 30 });

await Promise.all([
  page.waitForNavigation({ waitUntil: "networkidle2", timeout: 120000 }).catch(() => null),
  page.click("input#myBtn, input[type='submit'].btn-success")
]);

await new Promise(r => setTimeout(r, 6000));

const out = await page.evaluate(() => {
  const links = Array.from(document.querySelectorAll("a")).map(a => ({ text: (a.innerText || "").trim().slice(0, 140), href: a.href, cls: a.className || "" }));
  const tables = Array.from(document.querySelectorAll("table")).map((t, i) => ({ index: i, rows: t.querySelectorAll("tr").length, text: (t.innerText || "").slice(0, 800) }));
  return {
    url: location.href,
    title: document.title,
    textSample: document.body.innerText.slice(0, 5000),
    linkCount: links.length,
    links: links.slice(0, 400),
    tables
  };
});

fs.writeFileSync("easylaw_results_probe.json", JSON.stringify(out, null, 2));
await page.screenshot({ path: "easylaw_results_probe.png", fullPage: true });
await browser.close();
console.log("WROTE easylaw_results_probe.json and easylaw_results_probe.png");
