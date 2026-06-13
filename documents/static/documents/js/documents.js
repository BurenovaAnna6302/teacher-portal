// documents.js - Функциональность страницы нормативных документов с AJAX
// Версия: 2.2 - Исправлено: пагинация 8 документов на странице

class DocumentsApp {
    constructor(config) {
        this.documents = config.documents || [];
        this.categories = config.categories;
        this.levels = config.levels;
        this.years = config.years;
        // Исправлено: 8 документов на странице
        this.itemsPerPage = 8;
        this.currentPage = config.currentPage || 1;
        this.totalPages = config.totalPages || 1;

        this.filters = {
            category: [],
            level: [],
            year: []
        };

        this.loading = false;
        this.initialized = false;
    }

    async init() {
        if (this.initialized) return;

        console.log('🚀 Инициализация приложения документов с AJAX...');
        console.log('📄 Документов на странице:', this.itemsPerPage);

        this.initFilters();
        this.initPagination();
        this.initMobileFilters();

        // Рендерим документы из переданных данных
        this.renderDocuments(this.documents);
        this.updatePagination();

        this.initialized = true;
        console.log('✅ Приложение документов инициализировано');
    }

    initFilters() {
        // Обработка чекбоксов фильтров
        document.querySelectorAll('.filter-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', async (e) => {
                const category = e.target.dataset.category;
                const value = e.target.value;

                if (e.target.checked) {
                    // Добавляем значение в массив фильтров
                    if (!this.filters[category].includes(value)) {
                        this.filters[category].push(value);
                    }
                } else {
                    // Удаляем значение из массива фильтров
                    this.filters[category] = this.filters[category].filter(v => v !== value);
                }

                console.log('Фильтры после изменения:', this.filters);

                this.currentPage = 1;
                await this.loadDocuments();
                this.updateFilterStyles();
            });
        });

        // Кнопка сброса всех фильтров
        document.getElementById('clearAllFilters')?.addEventListener('click', () => this.clearAllFilters());
    }

    initPagination() {
        document.getElementById('prevPage')?.addEventListener('click', async () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                await this.loadDocuments();
                // Прокрутка наверх
                this.scrollToTop();
            }
        });

        document.getElementById('nextPage')?.addEventListener('click', async () => {
            if (this.currentPage < this.totalPages) {
                this.currentPage++;
                await this.loadDocuments();
                // Прокрутка наверх
                this.scrollToTop();
            }
        });

        document.addEventListener('click', async (e) => {
            if (e.target.classList.contains('pagination-page')) {
                const page = parseInt(e.target.dataset.page);
                if (page && page !== this.currentPage) {
                    this.currentPage = page;
                    await this.loadDocuments();
                    // Прокрутка наверх
                    this.scrollToTop();
                }
            }
        });
    }

    // Функция для прокрутки наверх
    scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
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
                await this.loadDocuments();
                // Прокрутка наверх
                this.scrollToTop();
            });
        }

        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.clearMobileFilters();
            });
        }
    }

    async loadDocuments() {
        if (this.loading) return;

        this.loading = true;
        const documentsGrid = document.getElementById('documentsGrid');
        documentsGrid.classList.add('loading');

        try {
            const params = new URLSearchParams({
                page: this.currentPage,
                per_page: this.itemsPerPage // Явно указываем количество на странице
            });

            // Добавляем фильтры в URL
            if (this.filters.category.length > 0) {
                this.filters.category.forEach(id => params.append('category', id));
            }

            if (this.filters.level.length > 0) {
                this.filters.level.forEach(id => params.append('level', id));
            }

            if (this.filters.year.length > 0) {
                this.filters.year.forEach(id => params.append('year', id));
            }

            console.log('Отправка запроса с параметрами:', params.toString());

            const response = await fetch(`/documents/api/?${params.toString()}`);
            const data = await response.json();

            console.log('Получены данные:', data);
            console.log('Всего страниц:', data.total_pages);

            this.totalPages = data.total_pages;
            this.renderDocuments(data.documents);
            this.updatePagination();

            // Обновляем URL
            const url = new URL(window.location);
            url.searchParams.set('page', this.currentPage);
            window.history.pushState({}, '', url);

        } catch (error) {
            console.error('❌ Ошибка загрузки документов:', error);
            documentsGrid.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Ошибка загрузки документов</p>
                </div>
            `;
        } finally {
            this.loading = false;
            documentsGrid.classList.remove('loading');
        }
    }

    renderDocuments(documents) {
        const documentsGrid = document.getElementById('documentsGrid');
        if (!documentsGrid) return;

        if (documents.length === 0) {
            documentsGrid.innerHTML = this.getEmptyStateHTML();
            return;
        }

        documentsGrid.innerHTML = documents.map(doc => this.getDocumentCardHTML(doc)).join('');
    }

    getDocumentCardHTML(doc) {
        const truncateText = (text, maxLength) => {
            if (!text) return '';
            if (text.length <= maxLength) return text;
            return text.substr(0, maxLength - 3) + '...';
        };

        return `
            <article class="document-card" data-id="${doc.id}">
                <div class="document-card-inner">
                    <!-- Document Header -->
                    <div class="document-header">
                        <div class="document-icon" style="background-color: ${doc.category.bg_color};">
                            <i class="fas fa-file-alt" style="color: ${doc.category.text_color};"></i>
                        </div>
                        <span class="document-category" style="background-color: ${doc.category.bg_color}; color: ${doc.category.text_color};">
                            ${doc.category.name}
                        </span>
                    </div>

                    <!-- Document Content -->
                    <div class="document-content">
                        <h3 class="document-title" title="${doc.title}">${truncateText(doc.title, 100)}</h3>
                        <p class="document-description" title="${doc.description}">${truncateText(doc.description, 150)}</p>

                        <!-- Document Details -->
                        <div class="document-details">
                            <div class="detail-item">
                                <i class="fas fa-layer-group"></i>
                                <div class="detail-text">
                                    <strong>Уровень документа:</strong> ${doc.level.name}
                                </div>
                            </div>
                            <div class="detail-item">
                                <i class="far fa-calendar"></i>
                                <div class="detail-text">
                                    <strong>Год принятия:</strong> ${doc.year}
                                </div>
                            </div>
                        </div>

                        <!-- Document Meta -->
                        <div class="document-meta">
                            <div class="meta-item">
                                <i class="far fa-calendar-alt"></i>
                                <span>${doc.date}</span>
                            </div>
                            <div class="meta-item">
                                <i class="fas fa-file-alt"></i>
                                <span>${doc.file_size}</span>
                            </div>
                        </div>

                        <!-- Document Actions -->
                        <div class="document-actions">
                            <a href="${doc.file_url || '#'}"
                               class="btn-download"
                               download
                               ${!doc.file_url ? 'disabled' : ''}>
                                <i class="fas fa-download"></i>
                                Скачать
                            </a>
                            <a href="${doc.file_url || '#'}"
                               class="btn-online"
                               target="_blank"
                               ${!doc.file_url ? 'disabled' : ''}>
                                <i class="fas fa-external-link-alt"></i>
                                Открыть онлайн
                            </a>
                        </div>
                    </div>
                </div>
            </article>
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

        // Сбрасываем фильтры
        this.filters = {
            category: [],
            level: [],
            year: []
        };

        // Сбрасываем UI - все чекбоксы
        document.querySelectorAll('.filter-checkbox').forEach(checkbox => {
            checkbox.checked = false;
        });

        // Сбрасываем активные классы
        document.querySelectorAll('.filter-option').forEach(option => {
            option.classList.remove('active');
        });

        this.currentPage = 1;
        await this.loadDocuments();
        // Прокрутка наверх
        this.scrollToTop();
    }

        populateMobileFilters() {
        const modalFilters = document.querySelector('.modal-filters');
        if (!modalFilters) return;

        // Функция для генерации HTML группы фильтров
        const generateFilterGroup = (title, category, items, icon) => {
            const selectedCount = this.filters[category].length;
            const countBadge = selectedCount > 0
                ? `<span class="filter-count-badge">${selectedCount}</span>`
                : '';

            return `
                <div class="mobile-filter-group" data-category="${category}">
                    <div class="mobile-filter-group-header" onclick="window.documentsApp.toggleFilterGroup(this)">
                        <div class="mobile-filter-group-title">
                            <i class="fas ${icon}"></i>
                            <span>${title}</span>
                            ${countBadge}
                        </div>
                        <i class="fas fa-chevron-down mobile-filter-toggle-icon"></i>
                    </div>
                    <div class="mobile-filter-group-content">
                        <div class="filter-options">
                            ${Object.values(items).map(item => `
                                <label class="filter-option">
                                    <input type="checkbox" class="filter-checkbox"
                                           data-category="${category}" value="${item.id}"
                                           ${this.filters[category].includes(item.id.toString()) ? 'checked' : ''}>
                                    ${category === 'category' && item.bg_color ? `<span class="filter-color-indicator" style="background-color: ${item.bg_color};"></span>` : ''}
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
                ${generateFilterGroup('По категории', 'category', this.categories, 'fa-folder')}
                ${generateFilterGroup('По уровню действия', 'level', this.levels, 'fa-layer-group')}
                ${generateFilterGroup('По году принятия', 'year', this.years, 'fa-calendar-alt')}
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

        // Собираем новые фильтры из модального окна
        const newFilters = {
            category: [],
            level: [],
            year: []
        };

        modalFilters.querySelectorAll('.filter-checkbox:checked').forEach(checkbox => {
            const category = checkbox.dataset.category;
            const value = checkbox.value;
            newFilters[category].push(value);
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
            level: [],
            year: []
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
            <div class="empty-state">
                <div class="empty-state-icon">
                    <i class="fas fa-file-alt"></i>
                </div>
                <h3 class="empty-state-title">Документы не найдены</h3>
                <p class="empty-state-description">
                    Попробуйте изменить параметры фильтрации
                </p>
                <button class="btn-reset-filters" onclick="window.documentsApp.clearAllFilters()">
                    <i class="fas fa-redo"></i> Сбросить фильтры
                </button>
            </div>
        `;
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    if (typeof documentsAppConfig !== 'undefined') {
        window.documentsApp = new DocumentsApp(documentsAppConfig);
        window.documentsApp.init();
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

    if (window.documentsApp && window.documentsApp.currentPage !== page) {
        window.documentsApp.currentPage = page;
        window.documentsApp.loadDocuments();
    }
});

// ===== КНОПКА "НАВЕРХ" =====
(function() {
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