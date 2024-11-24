$(document).ready(function() {
    console.log(`AddButtonAdd: RUN`);
    $('.single_line_add').each(function () {
        var fieldElement = $(this);
        var fieldName = fieldElement.attr('field_name');
        var relFieldName = fieldElement.attr('rel_field_name');
        var modelName = fieldElement.attr('model_name');
        var name = fieldElement.attr("name");
        var selectElement;

        // Создаём контейнер для текстового поля, кнопки и скрытого select
        const container = $("<div>", {
            class: "related-widget-wrapper single_line",
            "data-model-ref": modelName
        });

        // Перемещаем текстовое поле внутрь контейнера
        if (!fieldElement.parent().hasClass("related-widget-wrapper")) {
            fieldElement.before(container);
            container.append(fieldElement);
        }

        // Создаём скрытый select, если он ещё не существует
        selectElement = $(`#id_${fieldName}`);
        if (!selectElement.length) {
            selectElement = $("<select>", {
                id: `id_${fieldName}`,
                name: name,
                style: "display: none;"
            });
            container.append(selectElement);
            console.log(`AddButtonAdd: "${modelName}" создан селект id_${modelName} имя ${name}`);
        }

        // Создаём кнопку добавления
        const a = `a.add_id_${name}`;
        if (!container.find(a).length) {
            const id = `_id_${name}`
            const addButton = $("<a>", {
                class: "related-widget-wrapper-link add-related",
                "data-model": modelName,
                id: `add_id_${name}`,
                "data-popup": "yes",
                href: `/storage/${modelName}/add/?to_field=${id}&_popup=1`,
                title: "Добавить"
            }).append(
                $("<img>", {
                    src: "/static/admin/img/icon-addlink.svg",
                    alt: "",
                    style: "width: 20px; height: 20px;"
                })
            );
            container.append(addButton);
            console.log(`AddButtonAdd: "${modelName}" селект в контейнере, кнопка добавлена`);

        }
    });

    $('.auto_complete').each(function() {
        var fieldElement = $(this);
        var currentId = fieldElement.attr('data-initial-id');
        var modelName = fieldElement.attr('model_name');
        var relFieldName = fieldElement.attr('rel_field_name');
        console.log(`прокси для поля "${fieldElement.attr('field_name')}" =`, relFieldName);
        var fieldName = relFieldName || fieldElement.attr('field_name');
        var name = fieldElement.attr("name");

        // Меняем id у input для избежания конфликта
        if (fieldElement.attr("id") === `id_${name}`) {
            fieldElement.attr("id", `_id_${name}`);
            console.log(`Autofields: ID инпута изменен на "_id_${name}"`);
        }

        // Проверяем, существует ли скрытый select, если нет — создаем
        var selectElement = $(`#id_${name}`);

        if (!selectElement.length) {
            selectElement = $("<select>", {
                id: `id_${name}`, // ID совпадает с исходным для поля
                name: name,
                style: "display: none;"
            });
            fieldElement.after(selectElement);
            console.log(`Autofields: Создан новый select с id "id_${name}"`);
        }

        // Проверка на реопенинг: если есть значение, отправляем запрос
        if (currentId) {
            get_item_name_by_id();
        }

        var observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeName === 'OPTION') {
                            console.log('New option added:', node.value, node.textContent);
                            if (selectElement.children('option').length > 1) {
                                var lastOption = selectElement.find('option:last');
                                var selectedValue = lastOption.val();
                                selectElement.empty().append(lastOption).val(selectedValue).trigger('change');
                            }
                            fieldElement.val(node.textContent);
                        }
                    });
                }
            });
        });
        observer.observe(selectElement[0], { childList: true });

        function get_item_name_by_id(){

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
                        console.log(`Реопенинг: текстовое значение "${data.text}" установлено. ID =`, currentId);
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
                        field_name: fieldName,
                        allowed_fields: window.searchFieldsList || []
                    },
                    success: function(data) {
                        response($.map(data, function(item) {
                            return {
                                value: item.text, // Отображаемое имя
                                id: item.id       // ID записи
                            };
                        }));
                    }
                });
            },
            minLength: 2,
            delay: 300,
            select: function(event, ui) {
                fieldElement.val(ui.item.value);

                // Очищаем и обновляем select с правильным значением
                selectElement.empty().append(
                    $("<option>", {
                        value: fieldElement.hasClass('single_line_add') ? ui.item.id : ui.item.value,
                        selected: true
                    }).text(ui.item.value)
                );

                console.log('Autofields: Выбрано:', ui.item.value, ui.item.id);
                return false; // Отключаем стандартное поведение autocomplete
            },
            change: function(event, ui) {
                const manualText = fieldElement.val();
                if (!ui.item && manualText) {
                    // Если пользователь вручную ввел текст, очищаем select

                    selectElement.empty().append(
                    $("<option>", {
                        value: manualText,
                        selected: true
                    }).text(manualText));
                    console.log('Autofields: Введено вручную, очищаем select:', manualText);
                }
                return false; // Отключаем стандартное поведение autocomplete
            }
        });
    });
});
