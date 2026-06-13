// events.js - Функциональность страницы мероприятий с AJAX
class EventsApp {
    constructor(config) {
        this.audiences = config.audiences;
        this.formats = config.formats;
        this.activityTypes = config.activityTypes;
        this.subjects = config.subjects;
        this.events = config.events || [];
        this.itemsPerPage = config.itemsPerPage || 12;
        this.currentPage = config.currentPage || 1;
        this.totalPages = config.totalPages || 1;

        this.filters = {
            audience: [],
            format: [],
            activity_type: [],
            subject: []
        };

        this.sortBy = 'all';
        this.loading = false;
        this.initialized = false;
    }

    async init() {
        if (this.initialized) return;

        console.log('Инициализация приложения мероприятий с AJAX...');

        this.initFilters();
        this.initSorting();
        this.initPagination();
        this.initMobileFilters();
        this.initFavorites();
        this.initCardClick();

        // Рендерим мероприятия из переданных данных
        this.renderEvents(this.events);
        this.updatePagination();

        this.initialized = true;
        console.log('Приложение мероприятий инициализировано');
    }

    // Метод прокрутки вверх
    scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }

    initCardClick() {
        document.addEventListener('click', (e) => {
            // Находим ближайшую карточку мероприятия
            const card = e.target.closest('.events-card');
            if (card && !e.target.closest('.heart-btn')) {
                const eventId = card.dataset.id;
                if (eventId) {
                    console.log('Переход на мероприятие ID:', eventId);
                    window.location.href = `/events/${eventId}/`;
                }
            }
        });
    }

    initFilters() {
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
                await this.loadEvents();
                this.updateFilterStyles();
                // Прокрутка наверх после применения фильтров
                this.scrollToTop();
            });
        });

        document.getElementById('clearAllFilters')?.addEventListener('click', () => this.clearAllFilters());
    }

    initSorting() {
        const sortSelect = document.getElementById('sortSelect');
        if (sortSelect) {
            // Устанавливаем значение 'all' как выбранное
            sortSelect.value = 'all';

            sortSelect.addEventListener('change', async (e) => {
                this.sortBy = e.target.value;
                this.currentPage = 1;
                await this.loadEvents();
                // Прокрутка наверх после изменения сортировки
                this.scrollToTop();
            });
        }
    }

    initPagination() {
        document.getElementById('prevPage')?.addEventListener('click', async () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                await this.loadEvents();
                // Прокрутка наверх при смене страницы
                this.scrollToTop();
            }
        });

        document.getElementById('nextPage')?.addEventListener('click', async () => {
            if (this.currentPage < this.totalPages) {
                this.currentPage++;
                await this.loadEvents();
                // Прокрутка наверх при смене страницы
                this.scrollToTop();
            }
        });

        document.addEventListener('click', async (e) => {
            if (e.target.classList.contains('pagination-page')) {
                const page = parseInt(e.target.dataset.page);
                if (page && page !== this.currentPage) {
                    this.currentPage = page;
                    await this.loadEvents();
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
                await this.loadEvents();
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

    initFavorites() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('.heart-btn')) {
                const btn = e.target.closest('.heart-btn');
                btn.classList.toggle('active');
                const icon = btn.querySelector('i');
                icon.classList.toggle('far');
                icon.classList.toggle('fas');

                const eventId = btn.closest('.events-card')?.dataset.id;
                if (eventId) {
                    this.toggleFavorite(eventId, btn);
                }
                e.preventDefault();
                e.stopPropagation();
            }
        });
    }

    toggleFavorite(eventId, btn) {
        let favorites = JSON.parse(localStorage.getItem('event_favorites') || '[]');
        const index = favorites.indexOf(eventId);

        if (index === -1) {
            favorites.push(eventId);
            btn.title = 'Удалить из избранного';
        } else {
            favorites.splice(index, 1);
            btn.title = 'Добавить в избранное';
        }

        localStorage.setItem('event_favorites', JSON.stringify(favorites));
    }

    async loadEvents() {
        if (this.loading) return;

        this.loading = true;
        const eventsGrid = document.getElementById('eventsGrid');
        eventsGrid.classList.add('loading');

        try {
            const params = new URLSearchParams({
                page: this.currentPage,
                sort: this.sortBy,
            });

            // Добавляем фильтры
            this.filters.audience.forEach(id => params.append('audience[]', id));
            this.filters.format.forEach(id => params.append('format[]', id));
            this.filters.activity_type.forEach(id => params.append('activity_type[]', id));
            this.filters.subject.forEach(id => params.append('subject[]', id));

            const response = await fetch(`/events/api/?${params}`);
            const data = await response.json();

            this.totalPages = data.total_pages;
            this.renderEvents(data.events);
            this.updatePagination();

            // Обновляем URL
            const url = new URL(window.location);
            url.searchParams.set('page', this.currentPage);
            window.history.pushState({}, '', url);

        } catch (error) {
            console.error('❌ Ошибка загрузки мероприятий:', error);
            eventsGrid.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Ошибка загрузки мероприятий</p>
                </div>
            `;
        } finally {
            this.loading = false;
            eventsGrid.classList.remove('loading');
        }
    }

    renderEvents(events) {
        const eventsGrid = document.getElementById('eventsGrid');
        if (!eventsGrid) return;

        if (events.length === 0) {
            eventsGrid.innerHTML = this.getEmptyStateHTML();
            return;
        }

        eventsGrid.innerHTML = events.map(event => this.getEventCardHTML(event)).join('');
        this.restoreFavorites();
    }

    getEventCardHTML(event) {
        const truncateText = (text, maxLength) => {
            if (!text) return '';
            if (text.length <= maxLength) return text;
            return text.substr(0, maxLength - 3) + '...';
        };

        const formattedDate = this.formatDate(event.date);
        const badgeColor = event.activity_type.color;
        const textColor = event.activity_type.text_color;

        return `
            <article class="events-card" data-id="${event.id}">
                <div class="events-card-image">
                    <img src="${event.image_url || '/static/events/images/default-event.png'}"
                         alt="${event.title}"
                         class="events-image"
                         onerror="this.onerror=null; this.src='/static/events/images/default-event.png'">

                    <div class="category-badge"
                         style="background-color: ${badgeColor};
                                color: ${textColor};">
                        ${truncateText(event.activity_type.name, 20)}
                    </div>

                    <button class="heart-btn" title="Добавить в избранное">
                        <i class="far fa-heart"></i>
                    </button>
                </div>

                <div class="events-card-content">
                    <h3 class="events-title" title="${event.title}">${truncateText(event.title, 100)}</h3>
                    <p class="events-description" title="${event.description}">${truncateText(event.description, 120)}</p>

                    <div class="events-details">
                        <div class="detail-item">
                            <i class="fas fa-users"></i>
                            <div class="detail-text">
                                <strong>Целевая аудитория:</strong> ${event.audience.name}
                            </div>
                        </div>
                        <div class="detail-item">
                            <i class="fas fa-laptop"></i>
                            <div class="detail-text">
                                <strong>Формат проведения:</strong> ${event.format.name}
                            </div>
                        </div>
                        <div class="detail-item">
                            <i class="fas fa-graduation-cap"></i>
                            <div class="detail-text">
                                <strong>Предметная область:</strong> ${event.subject.name}
                            </div>
                        </div>
                    </div>

                    <div class="events-meta">
                        <div class="meta-item">
                            <i class="far fa-calendar-alt"></i>
                            <span>${formattedDate} • ${event.time}</span>
                        </div>
                        <div class="meta-item">
                            <i class="fas fa-map-marker-alt"></i>
                            <span>${truncateText(event.location, 40)}</span>
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
                if (checkbox.checked) {
                    option.classList.add('active');
                } else {
                    option.classList.remove('active');
                }
            }
        });
    }

    restoreFavorites() {
        const favorites = JSON.parse(localStorage.getItem('event_favorites') || '[]');
        document.querySelectorAll('.events-card').forEach(card => {
            const eventId = card.dataset.id;
            const heartBtn = card.querySelector('.heart-btn');
            const icon = heartBtn?.querySelector('i');

            if (heartBtn && icon) {
                if (favorites.includes(eventId)) {
                    heartBtn.classList.add('active');
                    heartBtn.title = 'Удалить из избранного';
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                } else {
                    heartBtn.classList.remove('active');
                    heartBtn.title = 'Добавить в избранное';
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                }
            }
        });
    }

    async clearAllFilters() {
        this.filters = {
            audience: [],
            format: [],
            activity_type: [],
            subject: []
        };

        document.querySelectorAll('.filter-checkbox').forEach(checkbox => {
            checkbox.checked = false;
        });

        const sortSelect = document.getElementById('sortSelect');
        if (sortSelect) {
            sortSelect.value = 'all';
        }
        this.sortBy = 'all';

        this.currentPage = 1;
        await this.loadEvents();
        this.updateFilterStyles();
        // Прокрутка наверх после сброса фильтров
        this.scrollToTop();
    }

        populateMobileFilters() {
        const modalFilters = document.querySelector('.modal-filters');
        if (!modalFilters) return;

        // Функция для генерации HTML группы фильтров
        const generateFilterGroup = (title, category, items, icon, colorField = 'color') => {
            const selectedCount = this.filters[category].length;
            const countBadge = selectedCount > 0
                ? `<span class="filter-count-badge">${selectedCount}</span>`
                : '';

            return `
                <div class="mobile-filter-group" data-category="${category}">
                    <div class="mobile-filter-group-header" onclick="window.eventsApp.toggleFilterGroup(this)">
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
                                    ${item[colorField] ? `<span class="filter-color-indicator" style="background-color: ${item[colorField]};"></span>` : ''}
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
                ${generateFilterGroup('По целевой аудитории', 'audience', this.audiences, 'fa-users', null)}
                ${generateFilterGroup('По формату проведения', 'format', this.formats, 'fa-laptop', null)}
                ${generateFilterGroup('По типу активности', 'activity_type', this.activityTypes, 'fa-bolt', 'color')}
                ${generateFilterGroup('По предметной области', 'subject', this.subjects, 'fa-book', null)}
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
            audience: [],
            format: [],
            activity_type: [],
            subject: []
        };

        modalFilters.querySelectorAll('.filter-checkbox:checked').forEach(checkbox => {
            const category = checkbox.dataset.category;
            const value = checkbox.value;
            newFilters[category].push(value);
        });

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
            audience: [],
            format: [],
            activity_type: [],
            subject: []
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
                    <i class="far fa-calendar-alt"></i>
                </div>
                <h3 class="empty-state-title">Мероприятия не найдены</h3>
                <p class="empty-state-description">
                    Попробуйте изменить параметры фильтров или сортировки
                </p>
                <button class="btn-reset-filters" onclick="window.eventsApp.clearAllFilters()">
                    <i class="fas fa-redo"></i> Сбросить фильтры
                </button>
            </div>
        `;
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    if (typeof eventsAppConfig !== 'undefined') {
        window.eventsApp = new EventsApp(eventsAppConfig);
        window.eventsApp.init();
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

    if (window.eventsApp && window.eventsApp.currentPage !== page) {
        window.eventsApp.currentPage = page;
        window.eventsApp.loadEvents();
        // Прокрутка наверх при навигации через историю
        if (window.eventsApp.scrollToTop) {
            window.eventsApp.scrollToTop();
        }
    }
});

// ===== КНОПКА "НАВЕРХ" =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('Инициализация кнопки "Наверх"...');

    // Проверяем, не создана ли уже кнопка
    if (document.getElementById('scrollToTop')) {
        console.log('Кнопка уже существует');
        return;
    }

    // Создаем кнопку
    const scrollButton = document.createElement('button');
    scrollButton.id = 'scrollToTop';
    scrollButton.className = 'scroll-to-top';
    scrollButton.setAttribute('aria-label', 'Наверх');
    scrollButton.setAttribute('title', 'Наверх');
    scrollButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
    document.body.appendChild(scrollButton);

    console.log('Кнопка создана и добавлена в DOM');

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
    setTimeout(function() {
        if (window.scrollY > 300) {
            scrollButton.classList.add('show');
        }
    }, 500);
});
// Добавьте в конец файла events.js
document.addEventListener('DOMContentLoaded', function() {
    // Обработка подсказок для места проведения
    const locationElements = document.querySelectorAll('.event-location-text');

    locationElements.forEach(el => {
        el.addEventListener('mouseenter', function(e) {
            const fullText = this.getAttribute('data-fulltext');
            if (fullText && fullText !== 'Онлайн') {
                // Создаем подсказку
                let tooltip = document.createElement('div');
                tooltip.className = 'custom-tooltip';
                tooltip.textContent = fullText;
                document.body.appendChild(tooltip);

                const rect = this.getBoundingClientRect();
                tooltip.style.position = 'fixed';
                tooltip.style.bottom = (window.innerHeight - rect.top + 10) + 'px';
                tooltip.style.left = rect.left + 'px';
                tooltip.style.background = '#1f2937';
                tooltip.style.color = 'white';
                tooltip.style.padding = '8px 12px';
                tooltip.style.borderRadius = '8px';
                tooltip.style.fontSize = '12px';
                tooltip.style.maxWidth = '300px';
                tooltip.style.zIndex = '10000';
                tooltip.style.boxShadow = '0 4px 12px rgba(0,0,0,0.25)';
                tooltip.style.whiteSpace = 'normal';
                tooltip.style.wordWrap = 'break-word';

                this.tooltip = tooltip;
            }
        });

        el.addEventListener('mouseleave', function() {
            if (this.tooltip) {
                this.tooltip.remove();
                this.tooltip = null;
            }
        });
    });
});