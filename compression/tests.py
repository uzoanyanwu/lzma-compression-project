from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import os
import tempfile
import shutil
import lzma
from .models import File, CompressionResult


class CompressionModelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_file_model_creation(self):
        """Test File model creation"""
        file_obj = File.objects.create(
            user=self.user,
            original_filename='test.txt',
            original_file_size=1024,
            file_path='/path/to/test.txt'
        )

        self.assertEqual(file_obj.user, self.user)
        self.assertEqual(file_obj.original_filename, 'test.txt')
        self.assertEqual(file_obj.original_file_size, 1024)
        self.assertEqual(str(file_obj), 'test.txt - testuser')

    def test_compression_result_model_creation(self):
        """Test CompressionResult model creation"""
        file_obj = File.objects.create(
            user=self.user,
            original_filename='test.txt',
            original_file_size=1024,
            file_path='/path/to/test.txt'
        )

        compression_result = CompressionResult.objects.create(
            file=file_obj,
            compressed_filename='test.xz',
            compressed_file_size=512,
            compression_ratio=50.0,
            compression_time=2.5,
            download_link='/download/1/'
        )

        self.assertEqual(compression_result.file, file_obj)
        self.assertEqual(compression_result.compressed_filename, 'test.xz')
        self.assertEqual(compression_result.compression_percentage, 50.0)
        self.assertEqual(compression_result.formatted_compression_time, '2.50 seconds')

    def test_compression_result_properties(self):
        """Test CompressionResult property methods"""
        file_obj = File.objects.create(
            user=self.user,
            original_filename='test.txt',
            original_file_size=1000,
            file_path='/path/to/test.txt'
        )

        # Test compression percentage calculation
        compression_result = CompressionResult.objects.create(
            file=file_obj,
            compressed_filename='test.xz',
            compressed_file_size=250,  # 75% compression
            compression_ratio=75.0,
            compression_time=65.5,  # Test minute formatting
            download_link='/download/1/'
        )

        self.assertEqual(compression_result.compression_percentage, 75.0)
        self.assertEqual(compression_result.formatted_compression_time, '1 minute 5 seconds')


class CompressionViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Create temporary media directory for tests
        self.test_media_dir = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self.test_media_dir

    def tearDown(self):
        # Clean up temporary media directory
        if os.path.exists(self.test_media_dir):
            shutil.rmtree(self.test_media_dir)

    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_dashboard_get_request(self):
        """Test dashboard GET request for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Compress Files')

    def test_file_upload_no_files(self):
        """Test file upload with no files"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('dashboard'))
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'No files uploaded')

    def test_file_upload_size_limit(self):
        """Test file upload size limit"""
        self.client.login(username='testuser', password='testpass123')

        # Create a file larger than 100MB (simulate with size)
        large_content = b'x' * (501 * 1024 * 1024)  # 501MB
        large_file = SimpleUploadedFile(
            "large_test.txt",
            large_content,
            content_type="text/plain"
        )

        response = self.client.post(reverse('dashboard'), {'files': large_file})
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('exceeds maximum limit', data['error'])

    def test_successful_single_file_upload_and_compression(self):
        """Test successful single file upload and compression"""
        self.client.login(username='testuser', password='testpass123')

        # Create a test file
        test_content = b'This is test content for compression testing. ' * 100  # Make it larger
        test_file = SimpleUploadedFile(
            "test.txt",
            test_content,
            content_type="text/plain"
        )

        response = self.client.post(reverse('dashboard'), {'files': test_file})
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('redirect_url', data)

        # Check that File and CompressionResult objects were created
        self.assertEqual(File.objects.count(), 1)
        self.assertEqual(CompressionResult.objects.count(), 1)

        file_obj = File.objects.first()
        self.assertEqual(file_obj.user, self.user)
        self.assertEqual(file_obj.original_filename, 'test.txt')

        compression_result = CompressionResult.objects.first()
        self.assertEqual(compression_result.file, file_obj)
        self.assertTrue(compression_result.compressed_filename.endswith('.xz'))

    def test_successful_multiple_file_upload_and_compression(self):
        """Test successful multiple file upload and compression"""
        self.client.login(username='testuser', password='testpass123')

        # Create multiple test files
        test_files = []
        for i in range(3):
            content = f'This is test content for file {i}. ' * 50
            test_file = SimpleUploadedFile(
                f"test{i}.txt",
                content.encode(),
                content_type="text/plain"
            )
            test_files.append(test_file)

        response = self.client.post(reverse('dashboard'), {'files': test_files})
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('redirect_url', data)

        # Should have created one master File object and one CompressionResult
        self.assertEqual(CompressionResult.objects.count(), 1)

    def test_compression_results_view(self):
        """Test compression results view"""
        self.client.login(username='testuser', password='testpass123')

        # Create test data
        file_obj = File.objects.create(
            user=self.user,
            original_filename='test.txt',
            original_file_size=1024,
            file_path='/path/to/test.txt'
        )

        compression_result = CompressionResult.objects.create(
            file=file_obj,
            compressed_filename='test.xz',
            compressed_file_size=512,
            compression_ratio=50.0,
            compression_time=2.5,
            download_link='/download/1/'
        )

        response = self.client.get(
            reverse('compression_results', kwargs={'result_id': compression_result.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Compression Results')
        self.assertContains(response, 'test.txt')
        self.assertContains(response, '50.0% reduction')

    def test_compression_results_unauthorized_access(self):
        """Test that users can only access their own compression results"""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )

        # Create compression result for other user
        file_obj = File.objects.create(
            user=other_user,
            original_filename='test.txt',
            original_file_size=1024,
            file_path='/path/to/test.txt'
        )

        compression_result = CompressionResult.objects.create(
            file=file_obj,
            compressed_filename='test.xz',
            compressed_file_size=512,
            compression_ratio=50.0,
            compression_time=2.5,
            download_link='/download/1/'
        )

        # Try to access as different user
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('compression_results', kwargs={'result_id': compression_result.id})
        )
        self.assertEqual(response.status_code, 404)


class CompressionFunctionalityTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self.test_dir

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_lzma_compression_functionality(self):
        """Test that LZMA compression actually works"""
        # Create test data
        test_data = b'This is repetitive test data. ' * 1000  # Highly compressible

        # Test direct LZMA compression
        compressed_data = lzma.compress(test_data, preset=6)
        decompressed_data = lzma.decompress(compressed_data)

        # Verify compression worked
        self.assertEqual(test_data, decompressed_data)
        self.assertLess(len(compressed_data), len(test_data))  # Should be smaller

        # Calculate compression ratio
        compression_ratio = (1 - (len(compressed_data) / len(test_data))) * 100
        self.assertGreater(compression_ratio, 0)  # Should achieve some compression

    def test_compression_metrics_accuracy(self):
        """Test that compression metrics are calculated correctly"""
        original_size = 1000
        compressed_size = 250

        file_obj = File.objects.create(
            user=self.user,
            original_filename='test.txt',
            original_file_size=original_size,
            file_path='/path/to/test.txt'
        )

        compression_result = CompressionResult.objects.create(
            file=file_obj,
            compressed_filename='test.xz',
            compressed_file_size=compressed_size,
            compression_ratio=75.0,
            compression_time=1.5,
            download_link='/download/1/'
        )

        # Test compression percentage calculation
        expected_percentage = (1 - (compressed_size / original_size)) * 100
        self.assertEqual(compression_result.compression_percentage, expected_percentage)

        # Test time formatting
        self.assertEqual(compression_result.formatted_compression_time, '1.50 seconds')


class CompressionIntegrationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Create temporary media directory
        self.test_media_dir = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self.test_media_dir

    def tearDown(self):
        if os.path.exists(self.test_media_dir):
            shutil.rmtree(self.test_media_dir)

    def test_complete_compression_workflow(self):
        """Test the complete workflow from upload to download"""
        self.client.login(username='testuser', password='testpass123')

        # Step 1: Upload file
        test_content = b'This is test content for full workflow testing. ' * 100
        test_file = SimpleUploadedFile(
            "workflow_test.txt",
            test_content,
            content_type="text/plain"
        )

        upload_response = self.client.post(reverse('dashboard'), {'files': test_file})
        self.assertEqual(upload_response.status_code, 200)

        upload_data = upload_response.json()
        self.assertTrue(upload_data['success'])

        # Step 2: Check results page
        compression_result = CompressionResult.objects.first()
        results_response = self.client.get(
            reverse('compression_results', kwargs={'result_id': compression_result.id})
        )
        self.assertEqual(results_response.status_code, 200)

        # Step 3: Download compressed file
        file_obj = compression_result.file
        download_response = self.client.get(
            reverse('download_compressed_file', kwargs={'file_id': file_obj.id})
        )
        self.assertEqual(download_response.status_code, 200)
        self.assertEqual(download_response['Content-Type'], 'application/octet-stream')

        # Verify the downloaded content can be decompressed
        downloaded_content = download_response.content
        decompressed_content = lzma.decompress(downloaded_content)
        self.assertEqual(decompressed_content, test_content)
