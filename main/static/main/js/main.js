/**
 * Main JavaScript file for Teacher Portal
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Teacher Portal initialized');

    // 1. Gallery expand/collapse functionality
    setupGalleryHover();

    // 2. Bookmark toggle (visual only)
    setupBookmarkButtons();

    // 3. Smooth scrolling for navigation
    setupSmoothScrolling();

    // 4. Telegram contact form submission
    setupTelegramForm();
});

/**
 * 1. Setup gallery hover effect for desktop
 */
function setupGalleryHover() {
    const galleryItems = document.querySelectorAll('.gallery-item-desktop');

    if (galleryItems.length === 0) return;

    // Set first item as active by default
    galleryItems[0].classList.add('gallery-item-active');

    // Hover effect for each gallery item
    galleryItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            // Remove active class from all items
            galleryItems.forEach(i => i.classList.remove('gallery-item-active'));
            // Add active class to hovered item
            this.classList.add('gallery-item-active');
        });
    });

    // Reset to first item when mouse leaves gallery
    const galleryContainer = document.querySelector('.gallery-desktop');
    if (galleryContainer) {
        galleryContainer.addEventListener('mouseleave', function() {
            galleryItems.forEach(i => i.classList.remove('gallery-item-active'));
            galleryItems[0].classList.add('gallery-item-active');
        });
    }
}

/**
 * 2. Setup bookmark buttons (visual toggle only)
 */
function setupBookmarkButtons() {
    const bookmarkButtons = document.querySelectorAll('.event-bookmark, .news-bookmark');

    bookmarkButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            event.stopPropagation();

            const icon = this.querySelector('i');
            const isBookmarked = icon.classList.contains('fas');

            // Toggle bookmark state
            if (isBookmarked) {
                icon.classList.remove('fas');
                icon.classList.add('far');
                console.log('Bookmark removed (visual only)');
            } else {
                icon.classList.remove('far');
                icon.classList.add('fas');
                console.log('Bookmark added (visual only)');
            }
        });
    });
}

/**
 * 3. Setup smooth scrolling for navigation
 */
function setupSmoothScrolling() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]:not([href="#"])');

    anchorLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            const targetId = this.getAttribute('href');

            if (targetId && targetId !== '#') {
                event.preventDefault();

                const targetElement = document.querySelector(targetId);

                if (targetElement) {
                    // Smooth scroll to target
                    window.scrollTo({
                        top: targetElement.offsetTop - 80,
                        behavior: 'smooth'
                    });

                    // Update URL hash without jumping
                    history.pushState(null, null, targetId);

                    // Update active nav link
                    updateActiveNavigation(targetId);
                }
            }
        });
    });
}

/**
 * Update active navigation link
 */
function updateActiveNavigation(targetId) {
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === targetId) {
            link.classList.add('active');
        }
    });
}

/**
 * 4. Setup Telegram contact form submission
 */
function setupTelegramForm() {
    const form = document.getElementById('contactForm');

    if (!form) {
        console.log('❌ Contact form not found on this page');
        return;
    }

    console.log('✅ Настраиваю форму Telegram');

    // Удаляем все старые обработчики событий
    const newForm = form.cloneNode(true);
    form.parentNode.replaceChild(newForm, form);

    // Получаем обновленные элементы
    const updatedForm = document.getElementById('contactForm');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = document.getElementById('btn-text');

    // Создаем спиннер, если его нет
    let btnSpinner = document.getElementById('btn-spinner');
    if (!btnSpinner && submitBtn) {
        const spinnerSpan = document.createElement('span');
        spinnerSpan.id = 'btn-spinner';
        spinnerSpan.style.display = 'none';
        spinnerSpan.innerHTML = '<div class="spinner"></div>';
        submitBtn.appendChild(spinnerSpan);
        btnSpinner = spinnerSpan;
    }

    // Добавляем обработчик закрытия модальных окон по ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal();
        }
    });

    // Добавляем обработчик закрытия модальных окон по клику на overlay
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal();
            }
        });
    });

    // Флаг для предотвращения двойной отправки
    let isSubmitting = false;

    /**
     * Показать модальное окно успеха
     */
    function showSuccessModal(message) {
        const modal = document.getElementById('successModal');
        const messageElement = document.getElementById('successMessage');

        if (messageElement) {
            messageElement.textContent = message;
        }

        if (modal) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden'; // Блокируем скролл
        }
    }

    /**
     * Показать модальное окно ошибки
     */
    function showErrorModal(message) {
        const modal = document.getElementById('errorModal');
        const messageElement = document.getElementById('errorMessage');

        if (messageElement) {
            messageElement.textContent = message;
        }

        if (modal) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden'; // Блокируем скролл
        }
    }

    /**
     * Закрыть все модальные окна
     */
    window.closeModal = function() {
        document.querySelectorAll('.modal-overlay').forEach(modal => {
            modal.style.display = 'none';
        });
        document.body.style.overflow = 'auto'; // Восстанавливаем скролл
    };

    /**
     * Валидация email
     */
    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    /**
     * Сброс ошибок
     */
    function resetErrors() {
        document.querySelectorAll('.error-message').forEach(el => {
            el.style.display = 'none';
        });
        document.querySelectorAll('.form-input, .form-textarea').forEach(el => {
            el.classList.remove('is-invalid');
        });
    }

    /**
     * Показать ошибку у конкретного поля
     */
    function showFieldError(fieldName, message) {
        const field = document.querySelector(`[name="${fieldName}"]`);
        const errorEl = document.getElementById(`${fieldName}-error`);

        if (field && errorEl) {
            field.classList.add('is-invalid');
            errorEl.textContent = message;
            errorEl.style.display = 'block';

            // Прокрутка к полю с ошибкой
            field.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    /**
     * Обработка отправки формы
     */
    updatedForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        e.stopPropagation();

        if (isSubmitting) {
            console.log('⏸️ Форма уже отправляется, пропускаем...');
            return;
        }

        console.log('🎯 Форма отправляется...');
        isSubmitting = true;

        resetErrors();

        // Собираем данные
        const formData = new FormData(this);
        const data = {
            name: formData.get('name') || '',
            email: formData.get('email') || '',
            subject: formData.get('subject') || '',
            message: formData.get('message') || ''
        };

        console.log('📤 Отправляемые данные:', data);

        // Валидация
        let isValid = true;
        let firstErrorField = null;

        if (!data.name.trim()) {
            showFieldError('name', 'Пожалуйста, введите ваше имя');
            isValid = false;
            if (!firstErrorField) firstErrorField = 'name';
        }

        if (!data.email.trim()) {
            showFieldError('email', 'Пожалуйста, введите email');
            isValid = false;
            if (!firstErrorField) firstErrorField = 'email';
        } else if (!isValidEmail(data.email)) {
            showFieldError('email', 'Пожалуйста, введите корректный email');
            isValid = false;
            if (!firstErrorField) firstErrorField = 'email';
        }

        if (!data.subject.trim()) {
            showFieldError('subject', 'Пожалуйста, укажите тему обращения');
            isValid = false;
            if (!firstErrorField) firstErrorField = 'subject';
        }

        if (!data.message.trim()) {
            showFieldError('message', 'Пожалуйста, напишите сообщение');
            isValid = false;
            if (!firstErrorField) firstErrorField = 'message';
        }

        if (!isValid) {
            console.log('❌ Валидация не пройдена');

            // Прокрутка к первому полю с ошибкой
            if (firstErrorField) {
                const field = document.querySelector(`[name="${firstErrorField}"]`);
                if (field) {
                    field.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }

            isSubmitting = false;
            return;
        }

        // Показываем загрузку
        if (submitBtn) {
            submitBtn.disabled = true;
            if (btnText) btnText.textContent = 'Отправка...';
            if (btnSpinner) btnSpinner.style.display = 'inline-block';
        }

        try {
            console.log('🌐 Отправляю POST на /contact/');

            const response = await fetch('/contact/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            console.log('📥 Ответ сервера. Статус:', response.status);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log('📊 Результат от сервера:', result);

            if (result.success) {
                console.log('✅ Сообщение успешно отправлено');
                showSuccessModal(result.message || 'Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.');
                updatedForm.reset(); // Очищаем форму
            } else {
                console.log('❌ Ошибка от сервера:', result.message);
                showErrorModal(result.message || 'Ошибка отправки. Пожалуйста, попробуйте позже.');
            }
        } catch (error) {
            console.error('💥 Ошибка при отправке формы:', error);
            showErrorModal('Ошибка соединения с сервером. Пожалуйста, проверьте интернет-соединение и попробуйте позже.');
        } finally {
            // Восстанавливаем кнопку
            if (submitBtn) {
                submitBtn.disabled = false;
                if (btnText) btnText.textContent = 'Отправить сообщение';
                if (btnSpinner) btnSpinner.style.display = 'none';
            }
            isSubmitting = false;
        }
    });
}

/**
 * Utility: Add CSS for spinner (if not in Bootstrap)
 */
function addSpinnerStyles() {
    if (!document.querySelector('#spinner-styles')) {
        const style = document.createElement('style');
        style.id = 'spinner-styles';
        style.textContent = `
            .spinner-border {
                display: inline-block;
                width: 1rem;
                height: 1rem;
                vertical-align: text-bottom;
                border: 0.2em solid currentColor;
                border-right-color: transparent;
                border-radius: 50%;
                animation: spinner-border 0.75s linear infinite;
            }

            @keyframes spinner-border {
                to { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }
}

// Add spinner styles on load
addSpinnerStyles();

/**
 * Utility: Detect mobile/desktop
 */
function isMobileDevice() {
    return window.innerWidth <= 768;
}

/**
 * Utility: Log gallery interactions
 */
function logGalleryInteraction(itemId, action) {
    console.log(`Gallery item ${itemId}: ${action}`);
}

// Add responsive behavior
window.addEventListener('resize', function() {
    console.log('Window resized to:', window.innerWidth, 'x', window.innerHeight);
});

// Initialize on load
console.log('Teacher Portal: Display functionality ready');



/**
 * Цветные бейджи для мероприятий и новостей
 * ТОЧНЫЕ ЦВЕТА ИЗ КАТАЛОГА
 */

// Цвета для мероприятий (из views.py events)
const eventColors = {
    'Вебинар': { bg: 'rgba(201, 228, 202, 0.85)', text: '#1e8c1e' },
    'Конкурс': { bg: 'rgba(184, 212, 232, 0.85)', text: '#0c4a6e' },
    'Конференция': { bg: 'rgba(232, 212, 240, 0.85)', text: '#6b21a8' },
    'Круглый стол': { bg: 'rgba(245, 213, 184, 0.85)', text: '#c2410c' },
    'Курсы повышения квалификации': { bg: 'rgba(212, 232, 240, 0.85)', text: '#075985' },
    'Мастер-класс': { bg: 'rgba(240, 232, 212, 0.85)', text: '#854d0e' },
    'Олимпиада': { bg: 'rgba(201, 228, 202, 0.85)', text: '#1e8c1e' },
    'Открытый урок': { bg: 'rgba(184, 212, 232, 0.85)', text: '#0c4a6e' },
    'Семинар': { bg: 'rgba(232, 212, 240, 0.85)', text: '#6b21a8' },
    'Слет': { bg: 'rgba(245, 213, 184, 0.85)', text: '#c2410c' },
    'Тренинг': { bg: 'rgba(212, 232, 240, 0.85)', text: '#075985' },
    'Форум': { bg: 'rgba(240, 232, 212, 0.85)', text: '#854d0e' },
    'default': { bg: 'rgba(200, 200, 200, 0.85)', text: '#000000' }
};

// Цвета для новостей (из views.py news)
const newsColors = {
    'Экстренные': { bg: 'rgba(255, 200, 200, 0.85)', text: '#cc0000' },
    'Важные': { bg: 'rgba(255, 230, 200, 0.85)', text: '#ff6600' },
    'Новости': { bg: 'rgba(201, 228, 202, 0.85)', text: '#1e8c1e' },
    'Аналитика': { bg: 'rgba(200, 220, 240, 0.85)', text: '#0066cc' },
    'Анонсы': { bg: 'rgba(240, 240, 180, 0.85)', text: '#cc9900' },
    'Документы': { bg: 'rgba(220, 240, 220, 0.85)', text: '#009900' },
    'Отчеты': { bg: 'rgba(240, 220, 220, 0.85)', text: '#cc3366' },
    'Рекомендации': { bg: 'rgba(230, 220, 240, 0.85)', text: '#6600cc' },
    'default': { bg: 'rgba(200, 200, 200, 0.85)', text: '#000000' }
};

// Функция раскраски бейджей мероприятий
function colorizeEventBadges() {
    const badges = document.querySelectorAll('.event-badge');

    badges.forEach(badge => {
        let type = badge.textContent.trim();
        type = type.replace(/\s+/g, ' ').trim();

        const colors = eventColors[type] || eventColors['default'];
        badge.style.backgroundColor = colors.bg;
        badge.style.color = colors.text;
        badge.style.border = 'none';
        badge.style.fontWeight = '700';
        badge.style.textTransform = 'uppercase';
        badge.style.letterSpacing = '0.5px';
        badge.style.fontSize = '13px';
        badge.style.padding = '8px 16px';
        badge.style.borderRadius = '8px';
        badge.style.display = 'inline-block';
        badge.style.width = 'auto';
    });
}

// Функция раскраски бейджей новостей
function colorizeNewsBadges() {
    const badges = document.querySelectorAll('.news-category');

    badges.forEach(badge => {
        let type = badge.textContent.trim();
        type = type.replace(/\s+/g, ' ').trim();

        const colors = newsColors[type] || newsColors['default'];
        badge.style.backgroundColor = colors.bg;
        badge.style.color = colors.text;
        badge.style.border = 'none';
        badge.style.fontWeight = '700';
        badge.style.textTransform = 'uppercase';
        badge.style.letterSpacing = '0.5px';
        badge.style.fontSize = '13px';
        badge.style.padding = '8px 16px';
        badge.style.borderRadius = '8px';
        badge.style.display = 'inline-block';
        badge.style.width = 'auto';
    });
}

// Функция раскраски всех бейджей
function colorizeAllBadges() {
    colorizeEventBadges();
    colorizeNewsBadges();
}

// Запускаем при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    colorizeAllBadges();
});

// Наблюдатель за изменениями в DOM (для динамической подгрузки)
const observer = new MutationObserver(function() {
    colorizeAllBadges();
});
observer.observe(document.body, { childList: true, subtree: true });