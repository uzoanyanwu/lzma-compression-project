# LZMA File Compression Web Application

A Django-based web application for compressing large-scale datasets using the LZMA algorithm. Designed for web-based research platforms and academic institutions to optimize storage of research data.

## Project Overview

**Topic**: LZMA for Compressing Large-Scale Datasets in Web-Based Research Platforms

**Objective**: Optimise storage of research data for academic institutions by providing a web-based compression solution with detailed metrics and analysis.

**Evaluation**: Measures compression ratios, processing times, file sizes, and space saved.

## Features

- **User Authentication**:
  - Email-based registration and login system
  - Secure password hashing
  - Password reset functionality with in-memory email backend for development
  - User-specific file isolation

- **File Upload & Management**:
  - Single and multiple file upload support
  - Maximum upload size: 100MB total per compression session
  - User-specific storage directories
  - Automatic file cleanup after download for security

- **LZMA Compression**:
  - High-efficiency compression using Python's built-in LZMA library
  - LZMA2 algorithm with preset 6 (balanced compression ratio and speed)
  - Single files compressed directly to `.xz` format
  - Multiple files automatically archived as ZIP then compressed

- **Compression Analysis**:
  - Compression ratio (percentage)
  - Original vs compressed file size comparison
  - Processing time measurement
  - Space saved calculation
  - Formatted time display (seconds, minutes, hours)

- **Results Management**:
  - View individual compression results
  - Paginated results history (10 items per page)
  - One-time download with automatic file deletion
  - Download tracking (prevents re-download of deleted files)

- **Security Features**:
  - User authentication required for all operations
  - CSRF protection on all forms
  - User-isolated file storage
  - Automatic file deletion after download
  - Secure password validation

## Technology Stack

### Backend
- **Framework**: Django 5.2.6
- **Language**: Python 3.x
- **Database**: SQLite3 (development) - easily configured for MySQL/PostgreSQL in production
- **Compression**: Python's built-in `lzma` module

### Frontend
- **Templates**: Django Template Language
- **Styling**: Tailwind CSS (via CDN)
- **JavaScript**: Vanilla JS for file upload handling and UI interactions

### Key Libraries
- `asgiref==3.9.2` - ASGI support
- `Django==5.2.6` - Web framework
- `sqlparse==0.5.3` - SQL parsing utilities

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step-by-Step Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd lzma-compression-project
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv

   # On macOS/Linux:
   source venv/bin/activate

   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser** (optional, for admin access):
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

7. **Access the application**:
   - Open your browser and navigate to `http://127.0.0.1:8000/`
   - Register a new account or login with existing credentials
   - Access admin panel at `http://127.0.0.1:8000/admin/` (if superuser created)

## Usage Guide

### User Workflow

1. **Registration/Login**:
   - Navigate to the landing page at `http://127.0.0.1:8000/`
   - Create a new account with email and password
   - Or login with existing credentials
   - Password reset available via email (in-memory backend in development)

2. **Upload Files for Compression**:
   - After login, you'll be redirected to the dashboard
   - Upload files by:
     - Clicking "Browse Files" to select from your computer
     - Dragging and dropping files onto the upload area (if supported)
   - Multiple files can be selected at once
   - Total upload size must not exceed 100MB

3. **Compression Process**:
   - Click "Start Compression" or equivalent button
   - The system will:
     - For single files: Compress directly using LZMA
     - For multiple files: Create a ZIP archive first, then compress with LZMA
   - Compression happens synchronously (you'll see progress indication)

4. **View Compression Results**:
   - After compression completes, you'll be redirected to the results page
   - View detailed metrics:
     - Original file size
     - Compressed file size
     - Compression ratio (percentage)
     - Time taken for compression
     - Space saved
   - Access the download link for your compressed file

5. **Download Compressed Files**:
   - Click "Download Compressed File" button
   - File downloads with `.xz` extension
   - **Important**: Files are automatically deleted from the server after download for security
   - Each file can only be downloaded once
   - Attempting to re-download will show a message indicating the file was already downloaded

6. **View All Results**:
   - Access your compression history at `/results/`
   - View all past compression operations
   - Paginated display (10 results per page)
   - Each result shows compression metrics

7. **Logout**:
   - Click logout to end your session
   - Returns to the landing page


## Configuration Settings
### Email Backend (Development)
```python
EMAIL_BACKEND = 'users.email_backend.InMemoryEmailBackend'
```
- Custom backend stores emails in memory
- Accessible at `/view-reset-email/` for testing
- **Production**: Configure SMTP backend for real email delivery

### Database
- **Development**: SQLite3 (`db.sqlite3`)
- **Production**: Easily configurable for PostgreSQL or MySQL

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
python manage.py test
```
