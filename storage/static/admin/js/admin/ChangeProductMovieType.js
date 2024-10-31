$(document).ready(function() {
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
                const reasonField = $('#id_reason');
                reasonField.empty();  // Очищаем поле
                $.each(data, function(index, choice) {
                    reasonField.append(new Option(choice.name, choice.id));
                });
                // Делаем поле обязательным в зависимости от типа перемещения
                if (['move', 'warehouse', 'distribute'].includes(processType)) {
                    reasonField.prop('required', true);
                } else {
                    reasonField.prop('required', false);
                }
            },
            error: function(xhr, status, error) {
                console.error('Ошибка при загрузке данных:', status, error);
            }
        });
    });
});
