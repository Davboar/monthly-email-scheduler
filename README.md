# Monthly Email Scheduler (Gmail + GitHub Actions)

This little tool lets you send an email automatically on a fixed day every month (e.g. the 23rd),
from **your own Gmail account**, for free, using **GitHub Actions**.

## How to use it (10–15 minutes)

### 1. Create your own copy (no coding needed)

1. Make sure you are logged in to GitHub.
2. Open this page (the repository).
3. Click the green **"Use this template"** button → **"Create a new repository"**.
4. Choose a repository name (e.g. `my-monthly-email`), keep it:
   - Public or Private (your choice)
5. Click **Create repository**.

You now have your own copy.

### 2. Prepare your Gmail account (App Password)

1. Go to https://myaccount.google.com and log in to the Gmail account you want to send from.
2. On the left, click **Security**.
3. Under **"Signing in to Google"**:
   - Turn on **2-Step Verification** (if not already).
4. Once 2FA is enabled, go back to **Security** → **App passwords**.
5. Create a new app password:
   - App: **Mail**
   - Device: **Other (Custom name)**, e.g. `GitHubScheduler`
6. Google will show a 16-character password (e.g. `abcd efgh ijkl mnop`).
   **Copy it** (you’ll only see it once).

### 3. Add your secrets in GitHub (email + app password)

1. Go to **your copy** of the repo on GitHub.
2. Click **Settings**.
3. On the left, click **Secrets and variables → Actions**.
4. Under **Secrets → Repository secrets**, click **New repository secret** and create:

   - **Name:** `FROM_EMAIL`  
     **Value:** your Gmail address (e.g. `you@gmail.com`)

   - **Name:** `APP_PASSWORD`  
     **Value:** the app password from step 2 (the 16-character code)

   - **Name:** `TO_EMAIL`  
     **Value:** the email that should receive the message (e.g. your doctor)

### 4. Configure message and schedule (Variables)

Still on **Settings → Secrets and variables → Actions**, now go to the **Variables** tab.

Create these variables (or edit if they already exist):

- `TO_EMAILS` → leave empty or put extra recipients (comma-separated)
- `SUBJECT` → e.g. `Monthly GP Update`
- `BODY_TEXT` → e.g.

  ```text
  Hello Dr Smith,

  This is my monthly update.

  Kind regards,
  David
