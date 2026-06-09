# 🆘 Jimmy Bot Dashboard - Troubleshooting Guide

## 🔴 Dashboard Issues

### Issue: "API status: Loading..." (Forever)

**Symptoms:**
- Dashboard loads but shows "API status: Loading…" indefinitely
- Other content displays but status doesn't change
- No error messages in browser

**Solutions:**

1. **Check if backend is running:**
   ```bash
   # For local development
   curl http://localhost:8000/health
   # Should return: {"status":"ok"}
   
   # For deployed backend
   curl https://your-bot-url.onrender.com/health
   ```

2. **Verify API URL is correct:**
   - Check browser console (F12 → Console tab)
   - Look for "API Base URL:" logs
   - Ensure no trailing slashes
   - Check for typos in domain

3. **Check CORS configuration:**
   - Open browser DevTools (F12 → Network)
   - Refresh page
   - Look for `/health` request
   - Check response headers for `Access-Control-Allow-Origin`

4. **Set API URL in browser:**
   - Go to Dashboard Settings
   - Manually enter your API URL
   - Save and refresh

**Still not working?**
- Clear browser cache (Ctrl+Shift+Delete)
- Try in private/incognito mode
- Test with: `curl -v https://your-api/health`

---

### Issue: "Settings won't save"

**Symptoms:**
- Click "Save production settings" but nothing happens
- Or shows error message
- Settings clear but don't persist

**Solutions:**

1. **Verify endpoint exists:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/admin/settings \
     -H "Content-Type: application/json" \
     -d '{"telegram_bot_token":"test"}'
   ```

2. **Check for validation errors:**
   - Open browser DevTools (F12 → Network)
   - Find the POST request to `/admin/settings`
   - Check the response body for error details
   - Fix validation issues (e.g., invalid URLs)

3. **Ensure backend accepts the data:**
   - Verify all fields match backend schema
   - Check required vs optional fields
   - Test with minimal data first:
   ```bash
   curl -X POST http://localhost:8000/api/v1/admin/settings \
     -H "Content-Type: application/json" \
     -d '{}'
   ```

4. **Check for CORS errors:**
   - If request is blocked by CORS
   - Backend needs to allow GitHub Pages origin
   - See [DASHBOARD_CONFIG.md](DASHBOARD_CONFIG.md) for CORS setup

---

### Issue: "Blank dashboard / No data showing"

**Symptoms:**
- Dashboard page loads
- All components appear but empty
- No users, messages, or analytics

**Solutions:**

1. **Check analytics endpoint:**
   ```bash
   curl http://localhost:8000/api/v1/admin/analytics
   # Should return JSON with data
   ```

2. **Populate test data:**
   ```bash
   # Run seed script
   python init_database.py
   
   # Or add test data:
   curl -X POST http://localhost:8000/api/v1/messages \
     -H "Content-Type: application/json" \
     -d '{"user_id":"test","content":"hello"}'
   ```

3. **Check database connection:**
   - Verify DATABASE_URL is set
   - Test database access:
   ```bash
   sqlite3 ./data/bot.db "SELECT COUNT(*) FROM users;"
   ```

4. **Check API permissions:**
   - Ensure `/api/v1/admin/*` endpoints are accessible
   - No authentication required for demo mode
   - Check for rate limiting

---

### Issue: WhatsApp QR code not appearing

**Symptoms:**
- "Start WhatsApp connection" button clicked
- Loading spinner shows but QR never appears
- Error message shown

**Solutions:**

1. **Check WhatsApp integration enabled:**
   ```python
   # In .env
   WHATSAPP_ENABLED=true
   WHATSAPP_ACCESS_TOKEN=your_token
   ```

2. **Check backend WhatsApp endpoint:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/whatsapp-qr/start-connection \
     -H "Content-Type: application/json" \
     -d '{"name":"test"}'
   ```

3. **Check backend logs:**
   ```bash
   # Look for WhatsApp connection errors
   tail -f ./logs/bot.log | grep -i whatsapp
   ```

4. **Reset WhatsApp connection:**
   - Delete connection state file:
   ```bash
   rm -rf ./data/whatsapp_connections/
   ```
   - Try again

5. **Update WhatsApp library:**
   ```bash
   pip install --upgrade whatsapp-web.py
   ```

---

### Issue: Telegram webhook not connecting

**Symptoms:**
- Telegram setup shows webhook URL
- Messages not being received
- Or shows "error updating webhook"

**Solutions:**

1. **Verify webhook URL is accessible:**
   ```bash
   # Replace URL with your actual URL
   curl -v https://your-bot-url.onrender.com/api/v1/telegram/webhook
   # Should return 405 (GET not allowed) or similar
   ```

2. **Test webhook with Telegram API:**
   ```bash
   curl -X POST https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook \
     -d "url=https://your-bot-url.onrender.com/api/v1/telegram/webhook"
   ```

3. **Check Telegram bot token:**
   ```bash
   curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe
   # Should return bot info
   ```

4. **Verify HTTPS (required by Telegram):**
   - Telegram only accepts HTTPS webhooks
   - HTTP will not work
   - Test with: `curl -v https://...`

5. **Check webhook logs:**
   ```bash
   # Watch backend logs for webhook calls
   tail -f ./logs/bot.log | grep -i webhook
   ```

6. **Resync webhook:**
   ```bash
   # Delete webhook
   curl -X POST https://api.telegram.org/bot<TOKEN>/setWebhook \
     -d "url="
   
   # Then re-set from dashboard
   ```

---

### Issue: Users list shows "connected accounts" but no data

**Symptoms:**
- "Connected accounts" section shows
- But the user table is empty
- Or shows old data

**Solutions:**

1. **Check users endpoint:**
   ```bash
   curl http://localhost:8000/api/v1/admin/users
   # Should return array of user objects
   ```

2. **Add test users:**
   ```bash
   # Telegram command: /start (creates user)
   # Or create via API:
   curl -X POST http://localhost:8000/api/v1/admin/users \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser","email":"test@example.com"}'
   ```

3. **Check pagination:**
   - Dashboard fetches first 50 users
   - If you have more, they won't show initially
   - Click "Load more" at bottom

4. **Refresh data:**
   - Dashboard auto-refreshes every 30 seconds
   - Or click refresh button
   - Or press F5 to reload page

---

### Issue: Analytics charts showing blank

**Symptoms:**
- Dashboard loads
- Chart containers appear
- But no actual chart data/visualization

**Solutions:**

1. **Check analytics data:**
   ```bash
   curl http://localhost:8000/api/v1/admin/analytics
   # Should return complete analytics object
   ```

2. **Check date range data:**
   ```bash
   curl http://localhost:8000/api/v1/admin/analytics/messages?days=7
   # Should return dates and counts arrays
   ```

3. **Check chart library loaded:**
   - Open browser DevTools (F12 → Console)
   - Check for Recharts errors
   - Verify no JavaScript errors

4. **Refresh chart data:**
   - Wait 10 seconds for auto-refresh
   - Or click refresh button
   - Or close and reopen dashboard

---

## 🟡 Backend Issues

### Issue: Backend won't start

**Symptoms:**
- Running `python run_bot.py` shows errors
- Port 8000 already in use
- Module import errors

**Solutions:**

1. **Check Python version:**
   ```bash
   python --version
   # Should be Python 3.10 or higher
   ```

2. **Check dependencies installed:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Port already in use:**
   ```bash
   # Kill process using port 8000
   # Windows:
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   
   # Mac/Linux:
   lsof -i :8000
   kill -9 <PID>
   ```

4. **Check database exists:**
   ```bash
   # Create if missing:
   python init_database.py
   ```

5. **Check .env file:**
   - Ensure .env exists in root
   - Has required variables
   - No syntax errors

---

### Issue: Database migration errors

**Symptoms:**
- "Table already exists" error
- "Column not found" errors
- Migration failures

**Solutions:**

1. **Reset database (dev only):**
   ```bash
   rm -f ./data/bot.db
   python init_database.py
   ```

2. **Run migrations manually:**
   ```bash
   alembic upgrade head
   ```

3. **Check migration files:**
   ```bash
   ls -la alembic/versions/
   ```

4. **Revert last migration (if needed):**
   ```bash
   alembic downgrade -1
   ```

---

### Issue: API endpoint returning 404

**Symptoms:**
- Curl test returns 404
- Dashboard shows "endpoint not found"
- Wrong URL?

**Solutions:**

1. **Verify endpoint exists:**
   ```bash
   # List all routes:
   python -c "from src.main import app; [print(r.path) for r in app.routes]"
   ```

2. **Check exact path:**
   - API endpoints use: `/api/v1/{route}`
   - Ensure trailing slash correct (usually no trailing slash)
   - Test with: `curl http://localhost:8000/api/v1/admin/analytics`

3. **Check method (GET vs POST):**
   ```bash
   # GET endpoints:
   curl http://localhost:8000/api/v1/admin/analytics
   
   # POST endpoints:
   curl -X POST http://localhost:8000/api/v1/admin/settings \
     -H "Content-Type: application/json" \
     -d '{...}'
   ```

---

## 🟢 Connection Issues

### Issue: Cannot connect to deployed backend

**Symptoms:**
- Works locally but fails on GitHub Pages
- CORS errors in browser
- Network timeout

**Solutions:**

1. **Test backend accessibility:**
   ```bash
   # From anywhere:
   curl https://your-bot-url.onrender.com/health
   # Should work from any network
   ```

2. **Check CORS headers:**
   ```bash
   curl -i https://your-bot-url.onrender.com/health
   # Look for: Access-Control-Allow-Origin: *
   ```

3. **Update dashboard API URL:**
   - GitHub Settings > Secrets
   - Update `NEXT_PUBLIC_API_BASE`
   - Redeploy dashboard
   - Wait 30 seconds for new deploy

4. **Test from dashboard directly:**
   - Go to dashboard settings
   - Enter your API URL manually
   - Save and refresh
   - Check console for actual errors

---

## 📊 Performance Issues

### Issue: Dashboard loads slowly

**Symptoms:**
- Page takes 5+ seconds to load
- Lag when scrolling
- Charts take time to render

**Solutions:**

1. **Reduce update frequency:**
   - Edit dashboard/app/page.tsx
   - Change interval from 10s to 30s
   - Reduces API calls

2. **Limit data fetched:**
   ```bash
   # Only fetch 10 users instead of 50:
   curl http://localhost:8000/api/v1/admin/users?limit=10
   ```

3. **Add caching headers:**
   - Backend should set Cache-Control headers
   - Reduces database queries

4. **Check network latency:**
   - Open DevTools (F12 → Network)
   - Check request times
   - API should respond in <500ms

---

## 📞 Getting Help

**Still stuck?**

1. Check browser console for errors: F12 → Console
2. Check backend logs: `tail -f ./logs/bot.log`
3. Test endpoints directly with curl
4. Search existing GitHub issues
5. Create new issue with:
   - Error message
   - Steps to reproduce
   - Backend URL
   - Browser/OS info

---

## 🔧 Advanced Debugging

### Enable verbose logging:
```bash
# Backend
export DEBUG=true
python run_bot.py

# Frontend
export NEXT_DEBUG=1
npm run dev
```

### Check all API endpoints:
```bash
curl http://localhost:8000/api/v1/openapi.json | python -m json.tool | grep "path"
```

### Monitor real-time requests:
```bash
# Backend
python -m pytest tests/test_integration.py -v -s

# Frontend
npm run dev -- --debug
```

---

For more help, see [DASHBOARD_CONFIG.md](DASHBOARD_CONFIG.md) and [BACKEND_DEPLOYMENT.md](BACKEND_DEPLOYMENT.md).
