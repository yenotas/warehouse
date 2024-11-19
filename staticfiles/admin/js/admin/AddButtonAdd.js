$(document).ready(function () {
    console.log(`AddButtonAdd: RUN`);
    $('.single_line_add').each(function () {
        const fieldElement = $(this);
        const fieldName = fieldElement.attr('field_name');
        const modelName = fieldElement.attr('model_name');
        const name = fieldElement.attr("name");
        let selectElement;

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
        selectElement = $(`#id_${modelName}`);
        if (!selectElement.length) {
            selectElement = $("<select>", {
                id: `id_${modelName}`,
                name: name,
                style: "display: none;"
            });
            container.append(selectElement);
            console.log(`AddButtonAdd: "${modelName}" создан селект id_${modelName} имя ${name}`);
        }

        // Создаём кнопку добавления
        if (!container.find(`a#add_id_${modelName}`).length) {
            const addButton = $("<a>", {
                class: "related-widget-wrapper-link add-related",
                id: `add_id_${modelName}`,
                "data-popup": "yes",
                href: `/admin/storage/${modelName}/add/?_to_field=id&_popup=1`,
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

        // Функция обновления поля после изменения select
//        function updateFieldFromSelect() {
//            const selectedOption = selectElement.find('option:selected');
//            if (selectedOption.length) {
//                const selectedValue = selectedOption.val();
//                const selectedText = selectedOption.text();
//
//                // Устанавливаем имя в текстовое поле
//                fieldElement.val(selectedText);
//
//                // Обновляем select с текущим значением
//                selectElement.empty().append(
//                    $("<option>", {
//                        value: selectedValue,
//                        selected: true
//                    }).text(selectedText)
//                );
//                console.log('Поле обновлено:', selectedText, selectedValue);
//            }
//        }
//
//        // Привязываем обработку события change
//        selectElement.on('change', updateFieldFromSelect);

        // Принудительное обновление при добавлении новых записей
//        $(document).on('focusout', `a#add_id_${modelName}`, function () {
//            setTimeout(function () {
//                // Проверяем изменения в select
//                $.ajax({
//                    url: `/admin/storage/${modelName}/`,
//                    success: function () {
//                        // Инициируем обновление select
//                        selectElement.trigger('change');
//                    }
//                });
//            }, 100);
//        });

        // Инициализация поля при загрузке формы
//        if (fieldElement.val()) {
//            $.ajax({
//                url: '/autocomplete/',
//                dataType: 'json',
//                data: {
//                    model_name: modelName,
//                    field_name: fieldName,
//                    item_id: fieldElement.val()
//                },
//                success: function (data) {
//                    if (data.text) {
//                        fieldElement.val(data.text);
//                        selectElement.empty().append(
//                            $("<option>", {
//                                value: fieldElement.val(),
//                                selected: true
//                            }).text(data.text)
//                        );
//                        console.log('Инициализация завершена:', data.text);
//                    }
//                },
//                error: function (jqXHR, exception) {
//                    console.log('Ошибка при инициализации:', exception);
//                }
//            });
//        }
    });
});
