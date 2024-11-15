$(document).ready(function() {
    $('.single_line_add').each(function() {
        const fieldElement = $(this);
        const fieldName = fieldElement.attr('field_name');
        const modelName = fieldElement.attr('model_name');
        const name = fieldElement.attr("name");
        var selectElement = null;

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
                                value: item.text,
                                id: item.id
                            };
                        }));
                    }
                });
            },
            minLength: 2,
            select: function(event, ui) {

                fieldElement.val(ui.item.value);

                // Проверяем, существует ли скрытый select с id `id_<имя поля>`
                let name = fieldElement.attr("name");

                if (fieldElement.attr("id") == 'id_'+name) {
                    fieldElement.attr("id", '_id_'+name)
                    console.log('заменил _id');
                }

                if (!selectElement) {

                    // создаем новый скрытый select
                    let selectElement = $("<select>", {
                        id: `id_${name}`,
                        name: name,
                        style: "display: none;"
                    });
                    selectElement.append(
                        $("<option>", {
                            value: ui.item.id,
                            selected: true
                        }).text(ui.item.value)
                    );
                    selectElement.insertAfter(fieldElement);
                    console.log(selectElement.length, ui.item.value, ui.item.id);

                } else {
                    selectElement
                    .empty()
                    .append(
                        $("<option>", {
                            value: ui.item.id,
                            selected: true
                        }).text(ui.item.value)
                    );
                    console.log(selectElement.length, ui.item.value, ui.item.name);
                }
                return false;
            }
        });
    });
});
