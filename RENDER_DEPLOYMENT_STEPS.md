# EXACT Steps to Fix Render.com Port Binding Issue

## Step 1: Update Your Render.com Service Settings

Go to your Render.com dashboard and update these settings:

### Build Command:
\`\`\`
pip install --upgrade pip && pip install -r requirements.txt
\`\`\`

### Start Command (CRITICAL - Use this exact command):
\`\`\`
python app.py
\`\`\`

**OR if you prefer gunicorn:**
\`\`\`
gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app:app
\`\`\`

### Environment Variables:
- Key: `PYTHON_VERSION`, Value: `3.11.9`

## Step 2: The Key Fix

The critical issue was that your Flask app MUST:
1. ✅ Bind to `0.0.0.0` (not localhost)
2. ✅ Use the `PORT` environment variable
3. ✅ Start immediately when the container starts

## Step 3: Alternative - Simple Python Start

Instead of gunicorn, use direct Python execution:
- **Start Command**: `python app.py`
- This ensures immediate port binding

## Step 4: Verify the Fix

After deployment, check logs for:
\`\`\`
Starting Flask app on 0.0.0.0:10000
\`\`\`

## Why This Fixes the Issue:

1. **Direct Python execution** starts faster than gunicorn
2. **0.0.0.0 binding** allows Render to detect the port
3. **Immediate startup** prevents port scan timeout
4. **PORT environment variable** is automatically provided by Render

## If Still Having Issues:

Try this alternative start command:
\`\`\`
python -c "from app import app; import os; app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))"
\`\`\`
