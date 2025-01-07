window.dismissChangeRelatedObjectPopup = function (win, objId, newRepr) {
    console.log('dismissChangeRelatedObjectPopup called:', objId, newRepr);

    const id = win.name.replace(/^change_/, '');
    const elem = document.getElementById(id);

    if (elem) {
        elem.value = newRepr;
        elem.dispatchEvent(new Event('change'));

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
    function window_name_to_id(name) {
        return name.replace(/^(change|add|delete)_/, '');
    }

    window.dismissAddRelatedObjectPopup = function(win, newId, newRepr) {
        var textFieldId = window_name_to_id(win.name);
        var elem = $('#' + textFieldId);

        elem.val(newRepr);

        var hiddenFieldId = textFieldId.replace('_name', '_id');
        $('#' + hiddenFieldId ).val(newId);
        elem.trigger('change');
        $('#' + hiddenFieldId ).trigger('change');
        win.close();
    }

    // Инициализация автозаполнения
    window.initializeAutoCompleteFields = function() {
        $('.auto_complete').each(function() {
            var fieldElement = $(this);
            var id = fieldElement.attr('id');
            var fieldName = fieldElement.data('field-name');
            var modelName = fieldElement.data('model-name');
            var dataFilter = fieldElement.data('filter');
            var filterField = fieldElement.data('filter_field');
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
                    const isEdit = hiddenInput.length && hiddenInput.val();
                    const recordId = hiddenInput.val();
                    const url = isEdit
                        ? `${baseUrl}/${recordId}/change/?_to_field=id&_popup=1`
                        : `${baseUrl}/add/?_popup=1&to_field=${id}`;
                    const win_name = isEdit ? "change_"+id : "add_"+id;
                    const popupWindow = window.open(url, win_name, 'width=1200,height=300,resizable=yes,scrollbars=yes');
                    if (popupWindow) {
                        popupWindow.focus();
                    }
                });
            }

            fieldElement.autocomplete({
                minLength: 0,
                source: function(request, response) {
                    const term = request.term || '';
                    $.ajax({
                        url: '/autocomplete/',
                        dataType: 'json',
                        data: {
                            term: term,
                            model: modelName,
                            field: fieldName,
                            data_filter: dataFilter,
                            filter_field: filterField
                        },
                        success: function(data) {
                            let uniqueItems = data;
                            if (!isRelField) {
                                uniqueItems = data.filter((item, index, self) =>
                                    index === self.findIndex((t) => (t.value === item.value))
                                );
                            }
                            response($.map(uniqueItems, function(item) {
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

            fieldElement.on('focus', function() {
                console.log('focus!');
                if (!fieldElement.val()) {
                    fieldElement.autocomplete('search', '');
                }
            });
        });
    }

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const activeElement = document.activeElement;
            if (activeElement.tagName === 'INPUT' && activeElement.type === 'text') {
                activeElement.value = '';
                if ($(activeElement).hasClass('auto_complete')) {
                    initializeAutoCompleteFields();
                    $(activeElement).blur();
                    setTimeout(function() { activeElement.focus(); }, 20);
                }
            }
        }
         if (e.ctrlKey && e.key === 'Delete') {
            e.preventDefault();
            removeFocusedRow();
         }
    });

    // Функция для удаления строки формы из formset
    function removeFocusedRow() {
        var focusedElement = $(':focus'); // Получаем элемент, на котором сейчас фокус
        var formRow = focusedElement.closest('tbody tr'); // Находим ближайшую строку

        if (formRow.length) {
            // Найти первое поле в строке для извлечения номера формы
            var firstField = formRow.find('input, select, textarea').first();
            var fieldName = firstField.attr('name') || '';
            var match = fieldName.match(/form-(\d+)-/);

            if (match) {
                var formNumber = match[1];
                var checkboxName = `form-${formNumber}-DELETE`;
                var checkboxId = `id_${checkboxName}`;

                var deleteCheckbox = formRow.find('input[type="checkbox"][name$="-DELETE"]');

                // Если чекбокса нет, создаем его и добавляем в строку
                if (!deleteCheckbox.length) {
                    deleteCheckbox = $('<input>', {
                        type: 'checkbox',
                        name: checkboxName,
                        id: checkboxId,
                        value: 'on',
                    });
                    formRow.append(deleteCheckbox);
                }
                deleteCheckbox.click();
                deleteCheckbox.checked = true;
                deleteCheckbox.prop('checked', true);
                deleteCheckbox.trigger('change');
                formRow.addClass('hidden');
                console.log('Row marked for deletion. checked =', deleteCheckbox.checked);
                return
            }
        }
        console.log('No focused form row found.');
    }

    // Инициализация автозаполнения при загрузке страницы
    initializeAutoCompleteFields();
});