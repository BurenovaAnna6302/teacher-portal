// news.js - Функциональность страницы новостей с AJAX
// Версия: 4.0

class NewsApp {
    constructor(config) {
        // Добавлено поле news
        this.news = config.news || [];
        this.statuses = config.statuses;
        this.targetDirections = config.targetDirections;
        this.contentOrientations = config.contentOrientations;
        this.itemsPerPage = config.itemsPerPage || 9;
        this.currentPage = config.currentPage || 1;
        this.totalPages = config.totalPages || 1;

        this.filters = {
            status: [],
            target: [],
            content: [],
            dateFrom: null,
            dateTo: null
        };

        this.sortBy = 'date-desc';
        this.loading = false;
        this.initialized = false;
    }

    async init() {
        if (this.initialized) return;

        console.log('🚀 Инициализация приложения новостей с AJAX...');

        this.initFilters();
        this.initSorting();
        this.initPagination();
        this.initMobileFilters();
        this.initCardClick();

        // Используем данные из шаблона для первой загрузки
        this.renderNews(this.news);
        this.updatePagination();

        this.initialized = true;
        console.log('✅ Приложение новостей инициализировано');
    }

    // Функция для прокрутки наверх страницы
    scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }

    initCardClick() {
        document.addEventListener('click', (e) => {
            // Находим ближайшую карточку новости
            const card = e.target.closest('.news-card');
            if (card) {
                const newsId = card.dataset.id;
                if (newsId) {
                    console.log('Переход на новость ID:', newsId);
                    window.location.href = `/news/${newsId}/`;
                }
            }
        });
    }

    initFilters() {
        // Обработка чекбоксов фильтров
        document.querySelectorAll('.filter-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', async (e) => {
                const category = e.target.dataset.category;
                const value = e.target.value;

                if (e.target.checked) {
                    this.filters[category].push(value);
                } else {
                    this.filters[category] = this.filters[category].filter(v => v !== value);
                }

                this.currentPage = 1;
                await this.loadNews();
                this.updateFilterStyles();
                // Прокрутка наверх после применения фильтров
                this.scrollToTop();
            });
        });

        // Обработка дат
        document.getElementById('dateFrom')?.addEventListener('change', async (e) => {
            this.filters.dateFrom = e.target.value || null;
            this.currentPage = 1;
            await this.loadNews();
            this.scrollToTop();
        });

        document.getElementById('dateTo')?.addEventListener('change', async (e) => {
            this.filters.dateTo = e.target.value || null;
            this.currentPage = 1;
            await this.loadNews();
            this.scrollToTop();
        });

        // Кнопка сброса всех фильтров
        document.getElementById('clearAllFilters')?.addEventListener('click', async () => {
            await this.clearAllFilters();
            this.scrollToTop();
        });
    }

    initSorting() {
        const sortSelect = document.getElementById('sortSelect');
        if (sortSelect) {
            sortSelect.addEventListener('change', async (e) => {
                this.sortBy = e.target.value;
                this.currentPage = 1;
                await this.loadNews();
                this.scrollToTop();
            });
        }
    }

    initPagination() {
        document.getElementById('prevPage')?.addEventListener('click', async () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                await this.loadNews();
                this.scrollToTop();
            }
        });

        document.getElementById('nextPage')?.addEventListener('click', async () => {
            if (this.currentPage < this.totalPages) {
                this.currentPage++;
                await this.loadNews();
                this.scrollToTop();
            }
        });

        // Делегирование событий для кнопок пагинации
        document.addEventListener('click', async (e) => {
            if (e.target.classList.contains('pagination-page')) {
                const page = parseInt(e.target.dataset.page);
                if (page && page !== this.currentPage) {
                    this.currentPage = page;
                    await this.loadNews();
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
                await this.loadNews();
                this.scrollToTop();
            });
        }

        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.clearMobileFilters();
            });
        }
    }

    async loadNews() {
        if (this.loading) return;

        this.loading = true;
        const newsGrid = document.getElementById('newsGrid');

        // Показываем загрузку
        newsGrid.classList.add('loading');

        try {
            // Формируем URL с параметрами
            const params = new URLSearchParams({
                page: this.currentPage,
                sort: this.sortBy,
            });

            // Добавляем фильтры
            this.filters.status.forEach(id => params.append('status[]', id));
            this.filters.target.forEach(id => params.append('target[]', id));
            this.filters.content.forEach(id => params.append('content[]', id));

            if (this.filters.dateFrom) {
                params.append('date_from', this.filters.dateFrom);
            }
            if (this.filters.dateTo) {
                params.append('date_to', this.filters.dateTo);
            }

            // Выполняем AJAX-запрос
            const response = await fetch(`/news/api/?${params}`);
            const data = await response.json();

            // Обновляем данные
            this.totalPages = data.total_pages;

            // Рендерим новости
            this.renderNews(data.news);

            // Обновляем пагинацию
            this.updatePagination();

            // Обновляем URL в адресной строке (без перезагрузки)
            const url = new URL(window.location);
            url.searchParams.set('page', this.currentPage);
            window.history.pushState({}, '', url);

        } catch (error) {
            console.error('❌ Ошибка загрузки новостей:', error);
            newsGrid.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Ошибка загрузки новостей</p>
                </div>
            `;
        } finally {
            this.loading = false;
            newsGrid.classList.remove('loading');
        }
    }

    renderNews(newsItems) {
        const newsGrid = document.getElementById('newsGrid');
        if (!newsGrid) return;

        if (newsItems.length === 0) {
            newsGrid.innerHTML = this.getEmptyStateHTML();
            return;
        }

        newsGrid.innerHTML = newsItems.map(item => this.getNewsCardHTML(item)).join('');
    }

    getNewsCardHTML(item) {
        const truncateText = (text, maxLength) => {
            if (!text) return '';
            if (text.length <= maxLength) return text;
            return text.substr(0, maxLength - 3) + '...';
        };

        const formattedDate = this.formatDate(item.published_date);
        const badgeColor = item.status.color;
        const textColor = item.status.text_color || '#000000';

        return `
            <article class="news-card" data-id="${item.id}">
                <div class="news-card-image">
                    <img src="${item.image_url || '/static/news/images/default-news.png'}"
                         alt="${item.title}"
                         class="news-image"
                         onerror="this.onerror=null; this.src='/static/news/images/default-news.png'">

                    <div class="category-badge"
                         style="background-color: ${badgeColor};
                                color: ${textColor};">
                        ${truncateText(item.status.name, 20)}
                    </div>
                </div>

                <div class="news-card-content">
                    <h3 class="news-title" title="${item.title}">${truncateText(item.title, 100)}</h3>
                    <p class="news-excerpt" title="${item.excerpt}">${truncateText(item.excerpt, 200)}</p>

                    <div class="news-details">
                        <div class="detail-item">
                            <i class="fas fa-users"></i>
                            <div class="detail-text">
                                <strong>Целевая аудитория:</strong> ${truncateText(item.target_direction.name, 30)}
                            </div>
                        </div>
                        <div class="detail-item">
                            <i class="fas fa-bullseye"></i>
                            <div class="detail-text">
                                <strong>Направленность:</strong> ${truncateText(item.content_orientation.name, 30)}
                            </div>
                        </div>
                    </div>

                    <div class="news-meta">
                        <div class="meta-item">
                            <i class="far fa-calendar"></i>
                            <span>${formattedDate}</span>
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

        // Обновляем состояние кнопок
        if (prevBtn) {
            prevBtn.disabled = this.currentPage === 1;
        }

        if (nextBtn) {
            nextBtn.disabled = this.currentPage >= this.totalPages;
        }

        // Создаем кнопки страниц
        let pagesHTML = '';
        const maxVisiblePages = 5;
        let startPage = Math.max(1, this.currentPage - 2);
        let endPage = Math.min(this.totalPages, startPage + maxVisiblePages - 1);

        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }

        // Первая страница
        if (startPage > 1) {
            pagesHTML += `<button class="pagination-page" data-page="1">1</button>`;
            if (startPage > 2) pagesHTML += `<span class="pagination-ellipsis">...</span>`;
        }

        // Основные страницы
        for (let i = startPage; i <= endPage; i++) {
            pagesHTML += `<button class="pagination-page ${i === this.currentPage ? 'active' : ''}" data-page="${i}">${i}</button>`;
        }

        // Последняя страница
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

                if (this.filters[category].includes(value)) {
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
        // Сбрасываем фильтры
        this.filters = {
            status: [],
            target: [],
            content: [],
            dateFrom: null,
            dateTo: null
        };

        // Сбрасываем UI
        document.querySelectorAll('.filter-checkbox').forEach(checkbox => {
            checkbox.checked = false;
        });

        const dateFrom = document.getElementById('dateFrom');
        const dateTo = document.getElementById('dateTo');
        if (dateFrom) dateFrom.value = '';
        if (dateTo) dateTo.value = '';

        const sortSelect = document.getElementById('sortSelect');
        if (sortSelect) {
            sortSelect.value = 'date-desc';
        }
        this.sortBy = 'date-desc';

        this.currentPage = 1;
        await this.loadNews();
        this.updateFilterStyles();
    }

    populateMobileFilters() {
        const modalFilters = document.querySelector('.modal-filters');
        if (!modalFilters) return;

        const filtersHTML = `
            <div class="filters-list">
                <!-- Status Filter -->
                <div class="filter-group">
                    <h4 class="filter-group-title">По статусу информации</h4>
                    <div class="filter-options">
                        ${Object.values(this.statuses).map(status => `
                            <label class="filter-option">
                                <input type="checkbox" class="filter-checkbox"
                                       data-category="status" value="${status.id}">
                                <span class="filter-color-indicator" style="background-color: ${status.color};"></span>
                                <span class="filter-option-text">${status.name}</span>
                            </label>
                        `).join('')}
                    </div>
                </div>

                <!-- Target Direction Filter -->
                <div class="filter-group">
                    <h4 class="filter-group-title">По целевой аудитории</h4>
                    <div class="filter-options">
                        ${Object.values(this.targetDirections).map(target => `
                            <label class="filter-option">
                                <input type="checkbox" class="filter-checkbox"
                                       data-category="target" value="${target.id}">
                                <span class="filter-option-text">${target.name}</span>
                            </label>
                        `).join('')}
                    </div>
                </div>

                <!-- Content Orientation Filter -->
                <div class="filter-group">
                    <h4 class="filter-group-title">По направленности</h4>
                    <div class="filter-options">
                        ${Object.values(this.contentOrientations).map(content => `
                            <label class="filter-option">
                                <input type="checkbox" class="filter-checkbox"
                                       data-category="content" value="${content.id}">
                                <span class="filter-option-text">${content.name}</span>
                            </label>
                        `).join('')}
                    </div>
                </div>

                <!-- Date Filter -->
                <div class="filter-group">
                    <h4 class="filter-group-title">Дата публикации</h4>
                    <div class="date-filter-wrapper">
                        <div class="date-input-group">
                            <input type="date" id="mobileDateFrom" class="date-input" value="${this.filters.dateFrom || ''}">
                            <i class="fas fa-calendar-alt date-icon"></i>
                        </div>
                        <div class="date-input-group">
                            <input type="date" id="mobileDateTo" class="date-input" value="${this.filters.dateTo || ''}">
                            <i class="fas fa-calendar-alt date-icon"></i>
                        </div>
                    </div>
                </div>
            </div>
        `;

        modalFilters.innerHTML = filtersHTML;

        // Устанавливаем состояния чекбоксов
        modalFilters.querySelectorAll('.filter-checkbox').forEach(checkbox => {
            const category = checkbox.dataset.category;
            const value = checkbox.value;
            checkbox.checked = this.filters[category].includes(value);
        });
    }

    applyMobileFilters() {
        const modalFilters = document.querySelector('.modal-filters');
        if (!modalFilters) return;

        // Собираем новые фильтры
        const newFilters = {
            status: [],
            target: [],
            content: [],
            dateFrom: null,
            dateTo: null
        };

        modalFilters.querySelectorAll('.filter-checkbox').forEach(checkbox => {
            const category = checkbox.dataset.category;
            const value = checkbox.value;

            if (checkbox.checked) {
                newFilters[category].push(value);
            }
        });

        newFilters.dateFrom = modalFilters.querySelector('#mobileDateFrom')?.value || null;
        newFilters.dateTo = modalFilters.querySelector('#mobileDateTo')?.value || null;

        // Применяем фильтры
        this.filters = newFilters;
        this.syncMainFilters();
        this.currentPage = 1;
    }

    clearMobileFilters() {
        const modalFilters = document.querySelector('.modal-filters');
        if (!modalFilters) return;

        modalFilters.querySelectorAll('.filter-checkbox').forEach(checkbox => {
            checkbox.checked = false;
        });

        const dateFrom = modalFilters.querySelector('#mobileDateFrom');
        const dateTo = modalFilters.querySelector('#mobileDateTo');
        if (dateFrom) dateFrom.value = '';
        if (dateTo) dateTo.value = '';
    }

    syncMainFilters() {
        document.querySelectorAll('.filter-checkbox').forEach(checkbox => {
            const category = checkbox.dataset.category;
            const value = checkbox.value;
            checkbox.checked = this.filters[category].includes(value);
        });

        const dateFrom = document.getElementById('dateFrom');
        const dateTo = document.getElementById('dateTo');
        if (dateFrom) dateFrom.value = this.filters.dateFrom || '';
        if (dateTo) dateTo.value = this.filters.dateTo || '';
    }

    formatDate(dateString) {
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
    }

    getEmptyStateHTML() {
        return `
            <div class="empty-state">
                <div class="empty-state-icon">
                    <i class="far fa-newspaper"></i>
                </div>
                <h3 class="empty-state-title">Новости не найдены</h3>
                <p class="empty-state-description">
                    Попробуйте изменить параметры фильтров или сортировки
                </p>
                <button class="btn-reset-filters" onclick="window.newsApp.clearAllFilters()">
                    <i class="fas fa-redo"></i> Сбросить фильтры
                </button>
            </div>
        `;
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    if (typeof newsAppConfig !== 'undefined') {
        window.newsApp = new NewsApp(newsAppConfig);
        window.newsApp.init();
    }
});

// Закрыть модальное окно при нажатии Escape
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

    if (window.newsApp && window.newsApp.currentPage !== page) {
        window.newsApp.currentPage = page;
        window.newsApp.loadNews();
    }
});

// ===== КНОПКА "НАВЕРХ" =====
(function() {
    // Создаем кнопку
    const scrollButton = document.createElement('button');
    scrollButton.id = 'scrollToTop';
    scrollButton.className = 'scroll-to-top';
    scrollButton.setAttribute('aria-label', 'Наверх');
    scrollButton.setAttribute('title', 'Наверх');
    scrollButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
    document.body.appendChild(scrollButton);

    // Показываем/скрываем при прокрутке
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            scrollButton.classList.add('show');
        } else {
            scrollButton.classList.remove('show');
        }
    });

    // Прокрутка наверх при клике
    scrollButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // Проверяем позицию при загрузке
    if (window.scrollY > 300) {
        scrollButton.classList.add('show');
    }
})();