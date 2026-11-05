# Email alerts setup (about 10 minutes, free)

Sale Radar's site is static, so sign-ups and sending go through a small **Google Apps Script** web app that
you own. Subscriber emails live in a **private Google Sheet** in your Google account. They are never stored in
this public repo.

```
dashboard sign-up form ──POST──> Apps Script ──> private Sheet (pending) ──> confirmation email
GitHub scan (every 6h) ──POST alerts + secret──> Apps Script ──> emails confirmed subscribers
email "Unsubscribe" link ──GET──> Apps Script ──> marks the row unsubscribed
```

**Tip:** alerts are sent *from* the Google account that owns the script. Use a separate Gmail
(for example `saleradar.alerts@gmail.com`) if you don't want subscribers to see your personal address.
Consumer Gmail can send about 100 emails a day through Apps Script, which is plenty for friends and family.

## 1. Create the Sheet and script

1. Signed in to the Google account you want to send from, create a new Google Sheet (name it `Sale Radar subscribers`).
2. In the Sheet: **Extensions > Apps Script**.
3. Delete the sample code, paste the whole of `notify/apps-script/Code.gs`, and save.

## 2. Set the secret

1. In Apps Script: **Project Settings (gear) > Script properties > Add script property**:
   - `NOTIFY_SECRET` = a long random string (e.g. generate one with `python -c "import secrets;print(secrets.token_urlsafe(32))"`)
   - `SITE_URL` = `https://michaelissaa.github.io/sale-radar/`

## 3. Deploy

1. **Deploy > New deployment > Select type: Web app**.
2. Execute as: **Me**. Who has access: **Anyone** (needed so the sign-up form and unsubscribe links work).
3. Click Deploy, then authorise. Google warns the app is unverified because it's your own script: choose
   *Advanced > Go to project*. It asks to send email as you and edit the Sheet, which is all it does.
4. Copy the **Web app URL** (ends in `/exec`).

## 4. Connect it

1. GitHub repo > **Settings > Secrets and variables > Actions > New repository secret**:
   - `NOTIFY_URL` = the Web app URL
   - `NOTIFY_SECRET` = the same secret as step 2
2. Put the same Web app URL in `config/site.json` as `notify_url` and commit. This turns on the sign-up
   form on the dashboard. The URL is public by design (it's the sign-up endpoint); the secret is not.

## 5. Test

Sign up on the dashboard with your own email and click the confirmation link. Then in GitHub run
**Actions > Scan retailers and deploy dashboard > Run workflow**. The log's *Send email alerts* step shows how
many alerts were found and how many emails were sent. Emails only go out when a watched brand actually changes.

## What triggers an email

| Alert type (sign-up checkbox) | Sent when |
|---|---|
| Black Friday news | a brand announces its Black Friday sale, publishes confirmed dates, or its Black Friday sale goes live |
| Regular sales | a normal (not Black Friday branded) sale starts, or an active sale ends |
| Discount changes | the advertised discount changes during a live sale |

The same alert for the same brand isn't repeated within a cooldown (3 to 14 days depending on type), so a
flickering status can't spam anyone. Values the scanner couldn't re-check (stale) never trigger alerts.

## Privacy and the Spam Act

* Double opt-in: nothing is sent until the subscriber clicks the confirmation link.
* Every alert email identifies Sale Radar and has a working one-click unsubscribe link.
* To delete someone completely, delete their row in the Sheet.
* Changing code later: paste the new `Code.gs`, then **Deploy > Manage deployments > Edit > Version: New version**
  (this keeps the same URL).
