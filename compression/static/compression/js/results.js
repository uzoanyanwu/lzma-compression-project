// File download and link copying handler for results page
(function() {
  'use strict';

  // Make functions globally accessible for onclick attributes
  window.handleDownload = handleDownload;
  window.copyDownloadLink = copyDownloadLink;

  function handleDownload(event) {
    // Get the download button
    const downloadButton = document.getElementById('downloadButton');
    const copyLinkButton = document.getElementById('copyLinkButton');

    // Disable the button immediately
    downloadButton.onclick = null;
    downloadButton.style.pointerEvents = 'none';
    downloadButton.classList.remove('hover:bg-[#2d78d4]', 'cursor-pointer', 'bg-[#3d98f4]');
    downloadButton.classList.add('cursor-not-allowed', 'bg-gray-300', 'text-gray-500');
    downloadButton.querySelector('span').textContent = 'Downloading...';

    // Also disable the copy link button
    if (copyLinkButton) {
      copyLinkButton.disabled = true;
      copyLinkButton.classList.add('opacity-50', 'cursor-not-allowed');
      copyLinkButton.style.pointerEvents = 'none';
    }

    // After a short delay, update the button text
    setTimeout(() => {
      downloadButton.querySelector('span').textContent = 'File Downloaded & Deleted';

      // Show a notice that the file has been deleted
      const warningDiv = document.createElement('div');
      warningDiv.className = 'mx-4 mt-4';
      warningDiv.innerHTML = `
        <div class="bg-green-50 border-l-4 border-green-400 p-4 rounded">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-green-800">Download Complete</h3>
              <div class="mt-2 text-sm text-green-700">
                <p>Your file has been downloaded successfully. For security and privacy reasons, the files have been automatically deleted from our servers.</p>
              </div>
            </div>
          </div>
        </div>
      `;

      // Insert the notice after the header
      const contentContainer = document.querySelector('.layout-content-container');
      const header = contentContainer.querySelector('.flex.flex-wrap.justify-between');
      if (header && header.parentNode) {
        header.parentNode.insertBefore(warningDiv, header.nextSibling);
      }
    }, 1500); // Wait 1.5 seconds to simulate download start

    // Let the download proceed normally
    return true;
  }

  function copyDownloadLink(event) {
    const downloadUrl = event.target.closest('button').getAttribute('data-download-url');

    navigator.clipboard.writeText(downloadUrl).then(() => {
      // Show temporary success message
      const button = event.target.closest('button');
      const originalText = button.querySelector('span').textContent;
      button.querySelector('span').textContent = 'Copied!';
      button.classList.add('bg-green-100', 'text-green-700');

      setTimeout(() => {
        button.querySelector('span').textContent = originalText;
        button.classList.remove('bg-green-100', 'text-green-700');
      }, 2000);
    }).catch(err => {
      console.error('Failed to copy: ', err);
    });
  }
})();
