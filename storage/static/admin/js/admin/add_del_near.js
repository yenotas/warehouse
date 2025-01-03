document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-near-product');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();

            const productId = '{{ object.id }}'; // ID текущего продукта
            const nearProductId = this.getAttribute('data-id');

            fetch("{% url 'delete_near_product' %}", {
                method: 'POST',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}', // Не забудьте добавить CSRF-токен
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'product_id': productId,
                    'near_product_id': nearProductId,
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Обновляем страницу или удаляем элемент из DOM
                    alert(data.message);
                    location.reload(); // перезагрузите страницу или удалите элемент из списка
                } else {
                    alert(data.message);
                }
            })
            .catch(error => console.error('Ошибка:', error));
        });
    });
});
