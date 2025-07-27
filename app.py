"""
Flask OCR Web Application

A lightweight web application that accepts multiple images and extracts text using Tesseract OCR.
Deployed on Google Cloud Run
"""


from flask import Flask, request, render_template_string, Response, session, redirect, url_for
from PIL import Image, ImageOps, ImageFilter
from werkzeug.utils import secure_filename
import pytesseract
import logging
import json
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
MAX_FILES = 10  # Maximum number of files that can be uploaded at once

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
    <meta name="description" content="Upload multiple images to extract text using OCR technology">
</head>
<body class="bg-gray-100 min-h-screen flex flex-col items-center justify-center p-4">
    <div class="w-full max-w-4xl">
        <div class="bg-white p-8 rounded-lg shadow-lg">
            <!-- Header -->
            <div class="text-center mb-6">
                <h1 class="text-2xl font-bold text-gray-800 mb-2">Multi-File OCR Text Extraction</h1>
                <p class="text-gray-600 text-sm">Upload multiple images to extract text using AI-powered OCR</p>
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
                        Select Image Files (Multiple)
                    </label>
                    <input 
                        type="file" 
                        name="images" 
                        id="imageInput" 
                        accept="image/*" 
                        multiple
                        required
                        class="block w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 transition-colors" 
                    />
                    <p class="text-xs text-gray-500">
                        Supported formats: PNG, JPG, JPEG, GIF, BMP, WebP (max 10MB each, up to 10 files)
                    </p>
                </div>
                
                <!-- Selected Files List -->
                <div id="selectedFiles" class="hidden">
                    <h3 class="text-sm font-medium text-gray-700 mb-2">Selected Files:</h3>
                    <div id="filesList" class="space-y-2"></div>
                </div>
                
                <button 
                    type="submit" 
                    class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                    Extract Text from All Files
                </button>
            </form>
            
            <!-- Results Display -->
            {% if results %}
                <div class="mt-8">
                    <h2 class="text-lg font-semibold text-gray-700 mb-4">Extracted Text Results:</h2>
                    
                    <!-- Navigation Controls -->
                    <div class="flex items-center justify-between mb-4">
                        <button id="prevBtn" class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded disabled:opacity-50 disabled:cursor-not-allowed">
                            ← Previous
                        </button>
                        <span id="fileCounter" class="text-sm text-gray-600">
                            File 1 of {{ results|length }}
                        </span>
                        <button id="nextBtn" class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded disabled:opacity-50 disabled:cursor-not-allowed">
                            Next →
                        </button>
                    </div>
                    
                    <!-- Text Display -->
                    <div id="textDisplay" class="bg-gray-50 border border-gray-200 rounded-lg p-4 min-h-[200px]">
                        <div class="mb-2">
                            <strong class="text-gray-700">File:</strong> 
                            <span id="currentFileName" class="text-gray-600">{{ results[0].filename }}</span>
                        </div>
                        <pre id="currentText" class="text-gray-800 whitespace-pre-wrap text-sm font-mono">{{ results[0].text }}</pre>
                        <div class="mt-2 text-xs text-gray-500">
                            Characters extracted: <span id="charCount">{{ results[0].text|length }}</span>
                        </div>
                    </div>
                    
                    <!-- Download Buttons -->
                    <div class="mt-4 flex gap-2">
                        <form method="POST" action="/download-single" class="inline">
                            <input type="hidden" name="file_index" value="0">
                            <button type="submit" class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
                                Download This Text
                            </button>
                        </form>
                        
                        {% if results|length > 1 %}
                        <form method="POST" action="/download-all" class="inline">
                            <button type="submit" class="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded">
                                Download All Texts
                            </button>
                        </form>
                        {% endif %}
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
        const selectedFiles = document.getElementById('selectedFiles');
        const filesList = document.getElementById('filesList');
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const fileCounter = document.getElementById('fileCounter');
        const currentFileName = document.getElementById('currentFileName');
        const currentText = document.getElementById('currentText');
        const charCount = document.getElementById('charCount');
        
        let currentFileIndex = 0;
        const results = {{ results|tojson if results else '[]' }};
        
        // Show selected files
        imageInput.addEventListener('change', function() {
            if (imageInput.files.length > 0) {
                filesList.innerHTML = '';
                let totalSize = 0;
                let hasLargeFile = false;
                
                Array.from(imageInput.files).forEach((file, index) => {
                    const fileItem = document.createElement('div');
                    fileItem.className = 'flex items-center justify-between p-2 bg-gray-50 rounded border';
                    
                    const fileInfo = document.createElement('div');
                    fileInfo.className = 'flex-1';
                    fileInfo.innerHTML = `
                        <div class="text-sm font-medium text-gray-700">${file.name}</div>
                        <div class="text-xs text-gray-500">${(file.size / 1024 / 1024).toFixed(2)} MB</div>
                    `;
                    
                    const removeBtn = document.createElement('button');
                    removeBtn.type = 'button';
                    removeBtn.className = 'text-red-600 font-bold text-lg hover:text-red-800 ml-2';
                    removeBtn.innerHTML = '×';
                    removeBtn.title = 'Remove file';
                    removeBtn.onclick = function() {
                        // Create a new FileList without this file
                        const dt = new DataTransfer();
                        Array.from(imageInput.files).forEach((f, i) => {
                            if (i !== index) dt.items.add(f);
                        });
                        imageInput.files = dt.files;
                        imageInput.dispatchEvent(new Event('change'));
                    };
                    
                    fileItem.appendChild(fileInfo);
                    fileItem.appendChild(removeBtn);
                    filesList.appendChild(fileItem);
                    
                    totalSize += file.size;
                    if (file.size > 10 * 1024 * 1024) {
                        hasLargeFile = true;
                    }
                });
                
                selectedFiles.classList.remove('hidden');
                
                if (hasLargeFile) {
                    alert('One or more files exceed 10MB limit');
                }
                
                if (imageInput.files.length > 10) {
                    alert('Maximum 10 files allowed');
                }
            } else {
                selectedFiles.classList.add('hidden');
            }
        });
        
        // Navigation functions
        function updateDisplay() {
            if (results.length === 0) return;
            
            const result = results[currentFileIndex];
            currentFileName.textContent = result.filename;
            currentText.textContent = result.text;
            charCount.textContent = result.text.length;
            fileCounter.textContent = `File ${currentFileIndex + 1} of ${results.length}`;
            
            // Update navigation buttons
            prevBtn.disabled = currentFileIndex === 0;
            nextBtn.disabled = currentFileIndex === results.length - 1;
            
            // Update download form
            const downloadForm = document.querySelector('form[action="/download-single"] input[name="file_index"]');
            if (downloadForm) {
                downloadForm.value = currentFileIndex;
            }
        }
        
        if (prevBtn && nextBtn) {
            prevBtn.addEventListener('click', function() {
                if (currentFileIndex > 0) {
                    currentFileIndex--;
                    updateDisplay();
                }
            });
            
            nextBtn.addEventListener('click', function() {
                if (currentFileIndex < results.length - 1) {
                    currentFileIndex++;
                    updateDisplay();
                }
            });
        }
        
        // Initialize display if results exist
        if (results.length > 0) {
            updateDisplay();
        }
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Main route handler for the OCR application.
    
    GET: Display the upload form
    POST: Process uploaded images and extract text
    
    Returns string rendered HTML template with form and/or results
    """
    results = []
    error = None
    
    if request.method == 'POST':
        # Get uploaded files
        files = request.files.getlist('images')
        
        # Validate files
        if not files or all(file.filename == '' for file in files):
            error = "Please select at least one file to upload."
        elif len(files) > MAX_FILES:
            error = f"Maximum {MAX_FILES} files allowed per upload."
        else:
            try:
                results = []
                for file in files:
                    if file.filename == '':
                        continue
                        
                    if not allowed_file(file.filename):
                        error = f"Invalid file type for {file.filename}. Please upload: {', '.join(ALLOWED_EXTENSIONS)}"
                        break
                    
                    # Check file size
                    file.seek(0, 2)  # Seek to end
                    file_size = file.tell()
                    file.seek(0)  # Reset to beginning
                    
                    if file_size > MAX_FILE_SIZE:
                        error = f"File {file.filename} exceeds 10MB limit."
                        break
                    
                    # Extract text from image
                    try:
                        extracted_text = extract_text_from_image(file)
                        if extracted_text:
                            results.append({
                                'filename': file.filename,
                                'text': extracted_text,
                                'size': file_size
                            })
                        else:
                            results.append({
                                'filename': file.filename,
                                'text': "No text could be extracted from this image.",
                                'size': file_size
                            })
                    except Exception as e:
                        logger.error(f"Error processing {file.filename}: {str(e)}")
                        results.append({
                            'filename': file.filename,
                            'text': f"Error processing image: {str(e)}",
                            'size': file_size
                        })
                
                if not error and not results:
                    error = "No text could be extracted from any of the uploaded images."
                    
            except Exception as e:
                logger.error(f"Error processing upload: {str(e)}")
                error = "Failed to process the images. Please ensure they are valid image files."
    
    # Store results in session for download functionality
    if results:
        session['results'] = results
    
    return render_template_string(get_html_template(), 
                                results=results, 
                                error=error)

@app.route('/download-single', methods=['POST'])
def download_single():
    """Download a single extracted text file."""
    file_index = int(request.form.get('file_index', 0))
    results = session.get('results', [])
    
    if not results or file_index >= len(results):
        return "No results found", 404
    
    result = results[file_index]
    filename = f"extracted_text_{result['filename']}.txt"
    
    return Response(
        result['text'],
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

@app.route('/download-all', methods=['POST'])
def download_all():
    """Download all extracted texts as a single file."""
    results = session.get('results', [])
    
    if not results:
        return "No results found", 404
    
    # Create combined text content
    combined_text = ""
    for i, result in enumerate(results, 1):
        combined_text += f"=== File {i}: {result['filename']} ===\n"
        combined_text += f"Characters: {len(result['text'])}\n"
        combined_text += f"Size: {result['size']} bytes\n"
        combined_text += "=" * 50 + "\n\n"
        combined_text += result['text']
        combined_text += "\n\n" + "=" * 50 + "\n\n"
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"all_extracted_texts_{timestamp}.txt"
    
    return Response(
        combined_text,
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

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