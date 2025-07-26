# Flexbone Coding Challenge

---

## Deliverables Summary

### 1. Public Cloud Run URL
**Live Application:** https://flask-ocr-999651465930.us-central1.run.app

The application is fully functional and ready for testing. Users can:
- Upload images (PNG, JPG, JPEG, GIF, BMP, WebP)
- Extract text using OCR technology
- View results on same page

### 2. Implementation Writeup + OCR Approach

#### **OCR Implementation Approach**

The application uses **Tesseract OCR** with optimized configuration for maximum accuracy:

**Key Optimizations:**
- **Engine Mode (`--oem 3`)**: Uses the best available OCR engine for the platform
- **Page Segmentation (`--psm 6`)**: Treats images as uniform text blocks for better accuracy
- **Image Processing**: Automatic format detection and conversion via PIL/Pillow (removes noise and background artifacts so text standds out better)
- **Language Setting**: Specifically tuned to work for English (also noted on Front-End for users to know)
- **Error Handling**: Comprehensive validation and graceful error recovery

---
---

## Conclusion

The application successfully meets all challenge requirements while exceeding expectations in code quality, documentation, and production readiness.