(function($) {
    $(document).ready(function() {
        // Отключение стандартных элементов виджета
        $.fn.calendarWidget = function() {
            this.each(function() {
                var input = $(this);
                input.prop('type', 'text'); // Убедиться, что это текстовое поле
                input.css('cursor', 'pointer'); // Изменить курсор на указатель

                input.datepicker({
                    dateFormat: 'yy-mm-dd', // Формат даты
                    showOn: 'focus', // Показывать календарь при фокусе на поле
                    changeMonth: true,
                    changeYear: true
                });

                // Добавляем событие при клике
                input.on('click', function() {
                    $(this).datepicker('show'); // Показываем календарь
                });
            });

            return this;
        };

        // Применить календарный виджет ко всем полям даты
        $('input.vDateField').calendarWidget();
    });
})(django.jQuery);
