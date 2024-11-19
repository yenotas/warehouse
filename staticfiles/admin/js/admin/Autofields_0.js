$(document).ready(function() {
    // Применяем автозаполнение ко всем элементам с классом single_line_add
    $('.single_line_add').each(function() {
        const fieldElement = $(this);
        const fieldName = fieldElement.attr('field_name');
        const modelName = fieldElement.attr('model_name');

        fieldElement.autocomplete({
            source: function(request, response) {
                $.ajax({
                    url: '/autocomplete/',
                    dataType: "json",
                    data: {
                        term: request.term,
                        model_name: modelName,
                        field_name: fieldName
                    },
                    success: function(data) {
                        // Формируем список для автозаполнения
                        response($.map(data, function(item) {
                            return {
                                value: item.text,
                                id: item.id
                            };
                        }));
                    }
                });
            },
            minLength: 2,
            select: function(event, ui) {
                // Устанавливаем выбранное имя в текстовое поле
                fieldElement.val(ui.item.value);
                name = fieldElement.attr("name");
                console.log('',fieldName, $(`#id_${fieldName}`).val(), fieldElement.attr("id"), name, fieldElement.val())
                if (fieldElement.attr("id") == 'id_'+name) {
                    fieldElement.attr("id", '_id_'+name)
                    console.log('заменил _id');
                }
                if (!($('#id_'+name).val())) {
                    console.log('Создаем скрытое поле для хранения id');
                    const hiddenIdField = $("<input>", {
                        type: "hidden",
                        id: 'id_'+name,  // ID скрытого поля, совпадающего с именем в форме
                        name: name  // Поле для отправки в Django
                    }).val(ui.item.id);
                    hiddenIdField.insertAfter(fieldElement);
                } else {
                    $('#id_'+name).val(ui.item.id);
                }
                return false;
            }
        });
    });
});
