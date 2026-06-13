// practices.js - Функциональность страницы успешных практик
// Версия: 1.2 - Добавлена кнопка "Открыть онлайн"

class PracticesApp {
    constructor(config) {
        this.practices = config.practices || [];
        this.currentPage = config.currentPage || 1;
        this.totalPages = config.totalPages || 1;

        this.filters = {
            category: [],
            audience: [],
            format: [],
            difficulty: []
        };

        this.sortBy = 'none';
        this.loading = false;
        this.initialized = false;
        this.currentModalPractice = null;
    }

    async init() {
        if (this.initialized) return;

        console.log('🚀 Инициализация приложения успешных практик...');

        this.initFilters();
        this.initSorting();
        this.initPagination();
        this.initMobileFilters();
        this.initModal();

        this.renderPractices(this.practices);
        this.updatePagination();

        this.initialized = true;
        console.log('✅ Приложение успешных практик инициализировано');
    }

    scrollToTop() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
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

                this.currentPage = 1;
                await this.loadPractices();
                this.updateFilterStyles();
                this.scrollToTop();
            });
        });

        document.getElementById('clearAllFilters')?.addEventListener('click', () => this.clearAllFilters());
    }

    initSorting() {
        const sortSelect = document.getElementById('sortSelect');
        if (sortSelect) {
            sortSelect.value = this.sortBy;
            sortSelect.addEventListener('change', async (e) => {
                this.sortBy = e.target.value;
                this.currentPage = 1;
                await this.loadPractices();
                this.scrollToTop();
            });
        }
    }

    initPagination() {
        document.getElementById('prevPage')?.addEventListener('click', async () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                await this.loadPractices();
                this.scrollToTop();
            }
        });

        document.getElementById('nextPage')?.addEventListener('click', async () => {
            if (this.currentPage < this.totalPages) {
                this.currentPage++;
                await this.loadPractices();
                this.scrollToTop();
            }
        });

        document.addEventListener('click', async (e) => {
            if (e.target.classList.contains('pagination-page')) {
                const page = parseInt(e.target.dataset.page);
                if (page && page !== this.currentPage) {
                    this.currentPage = page;
                    await this.loadPractices();
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
                await this.loadPractices();
                this.scrollToTop();
            });
        }

        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.clearMobileFilters();
            });
        }
    }

    initModal() {
        const modal = document.getElementById('practiceModal');
        const closeBtn = document.getElementById('closePracticeModal');

        document.addEventListener('click', (e) => {
            const expandBtn = e.target.closest('.expand-btn');
            if (expandBtn) {
                e.preventDefault();
                e.stopPropagation();
                const practiceId = expandBtn.dataset.id;
                if (practiceId) {
                    this.openPracticeModal(practiceId);
                }
            }
        });

        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.closePracticeModal();
            });
        }

        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target.classList.contains('modal-overlay')) {
                    this.closePracticeModal();
                }
            });
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal && modal.classList.contains('active')) {
                this.closePracticeModal();
            }
        });
    }

    async openPracticeModal(practiceId) {
        const practice = this.practices.find(p => p.id == practiceId);
        if (!practice) return;

        this.currentModalPractice = practice;
        const modal = document.getElementById('practiceModal');
        const modalBody = document.getElementById('modalBody');

        const hasFile = practice.has_file || false;
        const fileUrl = practice.file_url || '#';
        const fileName = fileUrl.split('/').pop();

        const modalHTML = `
            <div class="modal-practice-content">
                <div class="modal-header-row">
                    <h4 class="modal-practice-title">${this.escapeHtml(practice.title)}</h4>
                </div>

                <div class="modal-section">
                    <h5 class="modal-section-title">Описание</h5>
                    <p class="modal-practice-description">${this.escapeHtml(practice.full_description || practice.short_description || 'Описание отсутствует')}</p>
                </div>

                <div class="modal-section">
                    <h5 class="modal-section-title">Характеристики</h5>
                    <div class="modal-characteristics">
                        <div class="modal-char-item">
                            <div class="char-icon" style="background-color: ${practice.category.icon_color}20;">
                                <i class="${practice.category.icon}" style="color: ${practice.category.icon_color};"></i>
                            </div>
                            <div class="char-content">
                                <div class="char-label">Категория</div>
                                <div class="char-value">${this.escapeHtml(practice.category.name)}</div>
                            </div>
                        </div>

                        ${practice.audience.value ? `
                        <div class="modal-char-item">
                            <div class="char-icon" style="background-color: #10b98120;">
                                <i class="fas fa-users" style="color: #6B7280;"></i>
                            </div>
                            <div class="char-content">
                                <div class="char-label">Целевая аудитория</div>
                                <div class="char-value">${this.escapeHtml(practice.audience.display)}</div>
                            </div>
                        </div>
                        ` : ''}

                        ${practice.format_type.value ? `
                        <div class="modal-char-item">
                            <div class="char-icon" style="background-color: #3b82f620;">
                                <i class="fas fa-chalkboard-user" style="color: #6B7280;"></i>
                            </div>
                            <div class="char-content">
                                <div class="char-label">Формат практики</div>
                                <div class="char-value">${this.escapeHtml(practice.format_type.display)}</div>
                            </div>
                        </div>
                        ` : ''}

                        ${practice.difficulty.value ? `
                        <div class="modal-char-item">
                            <div class="char-icon" style="background-color: ${practice.difficulty.color}20;">
                                <i class="${practice.difficulty.icon}" style="color: ${practice.difficulty.color};"></i>
                            </div>
                            <div class="char-content">
                                <div class="char-label">Уровень сложности</div>
                                <div class="char-value">${this.escapeHtml(practice.difficulty.display)}</div>
                            </div>
                        </div>
                        ` : ''}
                    </div>
                </div>

                <div class="modal-meta-row">
                    <div class="modal-meta-item">
                        <i class="far fa-calendar"></i>
                        <span>Опубликовано ${practice.published_date_display}</span>
                    </div>
                </div>

                ${hasFile ? `
                <div class="modal-actions">
                    <a href="${fileUrl}" class="modal-download-btn" download="${this.escapeHtml(fileName)}">
                        <i class="fas fa-download"></i>
                        Скачать материал
                    </a>
                    <a href="${fileUrl}" class="modal-view-btn" target="_blank" rel="noopener noreferrer">
                        <i class="fas fa-external-link-alt"></i>
                        Открыть онлайн
                    </a>
                </div>
                ` : ''}
            </div>
        `;

        modalBody.innerHTML = modalHTML;
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    closePracticeModal() {
        const modal = document.getElementById('practiceModal');
        modal.classList.remove('active');
        document.body.style.overflow = '';
        this.currentModalPractice = null;
    }

    async loadPractices() {
        if (this.loading) return;

        this.loading = true;
        const practicesGrid = document.getElementById('practicesGrid');
        practicesGrid.classList.add('loading');

        try {
            const params = new URLSearchParams({
                page: this.currentPage,
                sort: this.sortBy,
            });

            Object.keys(this.filters).forEach(category => {
                this.filters[category].forEach(id => params.append(`${category}[]`, id));
            });

            const response = await fetch(`/practices/api/?${params}`);
            const data = await response.json();

            this.totalPages = data.total_pages;
            this.practices = data.practices;
            this.renderPractices(data.practices);
            this.updatePagination();

        } catch (error) {
            console.error('❌ Ошибка загрузки практик:', error);
            practicesGrid.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Ошибка загрузки практик</p>
                </div>
            `;
        } finally {
            this.loading = false;
            practicesGrid.classList.remove('loading');
        }
    }

    renderPractices(practices) {
        const practicesGrid = document.getElementById('practicesGrid');
        if (!practicesGrid) return;

        if (practices.length === 0) {
            practicesGrid.innerHTML = this.getEmptyStateHTML();
            return;
        }

        practicesGrid.innerHTML = practices.map(practice => this.getPracticeCardHTML(practice)).join('');
    }

    getPracticeCardHTML(practice) {
        return `
            <article class="practice-card" data-id="${practice.id}">
                <div class="practice-card-inner">
                    <div class="practice-header">
                        <span class="practice-category-badge" style="background-color: ${practice.category.icon_color}20; color: ${practice.category.icon_color};">
                            <i class="${practice.category.icon}"></i>
                            ${this.escapeHtml(practice.category.name)}
                        </span>
                    </div>

                    <div class="practice-content">
                        <h3 class="practice-title" title="${this.escapeHtml(practice.title)}">${this.escapeHtml(practice.title)}</h3>
                        <p class="practice-description" title="${this.escapeHtml(practice.short_description)}">${this.escapeHtml(practice.short_description)}</p>

                        <div class="practice-badges-vertical">
                            ${practice.audience.value ? `
                            <div class="badge-item">
                                <i class="fas fa-users" style="color: #6B7280;"></i>
                                <span>${this.escapeHtml(practice.audience.display)}</span>
                            </div>
                            ` : ''}

                            ${practice.format_type.value ? `
                            <div class="badge-item">
                                <i class="fas fa-chalkboard-user" style="color: #6B7280;"></i>
                                <span>${this.escapeHtml(practice.format_type.display)}</span>
                            </div>
                            ` : ''}

                            ${practice.difficulty.value ? `
                            <div class="badge-item">
                                <i class="${practice.difficulty.icon}" style="color: ${practice.difficulty.color};"></i>
                                <span>${this.escapeHtml(practice.difficulty.display)}</span>
                            </div>
                            ` : ''}
                        </div>

                        <div class="practice-meta">
                            <span class="date-added">
                                <i class="far fa-calendar"></i>
                                ${practice.published_date_display}
                            </span>
                            <button class="expand-btn" data-id="${practice.id}">
                                <i class="fas fa-expand-alt"></i>
                                Подробнее
                            </button>
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

        if (prevBtn) prevBtn.disabled = this.currentPage === 1;
        if (nextBtn) nextBtn.disabled = this.currentPage >= this.totalPages;

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
            if (checkbox && checkbox.checked) {
                option.classList.add('active');
            } else if (checkbox) {
                option.classList.remove('active');
            }
        });
    }

    async clearAllFilters() {
        this.filters = { category: [], audience: [], format: [], difficulty: [] };

        document.querySelectorAll('.filter-checkbox').forEach(checkbox => {
            checkbox.checked = false;
        });

        const sortSelect = document.getElementById('sortSelect');
        if (sortSelect) sortSelect.value = 'none';
        this.sortBy = 'none';

        this.currentPage = 1;
        await this.loadPractices();
        this.updateFilterStyles();
        this.scrollToTop();
    }

        populateMobileFilters() {
        const modalFilters = document.querySelector('.modal-filters');
        if (!modalFilters) return;

        // Собираем категории из практик
        const categories = [...new Set(this.practices.map(p => p.category?.id).filter(Boolean))];
        const categoriesData = categories.map(id => {
            const practice = this.practices.find(p => p.category?.id === id);
            return practice ? practice.category : null;
        }).filter(Boolean);

        // Захардкоженные значения с метками, иконками и цветами
        const audiences = [
            { value: 'young', label: 'Молодые педагоги (до 3 лет)' },
            { value: 'experienced', label: 'Опытные педагоги' },
            { value: 'all', label: 'Все категории' }
        ];
        const formats = [
            { value: 'single', label: 'Опыт одного педагога', icon: 'fas fa-user', color: '#3b82f6' },
            { value: 'methodological', label: 'Опыт методического объединения', icon: 'fas fa-building', color: '#10b981' },
            { value: 'school', label: 'Школьный проект', icon: 'fas fa-school', color: '#f59e0b' },
            { value: 'municipal', label: 'Муниципальный опыт', icon: 'fas fa-city', color: '#ec4899' },
            { value: 'regional', label: 'Региональный опыт', icon: 'fas fa-map-marked-alt', color: '#8b5cf6' }
        ];
        const difficulties = [
            { value: 'easy', label: 'Лёгкий', icon: 'fas fa-leaf', color: '#10b981' },
            { value: 'medium', label: 'Средний', icon: 'fas fa-chart-simple', color: '#f59e0b' },
            { value: 'hard', label: 'Сложный', icon: 'fas fa-mountain', color: '#ef4444' }
        ];

        // Универсальная функция генерации группы аккордеона
        const generateFilterGroup = (title, category, items, icon, renderItem) => {
            const selectedCount = this.filters[category].length;
            const countBadge = selectedCount > 0
                ? `<span class="filter-count-badge">${selectedCount}</span>`
                : '';

            return `
                <div class="mobile-filter-group" data-category="${category}">
                    <div class="mobile-filter-group-header" onclick="window.practicesApp.toggleFilterGroup(this)">
                        <div class="mobile-filter-group-title">
                            <i class="fas ${icon}"></i>
                            <span>${title}</span>
                            ${countBadge}
                        </div>
                        <i class="fas fa-chevron-down mobile-filter-toggle-icon"></i>
                    </div>
                    <div class="mobile-filter-group-content">
                        <div class="filter-options">
                            ${items.map(item => renderItem(item)).join('')}
                        </div>
                    </div>
                </div>
            `;
        };

        const filtersHTML = `
            <div class="mobile-filters-accordion">
                ${generateFilterGroup('По категориям', 'category', categoriesData, 'fa-layer-group', cat => `
                    <label class="filter-option">
                        <input type="checkbox" class="filter-checkbox" data-category="category" value="${cat.id}" ${this.filters.category.includes(cat.id.toString()) ? 'checked' : ''}>
                        <span class="filter-color-indicator" style="background-color: ${cat.icon_color};"></span>
                        <span class="filter-option-text">${this.escapeHtml(cat.name)}</span>
                    </label>
                `)}
                ${generateFilterGroup('Целевая аудитория', 'audience', audiences, 'fa-users', aud => `
                    <label class="filter-option">
                        <input type="checkbox" class="filter-checkbox" data-category="audience" value="${aud.value}" ${this.filters.audience.includes(aud.value) ? 'checked' : ''}>
                        <span class="filter-option-text">${aud.label}</span>
                    </label>
                `)}
                ${generateFilterGroup('Формат практики', 'format', formats, 'fa-chalkboard-user', fmt => `
                    <label class="filter-option">
                        <input type="checkbox" class="filter-checkbox" data-category="format" value="${fmt.value}" ${this.filters.format.includes(fmt.value) ? 'checked' : ''}>
                        <span class="filter-icon-indicator" style="background-color: ${fmt.color}20; color: ${fmt.color};">
                            <i class="${fmt.icon}"></i>
                        </span>
                        <span class="filter-option-text">${fmt.label}</span>
                    </label>
                `)}
                ${generateFilterGroup('Уровень сложности', 'difficulty', difficulties, 'fa-signal', diff => `
                    <label class="filter-option">
                        <input type="checkbox" class="filter-checkbox" data-category="difficulty" value="${diff.value}" ${this.filters.difficulty.includes(diff.value) ? 'checked' : ''}>
                        <span class="filter-icon-indicator" style="background-color: ${diff.color}20; color: ${diff.color};">
                            <i class="${diff.icon}"></i>
                        </span>
                        <span class="filter-option-text">${diff.label}</span>
                    </label>
                `)}
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

    applyMobileFilters() {
        const modalFilters = document.querySelector('.modal-filters');
        if (!modalFilters) return;

        const newFilters = { category: [], audience: [], format: [], difficulty: [] };
        modalFilters.querySelectorAll('.filter-checkbox:checked').forEach(checkbox => {
            const category = checkbox.dataset.category;
            const value = checkbox.value;
            if (!newFilters[category].includes(value)) newFilters[category].push(value);
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
        this.filters = { category: [], audience: [], format: [], difficulty: [] };

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
                <div class="empty-state-icon"><i class="fas fa-star-of-life"></i></div>
                <h3 class="empty-state-title">Практики не найдены</h3>
                <p class="empty-state-description">Попробуйте изменить параметры фильтрации</p>
                <button class="btn-reset-filters" onclick="window.practicesApp.clearAllFilters()"><i class="fas fa-redo"></i> Сбросить фильтры</button>
            </div>
        `;
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    if (typeof practicesAppConfig !== 'undefined') {
        window.practicesApp = new PracticesApp(practicesAppConfig);
        window.practicesApp.init();
    }
});

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const modal = document.getElementById('mobileFiltersModal');
        if (modal && modal.classList.contains('active')) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
        const practiceModal = document.getElementById('practiceModal');
        if (practiceModal && practiceModal.classList.contains('active')) {
            practiceModal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }
});

window.addEventListener('popstate', function() {
    const params = new URLSearchParams(window.location.search);
    const page = parseInt(params.get('page')) || 1;
    if (window.practicesApp && window.practicesApp.currentPage !== page) {
        window.practicesApp.currentPage = page;
        window.practicesApp.loadPractices();
        if (window.practicesApp.scrollToTop) window.practicesApp.scrollToTop();
    }
});

(function() {
    if (document.getElementById('scrollToTop')) return;
    const scrollButton = document.createElement('button');
    scrollButton.id = 'scrollToTop';
    scrollButton.className = 'scroll-to-top';
    scrollButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
    document.body.appendChild(scrollButton);
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) scrollButton.classList.add('show');
        else scrollButton.classList.remove('show');
    });
    scrollButton.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
})();