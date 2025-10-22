from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, Http404
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import os
import lzma
import time
import json
import tempfile
import zipfile
from pathlib import Path
from .models import File, CompressionResult


@login_required
def dashboard(request):
    if request.method == 'POST':
        return handle_file_upload(request)
    return render(request, "compression/dashboard.html")


@login_required
def handle_file_upload(request):
    """Handle file upload and initiate compression"""
    if 'files' not in request.FILES:
        return JsonResponse({'error': 'No files uploaded'}, status=400)

    files = request.FILES.getlist('files')
    total_size = sum(file.size for file in files)

    # Check total file size limit (100MB)
    max_size = 100 * 1024 * 1024  # 100MB in bytes
    if total_size > max_size:
        return JsonResponse({
            'error': f'Total file size ({total_size / (1024*1024):.2f} MB) exceeds maximum limit of 100MB'
        }, status=400)

    try:
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', str(request.user.id))
        os.makedirs(upload_dir, exist_ok=True)

        # Save uploaded files and create File records
        uploaded_files = []
        for uploaded_file in files:
            # Create unique filename to avoid conflicts
            timestamp = str(int(time.time()))
            filename = f"{timestamp}_{uploaded_file.name}"
            file_path = os.path.join(upload_dir, filename)

            # Save file to disk
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            # Create File record
            file_record = File.objects.create(
                user=request.user,
                original_filename=uploaded_file.name,
                original_file_size=uploaded_file.size,
                file_path=file_path
            )
            uploaded_files.append(file_record)

        # Start compression process
        if len(uploaded_files) == 1:
            # Single file compression
            file_record = uploaded_files[0]
            compression_result = compress_single_file(file_record)
        else:
            # Multiple files - create zip first, then compress
            compression_result = compress_multiple_files(uploaded_files)

        return JsonResponse({
            'success': True,
            'redirect_url': reverse('compression_results', kwargs={'result_id': compression_result.id})
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def compress_single_file(file_record):
    """Compress a single file using LZMA"""
    start_time = time.time()

    # Read the original file
    with open(file_record.file_path, 'rb') as input_file:
        data = input_file.read()

    # Compress using LZMA
    compressed_data = lzma.compress(data, preset=6)  # Preset 6 is default for good compression

    # Create compressed filename that preserves original extension information
    # Format: originalname.original_ext.xz (so when decompressed, it becomes originalname.original_ext)
    original_name, original_ext = os.path.splitext(file_record.original_filename)
    if original_ext:
        # If there's an extension, include it in the compressed filename
        compressed_filename = f"{original_name}{original_ext}.xz"
    else:
        # If no extension, just add .xz
        compressed_filename = f"{file_record.original_filename}.xz"

    # Save compressed file
    compressed_dir = os.path.join(settings.MEDIA_ROOT, 'compressed', str(file_record.user.id))
    os.makedirs(compressed_dir, exist_ok=True)

    compressed_path = os.path.join(compressed_dir, compressed_filename)
    with open(compressed_path, 'wb') as output_file:
        output_file.write(compressed_data)

    end_time = time.time()
    compression_time = end_time - start_time

    # Create CompressionResult record
    download_url = f"/compression/download/{file_record.id}/"

    compression_result = CompressionResult.objects.create(
        file=file_record,
        compressed_filename=compressed_filename,
        compressed_file_size=len(compressed_data),
        compression_ratio=(1 - (len(compressed_data) / file_record.original_file_size)) * 100,
        compression_time=compression_time,
        download_link=download_url
    )

    return compression_result


def compress_multiple_files(file_records):
    """Compress multiple files by creating a zip first, then compressing with LZMA"""
    start_time = time.time()

    # Create a temporary zip file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_zip:
        with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            total_size = 0
            for file_record in file_records:
                zipf.write(file_record.file_path, file_record.original_filename)
                total_size += file_record.original_file_size

        # Read the zip file and compress with LZMA
        with open(temp_zip.name, 'rb') as zip_file:
            zip_data = zip_file.read()

        compressed_data = lzma.compress(zip_data, preset=6)

        # Clean up temp zip file
        os.unlink(temp_zip.name)

    # Create a combined filename
    if len(file_records) <= 3:
        filenames = [os.path.splitext(f.original_filename)[0] for f in file_records]
        base_name = '_'.join(filenames)
        compressed_filename = f"{base_name}.xz"
    else:
        compressed_filename = f"{len(file_records)}_files_archive.xz"

    # Ensure filename isn't too long
    if len(compressed_filename) > 200:
        compressed_filename = f"{len(file_records)}_files_archive.xz"

    # Save compressed file
    user_id = file_records[0].user.id
    compressed_dir = os.path.join(settings.MEDIA_ROOT, 'compressed', str(user_id))
    os.makedirs(compressed_dir, exist_ok=True)

    compressed_path = os.path.join(compressed_dir, compressed_filename)
    with open(compressed_path, 'wb') as output_file:
        output_file.write(compressed_data)

    end_time = time.time()
    compression_time = end_time - start_time

    # Create a master File record for the combined files
    master_file = File.objects.create(
        user=file_records[0].user,
        original_filename=f"{len(file_records)} files combined",
        original_file_size=total_size,
        file_path=compressed_path  # Store the compressed path as this is our main file
    )

    # Create CompressionResult record
    download_url = f"/compression/download/{master_file.id}/"

    compression_result = CompressionResult.objects.create(
        file=master_file,
        compressed_filename=compressed_filename,
        compressed_file_size=len(compressed_data),
        compression_ratio=(1 - (len(compressed_data) / total_size)) * 100,
        compression_time=compression_time,
        download_link=download_url
    )

    return compression_result


@login_required
def compression_results(request, result_id):
    """Display compression results"""
    try:
        result = CompressionResult.objects.get(id=result_id, file__user=request.user)
        return render(request, 'compression/results.html', {'result': result})
    except CompressionResult.DoesNotExist:
        raise Http404("Compression result not found")


@login_required
def all_results(request):
    """Display all compression results for the user with pagination"""
    # Get all results ordered by most recent first
    all_results = CompressionResult.objects.filter(
        file__user=request.user
    ).select_related('file').order_by('-timestamp')

    # Simple pagination with 10 items per page
    page_number = request.GET.get('page', 1)
    paginator = Paginator(all_results, 10)  # 10 items per page

    try:
        results_page = paginator.page(page_number)
    except PageNotAnInteger:
        results_page = paginator.page(1)
    except EmptyPage:
        results_page = paginator.page(paginator.num_pages)

    context = {
        'results': results_page,
        'total_count': all_results.count(),
    }

    return render(request, 'compression/all_results.html', context)
@login_required
def download_compressed_file(request, file_id):
    """Handle download of compressed files"""
    try:
        file_record = File.objects.get(id=file_id, user=request.user)
        compression_result = CompressionResult.objects.get(file=file_record)

        # Check if file has already been downloaded
        if compression_result.downloaded:
            messages.warning(
                request,
                f'This file was already downloaded on {compression_result.downloaded_at.strftime("%B %d, %Y at %I:%M %p")}. '
                'The files have been deleted from our servers for your security and privacy.'
            )
            return redirect('dashboard')

        compressed_path = os.path.join(
            settings.MEDIA_ROOT,
            'compressed',
            str(request.user.id),
            compression_result.compressed_filename
        )

        if not os.path.exists(compressed_path):
            # Mark as downloaded to prevent future download attempts
            compression_result.downloaded = True
            compression_result.downloaded_at = timezone.now()
            compression_result.save()

            messages.error(
                request,
                "Compressed file not found on server. The file may have been deleted or moved. "
            )
            return redirect('all_results')

        # Read file content before deletion
        with open(compressed_path, 'rb') as f:
            file_content = f.read()

        # Mark as downloaded
        compression_result.downloaded = True
        compression_result.downloaded_at = timezone.now()
        compression_result.save()

        # Delete the compressed file
        try:
            os.remove(compressed_path)
        except OSError as e:
            print(f"Error deleting compressed file: {e}")

        # Delete the original uploaded file(s)
        # Check if this was a multiple file upload (file_path points to compressed file)
        if file_record.file_path != compressed_path:
            # Single file or individual files from multiple upload
            if os.path.exists(file_record.file_path):
                try:
                    os.remove(file_record.file_path)
                except OSError as e:
                    print(f"Error deleting original file: {e}")

        # For multiple file uploads, try to clean up the upload directory
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', str(request.user.id))
        if os.path.exists(upload_dir):
            try:
                # Remove any files that were uploaded at the same time (within 10 seconds)
                upload_time = file_record.upload_timestamp.timestamp()
                for filename in os.listdir(upload_dir):
                    file_path = os.path.join(upload_dir, filename)
                    if os.path.isfile(file_path):
                        # Check if file was created around the same time
                        file_mtime = os.path.getmtime(file_path)
                        if abs(file_mtime - upload_time) < 10:  # Within 10 seconds
                            try:
                                os.remove(file_path)
                            except OSError as e:
                                print(f"Error deleting upload file {filename}: {e}")
            except Exception as e:
                print(f"Error cleaning upload directory: {e}")

        # Return the file for download
        response = HttpResponse(file_content, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{compression_result.compressed_filename}"'
        return response

    except (File.DoesNotExist, CompressionResult.DoesNotExist):
        messages.error(request, "File not found.")
        return redirect('dashboard')


@login_required
def compression_progress(request, file_id):
    """API endpoint to check compression progress"""
    # This is a simple implementation - in production you might want to use Celery
    # or another task queue for background processing
    try:
        file_record = File.objects.get(id=file_id, user=request.user)
        compression_result = CompressionResult.objects.filter(file=file_record).first()

        if compression_result:
            return JsonResponse({
                'status': 'completed',
                'progress': 100,
                'redirect_url': reverse('compression_results', kwargs={'result_id': compression_result.id})
            })
        else:
            return JsonResponse({
                'status': 'processing',
                'progress': 50  # Simple progress indication
            })

    except File.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'File not found'}, status=404)
