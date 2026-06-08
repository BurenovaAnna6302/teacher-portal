// profile.js - Полная версия с валидацией, тултипами, работой с фото и множественным выбором специализаций
// Версия: 3.1 - Исправлено отображение выбранных специализаций

class ProfileApp {
    constructor() {
        // Основные поля
        this.emailInput = document.getElementById('email');
        this.lastNameInput = document.getElementById('last_name');
        this.firstNameInput = document.getElementById('first_name');
        this.middleNameInput = document.getElementById('middle_name');
        this.educationalInstitutionInput = document.getElementById('educational_institution');
        this.experienceInput = document.getElementById('experience');
        this.specializationInput = document.getElementById('specializationInput');

        // Кнопка и форма
        this.saveBtn = document.getElementById('saveProfileBtn');
        this.profileForm = document.getElementById('profileForm');

        // Элементы ошибок
        this.emailError = document.getElementById('emailError');
        this.lastNameError = document.getElementById('lastNameError');
        this.firstNameError = document.getElementById('firstNameError');
        this.middleNameError = document.getElementById('middleNameError');
        this.educationalInstitutionError = document.getElementById('educationalInstitutionError');
        this.experienceError = document.getElementById('experienceError');
        this.specializationsError = document.getElementById('specializationsError');

        // Элементы фото
        this.photoInput = document.getElementById('photoInput');
        this.uploadPhotoBtn = document.getElementById('uploadPhotoBtn');
        this.removePhotoBtn = document.getElementById('removePhotoBtn');
        this.photoPreview = document.getElementById('photoPreview');
        this.initialsElement = document.getElementById('initials');

        // Для множественного выбора специализаций
        this.selectedSpecializations = [];
        this.allSpecializations = window.allSpecializations || [];

        // Сообщение об успехе
        this.successMessage = document.getElementById('profileSuccessMessage');

        // Для тултипов
        this.hoverTooltips = new Map();
        this.requirementTooltips = new Map();
        this.currentFocusedField = null;
        this.hoverTimeout = null;
        this.hoverTooltipElement = null;

        // CSRF токен
        this.csrfToken = this.getCsrfToken();

        console.log('ProfileApp инициализирован');
    }

    init() {
        console.log('Инициализация страницы профиля...');

        // Загружаем выбранные специализации из данных пользователя
        if (window.userData && window.userData.specializations) {
            this.selectedSpecializations = [...window.userData.specializations];
            console.log('Загружены специализации:', this.selectedSpecializations);
        }

        // Инициализация множественного выбора
        this.initMultiSelect();

        // Обновляем отображение в поле
        this.updateInputValue();

        // Обновляем чекбоксы в dropdown
        this.updateCheckboxes();

        // Обработка отправки формы
        if (this.profileForm) {
            this.profileForm.addEventListener('submit', (e) => this.handleSubmit(e));
        }

        // Кнопка загрузки фото
        if (this.uploadPhotoBtn) {
            this.uploadPhotoBtn.addEventListener('click', () => {
                this.photoInput.click();
            });
        }

        // Изменение фото
        if (this.photoInput) {
            this.photoInput.addEventListener('change', (e) => this.handlePhotoChange(e));
        }

        // Удаление фото
        if (this.removePhotoBtn) {
            this.removePhotoBtn.addEventListener('click', () => this.removePhoto());
        }

        // Настройка валидации полей
        this.setupFieldValidation();

        // Настройка тултипов при наведении
        this.setupHoverTooltips();

        // Настройка подсказок при фокусе
        this.setupFocusRequirements();

        // Обновление инициалов при изменении имени
        if (this.firstNameInput && this.lastNameInput && this.initialsElement) {
            this.firstNameInput.addEventListener('input', () => this.updateInitials());
            this.lastNameInput.addEventListener('input', () => this.updateInitials());
        }

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
            if (this.selectedSpecializations.length > 0) {
                this.specializationInput.value = this.selectedSpecializations.join(', ');
            } else {
                this.specializationInput.value = '';
                this.specializationInput.placeholder = 'Выберите предметы (необязательно)...';
            }
        }
    }

    updateCheckboxes() {
        const checkboxes = document.querySelectorAll('.dropdown-option input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.checked = this.selectedSpecializations.includes(checkbox.value);
        });
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
                    case 'last_name': inputElement = this.lastNameInput; break;
                    case 'first_name': inputElement = this.firstNameInput; break;
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
                this.validateEmail();
                this.updateEmailRequirements();
            });
            this.emailInput.addEventListener('blur', () => this.validateEmail(true));
        }

        // Фамилия
        if (this.lastNameInput) {
            this.lastNameInput.addEventListener('input', () => {
                this.clearError('lastNameError');
                this.validateName('lastName', this.lastNameInput);
                this.updateNameRequirements('last_name');
            });
            this.lastNameInput.addEventListener('blur', () => this.validateName('lastName', this.lastNameInput, true));
        }

        // Имя
        if (this.firstNameInput) {
            this.firstNameInput.addEventListener('input', () => {
                this.clearError('firstNameError');
                this.validateName('firstName', this.firstNameInput);
                this.updateNameRequirements('first_name');
            });
            this.firstNameInput.addEventListener('blur', () => this.validateName('firstName', this.firstNameInput, true));
        }

        // Отчество
        if (this.middleNameInput) {
            this.middleNameInput.addEventListener('input', () => {
                this.clearError('middleNameError');
                this.validateName('middleName', this.middleNameInput, false);
                this.updateNameRequirements('middle_name');
            });
            this.middleNameInput.addEventListener('blur', () => this.validateName('middleName', this.middleNameInput, false, true));
        }

        // Стаж
        if (this.experienceInput) {
            this.experienceInput.addEventListener('input', () => {
                this.clearError('experienceError');
                this.validateExperience();
                this.updateExperienceRequirements();
            });
            this.experienceInput.addEventListener('blur', () => this.validateExperience(true));
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
            'last_name': {
                element: this.lastNameInput,
                config: {
                    title: 'Требования к фамилии:',
                    requirements: [
                        { type: 'cyrillic', text: 'Только русские буквы' },
                        { type: 'hyphen', text: 'Можно использовать дефис (-)' },
                        { type: 'max', text: 'Максимум 30 символов' },
                        { type: 'capital', text: 'Первая буква заглавная' },
                        { type: 'example', text: 'Пример: Иванов или Петров-Водкин' }
                    ]
                }
            },
            'first_name': {
                element: this.firstNameInput,
                config: {
                    title: 'Требования к имени:',
                    requirements: [
                        { type: 'cyrillic', text: 'Только русские буквы' },
                        { type: 'hyphen', text: 'Можно использовать дефис (-)' },
                        { type: 'max', text: 'Максимум 30 символов' },
                        { type: 'capital', text: 'Первая буква заглавная' },
                        { type: 'example', text: 'Пример: Иван или Анна-Мария' }
                    ]
                }
            },
            'middle_name': {
                element: this.middleNameInput,
                config: {
                    title: 'Требования к отчеству:',
                    requirements: [
                        { type: 'cyrillic', text: 'Только русские буквы' },
                        { type: 'hyphen', text: 'Можно использовать дефис (-)' },
                        { type: 'max', text: 'Максимум 30 символов' },
                        { type: 'capital', text: 'Первая буква заглавная' },
                        { type: 'optional', text: 'Можно не заполнять' }
                    ]
                }
            },
            'experience': {
                element: this.experienceInput,
                config: {
                    title: 'Требования к стажу:',
                    requirements: [
                        { type: 'integer', text: 'Только целые числа' },
                        { type: 'range', text: 'От 0 до 100 лет' },
                        { type: 'example', text: 'Пример: 5 (лет)' },
                        { type: 'optional', text: 'Можно не заполнять' }
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
            const isValid = req.type === 'example' || req.type === 'optional' ? true :
                          this.checkRequirement(fieldId, req.type, inputElement.value);
            const icon = req.type === 'example' ? 'lightbulb' :
                       req.type === 'optional' ? 'info-circle' :
                       (isValid ? 'check' : 'circle');
            const statusClass = req.type === 'example' ? 'example' :
                              req.type === 'optional' ? 'optional' :
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
            if (req.type !== 'example' && req.type !== 'optional') {
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

    updateNameRequirements(fieldId) {
        let config;
        let inputElement;

        switch(fieldId) {
            case 'last_name':
                config = {
                    title: 'Требования к фамилии:',
                    requirements: [
                        { type: 'cyrillic', text: 'Только русские буквы' },
                        { type: 'hyphen', text: 'Можно использовать дефис (-)' },
                        { type: 'max', text: 'Максимум 30 символов' },
                        { type: 'capital', text: 'Первая буква заглавная' },
                        { type: 'example', text: 'Пример: Иванов или Петров-Водкин' }
                    ]
                };
                inputElement = this.lastNameInput;
                break;
            case 'first_name':
                config = {
                    title: 'Требования к имени:',
                    requirements: [
                        { type: 'cyrillic', text: 'Только русские буквы' },
                        { type: 'hyphen', text: 'Можно использовать дефис (-)' },
                        { type: 'max', text: 'Максимум 30 символов' },
                        { type: 'capital', text: 'Первая буква заглавная' },
                        { type: 'example', text: 'Пример: Иван или Анна-Мария' }
                    ]
                };
                inputElement = this.firstNameInput;
                break;
            case 'middle_name':
                config = {
                    title: 'Требования к отчеству:',
                    requirements: [
                        { type: 'cyrillic', text: 'Только русские буквы' },
                        { type: 'hyphen', text: 'Можно использовать дефис (-)' },
                        { type: 'max', text: 'Максимум 30 символов' },
                        { type: 'capital', text: 'Первая буква заглавная' },
                        { type: 'optional', text: 'Можно не заполнять' }
                    ]
                };
                inputElement = this.middleNameInput;
                break;
        }

        if (this.requirementTooltips.has(fieldId) && inputElement) {
            this.updateDynamicRequirements(fieldId, inputElement, config);
        }
    }

    updateExperienceRequirements() {
        if (this.requirementTooltips.has('experience') && this.experienceInput) {
            this.updateDynamicRequirements('experience', this.experienceInput, {
                title: 'Требования к стажу:',
                requirements: [
                    { type: 'integer', text: 'Только целые числа' },
                    { type: 'range', text: 'От 0 до 100 лет' },
                    { type: 'example', text: 'Пример: 5 (лет)' },
                    { type: 'optional', text: 'Можно не заполнять' }
                ]
            });
        }
    }

    checkRequirement(fieldId, type, value) {
        switch (type) {
            case 'format':
                return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) || value === '';
            case 'max':
                return value.length <= 30;
            case 'domain':
                return /@.+\..+/.test(value) || value === '';
            case 'cyrillic':
                return /^[А-Яа-яЁё\s\-]*$/.test(value);
            case 'hyphen':
                return /^[А-Яа-яЁё\-]+$/.test(value) || value === '';
            case 'capital':
                return value === '' || /^[А-ЯЁ]/.test(value);
            case 'range':
                if (value === '') return true;
                const num = parseInt(value);
                return !isNaN(num) && num >= 0 && num <= 100;
            case 'integer':
                return value === '' || /^\d+$/.test(value);
            default:
                return true;
        }
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

    validateEmail(fullValidation = false) {
        const email = this.emailInput.value.trim();

        if (!email && !fullValidation) {
            return false;
        }

        if (!email) {
            this.setError('emailError', 'Введите email');
            return false;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            this.setError('emailError', 'Введите корректный email адрес');
            return false;
        }

        if (email.length > 30) {
            this.setError('emailError', 'Email не должен превышать 30 символов');
            return false;
        }

        return true;
    }

    validateName(fieldName, inputElement, required = true, fullValidation = false) {
        const value = inputElement.value.trim();

        if (!required && !value) {
            return true;
        }

        if (!value && !fullValidation) {
            return false;
        }

        if (!value) {
            this.setError(fieldName + 'Error', 'Это поле обязательно для заполнения');
            return false;
        }

        const nameRegex = /^[А-Яа-яЁё\s\-]+$/;
        if (!nameRegex.test(value)) {
            this.setError(fieldName + 'Error', 'Только русские буквы, дефисы и пробелы');
            return false;
        }

        if (value.length > 30) {
            this.setError(fieldName + 'Error', 'Не более 30 символов');
            return false;
        }

        return true;
    }

    validateExperience(fullValidation = false) {
        const value = this.experienceInput.value.trim();

        if (!value) {
            return true;
        }

        const experience = parseInt(value);

        if (isNaN(experience)) {
            this.setError('experienceError', 'Введите число от 0 до 100');
            return false;
        }

        if (experience < 0) {
            this.setError('experienceError', 'Стаж не может быть отрицательным');
            return false;
        }

        if (experience > 100) {
            this.setError('experienceError', 'Стаж не может превышать 100 лет');
            return false;
        }

        return true;
    }

    handlePhotoChange(e) {
        const file = e.target.files[0];
        if (!file) return;

        const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
        if (!validTypes.includes(file.type)) {
            alert('Пожалуйста, выберите файл изображения (JPG, PNG)');
            this.photoInput.value = '';
            return;
        }

        if (file.size > 5 * 1024 * 1024) {
            alert('Размер файла не должен превышать 5MB');
            this.photoInput.value = '';
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const placeholder = this.photoPreview.querySelector('.profile-photo-placeholder');
            if (placeholder) {
                placeholder.style.display = 'none';
            }

            let img = this.photoPreview.querySelector('img');
            if (!img) {
                img = document.createElement('img');
                img.className = 'profile-photo-image';
                this.photoPreview.appendChild(img);
            }
            img.src = e.target.result;
            img.style.display = 'block';

            if (this.removePhotoBtn) {
                this.removePhotoBtn.style.display = 'block';
            }
        };
        reader.readAsDataURL(file);
    }

    removePhoto() {
        if (confirm('Вы уверены, что хотите удалить фото профиля?')) {
            let removeField = document.getElementById('removePhotoField');
            if (!removeField) {
                removeField = document.createElement('input');
                removeField.type = 'hidden';
                removeField.name = 'remove_photo';
                removeField.id = 'removePhotoField';
                removeField.value = 'true';
                this.profileForm.appendChild(removeField);
            } else {
                removeField.value = 'true';
            }

            this.photoInput.value = '';

            const img = this.photoPreview.querySelector('img');
            if (img) {
                img.remove();
            }

            const placeholder = this.photoPreview.querySelector('.profile-photo-placeholder');
            if (placeholder) {
                placeholder.style.display = 'flex';
                this.updateInitials();
            }

            if (this.removePhotoBtn) {
                this.removePhotoBtn.style.display = 'none';
            }
        }
    }

    updateInitials() {
        const firstName = document.getElementById('first_name')?.value || '';
        const lastName = document.getElementById('last_name')?.value || '';
        const initials = (firstName[0] || '') + (lastName[0] || '');

        const initialsElement = document.getElementById('initials');
        if (initialsElement) {
            initialsElement.textContent = initials || '?';
        }

        const sidebarInitials = document.getElementById('sidebarInitials');
        if (sidebarInitials) {
            sidebarInitials.textContent = initials || '?';
        }

        const headerInitials = document.getElementById('headerInitials');
        if (headerInitials) {
            headerInitials.textContent = initials || 'П';
        }

        const mobileInitials = document.getElementById('mobileInitials');
        if (mobileInitials) {
            mobileInitials.textContent = initials || 'П';
        }
    }

    showLoading() {
        if (this.saveBtn) {
            this.saveBtn.disabled = true;
            this.saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Сохранение...';
        }
    }

    hideLoading() {
        if (this.saveBtn) {
            this.saveBtn.disabled = false;
            this.saveBtn.innerHTML = '<i class="fas fa-save"></i> Сохранить изменения';
        }
    }

    showSuccessMessage() {
        if (this.successMessage) {
            this.successMessage.style.display = 'flex';
            setTimeout(() => {
                this.successMessage.classList.add('show');
            }, 10);

            setTimeout(() => {
                this.successMessage.classList.remove('show');
                setTimeout(() => {
                    this.successMessage.style.display = 'none';
                }, 300);
            }, 3000);
        }
    }

    getCsrfToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue;
    }

    async handleSubmit(e) {
        e.preventDefault();

        this.hideAllTooltips();

        this.showLoading();

        try {
            const formData = new FormData(this.profileForm);

            // Добавляем выбранные специализации
            this.selectedSpecializations.forEach(value => {
                formData.append('specializations', value);
            });

            const response = await fetch(window.location.pathname, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                if (data.photo_url) {
                    this.updateAvatar(data.photo_url);
                } else {
                    this.updateAvatar(null);
                }

                this.showSuccessMessage();

                const removeField = document.getElementById('removePhotoField');
                if (removeField) {
                    removeField.remove();
                }

                console.log('Профиль успешно сохранен');
            } else {
                throw new Error(data.message || 'Ошибка сохранения');
            }

        } catch (error) {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при сохранении. Попробуйте еще раз.');
        } finally {
            this.hideLoading();
        }
    }

    updateAvatar(photoUrl) {
        const headerAvatar = document.querySelector('#headerAvatar');
        if (headerAvatar) {
            if (photoUrl) {
                headerAvatar.innerHTML = `<img src="${photoUrl}" alt="Avatar" style="width: 32px; height: 32px; border-radius: 50%; object-fit: cover;">`;
            } else {
                const firstName = document.getElementById('first_name')?.value || '';
                const lastName = document.getElementById('last_name')?.value || '';
                const initials = (firstName[0] || '') + (lastName[0] || '') || 'П';
                headerAvatar.innerHTML = `<span id="headerInitials">${initials}</span>`;
            }
        }

        const sidebarAvatar = document.querySelector('#sidebarAvatar');
        if (sidebarAvatar) {
            if (photoUrl) {
                sidebarAvatar.innerHTML = `<img src="${photoUrl}" alt="Avatar" style="width: 60px; height: 60px; border-radius: 50%; object-fit: cover;">`;
            } else {
                const firstName = document.getElementById('first_name')?.value || '';
                const lastName = document.getElementById('last_name')?.value || '';
                const initials = (firstName[0] || '') + (lastName[0] || '') || '?';
                sidebarAvatar.innerHTML = `<span id="sidebarInitials">${initials}</span>`;
            }
        }

        const mobileAvatar = document.querySelector('#mobileAvatar');
        if (mobileAvatar) {
            if (photoUrl) {
                mobileAvatar.innerHTML = `<img src="${photoUrl}" alt="Avatar" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;">`;
            } else {
                const firstName = document.getElementById('first_name')?.value || '';
                const lastName = document.getElementById('last_name')?.value || '';
                const initials = (firstName[0] || '') + (lastName[0] || '') || 'П';
                mobileAvatar.innerHTML = `<span id="mobileInitials">${initials}</span>`;
            }
        }
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    window.profileApp = new ProfileApp();
    window.profileApp.init();
});