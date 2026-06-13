// surveys.js - Функциональность страницы опросников с AJAX
// Версия: 3.2 - Исправлена обработка фильтров и пагинации

class SurveysApp {
    constructor(config) {
        this.surveys = config.surveys || [];
        this.categories = config.categories;
        this.durations = config.durations;
        this.statuses = config.statuses;
        this.itemsPerPage = config.itemsPerPage || 12;
        this.currentPage = config.currentPage || 1;
        this.totalPages = config.totalPages || 1;

        this.filters = {
            category: [],
            duration: [],
            status: []
        };

        this.loading = false;
        this.initialized = false;
    }

    async init() {
        if (this.initialized) return;

        console.log('🚀 Инициализация приложения опросников с AJAX...');

        this.initFilters();
        this.initPagination();
        this.initMobileFilters();

        // Рендерим опросы из переданных данных
        this.renderSurveys(this.surveys);
        this.updatePagination();

        this.initialized = true;
        console.log('✅ Приложение опросников инициализировано');
    }

    // Функция для прокрутки наверх страницы
    scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }

    initFilters() {
        document.querySelectorAll('.filter-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', async (e) => {
                const category = e.target.dataset.category;
                const value = e.target.value;

                if (e.target.checked) {
                    if (!this.filters[category].includes(value)) {
                        this.filters[category].push(value);
                    }
                } else {
                    this.filters[category] = this.filters[category].filter(v => v !== value);
                }

                console.log('Фильтры после изменения:', this.filters);

                this.currentPage = 1;
                await this.loadSurveys();
                this.updateFilterStyles();
                // Прокрутка наверх после применения фильтров
                this.scrollToTop();
            });
        });

        document.getElementById('clearAllFilters')?.addEventListener('click', () => this.clearAllFilters());
    }

    initPagination() {
        document.getElementById('prevPage')?.addEventListener('click', async () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                await this.loadSurveys();
                // Прокрутка наверх при смене страницы
                this.scrollToTop();
            }
        });

        document.getElementById('nextPage')?.addEventListener('click', async () => {
            if (this.currentPage < this.totalPages) {
                this.currentPage++;
                await this.loadSurveys();
                // Прокрутка наверх при смене страницы
                this.scrollToTop();
            }
        });

        document.addEventListener('click', async (e) => {
            if (e.target.classList.contains('pagination-page')) {
                const page = parseInt(e.target.dataset.page);
                if (page && page !== this.currentPage) {
                    this.currentPage = page;
                    await this.loadSurveys();
                    // Прокрутка наверх при смене страницы
                    this.scrollToTop();
                }
            }
        });
    }

    initMobileFilters() {
        const openBtn = document.getElementById('openFiltersModal');
        const closeBtn = document.getElementById('closeFiltersModal');
        const modal = document.getElementById('mobileFiltersModal');
        const applyBtn = document.getElementById('applyMobileFilters');
        const resetBtn = document.getElementById('resetMobileFilters');

        if (openBtn && modal) {
            openBtn.addEventListener('click', () => {
                this.populateMobileFilters();
                modal.classList.add('active');
                document.body.style.overflow = 'hidden';
            });
        }

        if (closeBtn && modal) {
            closeBtn.addEventListener('click', () => {
                modal.classList.remove('active');
                document.body.style.overflow = '';
            });
        }

        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target.classList.contains('modal-overlay')) {
                    modal.classList.remove('active');
                    document.body.style.overflow = '';
                }
            });
        }

        if (applyBtn) {
            applyBtn.addEventListener('click', async () => {
                this.applyMobileFilters();
                modal.classList.remove('active');
                document.body.style.overflow = '';
                this.currentPage = 1;
                await this.loadSurveys();
                // Прокрутка наверх после применения фильтров из модального окна
                this.scrollToTop();
            });
        }

        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.clearMobileFilters();
            });
        }
    }

    async loadSurveys() {
        if (this.loading) return;

        this.loading = true;
        const surveysGrid = document.getElementById('surveysGrid');
        surveysGrid.classList.add('loading');

        try {
            const params = new URLSearchParams({
                page: this.currentPage
            });

            // Добавляем фильтры в URL
            if (this.filters.category.length > 0) {
                this.filters.category.forEach(id => params.append('category', id));
            }

            if (this.filters.duration.length > 0) {
                this.filters.duration.forEach(id => params.append('duration', id));
            }

            if (this.filters.status.length > 0) {
                this.filters.status.forEach(id => params.append('status', id));
            }

            console.log('Отправка запроса с параметрами:', params.toString());

            const response = await fetch(`/surveys/api/?${params.toString()}`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            console.log('Получены данные:', data);

            this.totalPages = data.total_pages || 1;
            this.renderSurveys(data.surveys || []);
            this.updatePagination();

            // Обновляем URL
            const url = new URL(window.location);
            url.searchParams.set('page', this.currentPage);
            window.history.pushState({}, '', url);

        } catch (error) {
            console.error('❌ Ошибка загрузки опросов:', error);
            surveysGrid.innerHTML = `
                <div class="error-message" style="grid-column: 1/-1; text-align: center; padding: 40px;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 48px; color: #dc2626; margin-bottom: 16px;"></i>
                    <p style="color: #6B7280; font-size: 16px;">Ошибка загрузки опросов. Пожалуйста, попробуйте позже.</p>
                </div>
            `;
        } finally {
            this.loading = false;
            surveysGrid.classList.remove('loading');
        }
    }

    renderSurveys(surveys) {
        const surveysGrid = document.getElementById('surveysGrid');
        if (!surveysGrid) return;

        if (!surveys || surveys.length === 0) {
            surveysGrid.innerHTML = this.getEmptyStateHTML();
            return;
        }

        surveysGrid.innerHTML = surveys.map(survey => this.getSurveyCardHTML(survey)).join('');
    }

    getSurveyCardHTML(survey) {
        const truncateText = (text, maxLength) => {
            if (!text) return '';
            if (text.length <= maxLength) return text;
            return text.substr(0, maxLength - 3) + '...';
        };

        const formatDate = (dateString) => {
            if (!dateString) return '';
            try {
                const date = new Date(dateString);
                return date.toLocaleDateString('ru-RU', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric'
                });
            } catch (e) {
                return dateString;
            }
        };

        // Определяем класс статуса
        const statusClass = survey.status_code === 'active' ? 'active' : 'completed';
        const statusText = survey.status_display || (survey.status_code === 'active' ? 'Активен' : 'Завершен');

        return `
            <a href="/surveys/${survey.id}/" class="surveys-card-link" style="text-decoration: none; color: inherit; display: block;">
                <article class="surveys-card" data-id="${survey.id}">
                    <div class="surveys-card-header">
                        <div class="survey-icon">
                            <i class="fas fa-clipboard-list"></i>
                        </div>
                        <div class="category-badge" style="background-color: ${survey.category?.bg_color || '#e5e7eb'}; color: ${survey.category?.text_color || '#374151'};">
                            ${truncateText(survey.category?.name || 'Без категории', 20)}
                        </div>
                    </div>

                    <div class="surveys-card-content">
                        <h3 class="surveys-title" title="${survey.title || ''}">${truncateText(survey.title || 'Без названия', 100)}</h3>
                        <p class="surveys-description" title="${survey.description || ''}">${truncateText(survey.description || 'Нет описания', 120)}</p>

                        <div class="surveys-description-spacing"></div>

                        <div class="surveys-details">
                            <div class="detail-item">
                                <i class="fas fa-clipboard-list"></i>
                                <span class="detail-text">${survey.questions_count || 0} вопросов</span>
                            </div>
                            <div class="detail-item">
                                <i class="far fa-clock"></i>
                                <span class="detail-text">${survey.duration || 'Не указано'}</span>
                            </div>
                            <div class="detail-item">
                                <i class="far fa-calendar"></i>
                                <span class="detail-text">Опубликовано ${formatDate(survey.created_date)}</span>
                            </div>
                        </div>

                        <div class="surveys-meta">
                            <div class="status-badge ${statusClass}">
                                ${statusText}
                            </div>
                        </div>
                    </div>
                </article>
            </a>
        `;
    }

    updatePagination() {
        const prevBtn = document.getElementById('prevPage');
        const nextBtn = document.getElementById('nextPage');
        const pagesContainer = document.getElementById('paginationPages');

        if (!pagesContainer) return;

        if (prevBtn) {
            prevBtn.disabled = this.currentPage === 1;
        }

        if (nextBtn) {
            nextBtn.disabled = this.currentPage >= this.totalPages;
        }

        let pagesHTML = '';
        const maxVisiblePages = 5;
        let startPage = Math.max(1, this.currentPage - 2);
        let endPage = Math.min(this.totalPages, startPage + maxVisiblePages - 1);

        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }

        if (startPage > 1) {
            pagesHTML += `<button class="pagination-page" data-page="1">1</button>`;
            if (startPage > 2) pagesHTML += `<span class="pagination-ellipsis">...</span>`;
        }

        for (let i = startPage; i <= endPage; i++) {
            pagesHTML += `<button class="pagination-page ${i === this.currentPage ? 'active' : ''}" data-page="${i}">${i}</button>`;
        }

        if (endPage < this.totalPages) {
            if (endPage < this.totalPages - 1) pagesHTML += `<span class="pagination-ellipsis">...</span>`;
            pagesHTML += `<button class="pagination-page" data-page="${this.totalPages}">${this.totalPages}</button>`;
        }

        pagesContainer.innerHTML = pagesHTML;
    }

    updateFilterStyles() {
        document.querySelectorAll('.filter-option').forEach(option => {
            const checkbox = option.querySelector('.filter-checkbox');
            if (checkbox) {
                const category = checkbox.dataset.category;
                const value = checkbox.value;

                if (this.filters[category] && this.filters[category].includes(value)) {
                    checkbox.checked = true;
                    option.classList.add('active');
                } else {
                    checkbox.checked = false;
                    option.classList.remove('active');
                }
            }
        });
    }

    async clearAllFilters() {
        console.log('Сброс всех фильтров');

        this.filters = {
            category: [],
            duration: [],
            status: []
        };

        document.querySelectorAll('.filter-checkbox').forEach(checkbox => {
            checkbox.checked = false;
        });

        document.querySelectorAll('.filter-option').forEach(option => {
            option.classList.remove('active');
        });

        this.currentPage = 1;
        await this.loadSurveys();
        // Прокрутка наверх после сброса фильтров
        this.scrollToTop();
    }

       populateMobileFilters() {
        const modalFilters = document.querySelector('.modal-filters');
        if (!modalFilters) return;

        // Универсальная функция генерации группы аккордеона
        const generateFilterGroup = (title, category, items, icon, colorField = null) => {
            const selectedCount = this.filters[category].length;
            const countBadge = selectedCount > 0
                ? `<span class="filter-count-badge">${selectedCount}</span>`
                : '';

            return `
                <div class="mobile-filter-group" data-category="${category}">
                    <div class="mobile-filter-group-header" onclick="window.surveysApp.toggleFilterGroup(this)">
                        <div class="mobile-filter-group-title">
                            <i class="fas ${icon}"></i>
                            <span>${title}</span>
                            ${countBadge}
                        </div>
                        <i class="fas fa-chevron-down mobile-filter-toggle-icon"></i>
                    </div>
                    <div class="mobile-filter-group-content">
                        <div class="filter-options">
                            ${Object.values(items || {}).map(item => `
                                <label class="filter-option">
                                    <input type="checkbox" class="filter-checkbox"
                                           data-category="${category}" value="${item.id}"
                                           ${this.filters[category].includes(item.id.toString()) ? 'checked' : ''}>
                                    ${colorField && item[colorField] ? `<span class="filter-color-indicator" style="background-color: ${item[colorField]};"></span>` : ''}
                                    <span class="filter-option-text">${this.escapeHtml(item.name)}</span>
                                </label>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
        };

        const filtersHTML = `
            <div class="mobile-filters-accordion">
                ${generateFilterGroup('По категории', 'category', this.categories, 'fa-layer-group', 'bg_color')}
                ${generateFilterGroup('По длительности', 'duration', this.durations, 'fa-clock', null)}
                ${generateFilterGroup('По статусу', 'status', this.statuses, 'fa-check-circle', null)}
            </div>
        `;

        modalFilters.innerHTML = filtersHTML;

        // Привязываем обработчики к чекбоксам
        modalFilters.querySelectorAll('.filter-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const category = e.target.dataset.category;
                const value = e.target.value;

                if (e.target.checked) {
                    if (!this.filters[category].includes(value)) {
                        this.filters[category].push(value);
                    }
                } else {
                    this.filters[category] = this.filters[category].filter(v => v !== value);
                }

                // Обновляем счётчик в заголовке группы
                this.updateFilterGroupCount(category);
            });
        });

        // Раскрываем первую группу по умолчанию
        const firstGroup = modalFilters.querySelector('.mobile-filter-group');
        if (firstGroup) {
            firstGroup.classList.add('expanded');
        }
    }

    // Новый метод: раскрытие/сворачивание группы фильтров
    toggleFilterGroup(headerElement) {
        const group = headerElement.closest('.mobile-filter-group');
        if (!group) return;

        // Закрываем все другие группы (аккордеон)
        const allGroups = group.parentElement.querySelectorAll('.mobile-filter-group');
        allGroups.forEach(g => {
            if (g !== group) {
                g.classList.remove('expanded');
            }
        });

        // Переключаем текущую группу
        group.classList.toggle('expanded');
    }

    // Новый метод: обновление счётчика выбранных значений
    updateFilterGroupCount(category) {
        const group = document.querySelector(`.mobile-filter-group[data-category="${category}"]`);
        if (!group) return;

        const count = this.filters[category].length;
        const titleElement = group.querySelector('.mobile-filter-group-title');

        // Удаляем старый бейдж, если есть
        const oldBadge = titleElement.querySelector('.filter-count-badge');
        if (oldBadge) oldBadge.remove();

        // Добавляем новый бейдж, если есть выбранные значения
        if (count > 0) {
            const badge = document.createElement('span');
            badge.className = 'filter-count-badge';
            badge.textContent = count;
            titleElement.appendChild(badge);
        }
    }

    // Новый метод: обновление всех счётчиков
    updateAllFilterGroupCounts() {
        Object.keys(this.filters).forEach(category => {
            this.updateFilterGroupCount(category);
        });
    }

    // Экранирование HTML
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    applyMobileFilters() {
        const modalFilters = document.querySelector('.modal-filters');
        if (!modalFilters) return;

        const newFilters = {
            category: [],
            duration: [],
            status: []
        };

        modalFilters.querySelectorAll('.filter-checkbox:checked').forEach(checkbox => {
            const category = checkbox.dataset.category;
            const value = checkbox.value;
            if (!newFilters[category].includes(value)) {
                newFilters[category].push(value);
            }
        });

        console.log('Применение фильтров из модального окна:', newFilters);

        this.filters = newFilters;
        this.syncMainFilters();
        this.updateAllFilterGroupCounts();
    }

    clearMobileFilters() {
        const modalFilters = document.querySelector('.modal-filters');
        if (!modalFilters) return;

        // Снимаем все галочки
        modalFilters.querySelectorAll('.filter-checkbox').forEach(checkbox => {
            checkbox.checked = false;
        });

        // Сбрасываем фильтры
        this.filters = {
            category: [],
            duration: [],
            status: []
        };

        // Обновляем все счётчики (удаляем бейджи)
        this.updateAllFilterGroupCounts();

        // Сворачиваем все группы, кроме первой
        const allGroups = modalFilters.querySelectorAll('.mobile-filter-group');
        allGroups.forEach((group, index) => {
            if (index === 0) {
                group.classList.add('expanded');
            } else {
                group.classList.remove('expanded');
            }
        });
    }

    syncMainFilters() {
        document.querySelectorAll('.filter-checkbox').forEach(checkbox => {
            const category = checkbox.dataset.category;
            const value = checkbox.value;
            checkbox.checked = this.filters[category]?.includes(value) || false;
        });

        this.updateFilterStyles();
    }

    getEmptyStateHTML() {
        return `
            <div class="empty-state" style="grid-column: 1/-1; text-align: center; padding: 60px 20px;">
                <div class="empty-state-icon" style="font-size: 64px; color: #9CA3AF; margin-bottom: 20px;">
                    <i class="fas fa-clipboard-list"></i>
                </div>
                <h3 class="empty-state-title" style="font-size: 20px; font-weight: 600; color: #1A1A1A; margin-bottom: 12px;">Опросы не найдены</h3>
                <p class="empty-state-description" style="font-size: 15px; color: #6B7280; max-width: 400px; margin: 0 auto 24px;">
                    Попробуйте изменить параметры фильтрации
                </p>
                <button class="btn-reset-filters" onclick="window.surveysApp.clearAllFilters()"
                        style="display: inline-flex; align-items: center; gap: 8px; padding: 12px 24px; background: #032D43; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer;">
                    <i class="fas fa-redo"></i> Сбросить фильтры
                </button>
            </div>
        `;
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    if (typeof surveysAppConfig !== 'undefined') {
        window.surveysApp = new SurveysApp(surveysAppConfig);
        window.surveysApp.init();
    } else {
        console.error('❌ surveysAppConfig не найден!');
    }
});

// Закрытие модального окна по Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const modal = document.getElementById('mobileFiltersModal');
        if (modal && modal.classList.contains('active')) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }
});

// Обработка кнопок "Назад"/"Вперед" в браузере
window.addEventListener('popstate', function() {
    const params = new URLSearchParams(window.location.search);
    const page = parseInt(params.get('page')) || 1;

    if (window.surveysApp && window.surveysApp.currentPage !== page) {
        window.surveysApp.currentPage = page;
        window.surveysApp.loadSurveys();
    }
});

// ===== КНОПКА "НАВЕРХ" =====
(function() {
    // Проверяем, есть ли уже кнопка
    if (document.getElementById('scrollToTop')) return;

    const scrollButton = document.createElement('button');
    scrollButton.id = 'scrollToTop';
    scrollButton.className = 'scroll-to-top';
    scrollButton.setAttribute('aria-label', 'Наверх');
    scrollButton.setAttribute('title', 'Наверх');
    scrollButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
    document.body.appendChild(scrollButton);

    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            scrollButton.classList.add('show');
        } else {
            scrollButton.classList.remove('show');
        }
    });

    scrollButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    if (window.scrollY > 300) {
        scrollButton.classList.add('show');
    }
})();