# Background Remover Service

A complete background removal service using Flask + rembg library, deployable to Render.com with a frontend that can be hosted on any web hosting service.

## Architecture

- **Frontend**: HTML/CSS/JavaScript (can be hosted on GoDaddy or any web hosting)
- **Backend**: Flask API with rembg library (deployed on Render.com)
- **Communication**: REST API with base64 encoded images

## Deployment Instructions

### 1. Deploy Backend to Render.com

1. Create a new account on [Render.com](https://render.com)
2. Connect your GitHub repository
3. Create a new "Web Service"
4. Configure the service:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app:app`
   - **Environment**: Python 3
5. Deploy and note your service URL (e.g., `https://your-app-name.onrender.com`)

### 2. Deploy Frontend to GoDaddy

1. Update the `API_BASE_URL` in `frontend/index.html` with your Render.com URL
2. Upload the `frontend/index.html` file to your GoDaddy hosting
3. Access your website

## Features

- ✅ Drag & drop image upload
- ✅ Multiple image format support (JPG, PNG, WEBP)
- ✅ Real-time processing with loading indicators
- ✅ Side-by-side comparison view
- ✅ Download processed images
- ✅ Mobile responsive design
- ✅ Error handling and validation
- ✅ CORS enabled for cross-origin requests

## API Endpoints

### GET /
Health check endpoint

### POST /remove-background
Remove background from image

**Request Body:**
\`\`\`json
{
  "image": "base64_encoded_image_data"
}
\`\`\`

**Response:**
\`\`\`json
{
  "success": true,
  "image": "data:image/png;base64,processed_image_data",
  "message": "Background removed successfully"
}
\`\`\`

## Local Development

1. Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

2. Run the Flask app:
\`\`\`bash
python app.py
\`\`\`

3. Open `frontend/index.html` in your browser and update the API_BASE_URL to `http://localhost:5000`

## Limitations on Render.com Free Tier

- Service may sleep after 15 minutes of inactivity
- 512MB RAM limit
- 750 hours/month usage limit
- Processing time may be slower due to resource constraints

## Troubleshooting

1. **CORS Issues**: Make sure flask-cors is installed and configured
2. **Memory Issues**: Large images may cause memory errors on free tier
3. **Timeout Issues**: Increase gunicorn timeout for large images
4. **Service Sleeping**: First request after inactivity may take longer

## Security Considerations

- File size validation (10MB limit)
- File type validation
- Error handling for malformed requests
- No file storage (images processed in memory)
