// File upload and compression handler for dashboard
(function() {
  'use strict';

  let selectedFiles = [];
  const maxSize = 50 * 1024 * 1024; // 50MB

  // Get DOM elements
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');
  const browseButton = document.getElementById('browseButton');
  const fileList = document.getElementById('fileList');
  const fileItems = document.getElementById('fileItems');
  const uploadButton = document.getElementById('uploadButton');
  const clearButton = document.getElementById('clearButton');
  const progressSection = document.getElementById('progressSection');
  const progressBar = document.getElementById('progressBar');
  const progressText = document.getElementById('progressText');
  const errorMessages = document.getElementById('errorMessages');
  const errorText = document.getElementById('errorText');

  // Initialize when DOM is loaded
  document.addEventListener('DOMContentLoaded', function() {
    initializeDragAndDrop();
    initializeButtonHandlers();
  });

  function initializeDragAndDrop() {
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      dropZone.addEventListener(eventName, preventDefaults, false);
      document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop area when dragging over
    ['dragenter', 'dragover'].forEach(eventName => {
      dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropZone.addEventListener(eventName, unhighlight, false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);
  }

  function initializeButtonHandlers() {
    // Handle browse button click
    browseButton.addEventListener('click', () => {
      fileInput.click();
    });

    // Handle file input change
    fileInput.addEventListener('change', (e) => {
      handleFiles(e.target.files);
    });

    // Clear button handler
    clearButton.addEventListener('click', () => {
      selectedFiles = [];
      fileInput.value = '';
      updateFileList();
      hideError();
    });

    // Upload button handler
    uploadButton.addEventListener('click', () => {
      if (selectedFiles.length === 0) {
        showError('Please select files to compress');
        return;
      }
      uploadFiles();
    });
  }

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  function highlight(e) {
    dropZone.classList.add('border-[#3d98f4]', 'bg-[#f8fafc]');
  }

  function unhighlight(e) {
    dropZone.classList.remove('border-[#3d98f4]', 'bg-[#f8fafc]');
  }

  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
  }

  function handleFiles(files) {
    hideError();
    const newFiles = Array.from(files);

    // Check total size
    const totalSize = [...selectedFiles, ...newFiles].reduce((sum, file) => sum + file.size, 0);
    if (totalSize > maxSize) {
      showError(`Total file size (${(totalSize / (1024*1024)).toFixed(2)} MB) exceeds maximum limit of 50MB`);
      return;
    }

    // Add new files to selection
    selectedFiles = [...selectedFiles, ...newFiles];
    updateFileList();
  }

  function updateFileList() {
    if (selectedFiles.length === 0) {
      fileList.style.display = 'none';
      return;
    }

    fileList.style.display = 'block';
    fileItems.innerHTML = '';

    selectedFiles.forEach((file, index) => {
      const fileItem = document.createElement('div');
      fileItem.className = 'flex items-center justify-between p-3 bg-[#f8fafc] rounded-lg border border-[#e1e7ef]';
      fileItem.innerHTML = `
        <div class="flex items-center gap-3">
          <div class="text-[#3d98f4]">
            <svg width="24" height="24" fill="currentColor" viewBox="0 0 256 256">
              <path d="M213.66,82.34l-56-56A8,8,0,0,0,152,24H56A16,16,0,0,0,40,40V216a16,16,0,0,0,16,16H200a16,16,0,0,0,16-16V88A8,8,0,0,0,213.66,82.34ZM152,88V44l44,44Z"></path>
            </svg>
          </div>
          <div>
            <p class="text-[#111418] text-sm font-medium">${file.name}</p>
            <p class="text-[#60758a] text-xs">${formatFileSize(file.size)}</p>
          </div>
        </div>
        <button data-index="${index}" class="remove-file-btn text-[#ef4444] hover:text-[#dc2626] p-1">
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 256 256">
            <path d="M208.49,191.51a12,12,0,0,1-17,17L128,145,64.49,208.49a12,12,0,0,1-17-17L111,128,47.51,64.49a12,12,0,0,1,17-17L128,111l63.51-63.52a12,12,0,0,1,17,17L145,128Z"></path>
          </svg>
        </button>
      `;
      fileItems.appendChild(fileItem);
    });

    // Add event listeners to remove buttons
    document.querySelectorAll('.remove-file-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        const index = parseInt(this.getAttribute('data-index'));
        removeFile(index);
      });
    });

    // Update total size display
    const totalSize = selectedFiles.reduce((sum, file) => sum + file.size, 0);
    const totalSizeElement = document.createElement('div');
    totalSizeElement.className = 'mt-2 text-[#60758a] text-sm';
    totalSizeElement.textContent = `Total size: ${formatFileSize(totalSize)} / 50MB`;
    fileItems.appendChild(totalSizeElement);
  }

  function removeFile(index) {
    selectedFiles.splice(index, 1);
    updateFileList();
  }

  function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  function uploadFiles() {
    const formData = new FormData();
    selectedFiles.forEach(file => {
      formData.append('files', file);
    });

    // Add CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    formData.append('csrfmiddlewaretoken', csrfToken);

    // Show progress
    showProgress();
    progressText.textContent = 'Uploading files...';
    progressBar.style.width = '20%';

    // Get dashboard URL from data attribute
    const dashboardUrl = document.getElementById('uploadButton').getAttribute('data-dashboard-url');

    fetch(dashboardUrl, {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        progressText.textContent = 'Files uploaded, starting compression...';
        progressBar.style.width = '60%';

        // Simulate compression progress
        setTimeout(() => {
          progressText.textContent = 'Compression complete! Redirecting...';
          progressBar.style.width = '100%';

          setTimeout(() => {
            window.location.href = data.redirect_url;
          }, 1000);
        }, 2000);
      } else {
        hideProgress();
        showError(data.error || 'Upload failed');
      }
    })
    .catch(error => {
      hideProgress();
      showError('Network error: ' + error.message);
    });
  }

  function showProgress() {
    progressSection.style.display = 'block';
    fileList.style.display = 'none';
    dropZone.style.display = 'none';
  }

  function hideProgress() {
    progressSection.style.display = 'none';
    fileList.style.display = selectedFiles.length > 0 ? 'block' : 'none';
    dropZone.style.display = 'block';
  }

  function showError(message) {
    errorText.textContent = message;
    errorMessages.style.display = 'block';
  }

  function hideError() {
    errorMessages.style.display = 'none';
  }
})();
