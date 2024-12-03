django.jQuery(document).ready(function($) {
  // Обработчик события paste для поля 'name'
  $('#id_name').on('paste', function(event) {
    // Предотвращаем стандартное поведение, если нужно
    // event.preventDefault();

    // Получаем данные из буфера обмена
    var clipboardData = (event.originalEvent || event).clipboardData || window.clipboardData;
    var pastedData = clipboardData.getData('Text');

    // Вызываем функцию для обработки данных
    processPastedData(pastedData);
  });

  function processPastedData(pastedData) {
    // Разделяем данные на строки
    var rows = pastedData.trim().split(/\r?\n/);

    // Перебираем строки и разбиваем каждую на ячейки
    var dataRows = [];
    for (var i = 0; i < rows.length; i++) {
      var cells = rows[i].split('\t'); // Предполагаем, что данные разделены табуляцией
      if (cells.length === 5) {
        dataRows.push(cells);
      } else {
        alert('Ошибка: В строке ' + (i + 1) + ' неверное количество ячеек. Ожидалось 5.');
        return;
      }
    }

    // Если всё хорошо, добавляем строки в таблицу и заполняем данные
    addRowsToTable(dataRows);
  }

  function addRowsToTable(dataRows) {
    // Очищаем текущую форму (если нужно)
    // $('.table-row-form tbody').empty();

    for (var i = 0; i < dataRows.length; i++) {
      var rowData = dataRows[i];
      // Создаём новую строку формы
      var newRow = createFormRow(rowData, i);
      // Добавляем строку в таблицу
      $('.table-row-form tbody').append(newRow);
    }
  }

  function createFormRow(rowData, index) {
    // Клонируем шаблон строки или создаём новую строку
    // Предположим, что у вас есть функция getEmptyRow() для получения пустой строки формы
    var newRow = getEmptyRow(index);

    // Заполняем поля формы данными
    newRow.find('input[name="name"]').val(rowData[0]);
    newRow.find('input[name="product_sku"]').val(rowData[1]);
    newRow.find('input[name="supplier"]').val(rowData[2]);
    newRow.find('input[name="product_link"]').val(rowData[3]);
    newRow.find('input[name="packaging_unit"]').val(rowData[4]);

    // Возвращаем заполненную строку
    return newRow;
  }

  function getEmptyRow(index) {
    // Создаём новую строку формы с полями
    var newRow = $('<tr>');

    // Создаём ячейки с полями
    var nameCell = $('<td>').append(
      $('<input>', {
        type: 'text',
        name: 'name',
        id: 'id_name_' + index
      })
    );

    var linkCell = $('<td>').append(
      $('<input>', {
        type: 'text',
        name: 'product_link',
        id: 'id_product_link_' + index
      })
    );

    var skuCell = $('<td>').append(
      $('<input>', {
        type: 'text',
        name: 'product_sku',
        id: 'id_product_sku_' + index
      })
    );

    var supplierCell = $('<td>').append(
      $('<input>', {
        type: 'text',
        name: 'supplier',
        id: 'id_supplier_' + index
      })
    );

    var unitCell = $('<td>').append(
      $('<input>', {
        type: 'text',
        name: 'packaging_unit',
        id: 'id_packaging_unit_' + index
      })
    );

    // Добавляем ячейки в строку
    newRow.append(nameCell, skuCell, supplierCell, linkCell, unitCell);

    return newRow;
  }

});
