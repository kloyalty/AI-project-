// Agreement Studio - Main JavaScript
// Smooth interactions and progressive enhancement

document.addEventListener('DOMContentLoaded', () => {
    // Smooth scroll behavior
    document.documentElement.style.scrollBehavior = 'smooth';
    
    // Add fade-in animations to elements
    observeElements();
    
    // Auto-resize textareas
    autoResizeTextareas();
    
    // Enhance form submissions
    enhanceForms();
});

// Intersection Observer for fade-in animations
function observeElements() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    document.querySelectorAll('.fade-in').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.8s ease-out, transform 0.8s ease-out';
        observer.observe(el);
    });
}

// Auto-resize textareas
function autoResizeTextareas() {
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        // Set initial height
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
        
        // Add input listener
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
}

// Enhance form submissions with loading states
function enhanceForms() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.disabled = true;
                const originalText = submitBtn.textContent;
                submitBtn.textContent = 'Processing...';
                
                // Re-enable after 5 seconds as fallback
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalText;
                }, 5000);
            }
        });
    });
}

// Utility: Add glow effect on hover
function addGlowEffect(element) {
    element.addEventListener('mouseenter', function() {
        this.style.boxShadow = '0 0 30px rgba(204, 120, 92, 0.4)';
    });
    
    element.addEventListener('mouseleave', function() {
        this.style.boxShadow = '';
    });
}

// Utility: Smooth page transitions
function smoothTransition(url) {
    document.body.style.opacity = '0';
    document.body.style.transform = 'translateY(-20px)';
    document.body.style.transition = 'opacity 0.4s ease-out, transform 0.4s ease-out';
    
    setTimeout(() => {
        window.location.href = url;
    }, 400);
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter to submit forms
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const activeForm = document.activeElement.closest('form');
        if (activeForm) {
            activeForm.requestSubmit();
        }
    }
});

// Print optimization
window.addEventListener('beforeprint', () => {
    document.body.classList.add('printing');
});

window.addEventListener('afterprint', () => {
    document.body.classList.remove('printing');
});

