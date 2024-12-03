django.jQuery(document).ready(function($) {

    console.log('DoubleClickAdd');

    $('.single_line').each(function () {
        var fieldElement = $(this);
        var id = fieldElement.attr('id');
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
        if (id.split('_')[1] === `${name}`) {
            fieldElement.attr("id", '_'+id);
            console.log(`Autofields: ID инпута изменен на "_${id}"`);
        }


        if (fieldElement.parent().hasClass("t_row")) {
            console.log('fieldElement в контейнере');
            fieldElement.before(container);
            container.append(fieldElement);
            table_view = true;
        }

        // Создаём скрытый select, если он ещё не существует
        selectElement = $(`#${id}`);
        if (!selectElement.length) {
            selectElement = $("<select>", {
                id: `${id}`,
                name: name,
                style: "display: none;"
            });
           container.append(selectElement);
           console.log(`"${modelName}" создан селект ${id} имя ${name}`);
        }

        let addButton = `a.add_${id}`;
        if (!container.find(addButton).length) {
            const to_field = `_${id}`;
            addButton = $("<a>", {
                "class": "related-widget-wrapper-link add-related",
                "data-model": modelName,
                "id": `add_${id}`,
                "data-popup": "yes",
                "style": "display: none;",
                "href": `/storage/${modelName}/add/?to_field=${to_field}&_popup=1`
            });

        container.append(addButton);

        }

        fieldElement.on('dblclick', function(event) {
            event.preventDefault();
            addButton.click();
            /*var url = `/storage/${modelName}/add/?_popup=1&to_field=${id}`;
            var win = window.open(url, '_blank', 'width=1200,height=300,resizable=yes,scrollbars=yes');
            win.focus();*/
        });


        // Обработчик события optionAdded
        selectElement.on('optionAdded', function(event) {
            console.log('New option added:', event);
            selectElement.find('option:selected').remove();
            selectElement.find('option:last').prop('selected', true);
            var selectedText = selectElement.find('option:selected').text();
            fieldElement.val(selectedText);
        });

        var observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeName === 'OPTION') {
                            console.log('New option added:', node.value, node.textContent);
                            if (selectElement.children('option').length > 1) {
                                selectElement.find('option:selected').remove();
                                selectElement.find('option:last').prop('selected', true);
                            }
                            fieldElement.val(node.textContent);
                        }
                    });
                }
            });
        });
        observer.observe(selectElement[0], { childList: true });

    });

});