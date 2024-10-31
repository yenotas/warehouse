$(document).ready(function() {
    let escPressed = false;
    let createNew = false;

    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            escPressed = true;
        }
    });

    $(document).on('input', '.select2-search__field', function() {
        let searchTerm = $(this).val();

        if (searchTerm) {
            $.ajax({
                url: '/categories-autocomplete/',
                type: 'GET',
                data: { q: searchTerm },
                success: function(data) {
                    if (data.results.length === 0) {
                        $('.select2-search__field').off('blur').on('blur', function() {
                            if (escPressed) {
                                escPressed = false;
                                return;
                            } else {
                                createNew = true;
                            }
                        });

                        $('.select2-search__field').off('keypress keydown').on('keypress keydown', function(e) {
                            if (['keypress', 'keydown'].includes(e.type) && e.which == 13) {
                                createNew = true;
                            } else createNew = false;

                            if (!escPressed && searchTerm.length > 1 && createNew) {
                                createNew = false;
                                $.ajax({
                                    url: '/categories-autocomplete/',
                                    type: 'GET',
                                    data: { 'create': '1', q: searchTerm },
                                    success: function(data) {
                                        let result = data.results[0];
                                        $('#id_category').empty().append(new Option(result.text, result.id, true, true)).trigger('change');
                                    },
                                    error: function(xhr, status, error) {
                                        console.error('Ошибка при добавлении новой категории:', status, error);
                                    }
                                });
                            }
                        });
                    } else {
                        $('#id_category').empty().append(data.results.map(function(item) {
                            return new Option(item.text, item.id, false, false);
                        }));
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Ошибка при поиске категорий:', status, error);
                }
            });
        }
    });
});
