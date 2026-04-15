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
await new Promise(r => setTimeout(r, 5000));

const out = await page.evaluate(() => {
  const table = document.querySelector("table");
  const allTables = Array.from(document.querySelectorAll("table"));
  const rows = Array.from(document.querySelectorAll("table tbody tr")).slice(0, 3).map((tr, i) => ({
    idx: i,
    html: tr.outerHTML,
    text: tr.innerText
  }));
  const clickable = Array.from(document.querySelectorAll("[onclick]"))
    .map(el => ({ tag: el.tagName, cls: el.className || "", onclick: el.getAttribute("onclick") || "", text: (el.innerText || "").trim().slice(0, 120) }))
    .slice(0, 200);
  const cells = Array.from(document.querySelectorAll("td, th")).slice(0, 40).map(el => ({
    tag: el.tagName,
    text: (el.innerText || "").trim().slice(0, 80),
    cls: el.className || "",
    html: el.outerHTML.slice(0, 300)
  }));

  return {
    url: location.href,
    tables: allTables.map((t, i) => ({ i, id: t.id || "", cls: t.className || "", rows: t.querySelectorAll("tr").length })),
    firstTableHtml: table ? table.outerHTML.slice(0, 12000) : "",
    rows,
    clickable,
    cells
  };
});

fs.writeFileSync("easylaw_dom_probe.json", JSON.stringify(out, null, 2));
await browser.close();
console.log("WROTE easylaw_dom_probe.json");
