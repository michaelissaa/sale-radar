/**
 * Sale Radar email alerts: Google Apps Script web app.
 *
 * Stores subscribers in a PRIVATE Google Sheet (bound to this script), sends a confirmation email
 * (double opt-in), sends alert digests when the GitHub scanner posts changes, and handles
 * one-click unsubscribe. Setup: see notify/README.md.
 *
 * Script property required: NOTIFY_SECRET (same value as the GitHub secret).
 * Optional script property: SITE_URL (dashboard URL, used in emails).
 */

// ------------------------------------------------------------------ pure logic (unit-tested in Node)
var PREF_KINDS = {
  black_friday: ['bf_announced', 'bf_dates', 'bf_reminder', 'bf_live', 'bf_ended'],
  sales: ['sale_live', 'sale_ended'],
  discounts: ['discount'],
};
var EMAIL_RE = /^[^\s@<>()",;]+@[^\s@<>()",;]+\.[a-z]{2,}$/i;
var MAX_BRANDS = 200;

function normaliseSubscription(body) {
  if (!body || typeof body !== 'object') return { ok: false, error: 'Bad request' };
  if (body.website) return { ok: false, error: 'Bad request' }; // honeypot field filled = bot
  var email = String(body.email || '').trim().toLowerCase();
  if (email.length > 254 || !EMAIL_RE.test(email)) return { ok: false, error: 'Please enter a valid email address' };
  var brands = Array.isArray(body.brands) ? body.brands.map(String) : [];
  brands = brands.filter(function (b) { return b === '*' || /^[a-z0-9-]{1,40}$/.test(b); }).slice(0, MAX_BRANDS);
  if (!brands.length) return { ok: false, error: 'Choose at least one brand' };
  if (brands.indexOf('*') >= 0) brands = ['*'];
  var prefs = (Array.isArray(body.prefs) ? body.prefs : []).filter(function (p) { return PREF_KINDS[p]; });
  if (!prefs.length) return { ok: false, error: 'Choose at least one alert type' };
  return { ok: true, email: email, brands: brands, prefs: prefs };
}

function kindsFor(prefs) {
  var out = [];
  prefs.forEach(function (p) { (PREF_KINDS[p] || []).forEach(function (k) { out.push(k); }); });
  return out;
}

function matchAlerts(sub, alerts) {
  var kinds = kindsFor(sub.prefs);
  var all = sub.brands.indexOf('*') >= 0;
  return alerts.filter(function (a) {
    return kinds.indexOf(a.kind) >= 0 && (all || sub.brands.indexOf(a.brand) >= 0);
  });
}

function escapeHtml(s) {
  return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
  });
}

function safeUrl(u) {
  return /^https:\/\//i.test(String(u || '')) ? String(u) : '';
}

function renderAlertEmail(alerts, siteUrl, unsubUrl) {
  var names = alerts.map(function (a) { return a.brand_name; }).filter(function (n, i, all) { return all.indexOf(n) === i; });
  var subject = alerts.length === 1 ? alerts[0].title : 'Sale Radar: ' + alerts.length + ' updates (' +
    names.slice(0, 3).join(', ') + (names.length > 3 ? ', ...' : '') + ')';
  var items = alerts.map(function (a) {
    var link = safeUrl(a.url);
    return '<tr><td style="padding:12px 0;border-bottom:1px solid #e6e6e8">' +
      '<div style="font-weight:600;font-size:15px">' + escapeHtml(a.title) + '</div>' +
      (a.detail ? '<div style="color:#52525b;margin-top:4px">' + escapeHtml(a.detail) + '</div>' : '') +
      (link ? '<div style="margin-top:6px"><a href="' + escapeHtml(link) + '" style="color:#047857">Open retailer page</a></div>' : '') +
      '</td></tr>';
  }).join('');
  var html = '<div style="font-family:system-ui,-apple-system,sans-serif;max-width:560px;color:#18181b">' +
    '<h2 style="font-size:18px;margin:0 0 8px">Sale Radar</h2><table style="width:100%;border-collapse:collapse">' + items + '</table>' +
    '<p style="margin-top:16px"><a href="' + escapeHtml(safeUrl(siteUrl)) + '" style="color:#047857">Open the dashboard</a></p>' +
    '<p style="color:#71717a;font-size:12px;margin-top:24px">Prices and dates are as published by the retailer at the time of the scan. Check at checkout. ' +
    'You are receiving this because you subscribed to Sale Radar alerts. ' +
    '<a href="' + escapeHtml(unsubUrl) + '" style="color:#71717a">Unsubscribe</a></p></div>';
  var text = alerts.map(function (a) { return a.title + (a.detail ? '\n' + a.detail : '') + (safeUrl(a.url) ? '\n' + a.url : ''); }).join('\n\n') +
    '\n\nDashboard: ' + safeUrl(siteUrl) + '\nUnsubscribe: ' + unsubUrl;
  return { subject: subject, html: html, text: text };
}

function renderConfirmEmail(confirmUrl, sub) {
  var what = sub.brands[0] === '*' ? 'all brands' : sub.brands.length + ' brand' + (sub.brands.length === 1 ? '' : 's');
  return {
    subject: 'Confirm your Sale Radar alerts',
    html: '<div style="font-family:system-ui,sans-serif;max-width:520px;color:#18181b"><h2 style="font-size:18px">Confirm your alerts</h2>' +
      '<p>Someone (hopefully you) asked to get Sale Radar emails for ' + escapeHtml(what) + '.</p>' +
      '<p><a href="' + escapeHtml(confirmUrl) + '" style="background:#18181b;color:#fff;padding:10px 14px;border-radius:8px;text-decoration:none">Confirm alerts</a></p>' +
      '<p style="color:#71717a;font-size:12px">If this wasn\'t you, ignore this email and nothing will be sent.</p></div>',
    text: 'Confirm your Sale Radar alerts for ' + what + ':\n' + confirmUrl + '\n\nIf this was not you, ignore this email.',
  };
}

// ------------------------------------------------------------------ Apps Script handlers
var HEADERS = ['email', 'brands', 'prefs', 'status', 'token', 'pending', 'created', 'confirmed', 'last_sent', 'unsub'];

function sheet_() {
  var ss = SpreadsheetApp.getActive();
  var sh = ss.getSheetByName('subscribers') || ss.insertSheet('subscribers');
  if (sh.getLastRow() === 0) sh.appendRow(HEADERS);
  return sh;
}

function rows_() {
  var sh = sheet_();
  var vals = sh.getDataRange().getValues();
  return vals.slice(1).map(function (r, i) {
    var o = { row: i + 2 };
    HEADERS.forEach(function (h, j) { o[h] = r[j]; });
    return o;
  });
}

function write_(o) {
  var sh = sheet_();
  var vals = HEADERS.map(function (h) { return o[h] == null ? '' : o[h]; });
  if (o.row) sh.getRange(o.row, 1, 1, HEADERS.length).setValues([vals]);
  else sh.appendRow(vals);
}

function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

function page_(title, msg) {
  return HtmlService.createHtmlOutput('<div style="font-family:system-ui,sans-serif;max-width:480px;margin:48px auto;padding:0 16px">' +
    '<h2>' + escapeHtml(title) + '</h2><p>' + escapeHtml(msg) + '</p>' +
    (siteUrl_() ? '<p><a href="' + escapeHtml(siteUrl_()) + '">Back to Sale Radar</a></p>' : '') + '</div>').setTitle(title);
}

function siteUrl_() { return PropertiesService.getScriptProperties().getProperty('SITE_URL') || ''; }

function doPost(e) {
  var body;
  try { body = JSON.parse(e.postData.contents); } catch (err) { return json_({ ok: false, error: 'Bad JSON' }); }
  if (body.action === 'subscribe') return json_(subscribe_(body));
  if (body.action === 'notify') return json_(notify_(body));
  return json_({ ok: false, error: 'Unknown action' });
}

function subscribe_(body) {
  var s = normaliseSubscription(body);
  if (!s.ok) return s;
  var cache = CacheService.getScriptCache();
  var key = 'rl:' + Utilities.base64EncodeWebSafe(s.email).slice(0, 200);
  var n = Number(cache.get(key) || 0);
  if (n >= 3) return { ok: false, error: 'Too many requests for this email today' };
  cache.put(key, String(n + 1), 21600);
  if (MailApp.getRemainingDailyQuota() < 5) return { ok: false, error: 'Sign-ups are paused for today, try tomorrow' };
  var lock = LockService.getScriptLock(); lock.waitLock(20000);
  try {
    var existing = rows_().filter(function (r) { return r.email === s.email; })[0];
    var token = Utilities.getUuid();
    var rec = existing || { email: s.email, status: 'pending', created: new Date().toISOString() };
    if (!rec.unsub) rec.unsub = Utilities.getUuid(); // permanent, so links in old emails keep working
    // changes only apply after the confirm link is clicked, so nobody can alter someone else's alerts
    rec.token = token;
    rec.pending = JSON.stringify({ brands: s.brands, prefs: s.prefs });
    write_(rec);
  } finally { lock.releaseLock(); }
  var url = ScriptApp.getService().getUrl() + '?action=confirm&token=' + encodeURIComponent(token);
  var m = renderConfirmEmail(url, s);
  MailApp.sendEmail({ to: s.email, subject: m.subject, htmlBody: m.html, body: m.text, name: 'Sale Radar' });
  return { ok: true };
}

var TOKEN_RE = /^[0-9a-f-]{36}$/i;
var ACTION_TEXT = {
  confirm: { title: 'Confirm your alerts', button: 'Confirm alerts', done: 'Alerts confirmed',
             msg: 'You will get an email when your chosen brands announce or change a Black Friday sale. Every email has an unsubscribe link.' },
  unsubscribe: { title: 'Unsubscribe', button: 'Unsubscribe me', done: 'Unsubscribed', msg: 'You will not get any more Sale Radar emails.' },
};

// Email links only show a page with a button. Mail security scanners open links but don't press
// buttons, so they can no longer confirm or unsubscribe someone by accident.
function doGet(e) {
  var p = (e && e.parameter) || {};
  var token = String(p.token || '');
  var t = ACTION_TEXT[p.action];
  if (!t || !TOKEN_RE.test(token)) return page_('Sale Radar alerts', 'Nothing to do here.');
  var html = '<div style="font-family:system-ui,sans-serif;max-width:480px;margin:48px auto;padding:0 16px" id="box">' +
    '<h2>' + escapeHtml(t.title) + '</h2>' +
    '<button id="go" style="background:#18181b;color:#fff;border:0;padding:10px 16px;border-radius:8px;font-size:15px;cursor:pointer">' + escapeHtml(t.button) + '</button>' +
    '<p id="msg" style="color:#52525b"></p></div>' +
    '<script>document.getElementById("go").onclick=function(){var b=this;b.disabled=true;b.textContent="Working...";' +
    'google.script.run.withSuccessHandler(function(r){document.getElementById("box").innerHTML="<h2>"+r.title+"</h2><p>"+r.msg+"</p>";})' +
    '.withFailureHandler(function(){b.disabled=false;b.textContent=' + JSON.stringify(t.button) + ';document.getElementById("msg").textContent="Something went wrong, please try again.";})' +
    '.apiAction(' + JSON.stringify(p.action) + ',' + JSON.stringify(token) + ');};</script>';
  return HtmlService.createHtmlOutput(html).setTitle(t.title);
}

// Called from the button above via google.script.run (public name, no trailing underscore).
function apiAction(action, token) {
  var t = ACTION_TEXT[action];
  token = String(token || '');
  if (!t || !TOKEN_RE.test(token)) return { title: 'Link expired', msg: 'This link is no longer valid.' };
  var lock = LockService.getScriptLock(); lock.waitLock(20000);
  try {
    var r = rows_().filter(function (x) { return action === 'unsubscribe' ? x.unsub === token : x.token === token; })[0];
    if (!r) return { title: 'Link expired', msg: 'This link is no longer valid. Sign up again from the dashboard.' };
    if (action === 'confirm') {
      var pend = r.pending ? JSON.parse(r.pending) : null;
      if (pend) { r.brands = JSON.stringify(pend.brands); r.prefs = JSON.stringify(pend.prefs); r.pending = ''; }
      r.status = 'active'; r.confirmed = new Date().toISOString();
    } else {
      r.status = 'unsubscribed'; r.pending = '';
    }
    write_(r);
  } finally { lock.releaseLock(); }
  return { title: escapeHtml(t.done), msg: escapeHtml(t.msg) };
}

function notify_(body) {
  var secret = PropertiesService.getScriptProperties().getProperty('NOTIFY_SECRET');
  if (!secret || body.secret !== secret) return { ok: false, error: 'Unauthorised' };
  var alerts = Array.isArray(body.alerts) ? body.alerts : [];
  var site = safeUrl(body.site_url) || siteUrl_();
  var base = ScriptApp.getService().getUrl();
  var emails = 0, recipients = 0, skipped = 0;
  rows_().forEach(function (r) {
    if (r.status !== 'active') return;
    var sub = { brands: JSON.parse(r.brands || '[]'), prefs: JSON.parse(r.prefs || '[]') };
    var mine = matchAlerts(sub, alerts);
    if (!mine.length) return;
    if (MailApp.getRemainingDailyQuota() < 1) { skipped++; return; }
    var m = renderAlertEmail(mine, site, base + '?action=unsubscribe&token=' + encodeURIComponent(r.unsub));
    MailApp.sendEmail({ to: r.email, subject: m.subject, htmlBody: m.html, body: m.text, name: 'Sale Radar' });
    r.last_sent = new Date().toISOString(); write_(r);
    emails++; recipients++;
  });
  return { ok: true, emails: emails, recipients: recipients, skipped_quota: skipped, quota_left: MailApp.getRemainingDailyQuota() };
}
