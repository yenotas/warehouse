django.jQuery(document).ready(function($) {
  var totalForms = $('#id_form-TOTAL_FORMS');

  // Инициализируем обработчики для существующих строк
  $('.table-row-form tbody tr').each(function() {
    var row = $(this);
    initializeRow(row);
  });

  // Обработчик события вставки в первое поле первой строки
  var firstFieldName = formFields[0];
  $('#id_form-0-' + firstFieldName).on('paste', function(event) {
    event.preventDefault(); // Предотвращаем стандартное поведение

    var clipboardData = (event.originalEvent || event).clipboardData || window.clipboardData;
    var pastedData = clipboardData.getData('Text');

    processPastedData(pastedData);
  });

  function processPastedData(pastedData) {
    var rows = pastedData.trim().split(/\r?\n/);

    // Разбиваем данные на строки и ячейки
    var dataRows = [];
    for (var i = 0; i < rows.length; i++) {
      var cells = rows[i].split('\t'); // Используем табуляцию как разделитель
      if (cells.length <= formFields.length) {
        dataRows.push(cells);
      } else {
        alert('Ошибка: В строке ' + (i + 1) + ' неверное количество ячеек ('+ cells.length +'). Ожидалось максимум ' + formFields.length);
        return;
      }
    }

    // Добавляем новые формы, если необходимо
    var numNewForms = dataRows.length - 1;
    for (var i = 0; i < numNewForms; i++) {
      addEmptyForm();
    }

    // Заполняем формы данными
    for (var i = 0; i < dataRows.length; i++) {
      var rowData = dataRows[i];
      populateForm(i, rowData);
    }
  }

  function addEmptyForm() {
    var formIndex = totalForms.val();
    var emptyFormHtml = $('#empty_form').html().replace(/__prefix__/g, formIndex);
    $('.table-row-form tbody').append(emptyFormHtml);

    // Увеличиваем счетчик форм
    totalForms.val(parseInt(formIndex) + 1);

    // Инициализируем обработчики для новой строки
    var newRow = $('.table-row-form tbody tr').last();
    initializeRow(newRow);
  }

  function populateForm(index, rowData) {
    for (var j = 0; j < formFields.length; j++) {
      var fieldName = formFields[j];
      var fieldValue = rowData[j];

      // Пропускаем поле изображения
      if (fieldName === 'product_image' || fieldName.endsWith('image')) {
        continue;
      }

      $('#id_form-' + index + '-' + fieldName).val(fieldValue);
    }
  }

  function initializeRow(row) {
    // Обработка изображений, если поле изображения присутствует
    if (formFields.includes('product_image') || formFields.includes('image')) {
      // Инициализация обработчиков для изображения
      var imagePreviewContainer = row.find('.image_preview_container');
      var imagePreview = row.find('.image_preview');
      var removeImageButton = row.find('.remove_image_button');
      var imagePasteArea = row.find('.image_paste_area');
      var productImageInput = row.find('input[type="file"]');

      // код для обработки кликов, вставки изображений и т.д.
    }

    // Другие инициализации, если нужны
  }

  // код для обработки изображений (resizeImage и т.д.)
});
