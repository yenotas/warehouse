django.jQuery(document).ready(function($) {

    console.log('Autofields');

    $('.auto_complete').each(function() {
        var fieldElement = $(this);
        var name = fieldElement.attr('name');
        var hiddenFieldName = name + '_id';

        fieldElement.autocomplete({
            minLength: 2, // Минимальное количество символов для запуска поиска
            source: function(request, response) {
                $.ajax({
                    url: '/autocomplete/', // URL для получения данных
                    dataType: 'json',
                    data: {
                        term: request.term
                    },
                    success: function(data) {
                        response($.map(data, function(item) {
                            return {
                                label: item.name, // Отображаемое имя
                                value: item.name, // Значение, которое будет вставлено в поле
                                id: item.id       // ID поставщика
                            };
                        }));
                    }
                });
            },
            select: function(event, ui) {
                fieldElement.val(ui.item.value);
                $('input[name="' + hiddenFieldName + '"]').val(ui.item.id);
                return false;
            },
            focus: function(event, ui) {
                fieldElement.val(ui.item.value);
                return false;
            }
        });
    });
});
