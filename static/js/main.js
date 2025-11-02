// Main JavaScript for Gmail Attachment Downloader

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();

    // Initialize form validation
    initializeFormValidation();

    // Format file sizes
    formatFileSizes();

    // Initialize search functionality
    initializeSearch();

    // Add loading states to buttons
    initializeLoadingStates();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Form validation
function initializeFormValidation() {
    // Gmail connection form
    const connectForm = document.querySelector('#connectForm');
    if (connectForm) {
        connectForm.addEventListener('submit', function(e) {
            const submitBtn = connectForm.querySelector('button[type="submit"]');
            submitBtn.innerHTML = '<span class="loading"></span> Processing...';
            submitBtn.disabled = true;
        });
    }

    // Login form
    const loginForm = document.querySelector('form[action*="login"]');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const email = loginForm.querySelector('input[name="email"]');
            const password = loginForm.querySelector('input[name="password"]');

            if (!validateEmail(email.value)) {
                e.preventDefault();
                showAlert('Please enter a valid email address', 'danger');
                email.focus();
                return;
            }
        });
    }
}

// Email validation
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Show alert messages
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.container');
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    alertContainer.insertBefore(alertDiv, alertContainer.firstChild);

    // Auto dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Format file sizes
function formatFileSizes() {
    const sizeElements = document.querySelectorAll('[data-file-size]');
    sizeElements.forEach(element => {
        const bytes = parseInt(element.dataset.fileSize);
        element.textContent = formatBytes(bytes);
    });
}

function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Initialize search functionality
function initializeSearch() {
    const searchInput = document.querySelector('#searchFilter');
    if (searchInput) {
        let searchTimeout;

        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                filterAttachments();
            }, 300);
        });
    }
}

// Filter attachments
function filterAttachments() {
    const searchTerm = document.querySelector('#searchFilter')?.value.toLowerCase() || '';
    const typeFilter = document.querySelector('#typeFilter')?.value || '';

    const items = document.querySelectorAll('.attachment-item');
    let visibleCount = 0;

    items.forEach(item => {
        const filename = item.dataset.filename?.toLowerCase() || '';
        const filetype = item.dataset.type || '';
        const subject = item.querySelector('[data-subject]')?.dataset.subject?.toLowerCase() || '';
        const sender = item.querySelector('[data-sender]')?.dataset.sender?.toLowerCase() || '';

        const matchesSearch = filename.includes(searchTerm) || 
                            subject.includes(searchTerm) || 
                            sender.includes(searchTerm);
        const matchesType = !typeFilter || filetype === typeFilter;

        if (matchesSearch && matchesType) {
            item.style.display = '';
            visibleCount++;
        } else {
            item.style.display = 'none';
        }
    });

    // Update results count
    const countElement = document.querySelector('#resultsCount');
    if (countElement) {
        countElement.textContent = `Showing ${visibleCount} of ${items.length} files`;
    }
}

// Initialize loading states
function initializeLoadingStates() {
    const submitButtons = document.querySelectorAll('button[type="submit"]');

    submitButtons.forEach(button => {
        const form = button.closest('form');
        if (form) {
            form.addEventListener('submit', function() {
                const originalText = button.innerHTML;
                button.innerHTML = '<span class="loading"></span> Processing...';
                button.disabled = true;

                // Re-enable after timeout as fallback
                setTimeout(() => {
                    button.innerHTML = originalText;
                    button.disabled = false;
                }, 30000);
            });
        }
    });
}

// Utility functions
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showAlert('Copied to clipboard!', 'success');
        });
    } else {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showAlert('Copied to clipboard!', 'success');
    }
}

// Export for global use
window.EmailDL = {
    showAlert,
    formatBytes,
    copyToClipboard,
    filterAttachments
};
