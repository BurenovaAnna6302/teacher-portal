// help.js - Скрипт для страницы помощи и поддержки
// Версия: 1.1 - Независимое открытие категорий

class HelpApp {
    constructor() {
        this.categoryHeaders = document.querySelectorAll('.category-header');
        this.faqQuestions = document.querySelectorAll('.faq-question');
    }

    init() {
        console.log('Инициализация страницы помощи...');

        // Инициализация аккордеонов категорий
        this.initCategoryAccordions();

        // Инициализация аккордеонов вопросов внутри категорий
        this.initFaqAccordions();

        console.log('Инициализация завершена');
    }

    initCategoryAccordions() {
        this.categoryHeaders.forEach(header => {
            header.addEventListener('click', (e) => {
                e.stopPropagation();
                const categoryCard = header.closest('.help-category-card');
                const content = categoryCard.querySelector('.category-content');
                const isOpen = content.classList.contains('open');

                // Закрываем ТОЛЬКО эту категорию, если она открыта
                // НЕ закрываем другие категории
                if (!isOpen) {
                    content.classList.add('open');
                    header.classList.add('open');
                } else {
                    content.classList.remove('open');
                    header.classList.remove('open');
                }
            });
        });
    }

    initFaqAccordions() {
        this.faqQuestions.forEach(question => {
            question.addEventListener('click', (e) => {
                e.stopPropagation();
                const faqItem = question.closest('.faq-item');
                const answer = faqItem.querySelector('.faq-answer');
                const isOpen = answer.classList.contains('open');

                // Закрываем ТОЛЬКО этот вопрос, если он открыт
                // НЕ закрываем другие вопросы
                if (!isOpen) {
                    answer.classList.add('open');
                    question.classList.add('open');
                } else {
                    answer.classList.remove('open');
                    question.classList.remove('open');
                }
            });
        });
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    window.helpApp = new HelpApp();
    window.helpApp.init();
});