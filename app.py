#!/usr/bin/env python3
import os
import sys
import socket
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

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
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

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
        "environment": "production"
    })
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/remove-background', methods=['POST', 'OPTIONS'])
def remove_background():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    
    try:
        import base64
        import io
        from PIL import Image
        from rembg import remove as rembg_remove
        import gc
        
        data = request.get_json()
        if not data or 'image' not in data:
            response = jsonify({"error": "No image data provided"})
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 400
        
        image_data = data['image']
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode and process
        image_bytes = base64.b64decode(image_data)
        
        # Size check
        if len(image_bytes) > 3 * 1024 * 1024:  # 3MB limit
            response = jsonify({"error": "Image too large - max 3MB"})
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 413
        
        # Process image
        input_image = Image.open(io.BytesIO(image_bytes))
        
        # Resize if needed
        if max(input_image.size) > 800:
            ratio = 800 / max(input_image.size)
            new_size = tuple(int(dim * ratio) for dim in input_image.size)
            input_image = input_image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        if input_image.mode != 'RGB':
            input_image = input_image.convert('RGB')
        input_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Remove background
        gc.collect()
        output_bytes = rembg_remove(img_byte_arr)
        output_base64 = base64.b64encode(output_bytes).decode('utf-8')
        
        # Cleanup
        del img_byte_arr, output_bytes, input_image
        gc.collect()
        
        response = jsonify({
            "success": True,
            "image": f"data:image/png;base64,{output_base64}",
            "message": "Background removed successfully"
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
        
    except Exception as e:
        response = jsonify({"error": f"Processing failed: {str(e)}"})
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
