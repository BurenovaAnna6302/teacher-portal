// register.js - Реализация валидации и множественного выбора
// Версия: 4.7 - ИСПРАВЛЕНЫ ТУЛТИПЫ (ПОЛНАЯ ВЕРСИЯ)

class RegisterApp {
    constructor() {
        // Основные поля
        this.emailInput = document.getElementById('email');
        this.passwordInput = document.getElementById('password');
        this.confirmPasswordInput = document.getElementById('confirm_password');
        this.firstNameInput = document.getElementById('first_name');
        this.lastNameInput = document.getElementById('last_name');
        this.middleNameInput = document.getElementById('middle_name');
        this.educationalInstitutionInput = document.getElementById('educational_institution');
        this.experienceInput = document.getElementById('experience');
        this.specializationInput = document.getElementById('specializationInput');

        // Кнопка и форма
        this.submitBtn = document.getElementById('submitBtn');
        this.registerForm = document.getElementById('registerForm');

        // Элементы ошибок
        this.emailError = document.getElementById('emailError');
        this.passwordError = document.getElementById('passwordError');
        this.confirmPasswordError = document.getElementById('confirmPasswordError');
        this.firstNameError = document.getElementById('firstNameError');
        this.lastNameError = document.getElementById('lastNameError');
        this.middleNameError = document.getElementById('middleNameError');
        this.educationalInstitutionError = document.getElementById('educationalInstitutionError');
        this.experienceError = document.getElementById('experienceError');
        this.specializationsError = document.getElementById('specializationsError');

        // Флаги для отслеживания touched полей
        this.emailTouched = false;
        this.passwordTouched = false;
        this.confirmPasswordTouched = false;
        this.firstNameTouched = false;
        this.lastNameTouched = false;
        this.middleNameTouched = false;
        this.experienceTouched = false;

        // Для множественного выбора специализаций
        this.selectedSpecializations = [];
        this.allSpecializations = [];

        // Для тултипов
        this.hoverTooltips = new Map();
        this.requirementTooltips = new Map();
        this.currentFocusedField = null;
        this.hoverTimeout = null;
        this.hoverTooltipElement = null;
        this.currentTooltip = null;

        console.log('RegisterApp инициализирован');
    }

    init() {
        console.log('Инициализация страницы регистрации...');

        // Собираем все специализации из чекбоксов
        const checkboxes = document.querySelectorAll('.dropdown-option input[type="checkbox"]');
        checkboxes.forEach(cb => {
            this.allSpecializations.push(cb.value);
            if (cb.checked) {
                this.selectedSpecializations.push(cb.value);
            }
        });

        // Обновляем отображение в поле
        this.updateInputValue();

        // Инициализация множественного выбора
        this.initMultiSelect();

        // Обработка отправки формы
        if (this.submitBtn) {
            this.submitBtn.addEventListener('click', (e) => this.handleSubmit(e));
        }

        if (this.registerForm) {
            this.registerForm.addEventListener('submit', (e) => {
                if (!this.validateForm(true)) {
                    e.preventDefault();
                }
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

        // При скролле скрываем тултипы
        window.addEventListener('scroll', () => {
            this.hideAllTooltips();
        });

        // При изменении размера окна скрываем тултипы
        window.addEventListener('resize', () => {
            this.hideAllTooltips();
        });

        console.log('Инициализация завершена');
    }

    initMultiSelect() {
        const container = document.querySelector('.multi-select-container');
        const input = this.specializationInput;
        const dropdown = document.getElementById('specializationDropdown');
        const searchInput = document.getElementById('dropdownSearchInput');
        const optionsContainer = document.getElementById('dropdownOptions');

        if (!container || !input || !dropdown) return;

        // Открытие/закрытие dropdown
        input.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = dropdown.classList.contains('show');
            // Закрываем все другие dropdown
            document.querySelectorAll('.multi-select-dropdown').forEach(d => d.classList.remove('show'));
            document.querySelectorAll('.multi-select-container').forEach(c => c.classList.remove('open'));

            if (!isOpen) {
                dropdown.classList.add('show');
                container.classList.add('open');
                setTimeout(() => {
                    if (searchInput) searchInput.focus();
                }, 100);
            } else {
                dropdown.classList.remove('show');
                container.classList.remove('open');
            }
        });

        // Поиск в dropdown (если есть)
        if (searchInput) {
            searchInput.addEventListener('input', () => {
                const searchTerm = searchInput.value.toLowerCase();
                const options = optionsContainer.querySelectorAll('.dropdown-option');
                options.forEach(option => {
                    const text = option.querySelector('span').textContent.toLowerCase();
                    option.style.display = text.includes(searchTerm) ? 'flex' : 'none';
                });
            });
        }

        // Обработка выбора чекбоксов
        if (optionsContainer) {
            optionsContainer.addEventListener('change', (e) => {
                if (e.target.type === 'checkbox') {
                    if (e.target.checked) {
                        if (!this.selectedSpecializations.includes(e.target.value)) {
                            this.selectedSpecializations.push(e.target.value);
                        }
                    } else {
                        this.selectedSpecializations = this.selectedSpecializations.filter(
                            item => item !== e.target.value
                        );
                    }
                    this.updateInputValue();
                }
            });
        }

        // Закрытие dropdown при клике вне
        document.addEventListener('click', (e) => {
            if (!container.contains(e.target)) {
                dropdown.classList.remove('show');
                container.classList.remove('open');
            }
        });
    }

    updateInputValue() {
        if (this.specializationInput) {
            this.specializationInput.value = this.selectedSpecializations.join(', ');
            if (this.specializationInput.value === '') {
                this.specializationInput.placeholder = 'Выберите предметы (необязательно)...';
            }
        }
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
                switch(fieldId) {
                    case 'email': inputElement = this.emailInput; break;
                    case 'password': inputElement = this.passwordInput; break;
                    case 'confirm_password': inputElement = this.confirmPasswordInput; break;
                    case 'first_name': inputElement = this.firstNameInput; break;
                    case 'last_name': inputElement = this.lastNameInput; break;
                    case 'middle_name': inputElement = this.middleNameInput; break;
                    case 'experience': inputElement = this.experienceInput; break;
                    default: return;
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
                if (this.confirmPasswordInput && this.confirmPasswordInput.value) {
                    this.validateConfirmPassword(false);
                }
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

        // Подтверждение пароля
        if (this.confirmPasswordInput) {
            this.confirmPasswordInput.addEventListener('input', () => {
                this.clearError('confirmPasswordError');
                this.validateConfirmPassword(false);
                this.updateConfirmPasswordRequirements();
            });

            this.confirmPasswordInput.addEventListener('blur', () => {
                this.confirmPasswordTouched = true;
                if (this.confirmPasswordInput.value !== '') {
                    this.validateConfirmPassword(true);
                } else {
                    this.clearError('confirmPasswordError');
                }
            });
        }

        // Имя
        if (this.firstNameInput) {
            this.firstNameInput.addEventListener('input', () => {
                this.clearError('firstNameError');
                this.validateFirstName(false);
                this.updateNameRequirements('first_name', this.firstNameInput, 'Имя');
            });

            this.firstNameInput.addEventListener('blur', () => {
                this.firstNameTouched = true;
                if (this.firstNameInput.value.trim() !== '') {
                    this.validateFirstName(true);
                } else {
                    this.clearError('firstNameError');
                }
            });
        }

        // Фамилия
        if (this.lastNameInput) {
            this.lastNameInput.addEventListener('input', () => {
                this.clearError('lastNameError');
                this.validateLastName(false);
                this.updateNameRequirements('last_name', this.lastNameInput, 'Фамилия');
            });

            this.lastNameInput.addEventListener('blur', () => {
                this.lastNameTouched = true;
                if (this.lastNameInput.value.trim() !== '') {
                    this.validateLastName(true);
                } else {
                    this.clearError('lastNameError');
                }
            });
        }

        // Отчество (необязательное)
        if (this.middleNameInput) {
            this.middleNameInput.addEventListener('input', () => {
                this.clearError('middleNameError');
                this.validateMiddleName(false);
            });

            this.middleNameInput.addEventListener('blur', () => {
                this.middleNameTouched = true;
                if (this.middleNameInput.value.trim() !== '') {
                    this.validateMiddleName(true);
                } else {
                    this.clearError('middleNameError');
                }
            });
        }

        // Образовательное учреждение (необязательное)
        if (this.educationalInstitutionInput) {
            this.educationalInstitutionInput.addEventListener('input', () => {
                this.clearError('educationalInstitutionError');
            });
        }

        // Опыт работы
        if (this.experienceInput) {
            this.experienceInput.addEventListener('input', () => {
                this.clearError('experienceError');
                this.validateExperience(false);
            });

            this.experienceInput.addEventListener('blur', () => {
                this.experienceTouched = true;
                if (this.experienceInput.value.trim() !== '') {
                    this.validateExperience(true);
                } else {
                    this.clearError('experienceError');
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
            if (!this.hoverTooltipElement || this.hoverTooltipElement !== element) {
                return;
            }

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

            // Корректируем позицию по горизонтали
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
                    if (tooltip.parentNode) {
                        tooltip.remove();
                    }
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
                    if (tooltip.parentNode) {
                        tooltip.remove();
                    }
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
            },
            'confirm_password': {
                element: this.confirmPasswordInput,
                config: {
                    title: 'Подтверждение пароля:',
                    requirements: [
                        { type: 'match', text: 'Пароли должны совпадать' }
                    ]
                }
            },
            'first_name': {
                element: this.firstNameInput,
                config: {
                    title: 'Требования к имени:',
                    requirements: [
                        { type: 'required', text: 'Обязательное поле' },
                        { type: 'russian', text: 'Только русские буквы' },
                        { type: 'max', text: 'Максимум 30 символов' },
                        { type: 'example', text: 'Пример: Иван' }
                    ]
                }
            },
            'last_name': {
                element: this.lastNameInput,
                config: {
                    title: 'Требования к фамилии:',
                    requirements: [
                        { type: 'required', text: 'Обязательное поле' },
                        { type: 'russian', text: 'Только русские буквы' },
                        { type: 'max', text: 'Максимум 30 символов' },
                        { type: 'example', text: 'Пример: Иванов' }
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
            const isValid = req.type === 'example' ? true :
                          this.checkRequirement(fieldId, req.type, inputElement.value);
            const icon = req.type === 'example' ? 'lightbulb' :
                       (isValid ? 'check' : 'circle');
            const statusClass = req.type === 'example' ? 'example' :
                              (isValid ? 'valid' : 'invalid');

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
                if (requirements.dataset.hovering === 'false' &&
                    document.activeElement !== inputElement) {
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

    updateConfirmPasswordRequirements() {
        if (this.requirementTooltips.has('confirm_password') && this.confirmPasswordInput) {
            const isValid = this.checkConfirmPassword();
            const requirements = this.requirementTooltips.get('confirm_password');
            if (requirements) {
                const reqElement = requirements.querySelector('.requirement');
                if (reqElement) {
                    reqElement.className = `requirement match ${isValid ? 'valid' : 'invalid'}`;
                    reqElement.innerHTML = `
                        <i class="fas fa-${isValid ? 'check' : 'circle'}"></i>
                        <span>Пароли должны совпадать</span>
                    `;
                }
            }
        }
    }

    updateNameRequirements(fieldId, inputElement, fieldName) {
        if (this.requirementTooltips.has(fieldId) && inputElement) {
            this.updateDynamicRequirements(fieldId, inputElement, {
                title: `Требования к ${fieldName.toLowerCase()}:`,
                requirements: [
                    { type: 'required', text: 'Обязательное поле' },
                    { type: 'russian', text: 'Только русские буквы' },
                    { type: 'max', text: 'Максимум 30 символов' },
                    { type: 'example', text: `Пример: ${fieldName === 'Имя' ? 'Иван' : 'Иванов'}` }
                ]
            });
        }
    }

    checkRequirement(fieldId, type, value) {
        switch (type) {
            case 'required':
                return value.trim().length > 0;
            case 'max':
                return value.length <= 30;
            case 'length':
                return value.length >= 6;
            case 'chars':
                return /^[A-Za-z0-9!@#$%^&*]*$/.test(value);
            case 'format':
                return value === '' || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
            case 'domain':
                return value === '' || /@.+\..+/.test(value);
            case 'russian':
                return /^[А-Яа-яЁё\s\-]*$/.test(value);
            case 'match':
                return this.checkConfirmPassword();
            default:
                return true;
        }
    }

    checkConfirmPassword() {
        const password = this.passwordInput ? this.passwordInput.value : '';
        const confirm = this.confirmPasswordInput ? this.confirmPasswordInput.value : '';
        return password === confirm;
    }

    hideRequirements(fieldId) {
        if (this.requirementTooltips.has(fieldId)) {
            const tooltip = this.requirementTooltips.get(fieldId);
            if (tooltip && tooltip.parentNode) {
                tooltip.style.opacity = '0';
                setTimeout(() => {
                    if (tooltip.parentNode) {
                        tooltip.remove();
                    }
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
                    if (tooltip.parentNode) {
                        tooltip.remove();
                    }
                }, 150);
            }
        });
        this.requirementTooltips.clear();
        this.currentFocusedField = null;
        clearTimeout(this.hoverTimeout);
    }

    clearError(errorElementId) {
        const errorElement = document.getElementById(errorElementId);
        if (errorElement) {
            errorElement.textContent = '';
        }
    }

    setError(errorElementId, message) {
        const errorElement = document.getElementById(errorElementId);
        if (errorElement) {
            errorElement.textContent = message;
        }
    }

    validateEmail(showError = false) {
        const email = this.emailInput ? this.emailInput.value.trim() : '';

        if (!email) {
            if (showError && this.emailTouched) {
                this.setError('emailError', 'Введите email');
            }
            return false;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            if (showError) {
                this.setError('emailError', 'Введите корректный email адрес');
            }
            return false;
        }

        if (email.length > 30) {
            if (showError) {
                this.setError('emailError', 'Email не должен превышать 30 символов');
            }
            return false;
        }

        return true;
    }

    validatePassword(showError = false) {
        const password = this.passwordInput ? this.passwordInput.value : '';

        if (!password) {
            if (showError && this.passwordTouched) {
                this.setError('passwordError', 'Введите пароль');
            }
            return false;
        }

        if (password.length < 6) {
            if (showError) {
                this.setError('passwordError', 'Пароль должен содержать минимум 6 символов');
            }
            return false;
        }

        if (password.length > 30) {
            if (showError) {
                this.setError('passwordError', 'Пароль не должен превышать 30 символов');
            }
            return false;
        }

        return true;
    }

    validateConfirmPassword(showError = false) {
        const password = this.passwordInput ? this.passwordInput.value : '';
        const confirm = this.confirmPasswordInput ? this.confirmPasswordInput.value : '';

        if (!confirm) {
            if (showError && this.confirmPasswordTouched) {
                this.setError('confirmPasswordError', 'Подтвердите пароль');
            }
            return false;
        }

        if (password !== confirm) {
            if (showError) {
                this.setError('confirmPasswordError', 'Пароли не совпадают');
            }
            return false;
        }

        return true;
    }

    validateFirstName(showError = false) {
        const name = this.firstNameInput ? this.firstNameInput.value.trim() : '';

        if (!name) {
            if (showError && this.firstNameTouched) {
                this.setError('firstNameError', 'Введите имя');
            }
            return false;
        }

        if (!/^[А-Яа-яЁё\s\-]+$/.test(name)) {
            if (showError) {
                this.setError('firstNameError', 'Только русские буквы, дефисы и пробелы');
            }
            return false;
        }

        if (name.length > 30) {
            if (showError) {
                this.setError('firstNameError', 'Имя не должно превышать 30 символов');
            }
            return false;
        }

        return true;
    }

    validateLastName(showError = false) {
        const name = this.lastNameInput ? this.lastNameInput.value.trim() : '';

        if (!name) {
            if (showError && this.lastNameTouched) {
                this.setError('lastNameError', 'Введите фамилию');
            }
            return false;
        }

        if (!/^[А-Яа-яЁё\s\-]+$/.test(name)) {
            if (showError) {
                this.setError('lastNameError', 'Только русские буквы, дефисы и пробелы');
            }
            return false;
        }

        if (name.length > 30) {
            if (showError) {
                this.setError('lastNameError', 'Фамилия не должна превышать 30 символов');
            }
            return false;
        }

        return true;
    }

    validateMiddleName(showError = false) {
        const name = this.middleNameInput ? this.middleNameInput.value.trim() : '';

        if (!name) return true;

        if (!/^[А-Яа-яЁё\s\-]+$/.test(name)) {
            if (showError) {
                this.setError('middleNameError', 'Только русские буквы, дефисы и пробелы');
            }
            return false;
        }

        if (name.length > 30) {
            if (showError) {
                this.setError('middleNameError', 'Отчество не должно превышать 30 символов');
            }
            return false;
        }

        return true;
    }

    validateExperience(showError = false) {
        const value = this.experienceInput ? this.experienceInput.value.trim() : '';

        if (!value) return true;

        const num = parseInt(value);
        if (isNaN(num) || num < 0 || num > 100) {
            if (showError) {
                this.setError('experienceError', 'Стаж должен быть от 0 до 100 лет');
            }
            return false;
        }

        return true;
    }

    validateForm(showErrors = false) {
        let isValid = true;

        if (!this.validateEmail(showErrors)) isValid = false;
        if (!this.validatePassword(showErrors)) isValid = false;
        if (!this.validateConfirmPassword(showErrors)) isValid = false;
        if (!this.validateFirstName(showErrors)) isValid = false;
        if (!this.validateLastName(showErrors)) isValid = false;

        this.validateMiddleName(showErrors);
        this.validateExperience(showErrors);

        return isValid;
    }

    handleSubmit(e) {
        if (e) e.preventDefault();

        this.hideAllTooltips();

        this.emailTouched = true;
        this.passwordTouched = true;
        this.confirmPasswordTouched = true;
        this.firstNameTouched = true;
        this.lastNameTouched = true;
        this.middleNameTouched = true;
        this.experienceTouched = true;

        if (!this.validateForm(true)) {
            const firstError = document.querySelector('.form-error:not(:empty)');
            if (firstError) {
                firstError.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
            }
            return;
        }

        // Обновляем скрытые инпуты перед отправкой (только если есть выбранные специализации)
        const container = document.querySelector('.multi-select-container');
        if (container) {
            const existingHidden = container.querySelectorAll('input[type="hidden"]');
            existingHidden.forEach(h => h.remove());

            this.selectedSpecializations.forEach(value => {
                const hidden = document.createElement('input');
                hidden.type = 'hidden';
                hidden.name = 'specializations';
                hidden.value = value;
                container.appendChild(hidden);
            });
        }

        if (this.registerForm) {
            this.showLoading();
            this.registerForm.submit();
        }
    }

    showLoading() {
        if (this.submitBtn) {
            this.submitBtn.disabled = true;
            this.submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Регистрация...</span>';
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    try {
        window.registerApp = new RegisterApp();
        window.registerApp.init();
        console.log('Приложение регистрации успешно инициализировано');
    } catch (error) {
        console.error('Ошибка при инициализации приложения регистрации:', error);
    }
});