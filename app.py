import os
import logging
import gc
from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io
from PIL import Image
from rembg import remove

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get port from environment variable
PORT = int(os.environ.get('PORT', 10000))
logger.info(f"🚀 Starting app with PORT={PORT}")

# Create Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, 
     origins=['*'],
     methods=['GET', 'POST', 'OPTIONS'],
     allow_headers=['*'],
     supports_credentials=False
)

# Set max content length to 8MB (reduced from 16MB for free tier)
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024

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
            "environment": "production",
            "max_file_size": "8MB"
        }
        
        response = jsonify(response_data)
        response.headers['Access-Control-Allow-Origin'] = '*'
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
        logger.info("🎯 Starting background removal request")
        
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
            logger.info("📥 Decoding base64 image...")
            image_bytes = base64.b64decode(image_data)
            logger.info(f"📊 Image size: {len(image_bytes)} bytes")
            
            # Check if image is too large for free tier
            if len(image_bytes) > 5 * 1024 * 1024:  # 5MB limit
                response = jsonify({
                    "error": "Image too large for free tier",
                    "message": "Please use an image smaller than 5MB"
                })
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response, 413
                
        except Exception as e:
            logger.error(f"Base64 decode error: {str(e)}")
            response = jsonify({
                "error": "Invalid base64 image data",
                "message": "Could not decode the provided image data"
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 400
        
        try:
            logger.info("🖼️ Opening image with PIL...")
            input_image = Image.open(io.BytesIO(image_bytes))
            logger.info(f"📐 Image dimensions: {input_image.size}, mode: {input_image.mode}")
            
            # Resize image if too large (memory optimization)
            max_dimension = 1024
            if max(input_image.size) > max_dimension:
                logger.info(f"🔄 Resizing image from {input_image.size}")
                ratio = max_dimension / max(input_image.size)
                new_size = tuple(int(dim * ratio) for dim in input_image.size)
                input_image = input_image.resize(new_size, Image.Resampling.LANCZOS)
                logger.info(f"✅ Resized to: {input_image.size}")
            
        except Exception as e:
            logger.error(f"PIL image open error: {str(e)}")
            response = jsonify({
                "error": "Invalid image format",
                "message": "Could not process the provided image"
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 400
        
        try:
            logger.info("🔄 Converting image to bytes for rembg...")
            img_byte_arr = io.BytesIO()
            
            # Convert to RGB if necessary (rembg works better with RGB)
            if input_image.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', input_image.size, (255, 255, 255))
                background.paste(input_image, mask=input_image.split()[-1] if input_image.mode == 'RGBA' else None)
                input_image = background
            elif input_image.mode != 'RGB':
                input_image = input_image.convert('RGB')
            
            input_image.save(img_byte_arr, format='PNG', optimize=True)
            img_byte_arr = img_byte_arr.getvalue()
            
            logger.info("🤖 Starting AI background removal...")
            
            # Clear memory before heavy operation
            gc.collect()
            
            # Remove background
            output_bytes = remove(img_byte_arr)
            
            logger.info("✅ Background removal successful!")
            
            # Convert back to base64
            output_base64 = base64.b64encode(output_bytes).decode('utf-8')
            
            # Clear memory
            del img_byte_arr, output_bytes, input_image
            gc.collect()
            
            logger.info("📤 Sending response...")
            
            response = jsonify({
                "success": True,
                "image": f"data:image/png;base64,{output_base64}",
                "message": "Background removed successfully"
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
            
        except Exception as e:
            logger.error(f"Background removal error: {str(e)}")
            
            # Clear memory on error
            gc.collect()
            
            response = jsonify({
                "error": "Background removal failed",
                "message": f"Processing failed - try a smaller image (max 2MB recommended)"
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

# Global CORS headers
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

# For direct execution
if __name__ == '__main__':
    logger.info(f"🔥 DIRECT EXECUTION: Binding to 0.0.0.0:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)

# Alternative entry point
def main():
    logger.info(f"🔥 MAIN FUNCTION: Binding to 0.0.0.0:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
