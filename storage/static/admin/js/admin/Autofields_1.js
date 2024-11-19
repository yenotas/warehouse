$(document).ready(function() {
    $('.single_line_add').each(function() {
        var fieldElement = $(this);
        var fieldName = fieldElement.attr('field_name');
        var reopen = {};
        var modelName = fieldElement.attr('model_name');
        var name = fieldElement.attr("name");
        var item_id = fieldElement.val()
        var selectElement = null;
        console.log('reopen', item_id, name, fieldName, reopen[name])

        if (fieldElement.val() && name != fieldElement.attr('field_name') && !reopen[name]) {
            console.log('1) запрос по id:', name, fieldElement.attr('field_name'), fieldElement.attr('id'), );
            reopen[name] = true;

            $.ajax({
                url: '/autocomplete/',
                dataType: 'json',
                data: {
                    model_name: modelName,
                    field_name: fieldName,
                    item_id: fieldElement.val() // Отправляем ID
                },
                success: function(data) {
                    if (data.text) {
                        console.log('data', data.text)
                        fieldElement.val(data.text); // Устанавливаем имя в поле
                    }
                },
                error: function (jqXHR, exception) {
                    console.log('error', exception);
                }
            });
            // Проверяем, существует ли скрытый select с id `id_<имя поля>`

            if (fieldElement.attr("id") == 'id_'+name) {
                fieldElement.attr("id", '_id_'+name)
                console.log('1) заменил _id');
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
                        value: item_id,
                        selected: true
                    }).text(fieldElement.val())
                );
                fieldElement.after(selectElement);
                console.log('1) create', selectElement.length, fieldElement.val(), item_id);

            } else {
                selectElement
                .empty()
                .append(
                    $("<option>", {
                        value: item_id,
                        selected: true
                    }).text(fieldElement.val())
                );
                console.log('1) edited', selectElement.length, fieldElement.val(), item_id);
            }
        }

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
                    console.log('2) заменил _id');
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
                    fieldElement.after(selectElement);
                    console.log('2) create', selectElement.length, ui.item.value, ui.item.id);

                } else {
                    selectElement
                    .empty()
                    .append(
                        $("<option>", {
                            value: ui.item.id,
                            selected: true
                        }).text(ui.item.value)
                    );
                    console.log('2) edited', selectElement.length, ui.item.value, ui.item.id);
                }
                return false;
            }
        });
    });
});
