// news_detail.js - Функциональность страницы детального просмотра новости
// Версия: 2.0

class NewsDetailApp {
    constructor() {
        this.galleryModal = document.getElementById('galleryModal');
        this.modalImage = document.getElementById('modalImage');
        this.closeModalBtn = document.getElementById('closeGalleryModal');
        this.notificationContainer = null;
    }

    init() {
        console.log('Инициализация страницы детального просмотра новости...');
        this.initGallery();
        this.initModal();
    }

    initGallery() {
        window.openGalleryModal = (imageUrl) => {
            if (this.modalImage && this.galleryModal) {
                this.modalImage.src = imageUrl;
                this.galleryModal.classList.add('active');
                document.body.style.overflow = 'hidden';
            }
        };
    }

    initModal() {
        if (!this.galleryModal || !this.closeModalBtn) return;

        // Закрытие по кнопке
        this.closeModalBtn.addEventListener('click', () => {
            this.closeModal();
        });

        // Закрытие по клику на overlay
        this.galleryModal.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay')) {
                this.closeModal();
            }
        });

        // Закрытие по Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.galleryModal.classList.contains('active')) {
                this.closeModal();
            }
        });
    }

    closeModal() {
        if (this.galleryModal) {
            this.galleryModal.classList.remove('active');
            document.body.style.overflow = '';
            if (this.modalImage) {
                this.modalImage.src = '';
            }
        }
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    try {
        window.newsDetailApp = new NewsDetailApp();
        window.newsDetailApp.init();
        console.log('Приложение детального просмотра новости успешно инициализировано');
    } catch (error) {
        console.error('Ошибка при инициализации приложения:', error);
    }
});