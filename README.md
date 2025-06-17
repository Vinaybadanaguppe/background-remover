# Background Remover API

A Flask-based REST API that removes backgrounds from images using the powerful `rembg` library.

## Features

- Remove backgrounds from images using advanced AI
- Support for various image formats
- Simple REST API interface
- CORS enabled for cross-origin requests
- Health check endpoint
- Production-ready with Gunicorn

## API Endpoints

### Remove Background
- **URL**: `/remove`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Parameter**: `image` (file)
- **Response**: PNG image file with background removed
- **Status Codes**:
  - 200: Success
  - 400: No image uploaded
  - 500: Error processing image

### Health Check
- **URL**: `/health`
- **Method**: `GET`
- **Response**: String indicating API status
- **Status Code**: 200

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the development server:
```bash
python app.py
```

The server will start at `http://localhost:5000`

## Example Usage

Using cURL:
```bash
curl -X POST -F "image=@path/to/your/image.jpg" http://localhost:5000/remove --output output.png
```

Using Python requests:
```python
import requests

url = 'http://localhost:5000/remove'
files = {'image': open('input.jpg', 'rb')}
response = requests.post(url, files=files)

if response.status_code == 200:
    with open('output.png', 'wb') as f:
        f.write(response.content)
```

## Production Deployment

This project is configured for deployment on Render.com. The deployment configuration is specified in `render.yaml`.

# Background Remover API

A Flask-based REST API that removes backgrounds from images using the `rembg` library.

## Setup

1. Install the requirements:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
# Development
python app.py

# Production
gunicorn app:app -b 0.0.0.0:5000
```

## API Endpoints

### Remove Background
- **URL**: `/remove`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Parameter**: `image` (file)
- **Response**: PNG image file with background removed

### Health Check
- **URL**: `/health`
- **Method**: `GET`
- **Response**: String indicating API status

## Example Usage

```python
import requests

url = 'http://localhost:5000/remove'
files = {'image': open('input.jpg', 'rb')}
response = requests.post(url, files=files)

if response.status_code == 200:
    with open('output.png', 'wb') as f:
        f.write(response.content)
```

## Notes
- The API accepts image files in common formats (JPEG, PNG, etc.)
- The output is always in PNG format
- CORS is enabled for all routes, allowing cross-origin requests
