django.jQuery(document).ready(function ($) {
    $('.img_cell').each(function () {
        const imgCell = $(this);
        const productImageInput = imgCell.find('.product_image'); // Стандартное поле загрузки
        const imagePreview = imgCell.find('.image_preview');
        // const imagePasteArea = img_cell.find('.image_paste_area');
        const imagePasteAreaBG = imgCell.find('.image_paste_area_bg');
        const removeImageButton = imgCell.find('.remove_image_button');

        // Скрываем стандартный виджет загрузки
        productImageInput.closest('p.file-upload').hide();

        // Проверяем, есть ли уже загруженное изображение
        const currentImageLink = imgCell.find('p.file-upload a').attr('href');
        if (currentImageLink) {
            // Отображаем превью и кнопку удаления
            removeImageButton.show();
            imagePreview.attr('src', currentImageLink).show();
            imagePasteAreaBG.hide();

        }

        // Удаление изображения по кнопке "X"
        removeImageButton.on('click', function (e) {
            e.preventDefault();
            imagePreview.hide().attr('src', '#');
            imagePasteArea.show();
            imagePasteAreaBG.show();
            removeImageButton.hide();

            // Помечаем изображение для удаления в стандартном виджете
            const clearCheckbox = imgCell.find('[name$="-product_image-clear"]');
            if (clearCheckbox.length) {
                clearCheckbox.prop('checked', true);
            }
        });
    });
});
