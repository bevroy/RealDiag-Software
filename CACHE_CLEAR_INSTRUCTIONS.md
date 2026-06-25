# How to Clear Netlify Cache

## The Issue
When you update files (like videos or static assets), Netlify's CDN may cache the old version. This means users still see old content even after deployment.

## Solution 1: Clear Cache via Netlify Dashboard (Recommended)

1. Go to: https://app.netlify.com/
2. Select your RealDiag site
3. Click **Deploys** tab
4. Find the most recent deploy and click **Trigger deploy** → **Clear cache and deploy site**

This forces a fresh build and purges the CDN cache.

## Solution 2: Wait for Automatic Cache Expiration

The new cache headers set in `netlify.toml` will ensure video files are revalidated:
```toml
[[headers]]
  for = "/*.mp4"
  [headers.values]
    Cache-Control = "public, max-age=3600, must-revalidate"
```

Videos now refresh after 1 hour (3600 seconds).

## Solution 3: Hard Refresh in Browser

For immediate testing without waiting for deployment:

- **Chrome/Edge (Windows/Linux)**: Ctrl + Shift + R
- **Chrome/Edge (Mac)**: Cmd + Shift + R  
- **Firefox**: Ctrl + F5 or Cmd + Shift + R
- **Safari**: Cmd + Option + R

## Solution 4: Verify Which Video Is Deployed

Check the deployed site:
```bash
curl -sI https://www.realdiag.com/RealDiag_Demo_v2.mp4 | grep -E "(HTTP|Content-Length|Last-Modified)"
```

Should show:
- HTTP/2 200 (file exists)
- Content-Length: 1738694 (1.7MB)
- Recent Last-Modified date

## Current Deployment Status

**Latest commits:**
- `86d617d` - Fix search page (removed getConfig() dependency)
- `f73b343` - Fix video caching (added v2 filename + cache headers)

**Expected behavior after deployment:**
- Video file: `/RealDiag_Demo_v2.mp4` (1.7MB, Dec 14 version)
- Search page: Should load without errors
- Cache: Videos revalidate every hour

## Troubleshooting

### Video still wrong after clearing cache?
1. Check which file is referenced in code:
   ```bash
   grep -r "\.mp4" frontend/pages/index.js
   ```
   Should show: `RealDiag_Demo_v2.mp4`

2. Verify file exists in deployment:
   - View page source in browser
   - Look for `<source src="/RealDiag_Demo_v2.mp4">`

### Search page still showing errors?
1. Check browser console for specific error message
2. Verify API is accessible:
   ```bash
   curl https://realdiag-software.onrender.com/api/search/families
   ```
3. Check Netlify build logs for errors

## Next Steps

1. ✅ Code is fixed and pushed to GitHub
2. ⏳ Wait 2-3 minutes for Netlify to deploy
3. 🔄 Clear cache via Netlify dashboard (Solution 1 above)
4. ✅ Hard refresh browser (Ctrl+Shift+R)
5. ✅ Test search page and video

## Monitoring Deployment

Watch deployment progress:
- Netlify Dashboard: https://app.netlify.com/ → Deploys tab
- Look for "Deploy preview succeeded" or "Published"
- Check deploy log for any errors

Typical deploy time: 2-5 minutes
