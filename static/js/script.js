document.addEventListener("DOMContentLoaded", function () {
    const fadeInElements = document.querySelectorAll('.fade-in');
    fadeInElements.forEach(element => {
        element.classList.add('visible');
    });

    const themeToggle = document.getElementById('themeToggle');
    function setTheme(mode) {
        if (mode === 'dark') {
            document.body.classList.add('dark-mode');
            themeToggle.textContent = '☀️ Light Mode';
            localStorage.setItem('theme', 'dark');
        } else {
            document.body.classList.remove('dark-mode');
            themeToggle.textContent = '🌙 Dark Mode';
            localStorage.setItem('theme', 'light');
        }
        updateCardStyles(); // Обновляем стили карточек при смене темы
    }
    themeToggle.addEventListener('click', () => {
        if (document.body.classList.contains('dark-mode')) {
            setTheme('light');
        } else {
            setTheme('dark');
        }
    });
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);

    // Обработка кнопок с анимацией
    document.querySelectorAll('.animated-button').forEach(button => {
        button.addEventListener('click', () => {
            if (button.dataset.copy) {
                const textToCopy = button.getAttribute('data-copy');
                const originalText = button.getAttribute('data-text') || button.textContent;

                copyToClipboard(textToCopy);
                button.textContent = 'Copied!';
                setTimeout(() => {
                    button.textContent = originalText;
                }, 2000);
            }
        });

        button.addEventListener('mouseover', () => {
            button.classList.add('hovered');
        });

        button.addEventListener('mouseout', () => {
            button.classList.remove('hovered');
        });
    });

    // Обработка интерактивных карточек
    const interactiveCards = document.querySelectorAll('.interactive-card');
    function updateCardStyles() {
        const isDarkMode = document.body.classList.contains('dark-mode');
        interactiveCards.forEach(card => {
            card.dataset.defaultBg = isDarkMode ? 'var(--accent2)' : 'var(--accent2)';
            card.dataset.hoverBg = isDarkMode ? '#397768' : '#f0cca8';
            card.dataset.defaultColor = isDarkMode ? 'var(--text-color)' : 'var(--text-color)';
            card.dataset.hoverColor = isDarkMode ? 'var(--button-text)' : 'var(--button-text)';
        });
    }

    interactiveCards.forEach(card => {
        card.addEventListener('mouseover', () => {
            const hoverBg = card.dataset.hoverBg;
            const hoverColor = card.dataset.hoverColor;
            card.style.backgroundColor = hoverBg;
            card.style.color = hoverColor;
            card.style.transform = 'scale(1.05)';
            card.style.boxShadow = '0 8px 16px rgba(0, 0, 0, 0.2)';
        });

        card.addEventListener('mouseout', () => {
            const defaultBg = card.dataset.defaultBg;
            const defaultColor = card.dataset.defaultColor;
            card.style.backgroundColor = defaultBg;
            card.style.color = defaultColor;
            card.style.transform = 'scale(1)';
            card.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
        });
    });

    updateCardStyles(); // Инициализация стилей карточек

    // Копирование в буфер
    function copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(function () {
            showFlashMessage('Copied: ' + text);
        }, function (err) {
            console.error('Copy error: ', err);
        });
    }

    // Всплывающее сообщение
    function showFlashMessage(message) {
        const flashMessageDiv = document.getElementById('flash-message');
        flashMessageDiv.textContent = message;
        flashMessageDiv.classList.add('show');
        setTimeout(() => {
            flashMessageDiv.classList.remove('show');
        }, 3000);
    }

    // Интерактивные текстовые блоки
    const textBlocks = document.querySelectorAll('.text-block');

    textBlocks.forEach(block => {
        block.addEventListener('click', () => {
            const isFullContent = block.classList.contains('full-content');
            textBlocks.forEach(b => b.classList.remove('full-content'));
            if (!isFullContent) {
                block.classList.add('full-content');
            }
        });
    });

    document.addEventListener('click', (event) => {
        if (!event.target.closest('.text-block.full-content')) {
            textBlocks.forEach(block => {
                block.classList.remove('full-content');
            });
        }
    });

    // Анимация при скролле
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });

    fadeInElements.forEach(element => {
        observer.observe(element);
    });

    // Кнопка "Вверх"
    const backToTopButton = document.getElementById('back-to-top');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            backToTopButton.classList.add('show');
        } else {
            backToTopButton.classList.remove('show');
        }
    });

    backToTopButton.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // Плавная прокрутка для внутренних ссылок
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Модальные окна
    const modalTriggers = document.querySelectorAll('[data-modal]');
    const modalCloseButtons = document.querySelectorAll('.modal-close');

    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function () {
            const modal = document.querySelector(this.dataset.modal);
            modal.classList.add('is-active');
        });
    });

    modalCloseButtons.forEach(button => {
        button.addEventListener('click', function () {
            this.closest('.modal').classList.remove('is-active');
        });
    });

    // Подсказки (Tooltips)
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseover', function () {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.dataset.tooltip;
            document.body.appendChild(tooltip);
            const rect = this.getBoundingClientRect();
            tooltip.style.left = `${rect.left + window.scrollX + rect.width / 2 - tooltip.offsetWidth / 2}px`;
            tooltip.style.top = `${rect.top + window.scrollY - tooltip.offsetHeight - 10}px`;
        });

        element.addEventListener('mouseout', function () {
            document.querySelector('.tooltip')?.remove();
        });
    });

    // Карусель изображений
    const carousels = document.querySelectorAll('.carousel');
    carousels.forEach(carousel => {
        const slides = carousel.querySelectorAll('.carousel-slide');
        let currentIndex = 0;

        function showSlide(index) {
            slides.forEach((slide, i) => {
                slide.style.display = i === index ? 'block' : 'none';
            });
        }

        carousel.querySelector('.carousel-next')?.addEventListener('click', () => {
            currentIndex = (currentIndex + 1) % slides.length;
            showSlide(currentIndex);
        });

        carousel.querySelector('.carousel-prev')?.addEventListener('click', () => {
            currentIndex = (currentIndex - 1 + slides.length) % slides.length;
            showSlide(currentIndex);
        });

        showSlide(currentIndex);
    });

    // Автофокус на первой форме
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const firstInput = form.querySelector('input, select, textarea');
        if (firstInput) {
            firstInput.focus();
        }
    });

    // Валидация формы в реальном времени
    forms.forEach(form => {
        form.querySelectorAll('input').forEach(input => {
            input.addEventListener('input', function () {
                if (this.checkValidity()) {
                    this.style.borderColor = '#28a745'; // Зеленый для валидного ввода
                    this.style.boxShadow = '0 0 5px rgba(40, 167, 69, 0.5)';
                } else {
                    this.style.borderColor = '#dc3545'; // Красный для невалидного ввода
                    this.style.boxShadow = '0 0 5px rgba(220, 53, 69, 0.5)';
                }
            });
        });
    });
});