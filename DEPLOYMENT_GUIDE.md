# Complete Deployment Guide for Render.com

## Step-by-Step Instructions

### 1. Prepare Your Repository
Make sure your GitHub repository has these files in the root:
- `app.py`
- `requirements.txt`
- `runtime.txt`
- `.python-version`
- `Dockerfile`
- `render.yaml`

### 2. Render.com Service Configuration

#### Method 1: Using render.yaml (Recommended)
The `render.yaml` file will automatically configure your service.

#### Method 2: Manual Configuration
If render.yaml doesn't work, configure manually:

1. **Environment**: Python 3
2. **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
3. **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app:app`
4. **Environment Variables**:
   - `PYTHON_VERSION`: `3.11.9`
   - `POETRY_VERSION`: `` (empty to disable Poetry)

### 3. Alternative: Docker Deployment
If Python detection still fails:

1. Change **Environment** to "Docker"
2. Render will use the provided Dockerfile
3. No need to set build/start commands

### 4. Troubleshooting Common Issues

#### Issue: Python 3.13 Still Being Used
**Solution**: Add environment variable `PYTHON_VERSION=3.11.9`

#### Issue: Poetry Conflicts
**Solution**: Add environment variable `POETRY_VERSION=` (empty value)

#### Issue: Pillow Build Errors
**Solution**: Use Docker deployment or ensure system dependencies are installed

#### Issue: Memory Errors
**Solution**: Reduce image size or upgrade to paid plan

### 5. Testing Your Deployment

Once deployed, test these endpoints:
- `GET /` - Health check
- `POST /remove-background` - Background removal

### 6. Frontend Configuration

Update your frontend's `API_BASE_URL` to your Render.com URL:
\`\`\`javascript
const API_BASE_URL = 'https://your-service-name.onrender.com';
\`\`\`

### 7. Performance Optimization

For better performance on free tier:
- Keep service active with periodic health checks
- Optimize image sizes before processing
- Consider upgrading to paid plan for production use
