django.jQuery(document).ready(function($) {
  var totalForms = $('#id_form-TOTAL_FORMS');

  // Инициализируем обработчики для существующих строк
  $('.table-row-form tbody tr').each(function() {
    var row = $(this);
    initializeRow(row);
  });

  // Функция инициализации строки
  function initializeRow(row) {
    var imagePreviewContainer = row.find('.image_preview_container');
    var imagePreview = row.find('.image_preview');
    var removeImageButton = row.find('.remove_image_button');
    var imagePasteArea = row.find('.image_paste_area');
    var productImageInput = row.find('.product_image_input');

    // Одинарный клик - фокус на область вставки изображения
    imagePasteArea.on('click', function(event) {
      imagePasteArea.focus();
    });

    // Двойной клик - открытие диалога выбора файла
    imagePasteArea.on('dblclick', function(event) {
      productImageInput.click();
    });

    // Обработка изменения в input[type="file"]
    productImageInput.on('change', function() {
      var file = this.files[0];
      if (file) {
        resizeImage(file, 50, 50, function(resizedFile, dataURL) {
          // Заменяем файл в input[type="file"]
          var container = new DataTransfer();
          container.items.add(resizedFile);
          productImageInput[0].files = container.files;

          // Отображаем превью изображения
          imagePreview.attr('src', dataURL);
          imagePreview.css({ width: '50px', height: '50px' });
          imagePreview.show();
          imagePasteArea.hide();
          removeImageButton.show();
        });
      }
    });

    // Обработка вставки изображения из буфера обмена
    imagePasteArea.on('paste', function(event) {
      var items = (event.originalEvent.clipboardData || event.clipboardData).items;
      for (var i = 0; i < items.length; i++) {
        if (items[i].kind === 'file') {
          var file = items[i].getAsFile();
          resizeImage(file, 50, 50, function(resizedFile, dataURL) {
            var container = new DataTransfer();
            container.items.add(resizedFile);
            productImageInput[0].files = container.files;

            imagePreview.attr('src', dataURL);
            imagePreview.css({ width: '50px', height: '50px' });
            imagePreview.show();
            imagePasteArea.hide();
            removeImageButton.show();
          });
          console.log('Изображение вставлено из буфера обмена и масштабировано до 50x50 пикселей');
          break;
        }
      }
      setTimeout(function() {
        imagePasteArea.html('');
      }, 50);
    });

    // Обработка клика на кнопке удаления изображения
    removeImageButton.on('click', function(event) {
      event.preventDefault();
      imagePreview.hide();
      removeImageButton.hide();
      productImageInput.val('');
      imagePasteArea.show();
    });

    // Двойной клик по контейнеру превью изображения - открыть диалог выбора файла
    imagePreviewContainer.on('dblclick', function(event) {
      productImageInput.click();
    });
  }

  // Функция для масштабирования изображения (остается без изменений)
  function resizeImage(file, maxWidth, maxHeight, callback) {
    var reader = new FileReader();
    reader.onload = function(event) {
      var img = new Image();
      img.onload = function() {
        var canvas = document.createElement('canvas');
        canvas.width = maxWidth;
        canvas.height = maxHeight;
        var ctx = canvas.getContext('2d');

        ctx.clearRect(0, 0, maxWidth, maxHeight);
        ctx.drawImage(img, 0, 0, maxWidth, maxHeight);

        canvas.toBlob(function(blob) {
          var resizedFile = new File([blob], file.name, {
            type: file.type,
            lastModified: Date.now()
          });
          callback(resizedFile, canvas.toDataURL(file.type));
        }, file.type);
      }
      img.src = event.target.result;
    }
    reader.readAsDataURL(file);
  }
});