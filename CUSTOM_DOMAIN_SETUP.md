# Custom Domain Setup Guide
**Domain:** realdiag.com  
**Date:** November 20, 2025

---

## 📋 Domain Structure

| Subdomain | Purpose | Points To | Platform |
|-----------|---------|-----------|----------|
| `realdiag.com` | Main website | Netlify | Frontend |
| `www.realdiag.com` | WWW redirect | Netlify | Frontend |
| `api.realdiag.com` | Backend API | Render | Backend API |

---

## Step 1: DNS Configuration ⏱️ 10 min

### Where to Configure DNS
Log into your domain registrar (where you purchased realdiag.com) - common providers:
- GoDaddy, Namecheap, Google Domains, Cloudflare, etc.

### DNS Records to Add

**For Frontend (Netlify):**

Add these records in your DNS provider:

```
Type: A
Name: @
Value: 75.2.60.5
TTL: 3600 (or Auto)

Type: CNAME
Name: www
Value: realdiag.netlify.app
TTL: 3600 (or Auto)
```

**For Backend API (Render):**

```
Type: CNAME
Name: api
Value: realdiag-software.onrender.com
TTL: 3600 (or Auto)
```

**Important Notes:**
- `@` means the root domain (realdiag.com)
- DNS changes can take 5 minutes to 48 hours to propagate (usually < 1 hour)
- Keep your registrar's nameservers (don't change them unless using Cloudflare)

---

## Step 2: Netlify Domain Configuration ⏱️ 5 min

### Add Custom Domain

1. **Go to Netlify Dashboard:**
   - Visit https://app.netlify.com
   - Select your **RealDiag** site

2. **Add Domain:**
   - Go to **Domain management** (or **Domain settings**)
   - Click **Add custom domain** (or **Add a domain**)
   - Enter: `realdiag.com`
   - Click **Verify**
   - Click **Add domain**

3. **Add WWW Subdomain:**
   - Click **Add domain alias**
   - Enter: `www.realdiag.com`
   - Click **Add domain**

4. **Enable HTTPS:**
   - Netlify will automatically provision SSL certificates (Let's Encrypt)
   - Wait 2-5 minutes for certificate to be issued
   - Look for "HTTPS certificate provisioned" status

5. **Configure Redirects:**
   - In **Domain settings**, set:
     - Primary domain: `realdiag.com` (or `www.realdiag.com` if you prefer www)
     - Automatic redirect: www → non-www (or vice versa)

### Verify Netlify Setup

```bash
# Check DNS propagation (may take a few minutes)
nslookup realdiag.com

# Expected: Should show Netlify's IP (75.2.60.5)

# Test HTTPS
curl -I https://realdiag.com
# Should return: 200 OK with valid SSL
```

---

## Step 3: Render Domain Configuration ⏱️ 5 min

### Add Custom Domain for API

1. **Go to Render Dashboard:**
   - Visit https://dashboard.render.com
   - Select your `realdiag-software` web service

2. **Add Custom Domain:**
   - Go to **Settings** tab
   - Scroll to **Custom Domains** section
   - Click **Add Custom Domain**
   - Enter: `api.realdiag.com`
   - Click **Save**

3. **Verify DNS:**
   - Render will show CNAME target (should be `realdiag-software.onrender.com`)
   - Ensure your DNS CNAME record matches
   - Wait for "DNS configured" status

4. **SSL Certificate:**
   - Render automatically provisions SSL certificates
   - Wait 2-5 minutes for certificate to be issued
   - Status will show "Certificate Active"

### Verify Render Setup

```bash
# Check DNS propagation
nslookup api.realdiag.com
# Expected: Should show Render's servers

# Test API with new domain
curl https://api.realdiag.com/health
# Expected: {"ok":true}

# Verify SSL certificate
curl -I https://api.realdiag.com/version
# Should return: 200 OK with valid SSL
```

---

## Step 4: Update Application Configuration ⏱️ 5 min

### Update Backend CORS Settings

The backend needs to allow requests from your custom domain.

**In Render Dashboard → Environment Variables:**

Update or add these variables:

```bash
# Update CORS origins
CORS_ORIGINS=https://realdiag.com,https://www.realdiag.com,https://api.realdiag.com

# Optional: Update API base URL
API_BASE_URL=https://api.realdiag.com

# Optional: Set frontend URL
FRONTEND_URL=https://realdiag.com
```

This will trigger an automatic redeploy (~2-3 minutes).

### Update Frontend API URL

**Option A: Environment Variable (Recommended)**

In Netlify Dashboard → Environment Variables:

```bash
NEXT_PUBLIC_API_URL=https://api.realdiag.com
```

Then redeploy frontend.

**Option B: Code Change (if needed)**

If your frontend hardcodes the API URL, we'll need to update it in the code.

---

## Step 5: Verification & Testing ⏱️ 10 min

### DNS Propagation Check

```bash
# Check all domains resolve correctly
dig realdiag.com +short
dig www.realdiag.com +short
dig api.realdiag.com +short

# Or use online tool: https://dnschecker.org
```

### Test All Endpoints

```bash
# 1. Test main website
curl -I https://realdiag.com
# Expected: 200 OK with SSL

# 2. Test WWW redirect
curl -I https://www.realdiag.com
# Expected: 301 redirect to realdiag.com (or stays if www is primary)

# 3. Test API health
curl https://api.realdiag.com/health
# Expected: {"ok":true}

# 4. Test API version
curl https://api.realdiag.com/version
# Expected: {"app":"RealDiag","version":"1.0.0"}

# 5. Test symptom search from frontend
# Open browser: https://realdiag.com/symptom-search
# Enter symptoms and verify it works
```

### SSL Certificate Verification

```bash
# Check SSL certificate details
openssl s_client -connect realdiag.com:443 -servername realdiag.com < /dev/null 2>/dev/null | openssl x509 -noout -dates

# Check API SSL
openssl s_client -connect api.realdiag.com:443 -servername api.realdiag.com < /dev/null 2>/dev/null | openssl x509 -noout -dates
```

### Browser Testing

1. **Open in Browser:**
   - Visit https://realdiag.com
   - Check for padlock icon (valid SSL)
   - Open DevTools → Console
   - Look for no CORS errors

2. **Test Functionality:**
   - Navigate to Symptom Search
   - Enter symptoms (e.g., "headache, fever")
   - Verify results load from `api.realdiag.com`
   - Check Network tab for API calls

3. **Test All Pages:**
   - Home: https://realdiag.com
   - Symptom Search: https://realdiag.com/symptom-search
   - Rules: https://realdiag.com/rules
   - API Docs: https://api.realdiag.com/docs
   - Account: https://realdiag.com/account

---

## Step 6: Update External References ⏱️ 5 min

### Update Documentation

Files that may reference old URLs:
- `README.md`
- `DEPLOYMENT.md`
- `netlify.toml`
- Any marketing materials

### Update Sentry

If using Sentry, update allowed domains:

1. Go to https://sentry.io
2. Project Settings → Client Keys (DSN)
3. Add to allowed domains:
   - `realdiag.com`
   - `www.realdiag.com`
   - `api.realdiag.com`

### Update Search Engines

1. **Google Search Console:**
   - Add property for `realdiag.com`
   - Verify ownership (DNS TXT record or HTML file)
   - Submit sitemap

2. **Update robots.txt** (if needed)

---

## 🚨 Troubleshooting

### DNS Not Resolving

**Problem:** Domain doesn't resolve after adding DNS records

**Solutions:**
1. Wait longer (can take up to 48 hours, usually < 1 hour)
2. Check DNS records are correct (no typos)
3. Use `nslookup` or `dig` to check propagation
4. Clear DNS cache: `sudo systemd-resolve --flush-caches` (Linux)

### SSL Certificate Not Provisioning

**Problem:** "Certificate pending" stuck for > 10 minutes

**Solutions:**
1. Verify DNS is resolving correctly first
2. In Netlify: Try removing and re-adding the domain
3. In Render: Check CNAME target is correct
4. Ensure no CAA records blocking Let's Encrypt

### CORS Errors in Browser

**Problem:** "CORS policy: No 'Access-Control-Allow-Origin' header"

**Solutions:**
1. Verify backend `CORS_ORIGINS` includes `https://realdiag.com`
2. Check Render environment variables are saved
3. Wait for automatic redeploy (~2-3 minutes)
4. Hard refresh browser (Ctrl+Shift+R)

### Mixed Content Warnings

**Problem:** "Mixed Content: The page was loaded over HTTPS, but..."

**Solutions:**
1. Ensure all API calls use `https://` not `http://`
2. Check frontend environment variable `NEXT_PUBLIC_API_URL`
3. Update any hardcoded URLs in code

### WWW Not Redirecting

**Problem:** www.realdiag.com doesn't redirect to realdiag.com

**Solutions:**
1. In Netlify, set primary domain preference
2. Enable automatic HTTPS redirect
3. May take a few minutes after enabling

---

## ✅ Post-Setup Checklist

After completing all steps, verify:

- [ ] `realdiag.com` loads with valid SSL (green padlock)
- [ ] `www.realdiag.com` redirects correctly
- [ ] `api.realdiag.com/health` returns `{"ok":true}`
- [ ] `api.realdiag.com/docs` shows API documentation
- [ ] Symptom search works from `realdiag.com/symptom-search`
- [ ] No CORS errors in browser console
- [ ] All pages load correctly
- [ ] User accounts/login works
- [ ] SSL certificates valid (not expired)
- [ ] Security headers present (check with curl -I)
- [ ] Sentry capturing errors on new domain

---

## 📊 Expected Timeline

| Step | Time | Status |
|------|------|--------|
| DNS Configuration | 10 min | Manual |
| Netlify Domain Setup | 5 min | Manual |
| Render Domain Setup | 5 min | Manual |
| Update CORS/Environment | 5 min | Manual |
| DNS Propagation | 15-60 min | Automatic |
| SSL Certificate Provisioning | 2-10 min | Automatic |
| Testing & Verification | 10 min | Manual |
| **Total Time** | **~1-2 hours** | **(mostly waiting for DNS)** |

---

## 🎯 Quick Start Commands

```bash
# 1. Check current DNS (before changes)
nslookup realdiag.com
nslookup www.realdiag.com
nslookup api.realdiag.com

# 2. After DNS changes, wait 5-10 minutes, then check again
watch -n 30 'nslookup realdiag.com'

# 3. Test SSL certificates
curl -I https://realdiag.com
curl -I https://api.realdiag.com

# 4. Test API functionality
curl https://api.realdiag.com/health
curl https://api.realdiag.com/version

# 5. Monitor deployment logs
# Netlify: https://app.netlify.com (Deploys tab)
# Render: https://dashboard.render.com (Events tab)
```

---

## 📞 Need Help?

- **DNS Issues:** Contact your domain registrar support
- **Netlify Issues:** https://answers.netlify.com
- **Render Issues:** https://render.com/docs
- **SSL Issues:** Check Let's Encrypt status: https://letsencrypt.status.io

---

**Status:** Ready to begin custom domain setup  
**Estimated Completion:** 1-2 hours (including DNS propagation wait time)
