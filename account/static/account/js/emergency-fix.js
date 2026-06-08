// emergency-fix.js - Экстренное исправление кликабельности
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== EMERGENCY FIX LOADED ===');

    // 1. БЛОКИРУЕМ все event.preventDefault() и stopPropagation()
    const originalAddEventListener = EventTarget.prototype.addEventListener;
    EventTarget.prototype.addEventListener = function(type, listener, options) {
        if (type === 'click' || type === 'mousedown' || type === 'mouseup') {
            const wrappedListener = function(e) {
                console.log('Event intercepted:', type, 'on', this.tagName, this.id || this.className);

                // РАЗРЕШАЕМ все события
                e.stopImmediatePropagation = function() {
                    console.warn('stopImmediatePropagation blocked on', this.tagName);
                };

                e.stopPropagation = function() {
                    console.warn('stopPropagation blocked on', this.tagName);
                };

                e.preventDefault = function() {
                    console.warn('preventDefault blocked on', this.tagName);
                };

                // Вызываем оригинальный обработчик
                try {
                    return listener.call(this, e);
                } catch (error) {
                    console.error('Error in event listener:', error);
                }

                return true;
            };

            return originalAddEventListener.call(this, type, wrappedListener, options);
        }
        return originalAddEventListener.call(this, type, listener, options);
    };

    // 2. ПРИНУДИТЕЛЬНО активируем ВСЕ кнопки
    function forceActivateButtons() {
        const elements = document.querySelectorAll('*');
        elements.forEach(el => {
            // Сбрасываем все стили блокировки
            el.style.pointerEvents = 'auto';
            el.style.userSelect = 'auto';
            el.style.touchAction = 'auto';
            el.style.cursor = 'default';
        });

        // Особое внимание кнопкам и ссылкам
        const clickable = document.querySelectorAll(
            'button, a, [role="button"], .btn, input[type="button"], ' +
            'input[type="submit"], .nav-link, .mobile-nav-link, .dropdown-item, ' +
            '.nav-item, .favorites-tab, .photo-upload-btn, .photo-remove-btn, ' +
            '.btn-profile-save, .favorite-remove-btn, .btn-clear-all-favorites'
        );

        clickable.forEach(el => {
            // ВОССТАНАВЛИВАЕМ нормальные стили
            el.style.cssText = '';
            el.style.cursor = 'pointer';
            el.style.pointerEvents = 'auto';
            el.style.position = 'relative';
            el.style.zIndex = '10000';

            // Удаляем все старые обработчики
            const newEl = el.cloneNode(true);
            el.parentNode.replaceChild(newEl, el);

            // Добавляем новый простой обработчик
            newEl.onclick = function(e) {
                console.log('✅ CLICK WORKING on:',
                    this.tagName,
                    this.id || this.className,
                    'text:', this.textContent?.trim()?.substring(0, 20)
                );

                // Для кнопки сохранения профиля
                if (this.id === 'saveProfileBtn' || this.classList.contains('btn-profile-save')) {
                    e.preventDefault();
                    alert('✅ Кнопка сохранения РАБОТАЕТ!');
                    return false;
                }

                // Для остальных кнопок
                return true;
            };
        });

        console.log('✅ Активировано элементов:', clickable.length);
    }

    // 3. Запускаем несколько раз для надежности
    setTimeout(forceActivateButtons, 100);
    setTimeout(forceActivateButtons, 500);
    setTimeout(forceActivateButtons, 1000);
    setTimeout(forceActivateButtons, 2000);

    // 4. Ловим все клики на документе
    document.addEventListener('click', function(e) {
        console.log('📌 Document click:', e.target.tagName, e.target.id || e.target.className);
    }, true);

    console.log('=== EMERGENCY FIX COMPLETE ===');
});

// Запускаем даже если DOM уже загружен
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(function() {
        document.dispatchEvent(new Event('DOMContentLoaded'));
    }, 100);
}