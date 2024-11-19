$(document).ready(function () {
    $('.single_line_add').each(function () {
        const fieldElement = $(this);
        const fieldName = fieldElement.attr('field_name');
        const modelName = fieldElement.attr('model_name');
        const name = fieldElement.attr('name');

        // Создаем контейнер related-widget-wrapper
        const container = $("<div>", {
            class: "related-widget-wrapper single_line",
            "data-model-ref": modelName
        });

        // Клонируем исходное поле и обновляем его ID
        const clonedFieldElement = fieldElement.clone();
        clonedFieldElement.attr("id", `_id_${name}`);

        // Добавляем текстовое поле в контейнер
        container.append(clonedFieldElement);

        // Создаем скрытый select
        const selectElement = $("<select>", {
            id: `id_${modelName}`,
            name: name,
            style: "display: none;",
            "data-context": "available-source",
            "aria-describedby": `id_${modelName}_helptext`
        });

        // Добавляем select в контейнер
        container.append(selectElement);

        // Создаем кнопку добавления
        const addLink = $("<a>", {
            class: "related-widget-wrapper-link add-related",
            id: `add_id_${modelName}`,
            "data-popup": "yes",
            href: `/admin/storage/${modelName}/add/?_to_field=id&_popup=1`,
            title: "Добавить"
        });

        // Добавляем изображение иконки в кнопку
        const icon = $("<img>", {
            src: "/static/admin/img/icon-addlink.svg",
            alt: "",
            width: 20,
            height: 20
        });

        addLink.append(icon);
        container.append(addLink);

        // Заменяем только исходный элемент контейнером
        fieldElement.replaceWith(container);

            // Обработка новых записей, добавленных через кнопку
        $('body').on('change', `select#id_${modelName}`, function () {
            const selectedOption = $(this).find('option:selected');
            console.log('ADDED', selectedOption.val(), selectedOption.text());
            if (selectedOption.length) {
                const selectedValue = selectedOption.val();
                const selectedText = selectedOption.text();

                // Устанавливаем имя в текстовое поле
                fieldElement.val(selectedText);

                // Обновляем скрытый select
                selectElement.empty().append(
                    $("<option>", {
                        value: selectedValue,
                        selected: true
                    }).text(selectedText)
                );
            }
        });

        // Принудительное обновление при закрытии окна "Добавить"
        $(document).on('focusout', '.related-widget-wrapper-link.add-related', function () {
            setTimeout(function () {
                $(`select#id_${modelName}`).trigger('change');
            }, 100);
        });
    });
});
