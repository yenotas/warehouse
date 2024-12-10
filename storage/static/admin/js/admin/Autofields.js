window.dismissChangeRelatedObjectPopup = function (win, objId, newRepr) {
    console.log('dismissChangeRelatedObjectPopup called:', objId, newRepr);

    // Получаем ID поля из имени окна
    const id = win.name.replace(/^change_/, '');
    const elem = document.getElementById(id);

    if (elem) {
        // Обновляем значение текстового поля
        elem.value = newRepr;
        elem.dispatchEvent(new Event('change'));

        // Обновляем скрытое поле, если оно существует
        const hiddenField = document.getElementById(`${id.replace('_name', '_id')}`);
        if (hiddenField) {
            hiddenField.value = objId;
        }

    } else {
        console.error('Field not found for ID:', id);
    }

    console.log('win.close();');
    win.close();
};


django.jQuery(document).ready(function($) {

    function windowname_to_id(name) {
        return name.replace(/^(change|add|delete)_/, '');
    }

    window.dismissAddRelatedObjectPopup = function(win, newId, newRepr) {
        var textFieldId = windowname_to_id(win.name);
        var elem = $('#' + textFieldId);
        // для текстового поля
        elem.val(newRepr);
        // для скрытого поля
        var hiddenFieldId = textFieldId.replace('_name', '_id');
        $('#' + hiddenFieldId ).val(newId);
        elem.trigger('change');
        $('#' + hiddenFieldId ).trigger('change');
        win.close();
        console.log('dismiss: hidden id='+hiddenFieldId, 'order id='+newId, 'input elem id='+textFieldId, 'value='+newRepr);
    }

});

django.jQuery(document).ready(function($) {
    $('.auto_complete').each(function() {
        var fieldElement = $(this);
        var id = fieldElement.attr('id');
        var fieldName = fieldElement.data('field-name');
        var modelName = fieldElement.data('model-name');
        var isRelField = fieldElement.hasClass('rel_field');
        var hiddenFieldName = null;

        if (isRelField) {
            const container = $("<div>", {
                class: "related-widget-wrapper",
                "data-model-ref": modelName
            });
            if (fieldElement.parent().hasClass("t_row")) {
                console.log('fieldElement в контейнере');
                fieldElement.before(container);
                container.append(fieldElement);
            }

            hiddenFieldName = fieldElement.attr('name').replace('_name', '_id');
            const hiddenInput = $('input[name="' + hiddenFieldName + '"]');
            container.append(hiddenInput);

            fieldElement.on('dblclick', function(event) {
                event.preventDefault();

                const modelName = $(this).data('modelName');
                const idFieldName = $(this).attr('name').replace('_name', '_id');
                const hiddenInput = $(`[name="${idFieldName}"]`);
                const id = $(this).attr('id');

                const baseUrl = `/storage/${modelName}`;
                const isEdit = hiddenInput.length && hiddenInput.val(); // Проверяем, есть ли ID связанной записи
                const recordId = hiddenInput.val(); // Получаем ID, если он есть
                const url = isEdit
                    ? `${baseUrl}/${recordId}/change/?_to_field=id&_popup=1` // Редактирование
                    : `${baseUrl}/add/?_popup=1&to_field=${id}`; // Добавление
                const win_name = isEdit ? "change_"+id : "add_"+id
                const popupWindow = window.open(url, win_name, 'width=1200,height=300,resizable=yes,scrollbars=yes');
                if (popupWindow) {
                        popupWindow.focus();
                    }
            });
        }

        fieldElement.autocomplete({
            minLength: 2,
            source: function(request, response) {
                $.ajax({
                    url: '/autocomplete/',
                    dataType: 'json',
                    data: {
                        term: request.term,
                        model: modelName,
                        field: fieldName
                    },
                    success: function(data) {
                        response($.map(data, function(item) {
                            return {
                                label: item.label,
                                value: item.value,
                                id: item.id
                            };
                        }));
                    }
                });
            },
            select: function(event, ui) {
                fieldElement.val(ui.item.value);
                if (isRelField && hiddenFieldName) {
                    $('input[name="' + hiddenFieldName + '"]').val(ui.item.id);
                }
                return false;
            },
            focus: function(event, ui) {
                fieldElement.val(ui.item.value);
                return false;
            }
        });
    });
});
