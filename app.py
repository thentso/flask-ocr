"""
Flask OCR Web Application

A lightweight web application that accepts an image and extracts text using Tesseract OCR.
Deployed on Google Cloud Run
"""


from flask import Flask, request, render_template_string
from PIL import Image, ImageOps, ImageFilter
from werkzeug.utils import secure_filename
import pytesseract
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit

def allowed_file(filename):
    """
    Double check if the uploaded file is the proper image file type
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(img):
    """
    Preprocess the image for better OCR accuracy:
    - Convert to grayscale
    - Apply median filter to reduce noise
    - Binarize (threshold)
    """
    img = ImageOps.grayscale(img)
    img = img.filter(ImageFilter.MedianFilter())
    img = img.point(lambda x: 0 if x < 140 else 255, '1')
    return img

def extract_text_from_image(image_file):
    """
    Extract text from an uploaded image using Tesseract OCR.
        
    Should return the extracted text from the image
        
    Raises exception if OCR processing doesn't work
    """
    try:
        # Open and preprocess the image
        img = Image.open(image_file.stream)
        img = preprocess_image(img)
        
        # Configure Tesseract for better accuracy
        custom_config = r'--oem 3 --psm 6'
        
        # Extract text from image (English only)
        extracted_text = pytesseract.image_to_string(img, lang='eng', config=custom_config)
        
        logger.info(f"Successfully extracted text from image: {len(extracted_text)} characters")
        return extracted_text.strip()
        
    except Exception as e:
        logger.error(f"OCR processing failed: {str(e)}")
        raise

def get_html_template():
    """
    Return the HTML template for the OCR upload page. (returns template string)
    """
    return '''
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OCR Text Extraction Tool</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <meta name="description" content="Upload images to extract text using OCR technology">
</head>
<body class="bg-gray-100 min-h-screen flex flex-col items-center justify-center p-4">
    <div class="w-full max-w-md">
        <div class="bg-white p-8 rounded-lg shadow-lg">
            <!-- Header -->
            <div class="text-center mb-6">
                <h1 class="text-2xl font-bold text-gray-800 mb-2">OCR Text Extraction</h1>
                <p class="text-gray-600 text-sm">Upload an image to extract text using AI-powered OCR</p>
                <p class="text-xs text-blue-600 mt-1">Note: This tool currently works best for English text.</p>
            </div>
            
            <!-- Error Messages -->
            {% if error %}
                <div class="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                    <strong>Error:</strong> {{ error }}
                </div>
            {% endif %}
            
            <!-- Upload Form -->
            <form method="POST" enctype="multipart/form-data" class="flex flex-col gap-4" id="uploadForm">
                <div class="flex flex-col gap-2">
                    <label for="imageInput" class="text-sm font-medium text-gray-700">
                        Select Image File
                    </label>
                    <input 
                        type="file" 
                        name="image" 
                        id="imageInput" 
                        accept="image/*" 
                        required
                        class="block w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 transition-colors" 
                    />
                    <span id="fileInfo" class="hidden flex items-center gap-2 mt-1">
                        <span id="fileName" class="text-gray-600 text-sm"></span>
                        <button type="button" id="removeBtn" class="text-red-600 font-bold text-lg hover:text-red-800" title="Remove file">&times;</button>
                    </span>
                    <p class="text-xs text-gray-500">
                        Supported formats: PNG, JPG, JPEG, GIF, BMP, WebP (max 10MB)
                    </p>
                </div>
                <button 
                    type="submit" 
                    class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                    Extract Text
                </button>
            </form>
            
            <!-- Extracted Text Display -->
            {% if extracted_text %}
                <div class="mt-8">
                    <h2 class="text-lg font-semibold text-gray-700 mb-2">Extracted Text:</h2>
                    <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
                        <pre class="text-gray-800 whitespace-pre-wrap text-sm font-mono">{{ extracted_text }}</pre>
                    </div>
                    <div class="mt-2 text-xs text-gray-500">
                        Characters extracted: {{ extracted_text|length }}
                    </div>
                </div>
            {% endif %}
        </div>
        
        <!-- Footer -->
        <div class="text-center mt-4 text-xs text-gray-500">
            <p>Powered by Tesseract OCR • Built with Flask • Deployed on Google Cloud Run</p>
        </div>
    </div>

    <!-- JavaScript for enhanced UX -->
    <script>
        const imageInput = document.getElementById('imageInput');
        const fileInfo = document.getElementById('fileInfo');
        const fileName = document.getElementById('fileName');
        const removeBtn = document.getElementById('removeBtn');

        // Show selected file name
        imageInput.addEventListener('change', function() {
            if (imageInput.files.length > 0) {
                const file = imageInput.files[0];
                fileName.textContent = file.name;
                fileInfo.classList.remove('hidden');
                
                // Check file size (10MB limit)
                if (file.size > 10 * 1024 * 1024) {
                    alert('File size must be less than 10MB');
                    imageInput.value = '';
                    fileInfo.classList.add('hidden');
                }
            } else {
                fileName.textContent = '';
                fileInfo.classList.add('hidden');
            }
        });

        // Remove selected file
        removeBtn.addEventListener('click', function() {
            imageInput.value = '';
            fileName.textContent = '';
            fileInfo.classList.add('hidden');
        });
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Main route handler for the OCR application.
    
    GET: Display the upload form
    POST: Process uploaded image and extract text
    
    Returns string rendered HTML template with form and/or results
    """
    extracted_text = None
    error = None
    
    if request.method == 'POST':
        # Get uploaded file
        file = request.files.get('image')
        
        # Validate file
        if not file or file.filename == '':
            error = "Please select a file to upload."
        elif not allowed_file(file.filename):
            error = f"Invalid file type. Please upload: {', '.join(ALLOWED_EXTENSIONS)}"
        else:
            try:
                # Check file size
                file.seek(0, 2)  # Seek to end
                file_size = file.tell()
                file.seek(0)  # Reset to beginning
                
                if file_size > MAX_FILE_SIZE:
                    error = "File size exceeds 10MB limit."
                else:
                    # Extract text from image
                    extracted_text = extract_text_from_image(file)
                    
                    if not extracted_text:
                        error = "No text could be extracted from the image. Please try a different image."
                        
            except Exception as e:
                logger.error(f"Error processing upload: {str(e)}")
                error = "Failed to process the image. Please ensure it's a valid image file."
    
    return render_template_string(get_html_template(), 
                                extracted_text=extracted_text, 
                                error=error)

@app.errorhandler(413)
def too_large(e):
    """Handle file size too large errors."""
    return render_template_string(get_html_template(), 
                                error="File size exceeds the maximum allowed limit."), 413

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {str(e)}")
    return render_template_string(get_html_template(), 
                                error="An internal server error occurred. Please try again."), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)