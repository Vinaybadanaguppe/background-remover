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

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set max content length to 16MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        import sys
        import platform
        port = os.environ.get('PORT', 'Not set')
        return jsonify({
            "status": "healthy",
            "message": "Background Remover API is running",
            "version": "1.0.0",
            "port": port,
            "python_version": sys.version,
            "platform": platform.platform(),
            "rembg_available": True
        })
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Health check failed: {str(e)}"
        }), 500

@app.route('/remove-background', methods=['POST'])
def remove_background():
    """Remove background from uploaded image"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({
                "error": "No image data provided",
                "message": "Please provide base64 encoded image in 'image' field"
            }), 400
        
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
            return jsonify({
                "error": "Invalid base64 image data",
                "message": "Could not decode the provided image data"
            }), 400
        
        # Open image with PIL
        try:
            input_image = Image.open(io.BytesIO(image_bytes))
            logger.info(f"Processing image: {input_image.size}, mode: {input_image.mode}")
        except Exception as e:
            logger.error(f"PIL image open error: {str(e)}")
            return jsonify({
                "error": "Invalid image format",
                "message": "Could not process the provided image"
            }), 400
        
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
            
            return jsonify({
                "success": True,
                "image": f"data:image/png;base64,{output_base64}",
                "message": "Background removed successfully"
            })
            
        except Exception as e:
            logger.error(f"Background removal error: {str(e)}")
            return jsonify({
                "error": "Background removal failed",
                "message": f"Error processing image: {str(e)}"
            }), 500
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({
        "error": "File too large",
        "message": "The uploaded image is too large. Please use a smaller image."
    }), 413

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "error": "Internal server error",
        "message": "Something went wrong on our end"
    }), 500

# This ensures the app binds to the correct port when run directly
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Flask app on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)
