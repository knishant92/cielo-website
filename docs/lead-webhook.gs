// Cielo website → leads. Google Apps Script web app.
// Receives the pilot form as JSON, appends a row to the Sheet this script is bound to,
// and emails marketing.team@ with nishant.kumar@ in cc. Deploy as: Web app, Execute as Me, Anyone.
// Then paste the web-app URL into Cloudflare Pages → Settings → Variables and Secrets → LEAD_WEBHOOK.

var TO = "marketing.team@cieloecommerce.com";
var CC = "nishant.kumar@cieloecommerce.com";
var HEADERS = ["ts","pilot","name","brand","email","phone","channels","skus","category","notes","page","country","ip"];

function doPost(e) {
  var lead;
  try { lead = JSON.parse(e.postData.contents); } catch (err) { return out({ ok: false, error: "bad json" }); }
  var sh = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
  if (sh.getLastRow() === 0) sh.appendRow(HEADERS);
  sh.appendRow(HEADERS.map(function (k) { return lead[k] || ""; }));
  var subject = "Pilot enquiry · " + (lead.pilot || "") + " · " + (lead.brand || "");
  var body = HEADERS.filter(function (k) { return k !== "ip"; }).map(function (k) { return k.toUpperCase() + ": " + (lead[k] || ""); }).join("\n");
  MailApp.sendEmail({ to: TO, cc: CC, replyTo: lead.email || TO, subject: subject, body: body + "\n\nSheet: " + SpreadsheetApp.getActiveSpreadsheet().getUrl() });
  return out({ ok: true });
}

function doGet() { return out({ ok: true, service: "cielo lead webhook" }); }

function out(obj) { return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON); }
