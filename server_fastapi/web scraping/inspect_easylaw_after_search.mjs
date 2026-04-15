import puppeteer from "puppeteer";
import fs from "fs";

const browser = await puppeteer.launch({ headless: false, defaultViewport: null });
const page = await browser.newPage();
await page.goto("https://www.easylaw.ai/", { waitUntil: "domcontentloaded", timeout: 120000 });
await page.waitForSelector("textarea[name='Query'], #comment2", { timeout: 30000 });
await page.type("textarea[name='Query'], #comment2", "constitutional petition", { delay: 25 });
await Promise.all([
  page.waitForNavigation({ waitUntil: "networkidle2", timeout: 120000 }).catch(() => null),
  page.click("input#myBtn, input[type='submit'].btn-success")
]);
await new Promise(r => setTimeout(r, 6000));

const out = await page.evaluate(() => {
  const links = Array.from(document.querySelectorAll("a")).map(a => ({
    text: (a.innerText || "").trim().slice(0, 160),
    hrefAttr: a.getAttribute("href") || "",
    href: a.href || "",
    cls: a.className || "",
    onclick: a.getAttribute("onclick") || ""
  }));

  return {
    url: location.href,
    title: document.title,
    textSample: (document.body.innerText || "").slice(0, 7000),
    links: links.slice(0, 500)
  };
});

fs.writeFileSync("easylaw_after_search_probe.json", JSON.stringify(out, null, 2));
await page.screenshot({ path: "easylaw_after_search_probe.png", fullPage: true });
await browser.close();
console.log("WROTE easylaw_after_search_probe.json and easylaw_after_search_probe.png");
