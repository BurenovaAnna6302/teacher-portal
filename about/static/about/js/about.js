// about.js - Полная версия JavaScript для страницы "О нас"

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM загружен, инициализация страницы "О нас"');
    initAboutPage();
});

function initAboutPage() {
    console.log('Страница "О нас" загружена');

    initTeamCarousel();
    initFAQAccordion();
    initTeamCards();
    initGallery();
    initScrollAnimations();
    initImageErrorHandling();
    initContactAnchor();
    addDynamicStyles();
}

// Функция для карусели команды
function initTeamCarousel() {
    const carousel = document.querySelector('.amp-team-carousel');
    const prevBtn = document.querySelector('.amp-carousel-btn-prev');
    const nextBtn = document.querySelector('.amp-carousel-btn-next');

    console.log('Инициализация карусели команды:', {
        carousel: !!carousel,
        prevBtn: !!prevBtn,
        nextBtn: !!nextBtn
    });

    if (!carousel || !prevBtn || !nextBtn) {
        console.warn('Элементы карусели команды не найдены');
        return;
    }

    const scrollAmount = 400;

    function scrollLeft() {
        carousel.scrollBy({
            left: -scrollAmount,
            behavior: 'smooth'
        });
    }

    function scrollRight() {
        carousel.scrollBy({
            left: scrollAmount,
            behavior: 'smooth'
        });
    }

    prevBtn.addEventListener('click', scrollLeft);
    nextBtn.addEventListener('click', scrollRight);

    function updateButtonVisibility() {
        const isAtStart = carousel.scrollLeft <= 10;
        const isAtEnd = carousel.scrollLeft + carousel.clientWidth >= carousel.scrollWidth - 10;

        prevBtn.disabled = isAtStart;
        prevBtn.style.opacity = isAtStart ? '0.5' : '1';
        prevBtn.style.cursor = isAtStart ? 'not-allowed' : 'pointer';

        nextBtn.disabled = isAtEnd;
        nextBtn.style.opacity = isAtEnd ? '0.5' : '1';
        nextBtn.style.cursor = isAtEnd ? 'not-allowed' : 'pointer';
    }

    carousel.addEventListener('scroll', updateButtonVisibility);
    updateButtonVisibility();

    console.log('Карусель команды инициализирована');
}

// Функция для FAQ аккордеона
function initFAQAccordion() {
    const faqItems = document.querySelectorAll('.amp-faq-item');

    console.log('Найдено FAQ элементов:', faqItems.length);

    if (!faqItems.length) {
        console.warn('FAQ элементы не найдены');
        return;
    }

    faqItems.forEach(item => {
        const question = item.querySelector('.amp-faq-question');

        if (!question) return;

        question.addEventListener('click', () => {
            const isActive = item.classList.contains('active');

            faqItems.forEach(otherItem => {
                if (otherItem !== item && otherItem.classList.contains('active')) {
                    otherItem.classList.remove('active');
                }
            });

            if (isActive) {
                item.classList.remove('active');
            } else {
                item.classList.add('active');
            }
        });

        question.setAttribute('tabindex', '0');
        question.setAttribute('role', 'button');
    });

    if (faqItems.length > 0) {
        faqItems[0].classList.add('active');
    }

    console.log('FAQ аккордеон инициализирован');
}

// Функция для карточек команды
function initTeamCards() {
    const teamCards = document.querySelectorAll('.amp-team-card');

    console.log('Найдено карточек команды:', teamCards.length);

    if (!teamCards.length) {
        console.warn('Карточки команды не найдены');
        return;
    }

    teamCards.forEach(card => {
        let isFlipped = false;
        let isClickable = true;

        function flipCard() {
            if (!isClickable) return;

            isClickable = false;
            isFlipped = !isFlipped;

            if (isFlipped) {
                card.classList.add('flipped');
                console.log('Карточка перевернута');
            } else {
                card.classList.remove('flipped');
                console.log('Карточка перевернута обратно');
            }

            setTimeout(() => {
                isClickable = true;
            }, 800);
        }

        card.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            flipCard();
        });

        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                flipCard();
            }
        });

        card.setAttribute('tabindex', '0');
        card.setAttribute('role', 'button');
        card.setAttribute('aria-label', 'Информация о члене команды. Нажмите, чтобы перевернуть карточку');
    });

    console.log('Карточки команды инициализированы');
}

// Функция для галереи
function initGallery() {
    const galleryItems = document.querySelectorAll('.amp-gallery-item');

    console.log('Найдено элементов галереи:', galleryItems.length);

    if (!galleryItems.length) {
        console.warn('Элементы галереи не найдены');
        return;
    }

    galleryItems.forEach(item => {
        const image = item.querySelector('.amp-gallery-image');

        if (!image) return;

        item.addEventListener('click', () => {
            openLightbox(image.src, image.alt);
        });

        item.setAttribute('tabindex', '0');
        item.setAttribute('role', 'button');
    });

    console.log('Галерея инициализирована');
}

// Функция для лайтбокса
function openLightbox(src, alt) {
    const lightbox = document.createElement('div');
    lightbox.className = 'amp-lightbox';
    lightbox.innerHTML = `
        <div class="amp-lightbox-overlay"></div>
        <div class="amp-lightbox-content">
            <button class="amp-lightbox-close" aria-label="Закрыть">
                <i class="fas fa-times"></i>
            </button>
            <img src="${src}" alt="${alt}" class="amp-lightbox-image">
            <div class="amp-lightbox-caption">${alt}</div>
        </div>
    `;

    document.body.appendChild(lightbox);
    document.body.style.overflow = 'hidden';

    setTimeout(() => {
        lightbox.classList.add('active');
    }, 10);

    const closeBtn = lightbox.querySelector('.amp-lightbox-close');
    const overlay = lightbox.querySelector('.amp-lightbox-overlay');

    function closeLightbox() {
        lightbox.classList.remove('active');
        setTimeout(() => {
            if (lightbox.parentNode) {
                document.body.removeChild(lightbox);
            }
            document.body.style.overflow = '';
        }, 300);
    }

    closeBtn.addEventListener('click', closeLightbox);
    overlay.addEventListener('click', closeLightbox);

    document.addEventListener('keydown', function lightboxKeyHandler(e) {
        if (e.key === 'Escape') {
            closeLightbox();
            document.removeEventListener('keydown', lightboxKeyHandler);
        }
    });
}

// Функция для анимаций при скролле
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.amp-fade-in');

    if (!animatedElements.length) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '50px'
    });

    animatedElements.forEach(el => {
        observer.observe(el);
    });

    console.log('Анимации при скролле инициализированы');
}

// Функция для обработки якоря на главной странице
function initContactAnchor() {
    if (window.location.hash === '#contact-form') {
        setTimeout(() => {
            const contactForm = document.querySelector('#contact-form');
            if (contactForm) {
                contactForm.scrollIntoView({ behavior: 'smooth' });
            }
        }, 500);
    }
}

// Функция для обработки ошибок изображений
function initImageErrorHandling() {
    const images = document.querySelectorAll('img[onerror]');

    images.forEach(img => {
        img.addEventListener('error', function() {
            const onerrorAttr = this.getAttribute('onerror');
            const fallbackMatch = onerrorAttr ? onerrorAttr.match(/this\.src='([^']+)'/) : null;
            const fallbackSrc = fallbackMatch ? fallbackMatch[1] : null;

            if (fallbackSrc && this.src !== fallbackSrc) {
                console.log('Ошибка загрузки изображения, загружаем fallback');
                this.src = fallbackSrc;
                this.onerror = null;
            }
        });
    });
}

// Функция для добавления динамических стилей
function addDynamicStyles() {
    const styles = `
        .amp-lightbox {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s ease, visibility 0.3s ease;
        }
        .amp-lightbox.active {
            opacity: 1;
            visibility: visible;
        }
        .amp-lightbox-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.9);
        }
        .amp-lightbox-content {
            position: relative;
            z-index: 1001;
            max-width: 90%;
            max-height: 90%;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
            transform: scale(0.9);
            transition: transform 0.3s ease;
        }
        .amp-lightbox.active .amp-lightbox-content {
            transform: scale(1);
        }
        .amp-lightbox-close {
            position: absolute;
            top: 16px;
            right: 16px;
            width: 40px;
            height: 40px;
            background: white;
            border: none;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            z-index: 1002;
            font-size: 20px;
            color: #032D43;
            transition: all 0.3s ease;
        }
        .amp-lightbox-close:hover {
            background: #f0f0f0;
            transform: rotate(90deg);
        }
        .amp-lightbox-image {
            width: 100%;
            height: auto;
            max-height: 70vh;
            object-fit: contain;
            display: block;
        }
        .amp-lightbox-caption {
            padding: 16px;
            background: white;
            color: #032D43;
            text-align: center;
            font-size: 14px;
        }
        .amp-fade-in {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
        .amp-fade-in.visible {
            opacity: 1;
            transform: translateY(0);
        }
    `;

    if (!document.querySelector('#amp-dynamic-styles')) {
        const styleEl = document.createElement('style');
        styleEl.id = 'amp-dynamic-styles';
        styleEl.textContent = styles;
        document.head.appendChild(styleEl);
    }
}

console.log('Скрипт about.js загружен и готов к работе');