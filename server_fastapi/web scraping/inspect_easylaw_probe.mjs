import puppeteer from "puppeteer";
import fs from "fs";

const browser = await puppeteer.launch({ headless: false, defaultViewport: null });
const page = await browser.newPage();
await page.goto("https://www.easylaw.ai/", { waitUntil: "domcontentloaded", timeout: 120000 });
await new Promise(r => setTimeout(r, 8000));
const data = await page.evaluate(() => {
  const anchors = Array.from(document.querySelectorAll("a")).slice(0, 200).map(a => ({
    text: (a.innerText || "").trim().slice(0, 120),
    href: a.href,
    cls: a.className || ""
  }));
  const inputs = Array.from(document.querySelectorAll("input, textarea, select, button")).map(el => ({
    tag: el.tagName.toLowerCase(),
    type: el.getAttribute("type") || "",
    id: el.id || "",
    name: el.getAttribute("name") || "",
    placeholder: el.getAttribute("placeholder") || "",
    text: (el.innerText || "").trim().slice(0, 80),
    cls: el.className || ""
  }));
  return { url: location.href, title: document.title, anchors, inputs, bodyTextSample: document.body.innerText.slice(0, 3000) };
});
fs.writeFileSync("easylaw_probe.json", JSON.stringify(data, null, 2));
await page.screenshot({ path: "easylaw_probe.png", fullPage: true });
await browser.close();
console.log("WROTE easylaw_probe.json and easylaw_probe.png");
