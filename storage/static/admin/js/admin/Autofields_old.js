const autocompleteUrl = '/names-autocomplete/' + window.location.href.split('/storage/')[1].split('/')[0] + '/'
$(document).ready(function() {
    var $nameField = $('#id_name');

    $nameField.select2({
        ajax: {
            url: autocompleteUrl,
            dataType: 'json',
            delay: 250,
            data: function(params) {
                return {
                    q: params.term, // Поисковый запрос
                };
            },
            processResults: function(data) {
                return {
                    results: data.results,
                };
            },
            cache: true
        },
        minimumInputLength: 1,
        placeholder: 'Новая запись',
        allowClear: true,
        tags: true,  // Позволяем вводить новые значения
        createTag: function (params) {
            return {
                id: params.term,
                text: params.term,
                isNew: true
            };
        },
        templateResult: function (data) {
            var $result = $("<span></span>");

            $result.text(data.text);

            if (data.isNew) {
                $result.append(" <em>(новый)</em>");
            }

            return $result;
        },
        selectOnClose: true,
    });

    // Обработка отправки формы
    $('#add-form').on('submit', function(event) {
        event.preventDefault();
        var $form = $(this);
        $.ajax({
            url: '',
            type: 'POST',
            data: $form.serialize(),
            success: function(response) {
                // Обновляем таблицу результатов
                var $responseHtml = $(response);
                var $newResults = $responseHtml.find('#result_list').html();
                $('#result_list').html($newResults);
                // Очищаем поле ввода
                $nameField.val('').trigger('change');
                // Очищаем ошибки формы
                $('.errorlist').remove();
            },
            error: function(xhr) {
                // Отображаем ошибки
                var $responseHtml = $(xhr.responseText);
                var $errors = $responseHtml.find('.errorlist');
                $form.find('#id_name').after($errors);
            }
        });
    });
});
