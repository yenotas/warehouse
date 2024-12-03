django.jQuery(document).ready(function($) {

    console.log('Autofields');

    $('.auto_complete').each(function() {
        var fieldElement = $(this);

        var modelName = fieldElement.attr('model_name');
        var relFieldName = fieldElement.attr('rel_field_name');
        console.log(`прокси для поля "${fieldElement.attr('field_name')}" =`, relFieldName);
        var fieldName = relFieldName || fieldElement.attr('field_name');
        var name = fieldElement.attr("name");

        // Проверяем, существует ли скрытый select, если нет — создаем
        var selectElement = $(`#id_${name}`);

        if (!selectElement.length) {
            selectElement = $("<select>", {
                id: `id_${name}`, // ID совпадает с исходным для поля
                name: name,
                style: "display: none;"
            });
            selectElement.before(fieldElement);
            console.log(`Autofields: Создан новый select с id "id_${name}"`);
        }

        // Проверка на реопенинг: если есть значение, отправляем запрос
        if (fieldElement.val()) {
            get_item_name_by_id();
        }

        function get_item_name_by_id(){
            var currentId = fieldElement.val();
            console.log(`Autofields: "${modelName}" Реопенинг: поле "${fieldName}" имеет ID: ${currentId}`);

            // Запрос для получения текстового значения по ID
            $.ajax({
                url: '/autocomplete/',
                dataType: 'json',
                data: {
                    item_id: currentId,
                    model_name: modelName,
                    field_name: fieldName
                },
                success: function(data) {
                    if (data.text) {

                        // Обновляем select с текущим значением
                        selectElement.empty().append(
                            $("<option>", {
                                value: currentId,
                                selected: true
                            }).text(data.text)
                        );
                        console.log(`Реопенинг: текстовое значение "${data.text}" установлено.`);
                    }
                },
                error: function(jqXHR, exception) {
                    console.log('Autofields: Ошибка реопенинга:', exception, modelName, fieldName, currentId);
                }
            });
        }

        // Подключаем автозаполнение
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
                        response($.map(data, function(item) {
                            return {
                                value: item.text,  // Отображаемое имя
                                id: item.id || item.text  // ID записи
                            };
                        }));
                    }
                });
            },
            minLength: 2,
            select: function(event, ui) {
                fieldElement.val(ui.item.value);

                // Очищаем и обновляем select с правильным значением
                selectElement.empty().append(
                    $("<option>", {
                        value: ui.item.id,
                        selected: true
                    }).text(ui.item.value)
                );

                console.log('Autofields: Выбрано:', ui.item.value, ui.item.id);
                return false; // Отключаем стандартное поведение autocomplete
            },
            change: function(event, ui) {
                const manualText = fieldElement.val();
                if (!ui.item && manualText) {
                    // Если пользователь вручную ввел текст, копируем текст в select

                    selectElement.empty().append(
                    $("<option>", {
                        value: ui.item.id,
                        selected: true
                    }).text(fieldElement.val()));
                    console.log('Autofields: Введено вручную, очищаем select:', manualText);
                }
            }
        });

        // Обработка ввода вручную (если пользователь ничего не выбрал)
        /*fieldElement.on('input', function() {
            const currentText = fieldElement.val();
            selectElement.empty(); // Удаляем все options из select
            console.log(`Autofields: Поле "${fieldName}" изменено, удаляем старый ID.`);
        });*/
    });


});
