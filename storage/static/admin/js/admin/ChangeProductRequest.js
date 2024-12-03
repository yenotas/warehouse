django.jQuery(document).ready(function($) {
    // При изменении запроса на продукт
    $(document).on('change', '#id_product_request', function() {
        var productId = $(this).val();
        $.ajax({
            url: `/get-product-data/${productId}/`,
            type: 'get',
            headers: { 'X-CSRFToken': csrftoken },
            success: function(data) {
                $('#supplier').val(data.supplier);
                $('#cell_address').val(data.cell_address);
                $('#stock_quantity').val(data.stock_quantity);
                console.log(data);
            },
            error: function(xhr, status, error) {
                console.error('Ошибка при загрузке данных:', status, error);
            }
        });
    });
});