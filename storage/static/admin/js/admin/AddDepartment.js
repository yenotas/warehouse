$(document).ready(function() {

    let escPressed = false;

    $(document).on('input', '.select2-search__field', function() {
        var searchTerm = $(this).val();
        var $inputField = $(this);

        if (searchTerm) {
            $.ajax({
                url: '/departments-autocomplete/',
                type: 'GET',
                data: {
                    q: searchTerm,
                },
                success: function(data) {
                    if (data.results.length === 0) {
                        // Нет совпадений, устанавливаем обработчики для blur и keydown
                        // Удаляем предыдущие обработчики
                        $inputField.off('blur keydown');
                        // Добавляем новые обработчики
                        $inputField.on('blur', function(e) {
                            if (!escPressed) {
                                createNewDepartment($inputField.val());
                            } else {
                                escPressed = false;
                            }
                        });

                        $inputField.on('keydown', function(e) {
                            if (e.which == 13) { // Клавиша Enter
                                e.preventDefault(); // Предотвращаем отправку формы
                                createNewDepartment($inputField.val());
                            } else if (e.which == 27) { // Клавиша ESC
                                escPressed = true;
                            }
                        });
                    } else {
                        // Есть совпадения, обновляем список и удаляем обработчики
                        $inputField.off('blur keydown');
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

    function createNewDepartment(departmentName) {
        if (departmentName && departmentName.length > 1) {
            $.ajax({
                url: '/departments-autocomplete/',
                type: 'GET',
                data: {
                    'create': '1',
                    q: departmentName,
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
        }
    }

    // Код для удаления блока помощи и зашифрованного пароля
    if ($('.field-password').length) {
        $('.field-password .help').remove();
        $('.field-password p')[0].remove();
    }

});
