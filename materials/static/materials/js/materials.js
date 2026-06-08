// materials.js - Функциональность страницы методических материалов с поддержкой избранного через БД
// Версия: 3.0 - Добавлена сортировка "Без сортировки" по умолчанию

class MaterialsApp {
    constructor(config) {
        this.materials = config.materials || [];
        this.subjects = config.subjects;
        this.types = config.types;
        this.difficulty = config.difficulty;
        this.grades = config.grades;
        this.formats = config.formats;
        this.assessment = config.assessment;
        this.additional = config.additional;
        this.itemsPerPage = config.itemsPerPage || 12;
        this.currentPage = config.currentPage || 1;
        this.totalPages = config.totalPages || 1;

        this.filters = {
            subject: [],
            type: [],
            difficulty: [],
            grade: [],
            format: [],
            assessment: [],
            additional: []
        };

        this.favorites = new Set();
        this.sortBy = 'none';  // ← ИЗМЕНЕНО: по умолчанию "Без сортировки"
        this.loading = false;
        this.initialized = false;
        this.currentModalMaterial = null;
        this.isAuthenticated = window.userAuthenticated || false;
        this.favoritesLoaded = false;
    }

    async init() {
        if (this.initialized) return;

        console.log('🚀 Инициализация приложения методических материалов...');
        console.log('Пользователь авторизован:', this.isAuthenticated);
        console.log('Сортировка по умолчанию:', this.sortBy);

        this.initFilters();
        this.initSorting();
        this.initPagination();
        this.initMobileFilters();
        this.initModal();
        this.initAuthModal();

        if (this.isAuthenticated) {
            await this.loadFavoritesFromDB();
        }

        this.renderMaterials(this.materials);
        this.updatePagination();

        this.initialized = true;
        console.log('✅ Приложение методических материалов инициализировано');
    }

    // Функция для прокрутки наверх страницы
    scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }

    initAuthModal() {
        if (!document.getElementById('authRequiredModal')) {
            const modalHTML = `
                <div class="auth-modal" id="authRequiredModal">
                    <div class="auth-modal-overlay"></div>
                    <div class="auth-modal-content">
                        <div class="auth-modal-header">
                            <div class="auth-modal-icon">
                                <i class="fas fa-lock"></i>
                            </div>
                            <h3 class="auth-modal-title">Требуется авторизация</h3>
                            <button class="auth-modal-close" id="closeAuthModal">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        <div class="auth-modal-body">
                            <p class="auth-modal-message">
                                Чтобы сохранять материалы в избранное, необходимо войти в свой аккаунт или зарегистрироваться.
                            </p>
                            <div class="auth-modal-actions">
                                <a href="${window.loginUrl}" class="auth-modal-btn auth-modal-btn-primary">
                                    <i class="fas fa-sign-in-alt"></i>
                                    Войти
                                </a>
                                <a href="${window.registerUrl}" class="auth-modal-btn auth-modal-btn-secondary">
                                    <i class="fas fa-user-plus"></i>
                                    Регистрация
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHTML);

            const modal = document.getElementById('authRequiredModal');
            const closeBtn = document.getElementById('closeAuthModal');
            const overlay = modal.querySelector('.auth-modal-overlay');

            closeBtn.addEventListener('click', () => this.closeAuthModal());
            overlay.addEventListener('click', () => this.closeAuthModal());

            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && modal.classList.contains('active')) {
                    this.closeAuthModal();
                }
            });
        }
    }

    openAuthModal() {
        const modal = document.getElementById('authRequiredModal');
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }

    closeAuthModal() {
        const modal = document.getElementById('authRequiredModal');
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    async loadFavoritesFromDB() {
        if (this.favoritesLoaded) return;

        try {
            console.log('📥 Загрузка избранного из БД...');

            const response = await fetch('/account/favorites/list/', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                console.error('Ошибка загрузки избранного:', response.status);
                return;
            }

            const data = await response.json();

            if (data.success && data.favorites) {
                this.favorites.clear();
                data.favorites.forEach(id => this.favorites.add(id.toString()));
                console.log(`✅ Загружено ${this.favorites.size} избранных материалов`);
                this.updateAllFavoriteIcons();
            }

            this.favoritesLoaded = true;

        } catch (error) {
            console.error('❌ Ошибка загрузки избранного:', error);
        }
    }

    updateAllFavoriteIcons() {
        document.querySelectorAll('.favorite-btn').forEach(btn => {
            const materialId = btn.dataset.id;
            const icon = btn.querySelector('i');

            if (this.favorites.has(materialId)) {
                btn.classList.add('active');
                icon.classList.remove('far');
                icon.classList.add('fas');
            } else {
                btn.classList.remove('active');
                icon.classList.remove('fas');
                icon.classList.add('far');
            }
        });
    }

    async toggleFavorite(materialId) {
        if (!this.isAuthenticated) {
            this.openAuthModal();
            return;
        }

        try {
            const csrftoken = this.getCookie('csrftoken');
            const isFavorite = this.favorites.has(materialId.toString());

            const url = isFavorite
                ? `/account/favorites/remove/${materialId}/`
                : '/account/favorites/add/';

            const bodyData = isFavorite ? null : JSON.stringify({ material_id: materialId });

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: bodyData
            });

            const data = await response.json();

            if (data.success) {
                if (isFavorite) {
                    this.favorites.delete(materialId.toString());
                    console.log('✅ Материал удален из избранного');
                } else {
                    this.favorites.add(materialId.toString());
                    console.log('✅ Материал добавлен в избранное');
                }

                this.updateFavoriteIcon(materialId, !isFavorite);

                if (this.currentModalMaterial && this.currentModalMaterial.id == materialId) {
                    this.updateModalFavoriteIcon(!isFavorite);
                }
            } else {
                console.error('❌ Ошибка:', data.message);
                alert('Ошибка: ' + data.message);
            }

        } catch (error) {
            console.error('❌ Ошибка при работе с избранным:', error);
            alert('Произошла ошибка. Попробуйте еще раз.');
        }
    }

    updateFavoriteIcon(materialId, isFavorite) {
        const btn = document.querySelector(`.favorite-btn[data-id="${materialId}"]`);
        if (btn) {
            const icon = btn.querySelector('i');
            if (isFavorite) {
                btn.classList.add('active');
                icon.classList.remove('far');
                icon.classList.add('fas');
            } else {
                btn.classList.remove('active');
                icon.classList.remove('fas');
                icon.classList.add('far');
            }
        }
    }

    updateModalFavoriteIcon(isFavorite) {
        const modalBtn = document.querySelector('.modal-favorite-btn');
        if (modalBtn) {
            const modalIcon = modalBtn.querySelector('i');
            if (isFavorite) {
                modalBtn.classList.add('active');
                modalIcon.classList.remove('far');
                modalIcon.classList.add('fas');
            } else {
                modalBtn.classList.remove('active');
                modalIcon.classList.remove('fas');
                modalIcon.classList.add('far');
            }
        }
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
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
                await this.loadMaterials();
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
            sortSelect.value = this.sortBy;
            sortSelect.addEventListener('change', async (e) => {
                this.sortBy = e.target.value;
                this.currentPage = 1;
                await this.loadMaterials();
                // Прокрутка наверх после изменения сортировки
                this.scrollToTop();
            });
        }
    }

    initPagination() {
        document.getElementById('prevPage')?.addEventListener('click', async () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                await this.loadMaterials();
                // Прокрутка наверх при смене страницы
                this.scrollToTop();
            }
        });

        document.getElementById('nextPage')?.addEventListener('click', async () => {
            if (this.currentPage < this.totalPages) {
                this.currentPage++;
                await this.loadMaterials();
                // Прокрутка наверх при смене страницы
                this.scrollToTop();
            }
        });

        document.addEventListener('click', async (e) => {
            if (e.target.classList.contains('pagination-page')) {
                const page = parseInt(e.target.dataset.page);
                if (page && page !== this.currentPage) {
                    this.currentPage = page;
                    await this.loadMaterials();
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
                await this.loadMaterials();
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

    initModal() {
        const modal = document.getElementById('materialModal');
        const closeBtn = document.getElementById('closeMaterialModal');

        document.addEventListener('click', (e) => {
            if (e.target.closest('.expand-btn')) {
                const btn = e.target.closest('.expand-btn');
                const materialId = btn.dataset.id;
                this.openMaterialModal(materialId);
                e.stopPropagation();
            }
        });

        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.closeMaterialModal();
            });
        }

        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target.classList.contains('modal-overlay')) {
                    this.closeMaterialModal();
                }
            });
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.classList.contains('active')) {
                this.closeMaterialModal();
            }
        });
    }

    async openMaterialModal(materialId) {
        const material = this.materials.find(m => m.id == materialId);
        if (!material) return;

        this.currentModalMaterial = material;
        const modal = document.getElementById('materialModal');
        const modalBody = document.getElementById('modalBody');

        const isFavorite = this.favorites.has(materialId.toString());
        const favoriteIcon = isFavorite ? 'fas fa-heart' : 'far fa-heart';
        const favoriteClass = isFavorite ? 'active' : '';

        const modalHTML = `
            <div class="modal-material-content">
                <div class="modal-header-row">
                    <h4 class="modal-material-title">${this.escapeHtml(material.title)}</h4>
                    <button class="modal-favorite-btn ${favoriteClass}" data-id="${material.id}">
                        <i class="${favoriteIcon}"></i>
                    </button>
                </div>

                <div class="modal-section">
                    <h5 class="modal-section-title">Описание</h5>
                    <p class="modal-material-description">${this.escapeHtml(material.description)}</p>
                </div>

                <div class="modal-section">
                    <h5 class="modal-section-title">Характеристики</h5>
                    <div class="modal-characteristics">
                        <div class="modal-char-item">
                            <div class="char-icon" style="background-color: ${material.subject.bg_color}20;">
                                <i class="fas fa-book" style="color: ${material.subject.bg_color};"></i>
                            </div>
                            <div class="char-content">
                                <div class="char-label">Предмет</div>
                                <div class="char-value">${this.escapeHtml(material.subject.name)}</div>
                            </div>
                        </div>

                        <div class="modal-char-item">
                            <div class="char-icon" style="background-color: ${material.type.bg_color}20;">
                                <i class="fas fa-file-alt" style="color: ${material.type.bg_color};"></i>
                            </div>
                            <div class="char-content">
                                <div class="char-label">Тип материала</div>
                                <div class="char-value">${this.escapeHtml(material.type.name)}</div>
                            </div>
                        </div>

                        <div class="modal-char-item">
                            <div class="char-icon" style="background-color: #E5F1FC;">
                                <i class="fas fa-graduation-cap" style="color: #032D43;"></i>
                            </div>
                            <div class="char-content">
                                <div class="char-label">Класс/возрастная группа</div>
                                <div class="char-value">${this.escapeHtml(material.grade.name)}</div>
                            </div>
                        </div>

                        <div class="modal-char-item">
                            <div class="char-icon" style="background-color: #FEF3C7;">
                                <i class="fas fa-chart-line" style="color: #92400e;"></i>
                            </div>
                            <div class="char-content">
                                <div class="char-label">Уровень сложности</div>
                                <div class="char-value">${this.escapeHtml(material.difficulty.name)}</div>
                            </div>
                        </div>

                        <div class="modal-char-item">
                            <div class="char-icon" style="background-color: #F3F4F6;">
                                <i class="fas fa-users" style="color: #374151;"></i>
                            </div>
                            <div class="char-content">
                                <div class="char-label">Формат работы</div>
                                <div class="char-value">${this.escapeHtml(material.format.name)}</div>
                            </div>
                        </div>

                        <div class="modal-char-item">
                            <div class="char-icon" style="background-color: #F0F9FF;">
                                <i class="fas fa-star" style="color: #075985;"></i>
                            </div>
                            <div class="char-content">
                                <div class="char-label">Система оценки</div>
                                <div class="char-value">${this.escapeHtml(material.assessment.name)}</div>
                            </div>
                        </div>

                        <div class="modal-char-item">
                            <div class="char-icon" style="background-color: #FAF5FF;">
                                <i class="fas fa-tags" style="color: #6b21a8;"></i>
                            </div>
                            <div class="char-content">
                                <div class="char-label">Дополнительная категория</div>
                                <div class="char-value">${this.escapeHtml(material.additional.name)}</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="modal-actions">
                    <a href="${material.file_url || '#'}" class="modal-download-btn" target="_blank" ${!material.file_url ? 'disabled' : ''}>
                        <i class="fas fa-download"></i>
                        Скачать материал
                    </a>
                </div>
            </div>
        `;

        modalBody.innerHTML = modalHTML;
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';

        const modalFavoriteBtn = modalBody.querySelector('.modal-favorite-btn');
        if (modalFavoriteBtn) {
            modalFavoriteBtn.addEventListener('click', (e) => {
                this.toggleFavorite(materialId);
                e.stopPropagation();
            });
        }
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    closeMaterialModal() {
        const modal = document.getElementById('materialModal');
        modal.classList.remove('active');
        document.body.style.overflow = '';
        this.currentModalMaterial = null;
    }

    async loadMaterials() {
        if (this.loading) return;

        this.loading = true;
        const materialsGrid = document.getElementById('materialsGrid');
        materialsGrid.classList.add('loading');

        try {
            const params = new URLSearchParams({
                page: this.currentPage,
                sort: this.sortBy,
            });

            Object.keys(this.filters).forEach(category => {
                this.filters[category].forEach(id => params.append(`${category}[]`, id));
            });

            const response = await fetch(`/materials/api/?${params}`);
            const data = await response.json();

            this.totalPages = data.total_pages;
            this.materials = data.materials;
            this.renderMaterials(data.materials);
            this.updatePagination();

            const url = new URL(window.location);
            url.searchParams.set('page', this.currentPage);
            window.history.pushState({}, '', url);

        } catch (error) {
            console.error('❌ Ошибка загрузки материалов:', error);
            materialsGrid.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Ошибка загрузки материалов</p>
                </div>
            `;
        } finally {
            this.loading = false;
            materialsGrid.classList.remove('loading');
        }
    }

    renderMaterials(materials) {
        const materialsGrid = document.getElementById('materialsGrid');
        if (!materialsGrid) return;

        if (materials.length === 0) {
            materialsGrid.innerHTML = this.getEmptyStateHTML();
            return;
        }

        materialsGrid.innerHTML = materials.map(material => this.getMaterialCardHTML(material)).join('');

        document.querySelectorAll('.favorite-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const materialId = btn.dataset.id;
                this.toggleFavorite(materialId);
                e.stopPropagation();
            });
        });
    }

    getMaterialCardHTML(material) {
        const isFavorite = this.favorites.has(material.id.toString());
        const favoriteIcon = isFavorite ? 'fas fa-heart' : 'far fa-heart';
        const favoriteClass = isFavorite ? 'active' : '';

        return `
            <article class="material-card" data-id="${material.id}">
                <div class="material-card-inner">
                    <div class="material-header">
                        <span class="material-type-badge" style="background-color: ${material.type.bg_color}; color: ${material.type.text_color};">
                            ${this.escapeHtml(material.type.name)}
                        </span>
                        <button class="favorite-btn ${favoriteClass}" data-id="${material.id}">
                            <i class="${favoriteIcon}"></i>
                        </button>
                    </div>

                    <div class="material-content">
                        <h3 class="material-title" title="${this.escapeHtml(material.title)}">${this.escapeHtml(material.title)}</h3>
                        <p class="material-description" title="${this.escapeHtml(material.description)}">${this.escapeHtml(material.description)}</p>

                        <div class="material-badges-vertical">
                            <div class="badge-item">
                                <i class="fas fa-book" style="color: ${material.subject.bg_color};"></i>
                                <span>${this.escapeHtml(material.subject.name)}</span>
                            </div>
                            <div class="badge-item">
                                <i class="fas fa-graduation-cap" style="color: ${material.type.bg_color};"></i>
                                <span>${this.escapeHtml(material.grade.name)}</span>
                            </div>
                            <div class="badge-item">
                                <i class="fas fa-chart-line" style="color: #6B7280;"></i>
                                <span>${this.escapeHtml(material.difficulty.name)}</span>
                            </div>
                        </div>

                        <div class="material-meta">
                            <span class="date-added">
                                <i class="far fa-calendar"></i>
                                ${material.date_added || 'Дата не указана'}
                            </span>
                            <button class="expand-btn" data-id="${material.id}">
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

    async clearAllFilters() {
        this.filters = {
            subject: [],
            type: [],
            difficulty: [],
            grade: [],
            format: [],
            assessment: [],
            additional: []
        };

        document.querySelectorAll('.filter-checkbox').forEach(checkbox => {
            checkbox.checked = false;
        });

        const sortSelect = document.getElementById('sortSelect');
        if (sortSelect) {
            sortSelect.value = 'none';
        }
        this.sortBy = 'none';

        this.currentPage = 1;
        await this.loadMaterials();
        this.updateFilterStyles();
        // Прокрутка наверх после сброса фильтров
        this.scrollToTop();
    }

    populateMobileFilters() {
        const modalFilters = document.querySelector('.modal-filters');
        if (!modalFilters) return;

        const filtersHTML = `
            <div class="filters-list">
                <div class="filter-group">
                    <h4 class="filter-group-title">По предметным областям</h4>
                    <div class="filter-options">
                        ${Object.values(this.subjects).map(subject => `
                            <label class="filter-option">
                                <input type="checkbox" class="filter-checkbox"
                                       data-category="subject" value="${subject.id}"
                                       ${this.filters.subject.includes(subject.id.toString()) ? 'checked' : ''}>
                                <span class="filter-color-indicator" style="background-color: ${subject.bg_color};"></span>
                                <span class="filter-option-text">${this.escapeHtml(subject.name)}</span>
                            </label>
                        `).join('')}
                    </div>
                </div>

                <div class="filter-group">
                    <h4 class="filter-group-title">По типу материалов</h4>
                    <div class="filter-options">
                        ${Object.values(this.types).map(type => `
                            <label class="filter-option">
                                <input type="checkbox" class="filter-checkbox"
                                       data-category="type" value="${type.id}"
                                       ${this.filters.type.includes(type.id.toString()) ? 'checked' : ''}>
                                <span class="filter-color-indicator" style="background-color: ${type.bg_color};"></span>
                                <span class="filter-option-text">${this.escapeHtml(type.name)}</span>
                            </label>
                        `).join('')}
                    </div>
                </div>

                <div class="filter-group">
                    <h4 class="filter-group-title">По уровню сложности</h4>
                    <div class="filter-options">
                        ${Object.values(this.difficulty).map(diff => `
                            <label class="filter-option">
                                <input type="checkbox" class="filter-checkbox"
                                       data-category="difficulty" value="${diff.id}"
                                       ${this.filters.difficulty.includes(diff.id.toString()) ? 'checked' : ''}>
                                <span class="filter-option-text">${this.escapeHtml(diff.name)}</span>
                            </label>
                        `).join('')}
                    </div>
                </div>

                <div class="filter-group">
                    <h4 class="filter-group-title">По классам/возрастным группам</h4>
                    <div class="filter-options">
                        ${Object.values(this.grades).map(grade => `
                            <label class="filter-option">
                                <input type="checkbox" class="filter-checkbox"
                                       data-category="grade" value="${grade.id}"
                                       ${this.filters.grade.includes(grade.id.toString()) ? 'checked' : ''}>
                                <span class="filter-option-text">${this.escapeHtml(grade.name)}</span>
                            </label>
                        `).join('')}
                    </div>
                </div>

                <div class="filter-group">
                    <h4 class="filter-group-title">По форматам работы</h4>
                    <div class="filter-options">
                        ${Object.values(this.formats).map(format => `
                            <label class="filter-option">
                                <input type="checkbox" class="filter-checkbox"
                                       data-category="format" value="${format.id}"
                                       ${this.filters.format.includes(format.id.toString()) ? 'checked' : ''}>
                                <span class="filter-option-text">${this.escapeHtml(format.name)}</span>
                            </label>
                        `).join('')}
                    </div>
                </div>

                <div class="filter-group">
                    <h4 class="filter-group-title">По системе оценки</h4>
                    <div class="filter-options">
                        ${Object.values(this.assessment).map(assess => `
                            <label class="filter-option">
                                <input type="checkbox" class="filter-checkbox"
                                       data-category="assessment" value="${assess.id}"
                                       ${this.filters.assessment.includes(assess.id.toString()) ? 'checked' : ''}>
                                <span class="filter-option-text">${this.escapeHtml(assess.name)}</span>
                            </label>
                        `).join('')}
                    </div>
                </div>

                <div class="filter-group">
                    <h4 class="filter-group-title">Дополнительные категории</h4>
                    <div class="filter-options">
                        ${Object.values(this.additional).map(add => `
                            <label class="filter-option">
                                <input type="checkbox" class="filter-checkbox"
                                       data-category="additional" value="${add.id}"
                                       ${this.filters.additional.includes(add.id.toString()) ? 'checked' : ''}>
                                <span class="filter-option-text">${this.escapeHtml(add.name)}</span>
                            </label>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;

        modalFilters.innerHTML = filtersHTML;

        modalFilters.querySelectorAll('.filter-checkbox').forEach(checkbox => {
            const category = checkbox.dataset.category;
            const value = checkbox.value;
            checkbox.checked = this.filters[category].includes(value);
        });
    }

    applyMobileFilters() {
        const modalFilters = document.querySelector('.modal-filters');
        if (!modalFilters) return;

        const newFilters = {
            subject: [],
            type: [],
            difficulty: [],
            grade: [],
            format: [],
            assessment: [],
            additional: []
        };

        modalFilters.querySelectorAll('.filter-checkbox:checked').forEach(checkbox => {
            const category = checkbox.dataset.category;
            const value = checkbox.value;
            newFilters[category].push(value);
        });

        this.filters = newFilters;
        this.syncMainFilters();
    }

    clearMobileFilters() {
        const modalFilters = document.querySelector('.modal-filters');
        if (!modalFilters) return;

        modalFilters.querySelectorAll('.filter-checkbox').forEach(checkbox => {
            checkbox.checked = false;
        });
    }

    syncMainFilters() {
        document.querySelectorAll('.filter-checkbox').forEach(checkbox => {
            const category = checkbox.dataset.category;
            const value = checkbox.value;
            checkbox.checked = this.filters[category].includes(value);
        });
    }

    getEmptyStateHTML() {
        return `
            <div class="empty-state">
                <div class="empty-state-icon">
                    <i class="fas fa-book-open"></i>
                </div>
                <h3 class="empty-state-title">Материалы не найдены</h3>
                <p class="empty-state-description">
                    Попробуйте изменить параметры фильтрации
                </p>
                <button class="btn-reset-filters" onclick="window.materialsApp.clearAllFilters()">
                    <i class="fas fa-redo"></i> Сбросить фильтры
                </button>
            </div>
        `;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    if (typeof materialsAppConfig !== 'undefined') {
        window.materialsApp = new MaterialsApp(materialsAppConfig);
        window.materialsApp.init();
    }
});

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const modal = document.getElementById('mobileFiltersModal');
        if (modal && modal.classList.contains('active')) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }

        const authModal = document.getElementById('authRequiredModal');
        if (authModal && authModal.classList.contains('active')) {
            authModal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }
});

window.addEventListener('popstate', function() {
    const params = new URLSearchParams(window.location.search);
    const page = parseInt(params.get('page')) || 1;

    if (window.materialsApp && window.materialsApp.currentPage !== page) {
        window.materialsApp.currentPage = page;
        window.materialsApp.loadMaterials();
        if (window.materialsApp.scrollToTop) {
            window.materialsApp.scrollToTop();
        }
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