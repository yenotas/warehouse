django.jQuery(document).ready(function($) {
    const fieldsToDisableContainer = $('#id_fields_to_disable');
    const modelId = $('#id_model_name').val();
    const ruleId = window.location.pathname.includes('change')
                   ? window.location.pathname.split('/').slice(-3, -2)[0]
                   : null;

    // Если форма открыта в режиме изменения
    if (ruleId && modelId) {
        // console.log('ruleId', ruleId);

        // Получаем сохраненные поля
        fetch(`/get-saved-fields/?rule_id=${encodeURIComponent(ruleId)}`)
            .then(response => response.json())
            .then(data => {
                const savedFields = data['fields_to_disable'] || [];
                fetchFieldsForModel(modelId, savedFields);
                // console.log('get-saved-fields', savedFields);
            })
            .catch(error => console.error('Ошибка при загрузке полей:', error));

        $('#id_model_name').prop('disabled', true);
        $('<input>').attr({
            type: 'hidden',
            name: 'model_name',
            value: $('#id_model_name').val()
        }).appendTo('#id_model_name').parent();
    }

    // Обработчик смены модели
    $('#id_model_name').change(function() {
        const newModelId = $(this).val();
        if (newModelId) {
            fetchFieldsForModel(newModelId);
        }
    });

    // Функция для загрузки полей модели
    function fetchFieldsForModel(modelId, savedFields = []) {
        fieldsToDisableContainer.empty();

        if (modelId) {
            fetch(`/get-model-fields/?model_id=${encodeURIComponent(modelId)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.fields && data.fields.length > 0) {
                        data.fields.forEach(field => {
                            if (field.name !== "id") {
                                const checkbox = $(`
                                    <div class="flex-container checkbox-row">
                                        <input type="checkbox" id="field_${field.name}" name="fields_to_disable" value="${field.name}">
                                        <label class="vCheckboxLabel" for="field_${field.name}">${field.verbose_name}</label>
                                    </div>
                                `);
                                fieldsToDisableContainer.append(checkbox);
                            }
                        });

                        // Отмечаем сохраненные поля как выбранные
                        // console.log('savedFields', savedFields);

                        if (typeof savedFields === 'string') {
                            try {
                                savedFields = JSON.parse(savedFields); // Десериализация, если savedFields строка JSON
                            } catch (error) {
                                console.error("Ошибка при парсинге JSON:", error);
                                savedFields = []; // Устанавливаем пустой массив, если произошла ошибка
                            }
                        }

                        if (Array.isArray(savedFields)) {
                            savedFields.forEach(savedField => {
                                fieldsToDisableContainer.find(`input[value="${savedField}"]`).prop('checked', true);
                            });
                        } else {
                            console.error("savedFields не является массивом:", savedFields);
                        }
                    } else {
                        fieldsToDisableContainer.append('<p>Нет доступных полей для этой модели.</p>');
                    }
                })
                .catch(error => console.error('Ошибка при загрузке полей:', error));
        }
    }
    // При отправке формы сериализуем чекбоксы в JSON
    $('form').on('submit', function(event) {
        event.preventDefault(); // Предотвращаем отправку формы

        // Собираем значения отмеченных чекбоксов
        const selectedFields = [];
        fieldsToDisableContainer.find('input[type="checkbox"]:checked').each(function() {
            selectedFields.push($(this).val());
        });

        // Преобразуем в JSON и сохраняем в скрытое поле
        const jsonFields = JSON.stringify(selectedFields);
        $('#id_fields_to_disable').val(jsonFields);

        // Отправляем форму
        this.submit();
    });
});
