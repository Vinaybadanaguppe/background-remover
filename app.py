import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io
from PIL import Image
from rembg import remove

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get port from environment variable FIRST
PORT = int(os.environ.get('PORT', 10000))
logger.info(f"🚀 Starting app with PORT={PORT}")

# Create Flask app
app = Flask(__name__)

# Configure CORS with explicit settings
CORS(app, 
     origins=['*'],
     methods=['GET', 'POST', 'OPTIONS'],
     allow_headers=['*'],
     supports_credentials=False,
     send_wildcard=True
)

# Set max content length to 16MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route('/', methods=['GET', 'OPTIONS'])
def health_check():
    """Health check endpoint"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        return response
    
    try:
        response_data = {
            "status": "healthy",
            "message": "Background Remover API is running",
            "version": "1.0.0",
            "port": str(PORT),
            "rembg_available": True,
            "cors_enabled": True,
            "environment": "production"
        }
        
        response = jsonify(response_data)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        return response
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        response = jsonify({
            "status": "error",
            "message": f"Health check failed: {str(e)}"
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 500

@app.route('/remove-background', methods=['POST', 'OPTIONS'])
def remove_background():
    """Remove background from uploaded image"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        return response
    
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            response = jsonify({
                "error": "No image data provided",
                "message": "Please provide base64 encoded image in 'image' field"
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 400
        
        image_data = data['image']
        
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            logger.error(f"Base64 decode error: {str(e)}")
            response = jsonify({
                "error": "Invalid base64 image data",
                "message": "Could not decode the provided image data"
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 400
        
        try:
            input_image = Image.open(io.BytesIO(image_bytes))
            logger.info(f"Processing image: {input_image.size}, mode: {input_image.mode}")
        except Exception as e:
            logger.error(f"PIL image open error: {str(e)}")
            response = jsonify({
                "error": "Invalid image format",
                "message": "Could not process the provided image"
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 400
        
        try:
            img_byte_arr = io.BytesIO()
            input_image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            logger.info("Starting background removal...")
            output_bytes = remove(img_byte_arr)
            
            output_base64 = base64.b64encode(output_bytes).decode('utf-8')
            
            logger.info("Background removal successful")
            
            response = jsonify({
                "success": True,
                "image": f"data:image/png;base64,{output_base64}",
                "message": "Background removed successfully"
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
            
        except Exception as e:
            logger.error(f"Background removal error: {str(e)}")
            response = jsonify({
                "error": "Background removal failed",
                "message": f"Error processing image: {str(e)}"
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 500
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        response = jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 500

# Global CORS headers for all responses
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Max-Age'] = '86400'
    return response

# CRITICAL: This ensures immediate port binding
def create_app():
    """Application factory"""
    return app

# For direct execution (python app.py)
if __name__ == '__main__':
    logger.info(f"🔥 DIRECT EXECUTION: Binding to 0.0.0.0:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)

# For gunicorn execution
def application(environ, start_response):
    """WSGI application"""
    return app(environ, start_response)

# Alternative entry point
def main():
    logger.info(f"🔥 MAIN FUNCTION: Binding to 0.0.0.0:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
