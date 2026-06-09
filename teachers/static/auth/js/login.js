// login.js - Полная версия с AJAX, тултипами, требованиями и ошибками под полями
// Версия: 4.0 - Исправлена проблема CSRF

class LoginApp {
    constructor() {
        // Основные поля
        this.emailInput = document.getElementById('email');
        this.passwordInput = document.getElementById('password');

        // Кнопка и форма
        this.submitBtn = document.getElementById('submitBtn');
        this.loginForm = document.getElementById('loginForm');

        // Элементы ошибок (под полями)
        this.emailError = document.getElementById('emailError');
        this.passwordError = document.getElementById('passwordError');

        // Флаги для отслеживания, touched ли поле
        this.emailTouched = false;
        this.passwordTouched = false;

        // Для тултипов
        this.hoverTooltips = new Map();
        this.requirementTooltips = new Map();
        this.currentFocusedField = null;
        this.hoverTimeout = null;
        this.hoverTooltipElement = null;

        // Флаг для блокировки повторной отправки
        this.isSubmitting = false;

        console.log('LoginApp инициализирован');
    }

    // ✅ ДОБАВЛЕН МЕТОД ДЛЯ ПОЛУЧЕНИЯ CSRF-ТОКЕНА ИЗ COOKIE
    getCSRFToken() {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === ('csrftoken=')) {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        return cookieValue;
    }

    init() {
        console.log('Инициализация страницы входа...');

        // Обработка отправки формы (AJAX)
        if (this.submitBtn) {
            this.submitBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleSubmit(e);
            });
        }

        if (this.loginForm) {
            this.loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleSubmit(e);
            });
        }

        // Настройка валидации полей
        this.setupFieldValidation();

        // Настройка тултипов при наведении
        this.setupHoverTooltips();

        // Настройка подсказок при фокусе
        this.setupFocusRequirements();

        // Обработка кликов вне элементов для скрытия тултипов
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.input-hint-tooltip') &&
                !e.target.closest('.form-control') &&
                !e.target.closest('.hover-tooltip') &&
                !e.target.closest('.requirements-tooltip')) {
                this.hideAllTooltips();
            }
        });

        // Обработка скролла для обновления позиций тултипов
        window.addEventListener('scroll', () => {
            this.updateTooltipPositions();
        });

        // Обработка изменения размера окна
        window.addEventListener('resize', () => {
            this.updateTooltipPositions();
        });

        console.log('Инициализация завершена');
    }

    updateTooltipPositions() {
        // Обновляем позиции hover-тултипов
        this.hoverTooltips.forEach((tooltip, element) => {
            if (tooltip && tooltip.parentNode) {
                const rect = element.getBoundingClientRect();
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
                tooltip.style.top = (rect.bottom + scrollTop + 8) + 'px';
                tooltip.style.left = (rect.left + scrollLeft + rect.width / 2) + 'px';
                tooltip.style.transform = 'translateX(-50%)';
            }
        });

        // Обновляем позиции requirement-тултипов
        this.requirementTooltips.forEach((tooltip, fieldId) => {
            if (tooltip && tooltip.parentNode) {
                let inputElement;
                if (fieldId === 'email') {
                    inputElement = this.emailInput;
                } else if (fieldId === 'password') {
                    inputElement = this.passwordInput;
                } else {
                    return;
                }

                if (inputElement) {
                    const rect = inputElement.getBoundingClientRect();
                    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                    tooltip.style.top = (rect.bottom + scrollTop + 8) + 'px';
                    tooltip.style.left = rect.left + 'px';
                    tooltip.style.transform = 'none';
                }
            }
        });
    }

    setupFieldValidation() {
        // Email
        if (this.emailInput) {
            this.emailInput.addEventListener('input', () => {
                this.clearError('emailError');
                this.validateEmail(false);
                this.updateEmailRequirements();
            });

            this.emailInput.addEventListener('blur', () => {
                this.emailTouched = true;
                if (this.emailInput.value.trim() !== '') {
                    this.validateEmail(true);
                } else {
                    this.clearError('emailError');
                }
            });
        }

        // Пароль
        if (this.passwordInput) {
            this.passwordInput.addEventListener('input', () => {
                this.clearError('passwordError');
                this.validatePassword(false);
                this.updatePasswordRequirements();
            });

            this.passwordInput.addEventListener('blur', () => {
                this.passwordTouched = true;
                if (this.passwordInput.value !== '') {
                    this.validatePassword(true);
                } else {
                    this.clearError('passwordError');
                }
            });
        }
    }

    setupHoverTooltips() {
        const tooltipElements = document.querySelectorAll('.input-hint-tooltip');
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', () => {
                this.showHoverTooltip(element);
            });
            element.addEventListener('mouseleave', () => {
                setTimeout(() => {
                    this.hideHoverTooltip(element);
                }, 100);
            });
        });
    }

    showHoverTooltip(element) {
        clearTimeout(this.hoverTimeout);
        this.hoverTooltipElement = element;
        this.hoverTimeout = setTimeout(() => {
            if (!this.hoverTooltipElement || this.hoverTooltipElement !== element) return;
            this.hideAllHoverTooltips();
            const tooltipText = element.getAttribute('data-tooltip');
            if (!tooltipText) return;
            const tooltip = document.createElement('div');
            tooltip.className = 'hover-tooltip';
            tooltip.textContent = tooltipText;
            const rect = element.getBoundingClientRect();
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
            let top = rect.bottom + scrollTop + 8;
            let left = rect.left + scrollLeft + rect.width / 2;
            document.body.appendChild(tooltip);
            const tooltipRect = tooltip.getBoundingClientRect();
            if (left + tooltipRect.width / 2 > window.innerWidth + scrollLeft) {
                left = window.innerWidth + scrollLeft - tooltipRect.width / 2 - 10;
            }
            if (left - tooltipRect.width / 2 < scrollLeft) {
                left = tooltipRect.width / 2 + scrollLeft + 10;
            }
            tooltip.style.position = 'absolute';
            tooltip.style.top = top + 'px';
            tooltip.style.left = left + 'px';
            tooltip.style.transform = 'translateX(-50%)';
            tooltip.style.zIndex = '10000';
            tooltip.style.opacity = '0';
            setTimeout(() => {
                tooltip.style.transition = 'opacity 0.2s ease';
                tooltip.style.opacity = '1';
                tooltip.classList.add('show');
            }, 10);
            this.hoverTooltips.set(element, tooltip);
            setTimeout(() => {
                if (this.hoverTooltips.has(element)) {
                    this.hideHoverTooltip(element);
                }
            }, 3000);
        }, 50);
    }

    hideHoverTooltip(element) {
        if (this.hoverTooltips.has(element)) {
            const tooltip = this.hoverTooltips.get(element);
            if (tooltip && tooltip.parentNode) {
                tooltip.style.opacity = '0';
                setTimeout(() => {
                    if (tooltip.parentNode) tooltip.remove();
                }, 150);
            }
            this.hoverTooltips.delete(element);
        }
        this.hoverTooltipElement = null;
    }

    hideAllHoverTooltips() {
        this.hoverTooltips.forEach((tooltip, element) => {
            if (tooltip && tooltip.parentNode) {
                tooltip.style.opacity = '0';
                setTimeout(() => {
                    if (tooltip.parentNode) tooltip.remove();
                }, 150);
            }
        });
        this.hoverTooltips.clear();
        this.hoverTooltipElement = null;
    }

    setupFocusRequirements() {
        const fieldsConfig = {
            'email': {
                element: this.emailInput,
                config: {
                    title: 'Требования к Email:',
                    requirements: [
                        { type: 'format', text: 'Формат: user@example.com' },
                        { type: 'max', text: 'Максимум 30 символов' },
                        { type: 'domain', text: 'Должен содержать @ и домен' },
                        { type: 'example', text: 'Пример: ivanov@school.ru' }
                    ]
                }
            },
            'password': {
                element: this.passwordInput,
                config: {
                    title: 'Требования к паролю:',
                    requirements: [
                        { type: 'length', text: 'Минимум 6 символов' },
                        { type: 'max', text: 'Максимум 30 символов' },
                        { type: 'chars', text: 'Разрешены: буквы, цифры, !@#$%^&*' },
                        { type: 'example', text: 'Пример: Teacher123!' }
                    ]
                }
            }
        };
        Object.entries(fieldsConfig).forEach(([fieldId, { element, config }]) => {
            if (!element) return;
            element.addEventListener('focus', () => {
                this.hideAllTooltips();
                this.currentFocusedField = fieldId;
                setTimeout(() => {
                    if (document.activeElement === element) {
                        this.showRequirements(fieldId, element, config);
                    }
                }, 10);
            });
            element.addEventListener('blur', () => {
                setTimeout(() => {
                    if (this.currentFocusedField === fieldId &&
                        document.activeElement !== element &&
                        !document.activeElement?.closest('.requirements-tooltip')) {
                        this.hideRequirements(fieldId);
                        this.currentFocusedField = null;
                    }
                }, 200);
            });
            element.addEventListener('input', () => {
                if (this.requirementTooltips.has(fieldId)) {
                    this.updateDynamicRequirements(fieldId, element, config);
                }
            });
        });
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                setTimeout(() => {
                    this.hideAllTooltips();
                }, 10);
            }
        });
    }

    showRequirements(fieldId, inputElement, config) {
        this.requirementTooltips.forEach((tooltip, id) => {
            if (id !== fieldId && tooltip && tooltip.parentNode) {
                this.hideRequirements(id);
            }
        });
        const requirements = document.createElement('div');
        requirements.className = 'requirements-tooltip';
        requirements.dataset.field = fieldId;
        let html = `<div class="requirements-title">${config.title}</div>`;
        config.requirements.forEach(req => {
            const isValid = req.type === 'example' ? true : this.checkRequirement(fieldId, req.type, inputElement.value);
            const icon = req.type === 'example' ? 'lightbulb' : (isValid ? 'check' : 'circle');
            const statusClass = req.type === 'example' ? 'example' : (isValid ? 'valid' : 'invalid');
            html += `
                <div class="requirement ${req.type} ${statusClass}">
                    <i class="fas fa-${icon}"></i>
                    <span>${req.text}</span>
                </div>
            `;
        });
        requirements.innerHTML = html;
        const rect = inputElement.getBoundingClientRect();
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        requirements.style.position = 'absolute';
        requirements.style.top = (rect.bottom + scrollTop + 8) + 'px';
        requirements.style.left = rect.left + 'px';
        requirements.style.zIndex = '10001';
        requirements.style.opacity = '0';
        document.body.appendChild(requirements);
        setTimeout(() => {
            requirements.style.transition = 'opacity 0.2s ease';
            requirements.style.opacity = '1';
            requirements.classList.add('show');
        }, 10);
        this.requirementTooltips.set(fieldId, requirements);
        requirements.addEventListener('mouseenter', () => {
            requirements.dataset.hovering = 'true';
        });
        requirements.addEventListener('mouseleave', () => {
            requirements.dataset.hovering = 'false';
            setTimeout(() => {
                if (requirements.dataset.hovering === 'false' && document.activeElement !== inputElement) {
                    this.hideRequirements(fieldId);
                }
            }, 100);
        });
    }

    updateDynamicRequirements(fieldId, inputElement, config) {
        const requirements = this.requirementTooltips.get(fieldId);
        if (!requirements) return;
        const requirementElements = requirements.querySelectorAll('.requirement');
        config.requirements.forEach((req, index) => {
            if (req.type !== 'example') {
                const requirementElement = requirementElements[index];
                if (requirementElement) {
                    const isValid = this.checkRequirement(fieldId, req.type, inputElement.value);
                    const icon = isValid ? 'check' : 'circle';
                    const statusClass = isValid ? 'valid' : 'invalid';
                    requirementElement.className = `requirement ${req.type} ${statusClass}`;
                    requirementElement.innerHTML = `
                        <i class="fas fa-${icon}"></i>
                        <span>${req.text}</span>
                    `;
                }
            }
        });
    }

    updateEmailRequirements() {
        if (this.requirementTooltips.has('email') && this.emailInput) {
            this.updateDynamicRequirements('email', this.emailInput, {
                title: 'Требования к Email:',
                requirements: [
                    { type: 'format', text: 'Формат: user@example.com' },
                    { type: 'max', text: 'Максимум 30 символов' },
                    { type: 'domain', text: 'Должен содержать @ и домен' },
                    { type: 'example', text: 'Пример: ivanov@school.ru' }
                ]
            });
        }
    }

    updatePasswordRequirements() {
        if (this.requirementTooltips.has('password') && this.passwordInput) {
            this.updateDynamicRequirements('password', this.passwordInput, {
                title: 'Требования к паролю:',
                requirements: [
                    { type: 'length', text: 'Минимум 6 символов' },
                    { type: 'max', text: 'Максимум 30 символов' },
                    { type: 'chars', text: 'Разрешены: буквы, цифры, !@#$%^&*' },
                    { type: 'example', text: 'Пример: Teacher123!' }
                ]
            });
        }
    }

    checkRequirement(fieldId, type, value) {
        switch (type) {
            case 'length': return value.length >= 6;
            case 'max': return value.length <= 30;
            case 'chars': return /^[A-Za-z0-9!@#$%^&*]*$/.test(value);
            case 'format': return value === '' || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
            case 'domain': return value === '' || /@.+\..+/.test(value);
            default: return true;
        }
    }

    hideRequirements(fieldId) {
        if (this.requirementTooltips.has(fieldId)) {
            const tooltip = this.requirementTooltips.get(fieldId);
            if (tooltip && tooltip.parentNode) {
                tooltip.style.opacity = '0';
                setTimeout(() => {
                    if (tooltip.parentNode) tooltip.remove();
                }, 150);
            }
            this.requirementTooltips.delete(fieldId);
        }
    }

    hideAllTooltips() {
        this.hideAllHoverTooltips();
        this.requirementTooltips.forEach((tooltip, fieldId) => {
            if (tooltip && tooltip.parentNode) {
                tooltip.style.opacity = '0';
                setTimeout(() => {
                    if (tooltip.parentNode) tooltip.remove();
                }, 150);
            }
        });
        this.requirementTooltips.clear();
        this.currentFocusedField = null;
        clearTimeout(this.hoverTimeout);
    }

    clearError(errorElementId) {
        const errorElement = document.getElementById(errorElementId);
        if (errorElement) errorElement.textContent = '';
    }

    setError(errorElementId, message) {
        const errorElement = document.getElementById(errorElementId);
        if (errorElement) errorElement.textContent = message;
    }

    validateEmail(showError = false) {
        const email = this.emailInput.value.trim();
        if (!email) {
            if (showError && this.emailTouched) this.setError('emailError', 'Введите email');
            return false;
        }
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\@]+$/;
        if (!emailRegex.test(email)) {
            if (showError) this.setError('emailError', 'Введите корректный email адрес');
            return false;
        }
        if (email.length > 30) {
            if (showError) this.setError('emailError', 'Email не должен превышать 30 символов');
            return false;
        }
        return true;
    }

    validatePassword(showError = false) {
        const password = this.passwordInput.value;
        if (!password) {
            if (showError && this.passwordTouched) this.setError('passwordError', 'Введите пароль');
            return false;
        }
        if (password.length < 6) {
            if (showError) this.setError('passwordError', 'Пароль должен содержать минимум 6 символов');
            return false;
        }
        if (password.length > 30) {
            if (showError) this.setError('passwordError', 'Пароль не должен превышать 30 символов');
            return false;
        }
        return true;
    }

    validateForm(showErrors = false) {
        let isValid = true;
        if (!this.validateEmail(showErrors)) isValid = false;
        if (!this.validatePassword(showErrors)) isValid = false;
        return isValid;
    }

    showLoading() {
        if (this.submitBtn) {
            this.submitBtn.disabled = true;
            this.submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Вход...</span>';
        }
    }

    hideLoading() {
        if (this.submitBtn) {
            this.submitBtn.disabled = false;
            this.submitBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i><span>Войти</span>';
        }
    }

    handleSubmit(e) {
        if (e) e.preventDefault();
        if (this.isSubmitting) return;
        this.isSubmitting = true;

        this.hideAllTooltips();
        this.emailTouched = true;
        this.passwordTouched = true;

        if (!this.validateForm(true)) {
            const firstError = document.querySelector('.form-error:not(:empty)');
            if (firstError) firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            this.isSubmitting = false;
            return;
        }

        this.showLoading();

        const formData = new FormData(this.loginForm);

        // ✅ ПРАВИЛЬНОЕ ПОЛУЧЕНИЕ CSRF-ТОКЕНА
        let csrfToken = this.getCSRFToken();
        if (!csrfToken) {
            const csrfInput = this.loginForm.querySelector('[name=csrfmiddlewaretoken]');
            if (csrfInput) csrfToken = csrfInput.value;
        }

        fetch(this.loginForm.action || window.location.href, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken,
            },
            body: formData,
        })
        .then(response => {
            // ✅ ОБРАБОТКА ОШИБКИ CSRF
            if (response.status === 403) {
                throw new Error('Ошибка проверки безопасности. Обновите страницу и попробуйте снова.');
            }
            if (!response.ok) {
                throw new Error(`Ошибка сервера: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            this.hideLoading();
            this.isSubmitting = false;
            if (data.success) {
                window.location.href = data.redirect_url;
            } else if (data.errors) {
                if (data.errors.email) this.setError('emailError', data.errors.email);
                if (data.errors.password) this.setError('passwordError', data.errors.password);
                const firstError = document.querySelector('.form-error:not(:empty)');
                if (firstError) firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            } else {
                this.setError('passwordError', 'Неизвестная ошибка. Попробуйте позже.');
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            this.hideLoading();
            this.isSubmitting = false;
            this.setError('passwordError', error.message || 'Ошибка соединения. Проверьте интернет.');
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    try {
        window.loginApp = new LoginApp();
        window.loginApp.init();
        console.log('Приложение входа успешно инициализировано');
    } catch (error) {
        console.error('Ошибка инициализации:', error);
    }
});