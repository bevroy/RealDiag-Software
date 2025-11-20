# Custom Domain Setup Guide
**RealDiag Production Domain Configuration**  
Setup Date: November 20, 2025

---

## 🎯 Overview

This guide will help you set up your custom domain (e.g., `realdiag.com`) for production deployment.

**Current URLs:**
- Backend: `https://realdiag-software.onrender.com`
- Frontend: `https://realdiag.netlify.app`

**Target URLs:**
- Backend: `https://api.realdiag.com`
- Frontend: `https://realdiag.com` or `https://www.realdiag.com`

---

## Step 1: Purchase Domain (If Not Already Owned)

### Recommended Registrars:
1. **Namecheap** - https://www.namecheap.com
   - Price: ~$10-15/year for .com
   - Easy DNS management
   - Free WHOIS privacy

2. **Google Domains** - https://domains.google
   - Price: ~$12/year
   - Integrated with Google Cloud
   - Simple interface

3. **Cloudflare** - https://www.cloudflare.com/products/registrar
   - Price: At-cost (~$9/year)
   - Free SSL and CDN
   - Best for performance

**Purchase:** `realdiag.com` (or your preferred domain)

---

## Step 2: Configure DNS Records

### Option A: Using Netlify DNS (Recommended for Simplicity)

1. **Add Domain to Netlify:**
   - Go to https://app.netlify.com
   - Select your RealDiag site
   - Click **Domain settings**
   - Click **Add custom domain**
   - Enter: `realdiag.com`
   - Follow prompts to verify ownership

2. **Update Nameservers at Your Registrar:**
   
   Netlify will provide nameservers like:
   ```
   dns1.p08.nsone.net
   dns2.p08.nsone.net
   dns3.p08.nsone.net
   dns4.p08.nsone.net
   ```

   Go to your domain registrar (Namecheap, Google Domains, etc.) and update nameservers to these values.

3. **Netlify Will Auto-Configure:**
   - SSL certificate (via Let's Encrypt)
   - WWW redirect (www.realdiag.com → realdiag.com)
   - HTTPS enforcement
   - CDN distribution

4. **Add API Subdomain:**
   - In Netlify DNS settings, add a CNAME record:
     ```
     Type: CNAME
     Name: api
     Value: realdiag-software.onrender.com
     TTL: 3600
     ```

---

### Option B: Using Cloudflare DNS (Best for Performance & Security)

1. **Add Site to Cloudflare:**
   - Go to https://dash.cloudflare.com
   - Click **Add a site**
   - Enter: `realdiag.com`
   - Select Free plan
   - Cloudflare will scan existing DNS records

2. **Update Nameservers:**
   
   Cloudflare provides nameservers like:
   ```
   lara.ns.cloudflare.com
   ned.ns.cloudflare.com
   ```

   Update these at your domain registrar.

3. **Add DNS Records:**

   **For Frontend (Netlify):**
   ```
   Type: CNAME
   Name: @
   Content: realdiag.netlify.app
   Proxy status: Proxied (orange cloud)
   TTL: Auto
   ```

   ```
   Type: CNAME
   Name: www
   Content: realdiag.netlify.app
   Proxy status: Proxied (orange cloud)
   TTL: Auto
   ```

   **For Backend (Render):**
   ```
   Type: CNAME
   Name: api
   Content: realdiag-software.onrender.com
   Proxy status: Proxied (orange cloud)
   TTL: Auto
   ```

4. **Configure SSL/TLS:**
   - In Cloudflare dashboard → SSL/TLS
   - Set to **Full (strict)**
   - Enable **Always Use HTTPS**
   - Enable **Automatic HTTPS Rewrites**

5. **Enable Security Features:**
   - **Security** → **Settings** → Enable **Browser Integrity Check**
   - **Security** → **Bots** → Enable **Bot Fight Mode** (Free)
   - **Speed** → **Optimization** → Enable **Auto Minify** (JS, CSS, HTML)

---

## Step 3: Configure Netlify Custom Domain

1. **Add Custom Domain:**
   - Netlify dashboard → Your site → **Domain settings**
   - Click **Add custom domain**
   - Enter: `realdiag.com`
   - Click **Verify**

2. **Add WWW Subdomain:**
   - Click **Add domain alias**
   - Enter: `www.realdiag.com`
   - Netlify will redirect www → non-www automatically

3. **Enable HTTPS:**
   - Netlify auto-provisions SSL via Let's Encrypt
   - Wait 1-5 minutes for certificate
   - Verify HTTPS is active

4. **Force HTTPS:**
   - In domain settings, enable **Force HTTPS**
   - All HTTP requests will redirect to HTTPS

---

## Step 4: Configure Render Custom Domain

1. **Add Custom Domain:**
   - Go to https://dashboard.render.com
   - Select your `realdiag-software` service
   - Click **Settings** tab
   - Scroll to **Custom Domains**
   - Click **Add Custom Domain**
   - Enter: `api.realdiag.com`

2. **Verify DNS:**
   - Render will show DNS configuration needed
   - Ensure your CNAME record points to `realdiag-software.onrender.com`
   - Click **Verify** once DNS is configured

3. **SSL Certificate:**
   - Render auto-provisions SSL certificate
   - Wait 5-10 minutes for activation
   - Verify at: https://api.realdiag.com/health

---

## Step 5: Update Application Configuration

### Backend Configuration

Update CORS origins in Render environment variables:

```bash
CORS_ORIGINS=https://realdiag.com,https://www.realdiag.com
FRONTEND_URL=https://realdiag.com
API_BASE_URL=https://api.realdiag.com
```

### Frontend Configuration

Update API endpoint in Netlify environment variables:

```bash
NEXT_PUBLIC_API_URL=https://api.realdiag.com
```

Or if using runtime config, update `frontend/next.config.js`:

```javascript
module.exports = {
  publicRuntimeConfig: {
    apiUrl: process.env.NEXT_PUBLIC_API_URL || 'https://api.realdiag.com'
  }
}
```

---

## Step 6: Update API Calls in Frontend

Find and replace API URLs in your frontend code:

```bash
cd /workspaces/RealDiag-Software/frontend

# Search for hardcoded API URLs
grep -r "realdiag-software.onrender.com" pages/ --include="*.js" --include="*.jsx"
```

Update to use the custom domain:

**Before:**
```javascript
const response = await fetch('https://realdiag-software.onrender.com/api/endpoint');
```

**After:**
```javascript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.realdiag.com';
const response = await fetch(`${API_URL}/api/endpoint`);
```

---

## Step 7: Update Security Headers

Update CSP in `backend/services/security.py`:

```python
"Content-Security-Policy": (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self'; "
    "img-src 'self' data: https:; "
    "font-src 'self' data:; "
    "connect-src 'self' https://api.realdiag.com https://sentry.io; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "form-action 'self'; "
    "upgrade-insecure-requests;"
)
```

---

## Step 8: Test Configuration

### DNS Propagation Check

```bash
# Check if DNS has propagated
dig realdiag.com
dig www.realdiag.com
dig api.realdiag.com

# Or use online tool
# https://www.whatsmydns.net/#A/realdiag.com
```

### SSL Certificate Check

```bash
# Verify SSL certificates
curl -vI https://realdiag.com 2>&1 | grep -i "SSL certificate"
curl -vI https://api.realdiag.com 2>&1 | grep -i "SSL certificate"
```

### Functionality Tests

```bash
# Test backend API
curl https://api.realdiag.com/health
curl https://api.realdiag.com/version

# Test frontend
curl -I https://realdiag.com
curl -I https://www.realdiag.com  # Should redirect to realdiag.com
```

### Browser Test

1. Open: https://realdiag.com
2. Check that site loads correctly
3. Open DevTools → Network tab
4. Verify all API calls go to `api.realdiag.com`
5. Check for mixed content warnings (should be none)
6. Test symptom search functionality
7. Test user login/signup

---

## Step 9: Update Documentation & Links

### Update References

Files to update:
- `README.md` - Update live demo URLs
- `DEPLOYMENT.md` - Update deployment URLs
- `frontend/public/manifest.json` - Update start_url
- `backend/templates/index.html` - Update links if any

### Update External Services

- **Sentry:** Update "Allowed Domains" to include `realdiag.com`
- **OAuth (Epic/Cerner):** Update redirect URIs if using EHR integration
- **Analytics:** Update allowed domains if using Plausible/Matomo

---

## Step 10: Monitor & Verify

### First 24 Hours

- [ ] Check Sentry for any CORS errors
- [ ] Monitor Netlify analytics for traffic
- [ ] Check Render logs for API errors
- [ ] Verify all pages load correctly
- [ ] Test on multiple devices/browsers

### Performance Check

```bash
# Run load test with new domain
sed -i 's/realdiag-software.onrender.com/api.realdiag.com/g' load_test.sh
bash load_test.sh
```

### SEO Configuration

**Add to `frontend/pages/_app.js`:**
```javascript
<Head>
  <link rel="canonical" href="https://realdiag.com" />
  <meta property="og:url" content="https://realdiag.com" />
</Head>
```

---

## 🔧 Troubleshooting

### DNS Not Resolving

**Problem:** `dig realdiag.com` shows no results

**Solution:**
1. Verify nameservers are correctly updated at registrar
2. Wait 24-48 hours for DNS propagation
3. Clear local DNS cache: `sudo systemd-resolve --flush-caches`

### SSL Certificate Error

**Problem:** "Your connection is not private" error

**Solution:**
1. Wait 5-10 minutes for SSL provisioning
2. Check Netlify/Render dashboard for SSL status
3. Verify DNS CNAME records are correct
4. Force SSL regeneration in platform dashboard

### CORS Errors

**Problem:** Browser shows CORS policy errors

**Solution:**
1. Verify `CORS_ORIGINS` includes `https://realdiag.com`
2. Check no trailing slashes in URLs
3. Restart backend service after updating env vars
4. Clear browser cache and test in incognito

### Mixed Content Warnings

**Problem:** "Mixed Content" errors in console

**Solution:**
1. Search for `http://` URLs in frontend code
2. Update all to use `https://` or protocol-relative URLs
3. Update CSP `upgrade-insecure-requests` directive

### WWW Not Redirecting

**Problem:** `www.realdiag.com` doesn't redirect to `realdiag.com`

**Solution:**
1. Add www as domain alias in Netlify
2. Verify CNAME record for www subdomain
3. Check redirect rules in `netlify.toml`

---

## 📋 Quick Reference

### DNS Records Summary

| Type | Name | Value | TTL |
|------|------|-------|-----|
| CNAME | @ | realdiag.netlify.app | 3600 |
| CNAME | www | realdiag.netlify.app | 3600 |
| CNAME | api | realdiag-software.onrender.com | 3600 |
| TXT | @ | netlify-verification=... | 3600 |

### Environment Variables to Update

**Render:**
```bash
CORS_ORIGINS=https://realdiag.com,https://www.realdiag.com
FRONTEND_URL=https://realdiag.com
API_BASE_URL=https://api.realdiag.com
ENVIRONMENT=production
```

**Netlify:**
```bash
NEXT_PUBLIC_API_URL=https://api.realdiag.com
NEXT_PUBLIC_ENVIRONMENT=production
```

---

## 📱 Post-Setup Tasks

### 1. Update PWA Manifest

Edit `frontend/public/manifest.json`:
```json
{
  "name": "RealDiag",
  "short_name": "RealDiag",
  "start_url": "https://realdiag.com",
  "scope": "https://realdiag.com/",
  "id": "https://realdiag.com/"
}
```

### 2. Submit to Search Engines

**Google Search Console:**
1. Go to https://search.google.com/search-console
2. Add property: `https://realdiag.com`
3. Verify ownership via DNS TXT record
4. Submit sitemap: `https://realdiag.com/sitemap.xml`

**Bing Webmaster Tools:**
1. Go to https://www.bing.com/webmasters
2. Add site: `https://realdiag.com`
3. Verify and submit sitemap

### 3. Set Up Monitoring

**Uptime Monitoring:**
- UptimeRobot: https://uptimerobot.com
- Monitor: `https://realdiag.com` and `https://api.realdiag.com/health`
- Alert via email/Slack on downtime

**Performance Monitoring:**
- Google PageSpeed Insights
- WebPageTest.org
- Lighthouse CI

---

## ✅ Completion Checklist

- [ ] Domain purchased and registered
- [ ] DNS records configured
- [ ] Nameservers updated and propagated
- [ ] Custom domain added to Netlify
- [ ] Custom domain added to Render
- [ ] SSL certificates active for all domains
- [ ] Environment variables updated (backend)
- [ ] Environment variables updated (frontend)
- [ ] API URLs updated in frontend code
- [ ] CORS origins updated in backend
- [ ] Security headers updated
- [ ] All tests passing
- [ ] No CORS errors in browser console
- [ ] No mixed content warnings
- [ ] WWW redirecting correctly
- [ ] Documentation updated
- [ ] External services updated (Sentry, OAuth)
- [ ] Monitoring configured
- [ ] Search engine submission completed

---

## 🎉 Success!

Once all steps are complete, your production URLs will be:

- **Website:** https://realdiag.com
- **API:** https://api.realdiag.com
- **API Docs:** https://api.realdiag.com/docs

**Estimated Time:** 2-4 hours (including DNS propagation)

---

## 📞 Need Help?

**DNS Issues:** Check with your domain registrar support  
**SSL Issues:** Check Netlify/Render documentation  
**CORS Issues:** Review backend CORS configuration  
**Performance:** Run load tests and check Sentry logs

**Documentation:**
- Netlify Custom Domains: https://docs.netlify.com/domains-https/custom-domains/
- Render Custom Domains: https://render.com/docs/custom-domains
- Cloudflare Setup: https://developers.cloudflare.com/dns/
