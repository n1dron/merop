document.addEventListener('DOMContentLoaded', function() {
    // Обработчики кнопок
    document.getElementById('create-event')?.addEventListener('click', function() {
      window.location.href = "{% url 'event_create' %}";
    });
  
    document.getElementById('create-team')?.addEventListener('click', function() {
      window.location.href = "{% url 'team_create' %}";
    });
  
    // Анимация карточек
    const cards = document.querySelectorAll('.dashboard-card');
    cards.forEach((card, index) => {
      card.style.opacity = '0';
      card.style.transform = 'translateY(20px)';
      card.style.animation = `fadeInUp 0.5s ease forwards ${index * 0.1}s`;
    });
  
    // Добавляем стили для анимации
    const style = document.createElement('style');
    style.textContent = `
      @keyframes fadeInUp {
        from {
          opacity: 0;
          transform: translateY(20px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }
    `;
    document.head.appendChild(style);
  });