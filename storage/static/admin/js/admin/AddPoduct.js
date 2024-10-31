$(document).ready(function() {

    let escPressed = false;
    let createNew = false;

    // Обработчик для нажатия клавиш
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            escPressed = true;
            console.log('Escape');
        }
    });

    // Обработка события для добавления нового департамента
    $(document).on('input', '.select2-search__field', function() {
        var searchTerm = $(this).val(); // Получаем введенный текст
        console.log('Searching for:', searchTerm); // Логирование для отладки
        if (searchTerm) {
            $.ajax({
                url: '/departments-autocomplete/',
                type: 'GET',
                data: {
                    q: searchTerm,
                },
                success: function(data) {
                    if (data.results.length === 0) {
                        console.log('data', data);

                        // Если нет совпадений, можем добавить новый вариант только при потере фокуса или нажатии Enter
                        $('.select2-search__field').off('blur').on('blur', function(e) {
                            if (escPressed) {
                                escPressed = false;
                                return
                            } else {
                                createNew = true;
                            }
                        });
                        $('.select2-search__field').off('keypress keydown').on('keypress keydown', function(e) {
                            console.log('e.type', e.type, e.which);
                            if (['keypress', 'keydown'].includes(e.type) && e.which == 13) {
                                createNew = true;
                            } else createNew = false;

                            if (!escPressed && searchTerm.length > 1 && createNew) {
                                console.log('UPDATE!', searchTerm.length, searchTerm);
                                createNew = false;
                                $.ajax({
                                    url: '/departments-autocomplete/',
                                    type: 'GET',
                                    data: {
                                        'create': '1',
                                        q: searchTerm,
                                    },
                                    success: function(data) {
                                        // Добавляем новый отдел в список и выбираем его
                                        var result = data.results[0];
                                        $('#id_department').empty().append(data.results.map(function(item) {
                                            return new Option(item.text, item.id, true, true);
                                        }));
                                        $('#id_department').val(result.id).trigger('change');  // Устанавливаем как выбранный
                                    },
                                    error: function(xhr, status, error) {
                                        console.error('Ошибка при добавлении нового департамента:', status, error);
                                    }
                                });
                            };
                        });

                    } else {
                        // Если есть совпадения, можем обновить список
                        $('#id_department').empty().append(data.results.map(function(item) {
                            return new Option(item.text, item.id, false, false);
                        }));
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Ошибка при поиске отделов:', status, error);
                }
            });
        }
    });

});