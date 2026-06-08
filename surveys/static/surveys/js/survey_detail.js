// survey_detail.js - Функциональность детальной страницы опроса
// Версия: 5.3 - Исправлено определение статуса

class SurveyDetailApp {
    constructor() {
        this.modal = null;
        this.isCompleted = false;
    }

    init() {
        console.log('🚀 Инициализация страницы детального опроса...');
        console.log('URL текущей страницы:', window.location.href);

        // Проверяем статус опроса
        this.checkSurveyStatus();

        // Инициализируем обработчики
        this.initEventListeners();

        console.log('✅ Страница детального опроса инициализирована');
    }

    checkSurveyStatus() {
        console.log('🔍 Проверка статуса опроса...');

        // 1. Проверяем через data-атрибут в HTML (можно добавить в шаблон)
        const surveyContainer = document.querySelector('.survey-detail-page');
        if (surveyContainer && surveyContainer.dataset.surveyStatus) {
            const status = surveyContainer.dataset.surveyStatus;
            console.log('Статус из data-атрибута:', status);
            this.isCompleted = status === 'completed';
            if (this.isCompleted) {
                this.showCompletedModal();
                this.addInfoBanner();
            }
            return;
        }

        // 2. Ищем статус-бейдж по классам из HTML
        const statusBadge = document.querySelector('.status-badge');
        console.log('Найден статус-бейдж:', statusBadge);

        if (statusBadge) {
            console.log('Классы статус-бейджа:', statusBadge.classList);
            console.log('Текст статус-бейджа:', statusBadge.textContent.trim());

            // Проверяем классы из HTML (status-active / status-completed)
            if (statusBadge.classList.contains('status-completed')) {
                console.log('🔴 Опрос завершен (класс status-completed)');
                this.isCompleted = true;
                this.showCompletedModal();
                this.addInfoBanner();
                return;
            }

            // Проверяем текст
            const badgeText = statusBadge.textContent.trim().toLowerCase();
            if (badgeText.includes('завершен') || badgeText.includes('completed')) {
                console.log('🔴 Опрос завершен (по тексту)');
                this.isCompleted = true;
                this.showCompletedModal();
                this.addInfoBanner();
                return;
            }

            // Проверяем, есть ли форма (если нет формы - опрос завершен)
            const surveyForm = document.querySelector('.survey-form');
            if (!surveyForm) {
                console.log('🔴 Форма не найдена, опрос завершен');
                this.isCompleted = true;
                this.showCompletedModal();
                this.addInfoBanner();
                return;
            }

            console.log('🟢 Опрос активен');
        } else {
            console.log('❌ Статус-бейдж не найден');
        }
    }

    showCompletedModal() {
        // Проверяем, не открыто ли уже модальное окно
        if (document.getElementById('surveyCompletedModal')) {
            console.log('Модальное окно уже существует');
            return;
        }

        console.log('🎯 Показываем модальное окно');

        // Добавляем стили для модального окна
        this.addModalStyles();

        // Создаем модальное окно
        const modalHTML = `
            <div class="survey-completed-modal" id="surveyCompletedModal">
                <div class="modal-overlay"></div>
                <div class="modal-content">
                    <div class="modal-icon">
                        <i class="fas fa-hourglass-end"></i>
                    </div>
                    <h3 class="modal-title">Опрос завершен</h3>
                    <p class="modal-message">
                        Этот опрос больше не принимает ответы.<br>
                        Вы можете ознакомиться с вопросами в режиме просмотра.
                    </p>
                    <button class="modal-btn" id="closeCompletedModal">
                        <i class="fas fa-eye"></i> Понятно
                    </button>
                </div>
            </div>
        `;

        // Вставляем модальное окно в DOM
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Получаем ссылку на модальное окно
        this.modal = document.getElementById('surveyCompletedModal');

        // Добавляем обработчики закрытия
        this.initModalHandlers();
    }

    addModalStyles() {
        // Проверяем, добавлены ли уже стили
        if (document.getElementById('survey-modal-styles')) {
            console.log('Стили модального окна уже добавлены');
            return;
        }

        console.log('Добавляем стили модального окна');

        const style = document.createElement('style');
        style.id = 'survey-modal-styles';
        style.textContent = `
            .survey-completed-modal {
                display: flex !important;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 999999 !important;
                font-family: 'Manrope', sans-serif;
                align-items: center;
                justify-content: center;
            }

            .survey-completed-modal .modal-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
                backdrop-filter: blur(8px);
                animation: overlayFadeIn 0.3s ease;
            }

            .survey-completed-modal .modal-content {
                position: relative;
                width: 90%;
                max-width: 440px;
                background: white;
                border-radius: 28px;
                padding: 36px 32px;
                text-align: center;
                box-shadow: 0 30px 60px rgba(0, 0, 0, 0.4);
                z-index: 1000000 !important;
                animation: modalScaleIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
            }

            .survey-completed-modal .modal-icon {
                width: 88px;
                height: 88px;
                background: #FEF3C7;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 24px;
                color: #92400E;
                font-size: 40px;
                box-shadow: 0 8px 16px rgba(146, 64, 14, 0.15);
            }

            .survey-completed-modal .modal-title {
                color: #1A1A1A;
                font-size: 26px;
                font-weight: 700;
                margin: 0 0 12px 0;
                line-height: 1.3;
            }

            .survey-completed-modal .modal-message {
                color: #6B7280;
                font-size: 16px;
                line-height: 1.6;
                margin: 0 0 32px 0;
            }

            .survey-completed-modal .modal-btn {
                background: #032D43;
                color: white;
                border: none;
                border-radius: 14px;
                padding: 16px 36px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                display: inline-flex;
                align-items: center;
                gap: 10px;
                margin: 0 auto;
                border: 1px solid transparent;
                box-shadow: 0 4px 12px rgba(3, 45, 67, 0.25);
            }

            .survey-completed-modal .modal-btn:hover {
                background: #021F2E;
                transform: translateY(-3px);
                box-shadow: 0 8px 24px rgba(3, 45, 67, 0.35);
            }

            .survey-completed-modal .modal-btn i {
                font-size: 18px;
            }

            @keyframes overlayFadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            @keyframes modalScaleIn {
                0% {
                    opacity: 0;
                    transform: scale(0.8);
                }
                100% {
                    opacity: 1;
                    transform: scale(1);
                }
            }

            @media (max-width: 480px) {
                .survey-completed-modal .modal-content {
                    padding: 28px 24px;
                    width: 95%;
                }

                .survey-completed-modal .modal-icon {
                    width: 72px;
                    height: 72px;
                    font-size: 32px;
                    margin-bottom: 20px;
                }

                .survey-completed-modal .modal-title {
                    font-size: 22px;
                }

                .survey-completed-modal .modal-message {
                    font-size: 15px;
                    margin-bottom: 28px;
                }

                .survey-completed-modal .modal-btn {
                    width: 100%;
                    justify-content: center;
                    padding: 14px 24px;
                }
            }
        `;

        document.head.appendChild(style);
        console.log('✅ Стили модального окна добавлены');
    }

    initModalHandlers() {
        if (!this.modal) {
            console.log('❌ Модальное окно не найдено');
            return;
        }

        console.log('🔧 Инициализируем обработчики модального окна');

        const closeBtn = document.getElementById('closeCompletedModal');
        const overlay = this.modal.querySelector('.modal-overlay');

        if (!closeBtn) {
            console.log('❌ Кнопка закрытия не найдена');
            return;
        }

        if (!overlay) {
            console.log('❌ Оверлей не найден');
            return;
        }

        const closeModal = () => {
            console.log('Закрываем модальное окно');
            this.modal.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => {
                if (this.modal && this.modal.parentNode) {
                    this.modal.remove();
                    this.modal = null;
                }
            }, 300);
        };

        closeBtn.addEventListener('click', closeModal);
        overlay.addEventListener('click', closeModal);

        // Закрытие по Escape
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);
    }

    addInfoBanner() {
        // Проверяем, есть ли уже баннер
        if (document.querySelector('.survey-completed-banner')) {
            console.log('Баннер уже существует');
            return;
        }

        console.log('📢 Добавляем информационный баннер');

        // Добавляем стили для баннера
        this.addBannerStyles();

        const bannerHTML = `
            <div class="survey-completed-banner">
                <i class="fas fa-info-circle"></i>
                <span>Этот опрос завершен. Вы можете только просматривать вопросы.</span>
            </div>
        `;

        // Вставляем баннер перед секцией вопросов
        const questionsSection = document.querySelector('.survey-questions-section');
        if (questionsSection) {
            questionsSection.insertAdjacentHTML('beforebegin', bannerHTML);
            console.log('✅ Баннер добавлен перед секцией вопросов');
        } else {
            console.log('❌ Секция вопросов не найдена');
        }
    }

    addBannerStyles() {
        if (document.getElementById('survey-banner-styles')) return;

        const style = document.createElement('style');
        style.id = 'survey-banner-styles';
        style.textContent = `
            .survey-completed-banner {
                background: #FEF3C7;
                border: 1px solid #FDE68A;
                border-radius: 14px;
                padding: 18px 24px;
                margin: 0 0 24px 0;
                display: flex;
                align-items: center;
                gap: 14px;
                color: #92400E;
                font-size: 15px;
                line-height: 1.5;
                animation: bannerSlideDown 0.3s ease;
                box-shadow: 0 4px 12px rgba(146, 64, 14, 0.1);
            }

            .survey-completed-banner i {
                font-size: 22px;
                flex-shrink: 0;
            }

            .survey-completed-banner span {
                flex: 1;
            }

            @keyframes bannerSlideDown {
                from {
                    opacity: 0;
                    transform: translateY(-30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            @media (max-width: 768px) {
                .survey-completed-banner {
                    padding: 16px 20px;
                    font-size: 14px;
                }

                .survey-completed-banner i {
                    font-size: 20px;
                }
            }

            @media (max-width: 480px) {
                .survey-completed-banner {
                    padding: 14px 16px;
                    flex-wrap: wrap;
                    justify-content: center;
                    text-align: center;
                    gap: 10px;
                }
            }
        `;

        document.head.appendChild(style);
    }

    initEventListeners() {
        console.log('🔧 Инициализируем обработчики событий');

        // Обработка клика по кнопке отправки для завершенных опросов
        const submitBtn = document.querySelector('.btn-submit-survey');
        if (submitBtn && this.isCompleted) {
            console.log('Блокируем кнопку отправки');
            submitBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.showNotification('Этот опрос уже завершен и не принимает ответы', 'warning');
            });
        }

        // Обработка клика по опциям для завершенных опросов
        if (this.isCompleted) {
            console.log('Блокируем поля ввода');
            document.querySelectorAll('.option-card, .answer-textarea, .option-item').forEach(element => {
                element.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.showNotification('Поля недоступны для завершенных опросов', 'info');
                });
            });
        }
    }

    showNotification(message, type = 'info') {
        // Проверяем, есть ли уже уведомление
        if (document.querySelector('.survey-notification')) return;

        const notification = document.createElement('div');
        notification.className = `survey-notification ${type}`;
        notification.innerHTML = `
            <i class="fas ${type === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle'}"></i>
            <span>${message}</span>
        `;

        this.addNotificationStyles();

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'notificationSlideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    addNotificationStyles() {
        if (document.getElementById('survey-notification-styles')) return;

        const style = document.createElement('style');
        style.id = 'survey-notification-styles';
        style.textContent = `
            .survey-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                border-radius: 14px;
                padding: 16px 24px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
                display: flex;
                align-items: center;
                gap: 12px;
                z-index: 1000000;
                animation: notificationSlideIn 0.3s ease;
                border-left: 4px solid;
                max-width: 400px;
                font-family: 'Manrope', sans-serif;
            }

            .survey-notification.warning {
                border-left-color: #F59E0B;
            }

            .survey-notification.warning i {
                color: #F59E0B;
            }

            .survey-notification.info {
                border-left-color: #3B82F6;
            }

            .survey-notification.info i {
                color: #3B82F6;
            }

            .survey-notification i {
                font-size: 20px;
                flex-shrink: 0;
            }

            .survey-notification span {
                color: #1A1A1A;
                font-size: 14px;
                line-height: 1.5;
                flex: 1;
            }

            @keyframes notificationSlideIn {
                from {
                    opacity: 0;
                    transform: translateX(100%);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }

            @keyframes notificationSlideOut {
                from {
                    opacity: 1;
                    transform: translateX(0);
                }
                to {
                    opacity: 0;
                    transform: translateX(100%);
                }
            }

            @media (max-width: 480px) {
                .survey-notification {
                    left: 20px;
                    right: 20px;
                    max-width: none;
                    padding: 14px 20px;
                }

                .survey-notification i {
                    font-size: 18px;
                }

                .survey-notification span {
                    font-size: 13px;
                }
            }
        `;

        document.head.appendChild(style);
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM полностью загружен');
    window.surveyDetailApp = new SurveyDetailApp();
    window.surveyDetailApp.init();
});