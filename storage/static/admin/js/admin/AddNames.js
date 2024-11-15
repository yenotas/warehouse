const autocompleteUrl = '/names-autocomplete/' + window.location.href.split('/storage/')[1].split('/')[0] + '/'

$(document).ready(function() {

    let escPressed = false;
    let createNew = false;

    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            escPressed = true;
            console.log('Escape');
        }
    });

    $(document).on('input', '.select2-search__field', function() {
        var searchTerm = $(this).val();
        console.log('Searching for:', searchTerm);
        if (searchTerm) {
            $.ajax({
                url: autocompleteUrl,
                type: 'GET',
                data: {
                    q: searchTerm,
                },
                success: function(data) {
                    if (data.results.length === 0) {
                        console.log('data', data);

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
                                    url: autocompleteUrl,
                                    type: 'GET',
                                    data: {
                                        'create': '1',
                                        q: searchTerm,
                                    },
                                    success: function(data) {

                                        var result = data.results[0];
                                        $('#id_name').empty().append(data.results.map(function(item) {
                                            return new Option(item.text, item.id, true, true);
                                        }));
                                        $('#id_name').val(result.id).trigger('change');


                                    },
                                    error: function(xhr, status, error) {
                                        console.error('Ошибка при добавлении нового:', status, error);
                                    }
                                });
                            };
                        });

                    } else {

                        $('#id_name').empty().append(data.results.map(function(item) {
                            return new Option(item.text, item.id, false, false);
                        }));
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Ошибка при поиске:', status, error);
                }
            });
        }
    });

});