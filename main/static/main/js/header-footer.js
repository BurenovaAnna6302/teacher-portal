/**
 * Header and Footer functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('=== HEADER SCRIPT STARTED ===');

    // Desktop dropdowns - FIXED VERSION
    const dropdowns = document.querySelectorAll('.nav-dropdown');
    console.log('Found dropdowns:', dropdowns.length);

    dropdowns.forEach((dropdown, index) => {
        console.log(`Setting up dropdown ${index + 1}`);

        const toggle = dropdown.querySelector('.nav-dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');

        if (!toggle || !menu) {
            console.warn(`Dropdown ${index + 1}: missing elements`, { toggle: !!toggle, menu: !!menu });
            return;
        }

        console.log(`Dropdown ${index + 1}: elements found`);

        // Hover для десктопа
        dropdown.addEventListener('mouseenter', function() {
            console.log('Mouse ENTER dropdown');
            if (window.innerWidth >= 1024) {
                menu.classList.add('dropdown-show');
                console.log('Dropdown SHOW (hover)');
            }
        });

        dropdown.addEventListener('mouseleave', function() {
            console.log('Mouse LEAVE dropdown');
            if (window.innerWidth >= 1024) {
                menu.classList.remove('dropdown-show');
                console.log('Dropdown HIDE (hover)');
            }
        });

        // Click для мобильных
        toggle.addEventListener('click', function(e) {
            console.log('CLICK on dropdown toggle');

            if (window.innerWidth < 1024) {
                e.preventDefault();
                e.stopPropagation();

                // Закрываем все остальные dropdowns
                dropdowns.forEach(otherDropdown => {
                    if (otherDropdown !== dropdown) {
                        const otherMenu = otherDropdown.querySelector('.dropdown-menu');
                        if (otherMenu) {
                            otherMenu.classList.remove('dropdown-show');
                            console.log('Closed other dropdown');
                        }
                    }
                });

                // Переключаем текущий dropdown
                const isShowing = menu.classList.contains('dropdown-show');
                menu.classList.toggle('dropdown-show');
                console.log(isShowing ? 'Dropdown HIDE (click)' : 'Dropdown SHOW (click)');
            }
        });
    });

    // Закрываем dropdown при клике вне
    document.addEventListener('click', function(e) {
        const isDropdown = e.target.closest('.nav-dropdown');
        const isDropdownToggle = e.target.closest('.nav-dropdown-toggle');

        if (!isDropdown && !isDropdownToggle) {
            console.log('Click OUTSIDE dropdown');
            dropdowns.forEach(dropdown => {
                const menu = dropdown.querySelector('.dropdown-menu');
                if (menu) {
                    menu.classList.remove('dropdown-show');
                }
            });
        }
    });

    // Закрываем dropdown при ресайзе на мобильных
    window.addEventListener('resize', function() {
        console.log('Window resized to:', window.innerWidth);

        if (window.innerWidth >= 1024) {
            // На десктопе очищаем click-состояния
            dropdowns.forEach(dropdown => {
                const menu = dropdown.querySelector('.dropdown-menu');
                if (menu) {
                    menu.classList.remove('dropdown-show');
                }
            });
        }
    });

    console.log('=== HEADER SCRIPT COMPLETED ===');
});

function updateActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link, .mobile-nav-link');

    console.log('Current path:', currentPath);
    console.log('Found nav links:', navLinks.length);

    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        console.log('Link path:', linkPath);

        // Убираем активный класс со всех ссылок
        link.classList.remove('active');

        // Проверяем соответствие пути
        if (linkPath === currentPath) {
            console.log('Exact match:', linkPath);
            link.classList.add('active');
        }
        // Для главной страницы
        else if (currentPath === '/' && (linkPath === '/' || linkPath === '{% url "main:index" %}')) {
            console.log('Home match');
            link.classList.add('active');
        }
        // Для вложенных страниц (например, /about/, /news/, etc)
        else if (linkPath !== '/' && currentPath.includes(linkPath)) {
            console.log('Partial match:', linkPath, 'in', currentPath);
            link.classList.add('active');
        }
    });

    // Также обновляем активные ссылки в dropdown
    const dropdownItems = document.querySelectorAll('.dropdown-item');
    dropdownItems.forEach(item => {
        const itemPath = item.getAttribute('href');
        item.classList.remove('active');

        if (itemPath === currentPath) {
            item.classList.add('active');
        } else if (currentPath.includes(itemPath) && itemPath !== '/') {
            item.classList.add('active');
        }
    });
}

// Экспорт функций для тестирования
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        updateActiveNavLink
    };
}