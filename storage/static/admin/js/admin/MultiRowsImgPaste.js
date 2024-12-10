django.jQuery(document).ready(function($) {

  // Инициализируем обработчики для существующих строк
  window.initializeImgCell = function(img_cell) {
    initializeCell(img_cell);
  }

  $('.img_cell').each(function() {
    var img_cell = $(this);
    initializeCell(img_cell);
  });

  // Функция инициализации строки
  function initializeCell(img_cell) {
    var imagePreviewContainer = img_cell.find('.image_preview_container');
    var imagePreview = img_cell.find('.image_preview');
    var removeImageButton = img_cell.find('.remove_image_button');
    var imagePasteArea = img_cell.find('.image_paste_area');
    var imagePasteAreaBG = img_cell.find('.image_paste_area_bg');
    var productImageInput = img_cell.find('.product_image');

    // Одинарный клик - фокус на область вставки изображения
    imagePasteArea.on('click', function(event) {
      console.log('click');
      imagePasteArea.focus();
    });

    // Двойной клик - открытие диалога выбора файла
    imagePasteArea.on('dblclick', function(event) {
      console.log('dblclick');
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
          imagePasteAreaBG.hide();
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
          resizeImage(file, 1000, 50, function(resizedFile, dataURL) {
            var container = new DataTransfer();
            container.items.add(resizedFile);
            productImageInput[0].files = container.files;

            imagePreview.attr('src', dataURL);
            imagePasteAreaBG.hide();
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
      imagePasteAreaBG.show();
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
                // Вычисляем пропорции
                var ratio = maxHeight / img.height;

                var newWidth = img.width * ratio;
                var newHeight = img.height * ratio;

                // Создаем canvas для изменения размера
                var canvas = document.createElement('canvas');
                canvas.width = newWidth;
                canvas.height = newHeight;

                var ctx = canvas.getContext('2d');
                ctx.clearRect(0, 0, newWidth, newHeight);
                ctx.drawImage(img, 0, 0, newWidth, newHeight);

                // Преобразуем в Blob и передаем callback
                canvas.toBlob(function(blob) {
                    var resizedFile = new File([blob], file.name, {
                        type: file.type,
                        lastModified: Date.now()
                    });
                    callback(resizedFile, canvas.toDataURL(file.type));
                }, file.type);
            };
            img.src = event.target.result;
        };
        reader.readAsDataURL(file);
    }

});