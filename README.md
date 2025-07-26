# Flask OCR Web Application

A lightweight, production-ready web application that extracts text from uploaded images using Tesseract OCR. Built with Flask and deployed on Google Cloud Run for the Flexbone Coding Challenge.

**Public URL:** https://flask-ocr-999651465930.us-central1.run.app

## Quick Start

### Prerequisites

- Python 3.9+
- Docker
- Google Cloud SDK (for deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd flask-ocr
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR**
   ```bash
   # macOS
   brew install tesseract
   
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   
   # Windows
   # Download from: https://github.com/UB-Mannheim/tesseract/wiki
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:8080`

### Docker Development

1. **Build the image**
   ```bash
   docker build -t flask-ocr .
   ```

2. **Run the container**
   ```bash
   docker run -p 8080:8080 flask-ocr
   ```

## Deployment to Google Cloud Run

### Prerequisites

1. **Install Google Cloud SDK**
   ```bash
   # Follow instructions at: https://cloud.google.com/sdk/docs/install
   ```

2. **Authenticate and set project**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

### Deployment Steps

1. **Create Artifact Registry repository**
   ```bash
   gcloud artifacts repositories create flask-ocr-repo \
       --repository-format=docker \
       --location=us-central1 \
       --description="Docker repository for flask-ocr"
   ```

2. **Build and push Docker image**
   ```bash
   # Build for amd64 architecture (required for Cloud Run)
   docker buildx build --platform linux/amd64 \
       -t us-central1-docker.pkg.dev/YOUR_PROJECT_ID/flask-ocr-repo/flask-ocr:latest \
       --push .
   ```

3. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy flask-ocr \
       --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/flask-ocr-repo/flask-ocr:latest \
       --platform managed \
       --region us-central1 \
       --allow-unauthenticated
   ```

## Technical Implementation

### Key Components

#### 1. **Flask Application (`app.py`)**
- Logging for debugging and monitoring
- Security best practices (file size limits, type validation)

#### 2. **Docker Configuration (`Dockerfile`)**
- Multi-stage build optimization
- Security hardening (non-root user)
- Production-ready Gunicorn configuration

#### 3. **Frontend (HTML/CSS/JavaScript)**
- Responsive design with Tailwind CSS
- Accessibility considerations
- Error messages !
- **Image preprocessing**: Grayscale, denoise, and binarize images before OCR for improved accuracy.
- **English language only**: OCR is configured to extract English text (lang='eng').

### File Structure

```
flask-ocr/
├── app.py                 # Main Flask application
├── Dockerfile            # Docker configuration
├── requirements.txt      # Python dependencies
├── README.md            # Project documentation
└── venv/                # Virtual environment (not in repo)
```

## API Documentation

### Endpoints

#### `GET /`
- **Description**: Display the OCR upload form
- **Response**: HTML page with upload interface

#### `POST /`
- **Description**: Process uploaded image and extract text
- **Request**: Multipart form data with image file
- **Response**: HTML page with extracted text or error message

### Request Format
```
Content-Type: multipart/form-data
Body: image=<file>
```

### Response Format
- **Success**: HTML with extracted text displayed
- **Error**: HTML with error message displayed