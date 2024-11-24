$(document).ready(function() {

    const $password_sha = $('#id_password');
    if ($password_sha.length) {
        const $firstP = $password_sha.find('p').first();
        if ($firstP.length) {
            $firstP.css('display', 'none');
        }
    }

    const $resultTable = $('#result_list');
    if ($resultTable.length) {
        const $headers = $resultTable.find('th');
        $headers.each(function() { const $th = $(this);
            const $link = $th.find('a');
            if ($link.length) {
                $th.addClass('full-cell-link');
                $th.on('click', function() { window.location.href = $link.attr('href'); });
            }
        });
    }
    const $appTable = $('#nav-sidebar');
    if ($appTable.length) {
        const $headers = $appTable.find('th');
        $headers.each(function() { const $th = $(this);
            const $link = $th.find('a');
            if ($link.length) { $th.on('click', function() { window.location.href = $link.attr('href'); }); }
        });
    }

    // выключатель поля адрес доставки, если локация известна productRequesst
    var deliveryLocationField = $('#id_delivery_location');
    var deliveryAddressField = $('#id_delivery_address');

    function toggleDeliveryAddress() {
        var selectedValue = deliveryLocationField.val();
        if (['Монтаж', 'Подрядчик', 'Заказчик'].includes(selectedValue)) {
            deliveryAddressField.parents().eq(2).show();
        } else {
            deliveryAddressField.parents().eq(2).hide();
        }
    }
    deliveryLocationField.change(toggleDeliveryAddress);
    toggleDeliveryAddress();

    // выключатель поля Причина возврата поставщику productMovies
    var id_process_type = $('#id_process_type');
    var id_return_to_supplier_reason = $('#id_return_to_supplier_reason');

    function toggleSupplierReason() {
        var selectedValue = id_process_type.val();
        if (selectedValue == 'sup_return') {
            id_return_to_supplier_reason.parents().eq(2).show();
        } else {
            id_return_to_supplier_reason.parents().eq(2).hide();
        }
    }
    id_process_type.change(toggleSupplierReason);
    if (id_process_type.val()) { toggleSupplierReason() }

});

