$(document).ready(function() {

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
        if (selectedValue == 'Возврат поставщику') {
            id_return_to_supplier_reason.parents().eq(2).show();
        } else {
            id_return_to_supplier_reason.parents().eq(2).hide();
        }
    }
    id_process_type.change(toggleSupplierReason);
    toggleSupplierReason();

});