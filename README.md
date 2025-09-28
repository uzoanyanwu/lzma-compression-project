# LZMA File Compression Web Application

A Django-based web application that allows users to upload files and folders, compress them using the LZMA algorithm, and download the compressed results.

## Features

- **User Authentication**: Secure user registration, login, and password reset functionality
- **File Upload**: Support for single and multiple file uploads with drag-and-drop interface
- **Size Limit**: Maximum total upload size of 500MB per compression session
- **LZMA Compression**: High-efficiency compression using Python's LZMA library (preset 6)
- **Progress Tracking**: Real-time progress indication during compression
- **Compression Metrics**: Detailed statistics including compression ratio, time, and space saved
- **Download Links**: Direct download of compressed files with copy-to-clipboard functionality
- **Responsive UI**: Modern, mobile-friendly interface built with Tailwind CSS

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd lzma-compression-project
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

7. **Access the application**:
   - Open your browser and go to `http://127.0.0.1:8000/`
   - Register a new account or login with existing credentials

## Usage

### Upload and Compress Files

1. **Login** to your account
2. **Navigate** to the dashboard
3. **Upload files** by either:
   - Dragging and dropping files onto the drop zone
   - Clicking "Browse Files" to select files
4. **Review** selected files and total size (must be under 500MB)
5. **Click "Start Compression"** to begin the process
6. **Monitor progress** with the progress bar and status messages
7. **View results** on the results page with detailed metrics

### Compression Results

The results page displays:
- Original and compressed file sizes
- Compression ratio percentage
- Time taken for compression
- Space saved
- Download link for the compressed file

### Download Compressed Files

- Click "Download Compressed File" to download the LZMA-compressed file
- Use "Copy Download Link" to share the download URL
- Compressed files are saved with `.lzma` extension

## File Structure

```
lzma-compression-project/
├── compression/              # Main compression app
│   ├── models.py            # File and CompressionResult models
│   ├── views.py             # Upload and compression logic
│   ├── urls.py              # URL patterns
│   ├── templates/           # HTML templates
│   ├── templatetags/        # Custom template filters
│   └── tests.py            # Comprehensive test suite
├── users/                   # User authentication app
├── compressor/             # Django project settings
├── media/                  # Uploaded and compressed files
│   ├── uploads/            # Original uploaded files
│   └── compressed/         # LZMA compressed files
└── requirements.txt        # Python dependencies
```

## Models

### File Model
- `user`: Foreign key to User
- `original_filename`: Name of uploaded file
- `original_file_size`: Size in bytes
- `upload_timestamp`: When file was uploaded
- `file_path`: Path to stored file

### CompressionResult Model
- `file`: One-to-one relationship with File
- `compressed_filename`: Name of compressed file
- `compressed_file_size`: Size after compression
- `compression_ratio`: Compression percentage
- `compression_time`: Time taken in seconds
- `download_link`: URL for downloading
- `timestamp`: When compression completed

## API Endpoints

- `GET /dashboard/` - Main upload interface
- `POST /dashboard/` - Handle file uploads and compression
- `GET /results/<result_id>/` - Display compression results
- `GET /download/<file_id>/` - Download compressed file
- `GET /progress/<file_id>/` - Check compression progress

## Compression Algorithm

The application uses Python's `lzma` library with the following settings:
- **Algorithm**: LZMA2
- **Preset**: 6 (good compression ratio with reasonable speed)
- **Format**: Single files are compressed directly; multiple files are first archived as ZIP then compressed

## Testing

Run the comprehensive test suite:
```bash
python manage.py test compression
```

The test suite covers:
- Model creation and validation
- View functionality and authentication
- File upload and compression logic
- Complete workflow integration
- Edge cases and error handling

## Security Features

- User authentication required for all operations
- File size limits to prevent abuse
- User isolation (users can only access their own files)
- Secure file storage with user-specific directories
- CSRF protection on all forms

## Performance Considerations

- Files are processed synchronously (consider Celery for production)
- LZMA compression is CPU-intensive but provides excellent ratios
- Temporary files are cleaned up after processing
- Database indexes on foreign keys for efficient queries

## Production Deployment

For production deployment:
1. Set `DEBUG = False` in settings
2. Configure proper database (PostgreSQL recommended)
3. Set up static file serving
4. Use a task queue (Celery) for compression processing
5. Configure proper email backend for password resets
6. Set up proper logging and monitoring

## Browser Compatibility

- Modern browsers with HTML5 file API support
- JavaScript required for drag-and-drop and progress indication
- Responsive design works on mobile devices

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is developed for academic research purposes in web-based data compression applications.
