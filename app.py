from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io
from PIL import Image
from rembg import remove
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# CRITICAL: Configure CORS properly for cross-origin requests
CORS(app, 
     origins=['*'],  # Allow all origins for now
     methods=['GET', 'POST', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'Accept'],
     supports_credentials=False
)

# Set max content length to 16MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route('/', methods=['GET', 'OPTIONS'])
def health_check():
    """Health check endpoint"""
    try:
        # Handle preflight OPTIONS request
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
            return response
            
        port = os.environ.get('PORT', 'Not set')
        response_data = {
            "status": "healthy",
            "message": "Background Remover API is running",
            "version": "1.0.0",
            "port": port,
            "rembg_available": True,
            "cors_enabled": True
        }
        
        response = jsonify(response_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        response = jsonify({
            "status": "error",
            "message": f"Health check failed: {str(e)}"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@app.route('/remove-background', methods=['POST', 'OPTIONS'])
def remove_background():
    """Remove background from uploaded image"""
    try:
        # Handle preflight OPTIONS request
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
            return response
        
        # Get JSON data from request
        data = request.get_json()
        
        if not data or 'image' not in data:
            response = jsonify({
                "error": "No image data provided",
                "message": "Please provide base64 encoded image in 'image' field"
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        # Get base64 image data
        image_data = data['image']
        
        # Remove data:image/jpeg;base64, or similar prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            logger.error(f"Base64 decode error: {str(e)}")
            response = jsonify({
                "error": "Invalid base64 image data",
                "message": "Could not decode the provided image data"
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        # Open image with PIL
        try:
            input_image = Image.open(io.BytesIO(image_bytes))
            logger.info(f"Processing image: {input_image.size}, mode: {input_image.mode}")
        except Exception as e:
            logger.error(f"PIL image open error: {str(e)}")
            response = jsonify({
                "error": "Invalid image format",
                "message": "Could not process the provided image"
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        # Remove background using rembg
        try:
            # Convert image to bytes for rembg
            img_byte_arr = io.BytesIO()
            input_image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Remove background
            logger.info("Starting background removal...")
            output_bytes = remove(img_byte_arr)
            
            # Convert back to base64
            output_base64 = base64.b64encode(output_bytes).decode('utf-8')
            
            logger.info("Background removal successful")
            
            response = jsonify({
                "success": True,
                "image": f"data:image/png;base64,{output_base64}",
                "message": "Background removed successfully"
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
            
        except Exception as e:
            logger.error(f"Background removal error: {str(e)}")
            response = jsonify({
                "error": "Background removal failed",
                "message": f"Error processing image: {str(e)}"
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        response = jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@app.errorhandler(413)
def too_large(e):
    response = jsonify({
        "error": "File too large",
        "message": "The uploaded image is too large. Please use a smaller image."
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 413

@app.errorhandler(500)
def internal_error(e):
    response = jsonify({
        "error": "Internal server error",
        "message": "Something went wrong on our end"
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 500

# Add a catch-all OPTIONS handler
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'status': 'ok'})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# CRITICAL: This is the Render.com port binding fix
if __name__ == '__main__':
    # Get port from environment variable (Render.com requirement)
    port = int(os.environ.get('PORT', 5000))
    
    # Log the port for debugging
    logger.info(f"Starting Flask app on 0.0.0.0:{port}")
    
    # MUST bind to 0.0.0.0 for Render.com (not localhost or 127.0.0.1)
    app.run(
        host='0.0.0.0',  # Required by Render.com
        port=port,       # Use PORT environment variable
        debug=False
    )
