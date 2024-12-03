django.jQuery(document).ready(function($) {
  // Функция для масштабирования изображения
  function resizeImage(file, maxWidth, maxHeight, callback) {
    var reader = new FileReader();
    reader.onload = function(event) {
      var img = new Image();
      img.onload = function() {
        var canvas = document.createElement('canvas');
        canvas.width = maxWidth;
        canvas.height = maxHeight;
        var ctx = canvas.getContext('2d');

        // Очистка canvas и отрисовка изображения с новым размером
        ctx.clearRect(0, 0, maxWidth, maxHeight);
        ctx.drawImage(img, 0, 0, maxWidth, maxHeight);

        // Получаем данные изображения из canvas
        canvas.toBlob(function(blob) {
          // Создаём новый файл из blob
          var resizedFile = new File([blob], file.name, {
            type: file.type,
            lastModified: Date.now()
          });
          callback(resizedFile, event.target.result);
        }, file.type);
      }
      img.src = event.target.result;
    }
    reader.readAsDataURL(file);
  }
    let clickTimer = null; // Таймер для отслеживания кликов

    $('#image_paste_area').off('click').on('click', function() {
        event.stopPropagation(); // Останавливаем всплытие
        event.preventDefault();
        console.log('click');
        const events = $._data($('#image_paste_area')[0], "events");
        console.log(events.click);
        if (clickTimer) {
            clearTimeout(clickTimer); // Сбрасываем таймер, если это второй клик
            clickTimer = null;
            $('#id_product_image').click(); // Открываем диалог выбора файла
        } else {
            clickTimer = setTimeout(() => {
                clickTimer = null; // Сбрасываем таймер, если второго клика не последовало
            }, 500); // Устанавливаем интервал ожидания второго клика
        }
    });

  // Обработка изменения в input[type="file"]
  $('#id_product_image').on('change', function() {
    var file = this.files[0];
    if (file) {
      resizeImage(file, '100%', 50, function(resizedFile, dataURL) {
        // Заменяем файл в input[type="file"]
        var container = new DataTransfer();
        container.items.add(resizedFile);
        document.getElementById('id_product_image').files = container.files;

        // Отображаем превью изображения
        $('#image_preview').attr('src', dataURL);
        $('#image_preview').show();
        $('#image_paste_area').hide();
        $('#image_paste_area_bg').hide();
        showRemoveButton();
      });
    }
  });

  // Обработка вставки изображения из буфера обмена
  $('#image_paste_area').on('paste', function(event) {
    var items = (event.originalEvent.clipboardData || event.clipboardData).items;
    for (var i = 0; i < items.length; i++) {
      if (items[i].kind === 'file') {
        var file = items[i].getAsFile();
        resizeImage(file, '100%', 50, function(resizedFile, dataURL) {
          // Устанавливаем файл в input[type="file"]
          var container = new DataTransfer();
          container.items.add(resizedFile);
          document.getElementById('id_product_image').files = container.files;

          // Отображаем превью изображения
          $('#image_preview').attr('src', dataURL);
          $('#image_preview').show();
          $('#image_paste_area').hide();
          $('#image_paste_area_bg').hide();
          showRemoveButton();
        });
        console.log('Изображение вставлено из буфера обмена и масштабировано до 50x50 пикселей');
        break;
      }
    }
    setTimeout(function() {
      $('#image_paste_area').html('');
    }, 50);
  });

  // Функции управления превью и кнопкой удаления
  function showRemoveButton() {
    $('#remove_image_button').show();
  }

  function hideRemoveButton() {
    $('#remove_image_button').hide();
  }

    // Обработка удаления изображения
    $('#remove_image_button').on('click', function(event) {
        event.preventDefault(); // Останавливаем дальнейшее всплытие событий
        $('#image_preview').hide();
        hideRemoveButton();
        $('#image_paste_area').show();
        $('#image_paste_area_bg').show();
        $('#id_product_image').val(''); // Очищаем значение файла
    });

    // Клик по контейнеру превью для замены изображения
//    $('#image_preview_container').on('click', function(event) {
//        if ($('#id_product_image').val() === '') {
//            return;
//        }
//        $('#id_product_image').click();
//    });
});
