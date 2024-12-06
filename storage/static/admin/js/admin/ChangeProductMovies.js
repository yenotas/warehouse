django.jQuery(document).ready(function($) {
    // При изменении типа перемещения
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    $(document).on('change', '#id_process_type', function() {
        var processType = $(this).val();
        $.ajax({
            url: '/get_reason_choices/',
            data: {
                process_type: processType
            },
            type: 'get',
             success: function(data) {
                console.log(data);

                $('#id_reason').empty();  // Очищаем поле
                $.each(data.choices, function(index, choice) {
                    console.log(choice.text, choice.id);
                    $('#id_reason').append(new Option(choice.text, choice.id));
                });
                // Делаем поле обязательным в зависимости от типа перемещения
                if (['move', 'warehouse', 'distribute'].includes(processType)) {
                    $('#id_reason').prop('required', true);
                } else {
                    $('#id_reason').prop('required', false);
                }
            },
            error: function(xhr, status, error) {
                console.error('Ошибка при загрузке данных:', status, error);
            }
        });
    });
});
