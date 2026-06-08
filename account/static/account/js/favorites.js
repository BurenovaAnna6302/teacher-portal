// favorites.js - Управление избранным (только материалы)
// Версия: 4.2 - Добавлено модальное окно подтверждения

class FavoritesApp {
    constructor() {
        this.favoritesGrid = document.getElementById('favoritesGrid');
        this.clearAllBtn = document.getElementById('clearAllFavorites');
        this.notification = null;
        this.modal = document.getElementById('materialModal');
        this.modalBody = document.getElementById('modalBody');
        this.closeModalBtn = document.getElementById('closeMaterialModal');
        this.currentModalMaterial = null;
        this.confirmModal = null; // Модальное окно подтверждения
        this.pendingDeleteId = null; // ID для удаления
        this.pendingDeleteCard = null; // Карточка для удаления

        console.log('FavoritesApp инициализирован');
    }

    init() {
        console.log('Инициализация страницы избранного...');

        // Создаем модальное окно подтверждения
        this.createConfirmModal();

        // Инициализация кнопок удаления
        this.initRemoveButtons();

        // Инициализация кнопки очистки
        if (this.clearAllBtn) {
            this.clearAllBtn.addEventListener('click', () => this.showClearAllConfirm());
        }

        // Инициализация модального окна для просмотра материала
        this.initModal();

        // Инициализация кнопок "Подробнее"
        this.initExpandButtons();

        console.log('Инициализация завершена');
    }

    // ========== СОЗДАНИЕ МОДАЛЬНОГО ОКНА ПОДТВЕРЖДЕНИЯ ==========
    createConfirmModal() {
        // Проверяем, существует ли уже модальное окно
        if (document.getElementById('confirmDeleteModal')) {
            this.confirmModal = document.getElementById('confirmDeleteModal');
            return;
        }

        const modalHTML = `
            <div class="confirm-delete-modal" id="confirmDeleteModal" style="display: none;">
                <div class="modal-overlay"></div>
                <div class="modal-content">
                    <div class="modal-icon">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <h3 class="modal-title">Подтверждение удаления</h3>
                    <p class="modal-message" id="confirmDeleteMessage">
                        Вы уверены, что хотите удалить этот материал из избранного?
                    </p>
                    <div class="modal-actions">
                        <button class="btn-cancel" id="cancelDeleteBtn">
                            <i class="fas fa-times"></i> Отмена
                        </button>
                        <button class="btn-confirm" id="confirmDeleteBtn">
                            <i class="fas fa-trash"></i> Удалить
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.confirmModal = document.getElementById('confirmDeleteModal');

        // Добавляем стили
        this.addConfirmModalStyles();

        // Инициализируем обработчики модального окна
        this.initConfirmModalHandlers();
    }

    addConfirmModalStyles() {
        if (document.getElementById('confirm-modal-styles')) return;

        const style = document.createElement('style');
        style.id = 'confirm-modal-styles';
        style.textContent = `
            .confirm-delete-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 10001;
                display: none;
                align-items: center;
                justify-content: center;
                font-family: 'Manrope', sans-serif;
            }

            .confirm-delete-modal .modal-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(4px);
                cursor: pointer;
            }

            .confirm-delete-modal .modal-content {
                position: relative;
                background: white;
                border-radius: 20px;
                padding: 32px;
                max-width: 400px;
                width: 90%;
                text-align: center;
                animation: modalFadeIn 0.3s ease;
                box-shadow: 0 20px 35px rgba(0, 0, 0, 0.2);
                z-index: 10002;
            }

            .confirm-delete-modal .modal-icon {
                width: 70px;
                height: 70px;
                background: rgba(239, 68, 68, 0.1);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 20px;
            }

            .confirm-delete-modal .modal-icon i {
                font-size: 32px;
                color: #EF4444;
            }

            .confirm-delete-modal .modal-title {
                font-size: 22px;
                font-weight: 700;
                color: #1a1a1a;
                margin-bottom: 12px;
            }

            .confirm-delete-modal .modal-message {
                font-size: 15px;
                color: #6B7280;
                margin-bottom: 28px;
                line-height: 1.5;
            }

            .confirm-delete-modal .modal-actions {
                display: flex;
                gap: 12px;
                justify-content: center;
            }

            .confirm-delete-modal .btn-cancel,
            .confirm-delete-modal .btn-confirm {
                flex: 1;
                padding: 12px 20px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s;
                border: none;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }

            .confirm-delete-modal .btn-cancel {
                background: #f3f4f6;
                color: #374151;
            }

            .confirm-delete-modal .btn-cancel:hover {
                background: #e5e7eb;
                transform: translateY(-2px);
            }

            .confirm-delete-modal .btn-confirm {
                background: #EF4444;
                color: white;
            }

            .confirm-delete-modal .btn-confirm:hover {
                background: #DC2626;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
            }

            @keyframes modalFadeIn {
                from {
                    opacity: 0;
                    transform: scale(0.95);
                }
                to {
                    opacity: 1;
                    transform: scale(1);
                }
            }

            @keyframes modalFadeOut {
                from {
                    opacity: 1;
                    transform: scale(1);
                }
                to {
                    opacity: 0;
                    transform: scale(0.95);
                }
            }

            .favorite-card.removing {
                animation: cardFadeOut 0.3s ease forwards;
            }

            @keyframes cardFadeOut {
                from {
                    opacity: 1;
                    transform: translateX(0);
                }
                to {
                    opacity: 0;
                    transform: translateX(-20px);
                }
            }
        `;
        document.head.appendChild(style);
    }

    initConfirmModalHandlers() {
        if (!this.confirmModal) return;

        const cancelBtn = document.getElementById('cancelDeleteBtn');
        const confirmBtn = document.getElementById('confirmDeleteBtn');
        const overlay = this.confirmModal.querySelector('.modal-overlay');

        const closeModal = () => {
            this.confirmModal.style.animation = 'modalFadeOut 0.2s ease';
            setTimeout(() => {
                this.confirmModal.style.display = 'none';
                this.confirmModal.style.animation = '';
                document.body.style.overflow = '';
                this.pendingDeleteId = null;
                this.pendingDeleteCard = null;
            }, 200);
        };

        if (cancelBtn) cancelBtn.addEventListener('click', closeModal);
        if (overlay) overlay.addEventListener('click', closeModal);

        if (confirmBtn) {
            confirmBtn.addEventListener('click', async () => {
                if (this.pendingDeleteId && this.pendingDeleteCard) {
                    await this.performRemove(this.pendingDeleteId, this.pendingDeleteCard);
                }
                closeModal();
            });
        }

        // Закрытие по Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.confirmModal && this.confirmModal.style.display === 'flex') {
                closeModal();
            }
        });
    }

    showConfirmModal(itemId, cardElement) {
        this.pendingDeleteId = itemId;
        this.pendingDeleteCard = cardElement;

        if (this.confirmModal) {
            this.confirmModal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }
    }

    // ========== ОСТАЛЬНЫЕ МЕТОДЫ ==========
    initModal() {
        if (!this.modal || !this.closeModalBtn) return;

        this.closeModalBtn.addEventListener('click', () => {
            this.closeModal();
        });

        this.modal.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay')) {
                this.closeModal();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('active')) {
                this.closeModal();
            }
        });
    }

    initExpandButtons() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('.expand-btn')) {
                const btn = e.target.closest('.expand-btn');
                const materialId = btn.dataset.id;
                this.openMaterialModal(materialId);
                e.stopPropagation();
            }
        });
    }

    initRemoveButtons() {
        const removeButtons = document.querySelectorAll('.favorite-remove-btn');
        console.log('Найдено кнопок удаления:', removeButtons.length);

        removeButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.stopPropagation();
                e.preventDefault();

                const card = button.closest('.favorite-card');
                const itemId = button.dataset.id;

                console.log('Удаление элемента:', itemId);

                if (itemId && card) {
                    this.showConfirmModal(itemId, card);
                }
            });
        });
    }

    async performRemove(itemId, cardElement) {
        console.log('Выполнение удаления:', itemId);

        // Показываем анимацию удаления
        if (cardElement) {
            cardElement.classList.add('removing');
        }

        try {
            const response = await fetch(`/account/favorites/remove/${itemId}/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCsrfToken(),
                    'Content-Type': 'application/json'
                },
            });

            const data = await response.json();

            if (data.success) {
                // Удаляем карточку после анимации
                setTimeout(() => {
                    if (cardElement && cardElement.parentNode) {
                        cardElement.remove();
                    }
                    this.showNotification('Материал удален из избранного', 'success');

                    // Обновляем счетчик
                    this.updateSidebarCounter();

                    // Если избранное пустое, перезагружаем страницу
                    if (document.querySelectorAll('.favorite-card').length === 0) {
                        setTimeout(() => location.reload(), 800);
                    }
                }, 300);
            } else {
                if (cardElement) {
                    cardElement.classList.remove('removing');
                }
                this.showNotification(data.message || 'Не удалось удалить из избранного', 'error');
            }
        } catch (error) {
            console.error('Ошибка при удалении из избранного:', error);
            if (cardElement) {
                cardElement.classList.remove('removing');
            }
            this.showNotification('Проблема с соединением. Попробуйте позже.', 'error');
        }
    }

    async openMaterialModal(materialId) {
        const favoriteCard = document.querySelector(`.favorite-card[data-material-id="${materialId}"]`);

        if (!favoriteCard) return;

        const title = favoriteCard.querySelector('.favorite-title')?.textContent || '';
        const description = favoriteCard.querySelector('.favorite-description')?.textContent || '';

        const badgeItems = favoriteCard.querySelectorAll('.badge-item');
        let subject = '', grade = '', difficulty = '';

        badgeItems.forEach((item, index) => {
            const text = item.querySelector('span')?.textContent || '';
            if (index === 0) subject = text;
            else if (index === 1) grade = text;
            else if (index === 2) difficulty = text;
        });

        this.currentModalMaterial = {
            id: materialId,
            title: title,
            description: description,
            subject: { name: subject, bg_color: '#4f46e5' },
            type: { name: 'Методический материал', bg_color: '#032D43', text_color: '#FFFFFF' },
            grade: { name: grade },
            difficulty: { name: difficulty },
            format: { name: 'Индивидуальная' },
            assessment: { name: 'Без оценки' },
            additional: { name: 'Основной' },
            file_url: '#'
        };

        this.showMaterialModal(this.currentModalMaterial);
    }

    showMaterialModal(material) {
        if (!this.modal || !this.modalBody) return;

        const modalHTML = `
            <div class="modal-material-content">
                <div class="modal-header-row">
                    <h4 class="modal-material-title">${this.escapeHtml(material.title)}</h4>
                    <button class="modal-favorite-btn active" data-id="${material.id}" disabled>
                        <i class="fas fa-heart"></i>
                    </button>
                </div>

                <div class="modal-section">
                    <h5 class="modal-section-title">Описание</h5>
                    <p class="modal-material-description">${this.escapeHtml(material.description || 'Описание отсутствует')}</p>
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
                                <div class="char-value">${this.escapeHtml(material.subject.name || 'Не указан')}</div>
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
                                <div class="char-value">${this.escapeHtml(material.grade.name || 'Не указан')}</div>
                            </div>
                        </div>

                        <div class="modal-char-item">
                            <div class="char-icon" style="background-color: #FEF3C7;">
                                <i class="fas fa-chart-line" style="color: #92400e;"></i>
                            </div>
                            <div class="char-content">
                                <div class="char-label">Уровень сложности</div>
                                <div class="char-value">${this.escapeHtml(material.difficulty.name || 'Не указан')}</div>
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
                    <a href="${material.file_url}" class="modal-download-btn" target="_blank" ${!material.file_url ? 'disabled' : ''}>
                        <i class="fas fa-download"></i>
                        Скачать материал
                    </a>
                </div>
            </div>
        `;

        this.modalBody.innerHTML = modalHTML;
        this.modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    closeModal() {
        if (this.modal) {
            this.modal.classList.remove('active');
            document.body.style.overflow = '';
            this.currentModalMaterial = null;
        }
    }

    async showClearAllConfirm() {
        // Создаем отдельное модальное окно для очистки
        if (!this.confirmModal) {
            this.createConfirmModal();
        }

        const messageEl = document.getElementById('confirmDeleteMessage');
        if (messageEl) {
            messageEl.innerHTML = 'Вы уверены, что хотите очистить всё избранное? Это действие нельзя отменить.';
        }

        const confirmBtn = document.getElementById('confirmDeleteBtn');

        // Временно заменяем обработчик для очистки
        const originalConfirmHandler = confirmBtn.onclick;

        confirmBtn.onclick = async () => {
            await this.performClearAll();
            if (this.confirmModal) {
                this.confirmModal.style.display = 'none';
                document.body.style.overflow = '';
            }
            // Восстанавливаем исходный обработчик
            confirmBtn.onclick = originalConfirmHandler;
            // Восстанавливаем текст сообщения
            if (messageEl) {
                messageEl.innerHTML = 'Вы уверены, что хотите удалить этот материал из избранного?';
            }
        };

        this.confirmModal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    async performClearAll() {
        if (!this.clearAllBtn) return;

        try {
            this.clearAllBtn.disabled = true;
            this.clearAllBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Очистка...</span>';

            const response = await fetch('/account/favorites/clear/', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCsrfToken(),
                    'Content-Type': 'application/json'
                },
            });

            const data = await response.json();

            if (data.success) {
                const cards = document.querySelectorAll('.favorite-card');
                cards.forEach(card => {
                    card.classList.add('removing');
                });

                setTimeout(() => {
                    cards.forEach(card => card.remove());
                    this.showNotification('Все материалы удалены из избранного', 'success');
                    setTimeout(() => location.reload(), 800);
                }, 300);
            } else {
                this.showNotification(data.message || 'Не удалось очистить избранное', 'error');
            }
        } catch (error) {
            console.error('Ошибка при очистке избранного:', error);
            this.showNotification('Проблема с соединением. Попробуйте позже.', 'error');
        } finally {
            if (this.clearAllBtn) {
                this.clearAllBtn.disabled = false;
                this.clearAllBtn.innerHTML = '<i class="fas fa-trash-alt"></i><span>Очистить все</span>';
            }
        }
    }

    updateSidebarCounter() {
        const remainingCards = document.querySelectorAll('.favorite-card').length;
        const badgeElement = document.querySelector('.nav-item.active .nav-badge');

        if (badgeElement) {
            if (remainingCards > 0) {
                badgeElement.textContent = remainingCards;
            } else {
                badgeElement.remove();
            }
        }
    }

    getCsrfToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue;
    }

    // ========== ИЗМЕНЕНО ТОЛЬКО ЗДЕСЬ: УВЕДОМЛЕНИЕ ВВЕРХУ СТРАНИЦЫ ==========
   showNotification(message, type = 'success') {
    // Получаем элемент сообщения
    const messageElement = document.getElementById('favoritesSuccessMessage');
    if (!messageElement) return;

    // Обновляем текст и иконку
    const icon = messageElement.querySelector('i');
    const span = messageElement.querySelector('span');

    if (type === 'success') {
        icon.className = 'fas fa-check-circle';
        messageElement.classList.remove('error');
    } else {
        icon.className = 'fas fa-exclamation-circle';
        messageElement.classList.add('error');
    }
    span.textContent = message;

    // Показываем сообщение
    messageElement.style.display = 'flex';
    setTimeout(() => {
        messageElement.classList.add('show');
    }, 10);

    // Скрываем через 3 секунды
    setTimeout(() => {
        messageElement.classList.remove('show');
        setTimeout(() => {
            messageElement.style.display = 'none';
        }, 300);
    }, 3000);
}
}

// Добавляем анимации для уведомления
const animationStyles = document.createElement('style');
animationStyles.textContent = `
    @keyframes notificationSlideDown {
        from {
            opacity: 0;
            transform: translateX(-50%) translateY(-100%);
        }
        to {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }
    }
    @keyframes notificationSlideUp {
        from {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }
        to {
            opacity: 0;
            transform: translateX(-50%) translateY(-100%);
        }
    }
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(100%);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    @keyframes slideOut {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }
`;
document.head.appendChild(animationStyles);

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    try {
        window.favoritesApp = new FavoritesApp();
        window.favoritesApp.init();
        console.log('Приложение избранного успешно инициализировано');
    } catch (error) {
        console.error('Ошибка при инициализации приложения избранного:', error);
    }
});