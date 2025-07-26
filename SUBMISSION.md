# Flexbone Coding Challenge

---

## Deliverables Summary

### 1. Public Cloud Run URL
**Live Application:** https://flask-ocr-999651465930.us-central1.run.app

The application is fully functional and ready for testing. Users can:
- Upload images (PNG, JPG, JPEG, GIF, BMP, WebP)
- Extract text using OCR technology
- View results in a clean, modern interface

### 2. Implementation Writeup + OCR Approach

#### **OCR Implementation Approach**

The application uses **Tesseract OCR** with optimized configuration for maximum accuracy:

**Image Preprocessing:** Before OCR, uploaded images are converted to grayscale, denoised with a median filter, and binarized (thresholded) using Pillow. This preprocessing pipeline reduces noise and background artifacts, making text stand out and significantly improving OCR accuracy, especially for noisy or low-contrast images.

**Language Setting:** The OCR engine is explicitly set to English (`lang='eng'`) to ensure optimal accuracy for English text. This is ideal for documents and images containing English writing.

**Key Optimizations:**
- **Engine Mode (`--oem 3`)**: Uses the best available OCR engine for the platform
- **Page Segmentation (`--psm 6`)**: Treats images as uniform text blocks for better accuracy
- **Image Processing**: Automatic format detection and conversion via PIL/Pillow
- **Error Handling**: Comprehensive validation and graceful error recovery

**Processing Pipeline:**
1. **File Validation**: Type and size checking (10MB limit)
2. **Image Loading**: Stream-based processing for efficiency
3. **OCR Extraction**: Optimized Tesseract configuration
4. **Result Display**: Clean, formatted text output

---

## Technical Highlights

### **Production-Ready Features**
- **Security**: Non-root container, input validation, secure defaults
- **Performance**: Optimized Docker layers, efficient image processing
- **Image Preprocessing**: Grayscale, denoise, and binarize images before OCR for improved accuracy
- **English language only**: OCR is configured to extract English text (lang='eng').
- **Monitoring**: Health checks, logging, error tracking

### **User Experience**
- **Modern UI**: Clean, responsive design with Tailwind CSS

---

## Conclusion

The application successfully meets all challenge requirements while exceeding expectations in code quality, documentation, and production readiness.