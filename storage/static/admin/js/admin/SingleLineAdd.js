django.jQuery(document).ready(function($) {

    console.log('SingleLineAdd');

    $('.rel_field').each(function () {
        var fieldElement = $(this);
        var fieldName = fieldElement.attr('field_name');
        var relFieldName = fieldElement.attr('rel_field_name');
        var modelName = fieldElement.attr('model_name');
        var name = fieldElement.attr("name");
        var selectElement;

        // Создаём контейнер для текстового поля и скрытого select
        const container = $("<div>", {
            class: "related-widget-wrapper",
            "data-model-ref": modelName
        });

        // Меняем id у input для избежания конфликта
        if (fieldElement.attr("id") === `id_${name}`) {
            fieldElement.attr("id", `_id_${name}`);
            console.log(`Autofields: ID инпута изменен на "_id_${name}"`);
        }

        const label = $("label[for='id_"+name+"']");
        let table_view = false;

        if (label.parent().hasClass("t_row")) {
            console.log('label в контейнере');
            // Создаем контейнер заголовка таблицы и перемещаем метку внутрь
            label.before(container);
            container.append(label);
            table_view = true;
        } else {
            if (!fieldElement.parent().hasClass("related-widget-wrapper")) {
                console.log('fieldElement в контейнере');
                fieldElement.before(container);
                container.append(fieldElement);
            }
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
           console.log(`"${modelName}" создан селект id_${fieldName} имя ${name}`);
        }

        // Создаём кнопку добавления
        const a = `a.add_id_${name}`;
        if (!container.find(a).length) {
            const to_field = `_id_${name}`;
            let addButton = $("<a>", {
                class: "related-widget-wrapper-link add-related",
                "data-model": modelName,
                id: `add_id_${name}`,
                "data-popup": "yes",
                // href: `/storage/${modelName}/add/?to_field=${to_field}&_popup=1`,
                href: `${window.location.origin}/storage/${modelName}/add/?to_field=${to_field}&_popup=1`,
                title: "Добавить"
            }).append( $("<img>", {src: "/static/admin/img/icon-addlink.svg", alt: "Добавить"}));

            container.append(addButton);

            if (table_view) {
                console.log('Переопределил addButton');
                addButton.click(function(event) {
                    event.preventDefault();
                    const django = window.parent.django;
                    this.href = `${window.location.origin}/storage/${modelName}/add/?to_field=${to_field}&_popup=1`,
                    //showRelatedTablePopup(this);
                    django.contrib.admin.widgets.relatedFieldWidgetWrapper.showRelatedObjectLookupPopup(this);
                });
            }

            console.log(`"${modelName}" селект в контейнере, кнопка добавлена`);
        }
    });
});