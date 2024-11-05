$(document).ready(function() {
    // Кнопка для перемещения элементов из левого списка в правый
    $('#id_fields_to_disable_add_link').click(function(event) {
        event.preventDefault();
        MoveAcross('id_fields_to_disable_from', 'id_fields_to_disable_to');
    });

    // Кнопка для перемещения элементов из правого списка в левый
    $('#id_fields_to_disable_remove_link').click(function(event) {
        event.preventDefault();
        MoveAcross('id_fields_to_disable_to', 'id_fields_to_disable_from');
    });

    // Перестановка элементов для .field-groups и .field-fields_to_disable
    function swapElements(selector) {
        $(selector).each(function() {
            var $label = $(this).find('label.required');
            var $selectorDiv = $(this).find('div.selector');
            if ($label.length && $selectorDiv.length) {
                $label.insertBefore($selectorDiv);
            }
        });
    }

    swapElements('.field-groups');
    swapElements('.field-fields_to_disable');

    $('#id_model_name').change(updateFieldsToDisable);

    updateFieldsToDisable();

});


function updateFieldsToDisable() {
    console.log('MoveAcross', typeof MoveAcross)
    var modelName = $('#id_model_name').val();
    $.ajax({
        url: '/get-model-fields/',
        type: 'GET',
        data: {
            'model_name': modelName
        },
        success: function(data) {
            var fieldsToDisableFrom = $('#id_fields_to_disable_from');
            fieldsToDisableFrom.empty();

            $.each(data.fields, function(index, field) {
                var newOption = new Option(field.verbose_name, field.name);
                fieldsToDisableFrom.append(newOption);
            });


            setTimeout(function() {
                var selectElement = $('#id_fields_to_disable');
                if (selectElement) {
                    SelectFilter.init('id_fields_to_disable', 'Поля', false);
                    console.log('MoveAcross2', typeof MoveAcross)
                }
            }, 1300);

        },
        error: function(xhr, status, error) {
            console.error('Ошибка при получении полей модели:', status, error);
        }
    });
}




