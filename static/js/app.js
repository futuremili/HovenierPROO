// LandscapePro JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Date input validation for leave requests
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    
    if (startDateInput && endDateInput) {
        // Set minimum date to today
        const today = new Date().toISOString().split('T')[0];
        startDateInput.min = today;
        endDateInput.min = today;
        
        startDateInput.addEventListener('change', function() {
            endDateInput.min = this.value;
            if (endDateInput.value && endDateInput.value < this.value) {
                endDateInput.value = this.value;
            }
        });
    }

    // Confirmation dialogs for important actions
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                event.preventDefault();
            }
        });
    });

    // Auto-refresh time status every 30 seconds
    if (window.location.pathname === '/time-tracking' || window.location.pathname === '/dashboard') {
        setInterval(function() {
            // Could implement AJAX refresh here if needed
            // For now, we'll rely on manual refresh
        }, 30000);
    }

    // Mobile-friendly touch improvements
    if ('ontouchstart' in window) {
        document.body.classList.add('touch-device');
        
        // Add touch feedback to buttons
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(function(button) {
            button.addEventListener('touchstart', function() {
                this.classList.add('btn-touched');
            });
            
            button.addEventListener('touchend', function() {
                setTimeout(() => {
                    this.classList.remove('btn-touched');
                }, 150);
            });
        });
    }

    // Improve accessibility
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    dropdownToggles.forEach(function(toggle) {
        toggle.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                this.click();
            }
        });
    });

    // Form auto-save for longer forms (like leave requests)
    const autoSaveForms = document.querySelectorAll('[data-autosave]');
    autoSaveForms.forEach(function(form) {
        const formId = form.id;
        if (formId) {
            // Load saved data
            const savedData = localStorage.getItem(`autosave_${formId}`);
            if (savedData) {
                try {
                    const data = JSON.parse(savedData);
                    Object.keys(data).forEach(function(key) {
                        const input = form.querySelector(`[name="${key}"]`);
                        if (input && input.type !== 'submit') {
                            input.value = data[key];
                        }
                    });
                } catch (e) {
                    console.warn('Failed to restore form data:', e);
                }
            }

            // Save data on input
            form.addEventListener('input', debounce(function() {
                const formData = new FormData(form);
                const data = {};
                for (let [key, value] of formData.entries()) {
                    data[key] = value;
                }
                localStorage.setItem(`autosave_${formId}`, JSON.stringify(data));
            }, 1000));

            // Clear saved data on successful submit
            form.addEventListener('submit', function() {
                localStorage.removeItem(`autosave_${formId}`);
            });
        }
    });

    // Update time display
    updateTimeDisplay();
    setInterval(updateTimeDisplay, 1000);
});

// Utility function for debouncing
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Update current time display
function updateTimeDisplay() {
    const timeElements = document.querySelectorAll('.current-time');
    timeElements.forEach(function(element) {
        const now = new Date();
        element.textContent = now.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        });
    });
}

// Handle network status
window.addEventListener('online', function() {
    const offlineAlert = document.getElementById('offline-alert');
    if (offlineAlert) {
        offlineAlert.remove();
    }
});

window.addEventListener('offline', function() {
    const existingAlert = document.getElementById('offline-alert');
    if (!existingAlert) {
        const alert = document.createElement('div');
        alert.id = 'offline-alert';
        alert.className = 'alert alert-warning alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
        alert.style.zIndex = '9999';
        alert.innerHTML = `
            <i data-feather="wifi-off" class="me-2"></i>
            You're currently offline. Some features may not work.
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alert);
        feather.replace();
    }
});

// Service Worker registration for offline support (if needed)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Uncomment if you want to implement offline functionality
        // navigator.serviceWorker.register('/sw.js');
    });
}

// Touch-friendly improvements
document.addEventListener('touchstart', function() {}, {passive: true});
document.addEventListener('touchmove', function() {}, {passive: true});

// Prevent zoom on double-tap for better mobile experience
let lastTouchEnd = 0;
document.addEventListener('touchend', function (event) {
    const now = (new Date()).getTime();
    if (now - lastTouchEnd <= 300) {
        event.preventDefault();
    }
    lastTouchEnd = now;
}, false);
