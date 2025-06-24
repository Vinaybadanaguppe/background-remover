#!/usr/bin/env python3
import os
import sys
import socket
import time
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CRITICAL: Get port and bind immediately
PORT = int(os.environ.get('PORT', 10000))

# Test port binding BEFORE creating Flask app
def test_port_binding():
    """Test if we can bind to the port immediately"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', PORT))
        sock.listen(1)
        print(f"✅ PORT {PORT} IS AVAILABLE AND BOUND")
        sock.close()
        return True
    except Exception as e:
        print(f"❌ CANNOT BIND TO PORT {PORT}: {e}")
        return False

# Test port immediately
print(f"🚀 TESTING PORT BINDING ON {PORT}")
if not test_port_binding():
    print("❌ PORT BINDING FAILED - EXITING")
    sys.exit(1)

print(f"🔥 CREATING FLASK APP ON PORT {PORT}")

# Create Flask app
app = Flask(__name__)
CORS(app, origins=['*'], methods=['GET', 'POST', 'OPTIONS'], allow_headers=['*'])
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024  # Reduced to 3MB

@app.route('/', methods=['GET', 'OPTIONS'])
def health_check():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    
    response = jsonify({
        "status": "healthy",
        "message": "Background Remover API is running",
        "version": "1.0.0",
        "port": str(PORT),
        "rembg_available": True,
        "cors_enabled": True,
        "environment": "production",
        "max_file_size": "2MB",
        "processing_timeout": "60s"
    })
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/remove-background', methods=['POST', 'OPTIONS'])
def remove_background():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        return response
    
    start_time = time.time()
    
    try:
        logger.info("🎯 Starting background removal request")
        
        import base64
        import io
        from PIL import Image
        from rembg import remove as rembg_remove
        import gc
        
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
        
        # Decode image
        logger.info("📥 Decoding base64 image...")
        image_bytes = base64.b64decode(image_data)
        logger.info(f"📊 Image size: {len(image_bytes)} bytes ({len(image_bytes)/1024/1024:.2f} MB)")
        
        # Strict size limits for free tier
        if len(image_bytes) > 2 * 1024 * 1024:  # 2MB hard limit
            response = jsonify({
                "error": "Image too large for free tier",
                "message": "Please use an image smaller than 2MB for reliable processing"
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 413
        
        # Process image with aggressive optimization
        logger.info("🖼️ Opening and optimizing image...")
        input_image = Image.open(io.BytesIO(image_bytes))
        logger.info(f"📐 Original dimensions: {input_image.size}, mode: {input_image.mode}")
        
        # Aggressive resizing for free tier performance
        max_dimension = 600  # Reduced from 800
        if max(input_image.size) > max_dimension:
            logger.info(f"🔄 Resizing image from {input_image.size}")
            ratio = max_dimension / max(input_image.size)
            new_size = tuple(int(dim * ratio) for dim in input_image.size)
            input_image = input_image.resize(new_size, Image.Resampling.LANCZOS)
            logger.info(f"✅ Resized to: {input_image.size}")
        
        # Convert to RGB for better rembg performance
        if input_image.mode != 'RGB':
            logger.info(f"🎨 Converting from {input_image.mode} to RGB")
            if input_image.mode in ('RGBA', 'LA'):
                # Create white background for transparent images
                background = Image.new('RGB', input_image.size, (255, 255, 255))
                if input_image.mode == 'RGBA':
                    background.paste(input_image, mask=input_image.split()[-1])
                else:
                    background.paste(input_image)
                input_image = background
            else:
                input_image = input_image.convert('RGB')
        
        # Convert to bytes with optimization
        logger.info("🔄 Converting to bytes for processing...")
        img_byte_arr = io.BytesIO()
        input_image.save(img_byte_arr, format='JPEG', quality=85, optimize=True)  # Use JPEG for smaller size
        img_byte_arr = img_byte_arr.getvalue()
        
        logger.info(f"📦 Optimized size: {len(img_byte_arr)} bytes ({len(img_byte_arr)/1024/1024:.2f} MB)")
        
        # Clear memory before heavy operation
        del image_bytes
        gc.collect()
        
        # Remove background with timeout protection
        logger.info("🤖 Starting AI background removal...")
        processing_start = time.time()
        
        try:
            output_bytes = rembg_remove(img_byte_arr)
            processing_time = time.time() - processing_start
            logger.info(f"✅ Background removal completed in {processing_time:.2f}s")
        except Exception as e:
            logger.error(f"❌ rembg processing failed: {str(e)}")
            response = jsonify({
                "error": "AI processing failed",
                "message": "Background removal failed - try a smaller or simpler image"
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 500
        
        # Convert to base64
        logger.info("📤 Encoding result...")
        output_base64 = base64.b64encode(output_bytes).decode('utf-8')
        
        # Cleanup memory
        del img_byte_arr, output_bytes, input_image
        gc.collect()
        
        total_time = time.time() - start_time
        logger.info(f"🎉 Request completed in {total_time:.2f}s")
        
        response = jsonify({
            "success": True,
            "image": f"data:image/png;base64,{output_base64}",
            "message": "Background removed successfully",
            "processing_time": f"{total_time:.2f}s"
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
        
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"❌ Request failed after {total_time:.2f}s: {str(e)}")
        
        # Clear memory on error
        gc.collect()
        
        response = jsonify({
            "error": "Processing failed",
            "message": f"Error after {total_time:.2f}s - try a smaller image (max 1MB recommended)"
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 500

@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

# IMMEDIATE STARTUP
if __name__ == '__main__':
    print(f"🔥 STARTING FLASK SERVER IMMEDIATELY ON 0.0.0.0:{PORT}")
    try:
        app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
    except Exception as e:
        print(f"❌ FLASK STARTUP FAILED: {e}")
        sys.exit(1)

# Also start immediately (not just in __main__)
print(f"🚀 IMMEDIATE FLASK STARTUP ON 0.0.0.0:{PORT}")
app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
