from flask import Flask, request, send_file
from rembg import remove
from PIL import Image
import io
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/remove', methods=['POST'])
def remove_bg():
    try:
        if 'image' not in request.files:
            return "No image uploaded", 400

        input_file = request.files['image']
        input_bytes = input_file.read()
        
        # Process the image with RemBG
        output_bytes = remove(input_bytes)

        # Return the processed image
        return send_file(
            io.BytesIO(output_bytes),
            mimetype='image/png',
            as_attachment=True,
            download_name='output.png'
        )
    except Exception as e:
        return f"Error processing image: {str(e)}", 500

@app.route('/health', methods=['GET'])
def health_check():
    return "API is running", 200

if __name__ == '__main__':
    # Get port from environment variable for Render deployment
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
