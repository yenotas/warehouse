from django.db import models


class AccessLevels(models.Model):
    role = models.CharField(max_length=50, choices=[
        ('Администратор', 'Администратор'), ('Менеджер', 'Менеджер'),
        ('Склад', 'Склад'), ('Закупка', 'Закупка'), ('ИТР/Планировщик', 'ИТР/Планировщик')
    ], blank=True, null=True,  verbose_name="Уровень доступа")

    class Meta:
        verbose_name = "доступ"
        verbose_name_plural = "доступы"

    def __str__(self):
        return self.role


class Employees(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Имя Фамилия")
    email = models.CharField(max_length=255, blank=True, null=True, verbose_name="Email")
    tg = models.CharField(max_length=50, blank=True, null=True, verbose_name="Телеграм")
    department = models.CharField(max_length=50, verbose_name="Отдел/Цех", choices=[
        ('Склад', 'Склад'), ('Офис', 'Офис'), ('Монтаж', 'Монтаж'), ('Инженерный', 'Инженерный'),
        ('3D', '3D'), ('Снабжение', 'Снабжение'), ('AXO', 'AXO'), ('ПДО', 'ПДО'), ('ЧПУ', 'ЧПУ'),
        ('Столярный', 'Столярный'), ('Макетный', 'Макетный'), ('Малярный', 'Малярный'), ('Художественный', 'Художественный'),
        ('Сборочный', 'Сборочный')
    ])
    position_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Должность")
    access_type = models.ForeignKey(AccessLevels, on_delete=models.PROTECT, null=True, verbose_name="Уровень доступа")

    class Meta:
        verbose_name = "сотрудник"
        verbose_name_plural = "сотрудники"

    def __str__(self):
        return self.name


class Categories(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Категория товара", db_index=True)

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"

    def __str__(self):
        return self.name


class Suppliers(models.Model):
    name = models.CharField(blank=True, null=True, verbose_name="Поставщик")
    inn = models.CharField(max_length=50, blank=True, null=True, verbose_name="ИНН")
    ogrn = models.CharField(max_length=50, blank=True, null=True, verbose_name="ОГРН")
    address = models.CharField(blank=True, null=True, verbose_name="Адрес")
    contact_person = models.CharField(max_length=255, blank=True, null=True, verbose_name="Контактное лицо")
    website = models.CharField(max_length=255, blank=True, null=True, verbose_name="Web")
    email = models.CharField(max_length=255, blank=True, null=True, verbose_name="Email")
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="Телефон")
    tg = models.CharField(max_length=50, blank=True, null=True, verbose_name="Телеграм")

    class Meta:
        verbose_name = "поставщик"
        verbose_name_plural = "поставщики"

    def __str__(self):
        return self.name


#+
class Projects(models.Model):
    creation_date = models.DateField(auto_now_add=True, verbose_name="Дата записи")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Проект")
    detail_full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Полное название изделия")
    manager = models.ForeignKey(Employees, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Менеджер")
    engineer = models.ForeignKey(Employees, on_delete=models.PROTECT, related_name='projects_engineer_set', blank=True, null=True, verbose_name="Инженер")
    project_code = models.CharField(max_length=100, blank=True, null=True, verbose_name="Шифр проекта")
    detail_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Изделие")
    detail_code = models.CharField(max_length=100, blank=True, null=True, verbose_name="Шифр изделия")

    class Meta:
        verbose_name = "проект"
        verbose_name_plural = "проекты"

    def __str__(self):
        return self.name


#+
class Products(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Наименование")
    product_link = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ссылка")
    product_sku = models.CharField(max_length=100, blank=True, null=True, verbose_name="Артикул")
    category = models.ForeignKey(Categories, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Категория")
    supplier = models.ForeignKey(Suppliers, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Поставщик")
    packaging_unit = models.CharField(max_length=10, verbose_name="Единицы измерения", choices=[
        ('уп.', 'уп.'), ('шт.', 'шт.'), ('кв.м', 'кв.м'),
        ('п.м.', 'п.м.'), ('кг', 'кг'), ('л', 'л'), ('мл', 'мл')
    ])
    quantity_in_package = models.IntegerField(blank=True, null=True, verbose_name="Количество в упаковке")
    product_image = models.ImageField(upload_to="images/%Y/%m/%d/", editable=True, null=True, verbose_name="Фото/скриншот")
    near_products = models.ManyToManyField('self', blank=True, verbose_name="Похожие товары")

    class Meta:
        verbose_name = "товарное наименование"
        verbose_name_plural = "товарные наименования"

    def __str__(self):
        return self.name


#+
class ProductRequest(models.Model):
    request_date = models.DateField(auto_now_add=True, verbose_name="Дата запроса")
    product = models.ForeignKey(Products, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Наименование")
    project = models.ForeignKey(Projects, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Проект")
    order_about = models.CharField(blank=True, null=True, verbose_name="Комментарий")
    order_quantity = models.IntegerField(blank=True, null=True, verbose_name="Количество")
    responsible_employee = models.ForeignKey(Employees, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Ответственный")
    delivery_location = models.CharField(max_length=30, verbose_name="Куда везем?", choices=[
        ('Склад', 'Склад'), ('Офис', 'Офис'), ('Цех', 'Цех'), ('Монтаж', 'Монтаж'),
        ('Подрядчик', 'Подрядчик'), ('Заказчик', 'Заказчик'),
        ('Инженерный', 'Инженерный'), ('3D', '3D'), ('Снабжение', 'Снабжение'),
        ('AXO', 'AXO'), ('ПДО', 'ПДО'), ('ЧПУ', 'ЧПУ'), ('Столярный', 'Столярный'),
        ('Макетный', 'Макетный'), ('Малярный', 'Малярный'),
        ('Художественный', 'Художественный'), ('Сборочный', 'Сборочный')
    ])
    delivery_address = models.CharField(blank=True, null=True, verbose_name="Адрес")
    deadline_delivery_date = models.DateField(blank=True, null=True, verbose_name="Требуемая дата поставки")

    class Meta:
        verbose_name = "запрос на закуп"
        verbose_name_plural = "запросы на закуп"

    def __str__(self):
        return self.product.name


class Orders(models.Model):
    order_date = models.DateField(auto_now_add=True, verbose_name="Дата заказа")
    purchase = models.ForeignKey(ProductRequest, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Наименование")
    manager = models.ForeignKey(Employees, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Ответственный")
    accounted_in_1c = models.BooleanField(blank=True, null=True, verbose_name="Учтено в 1С")
    invoice_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Номер счета")
    delivery_status = models.CharField(max_length=50, verbose_name="Статус заказа", choices=[
        ('Ожидаем', 'Ожидаем'), ('Доставлено', 'Доставлено'), ('Склад', 'Склад'), ('Неполная', 'Неполная'),
        ('Частичный возврат', 'Частичный возврат'), ('Полный возврат', 'Полный возврат')
    ])
    documents = models.CharField(max_length=50, verbose_name="Документы", choices=[
        ('Нет', 'Нет'), ('УПД/СФ', 'УПД/СФ'), ('TTH/TH/AKT', 'TTH/TH/AKT'), ('ИП', 'ИП')
    ])
    waiting_date = models.DateField(blank=True, null=True, verbose_name="Ожидаемая дата поставки")

    class Meta:
        verbose_name = "заказ в закупку"
        verbose_name_plural = "заказы в закупку"

    def __str__(self):
        return self.purchase.product.name


class ProductMovies(models.Model):
    record_date = models.DateField(auto_now_add=True, verbose_name="Дата записи")
    product = models.ForeignKey(Products, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Наименование")
    process_type = models.CharField(max_length=50, choices=[
        ('Прием на склад', 'Прием на склад'), ('Выдача со склада', 'Выдача со склада'),
        ('Возврат на склад', 'Возврат на склад'), ('Возврат поставщику', 'Возврат поставщику'),
        ('Бронирование', 'Бронирование'), ('Перемещение в ячейку', 'Перемещение в ячейку')
    ], verbose_name="Тип перемещения")
    return_to_supplier_reason = models.CharField(max_length=50, choices=[
        ('Дефекты материалов', 'Дефекты материалов'), ('Дефекты изделий', 'Дефекты изделий'),
        ('Излишек', 'Излишек'), ('Несоответствие заказу', 'Несоответствие заказу'),
        ('Нарушение сроков поставки', 'Нарушение сроков поставки')
    ], blank=True, null=True, verbose_name="Причина возврата")
    document_flow = models.CharField(max_length=50, verbose_name="Документооборот", choices=[
        ('Нет', 'Нет'), ('ИП', 'ИП'), ('ЭДО', 'ЭДО'), ('Бумага', 'Бумага')
    ])
    employee = models.ForeignKey(Employees, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Для/от сотрудника")
    project = models.ForeignKey(Projects, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Для/из проекта")
    movie_quantity = models.IntegerField(blank=True, null=True, verbose_name="Количество")
    from_cell = models.ForeignKey('StorageCells', on_delete=models.PROTECT, blank=True, null=True, verbose_name="Адрес ячейки")

    class Meta:
        verbose_name = "запись о перемещении товара"
        verbose_name_plural = "записи перемещении товаров"

    def __str__(self):
        return self.product


class StorageCells(models.Model):
    record_date = models.DateField(auto_now_add=True, verbose_name="Дата размещения")
    process_entry = models.ForeignKey(ProductMovies, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Источник поступления")
    stock_quantity = models.IntegerField(blank=True, null=True, verbose_name="Количество")
    cell_address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Адрес ячейки")
    old_cell_address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Предыдущий адрес")

    class Meta:
        verbose_name = "адресную ячейку"
        verbose_name_plural = "адресные ячейки"

    def __str__(self):
        return self.cell_address


class PivotTable(models.Model):
    class Meta:
        verbose_name = "позицию"
        verbose_name_plural = "Сводная таблица"
