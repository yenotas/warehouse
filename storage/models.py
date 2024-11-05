from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.contrib.auth.models import AbstractUser, Group

access_type = [('Администратор', 'Администратор'), ('Менеджер', 'Менеджер'), ('Склад', 'Склад'), ('Закупка', 'Закупка'),
               ('ИТР/Планировщик', 'ИТР/Планировщик')]
deps_list = [('Склад', 'Склад'), ('Офис', 'Офис'), ('Монтаж', 'Монтаж'), ('Инженерный', 'Инженерный'),
             ('3D', '3D'), ('Снабжение', 'Снабжение'), ('AXO', 'AXO'), ('ПДО', 'ПДО'), ('ЧПУ', 'ЧПУ'),
             ('Столярный', 'Столярный'), ('Макетный', 'Макетный'), ('Малярный', 'Малярный'),
             ('Художественный', 'Художественный'), ('Сборочный', 'Сборочный')]


class Departments(models.Model):
    department = models.CharField(max_length=50, verbose_name="Отдел/Цех", default='Офис')

    class Meta:
        verbose_name = "Отдел/Цех"
        verbose_name_plural = "Подразделения компании"

    def __str__(self):
        return self.department


class CustomUser(AbstractUser):
    tg = models.CharField(max_length=255, verbose_name="Телеграм", blank=True, null=True)
    department = models.ForeignKey(Departments, verbose_name="Отдел/Цех", on_delete=models.SET_NULL, null=True)
    position_name = models.CharField(max_length=255, verbose_name="Должность", blank=True, null=True)
    groups = models.ManyToManyField(Group, verbose_name="Группы", related_name="custom_users")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Categories(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Категория товара", db_index=True)

    class Meta:
        verbose_name = "Категорию"
        verbose_name_plural = "Категории"

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
        verbose_name = "поставщика"
        verbose_name_plural = "Поставщики"

    def __str__(self):
        return self.name


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
    quantity_in_package = models.PositiveIntegerField(blank=True, null=True, verbose_name="Кол-во в упаковке", default=1)
    product_image = models.ImageField(upload_to="images/%Y/%m/%d/", editable=True, null=True, blank=True, verbose_name="Фото/скриншот")
    near_products = models.ManyToManyField('self', blank=True, verbose_name="Похожие товары")

    class Meta:
        verbose_name = "наименование"
        verbose_name_plural = "Товарные наименования"

    def __str__(self):
        return self.name


class Projects(models.Model):
    creation_date = models.DateField(auto_now_add=True, verbose_name="Дата записи")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Полное название проекта")
    detail_full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Полное название изделия")
    manager = models.ForeignKey(CustomUser, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Менеджер")
    engineer = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='projects_engineer_set', blank=True, null=True, verbose_name="Инженер")
    project_code = models.CharField(max_length=100, blank=True, null=True, verbose_name="Шифр проекта")
    detail_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Изделие")
    detail_code = models.CharField(max_length=100, blank=True, null=True, verbose_name="Шифр изделия")

    class Meta:
        verbose_name = "проект"
        verbose_name_plural = "Проекты"

    def __str__(self):
        return self.name


class ProductRequest(models.Model):
    request_date = models.DateField(auto_now_add=True, verbose_name="Дата запроса")
    project = models.ForeignKey(Projects, on_delete=models.PROTECT, verbose_name="Проект",
                                default=1)
    product = models.ForeignKey(Products, on_delete=models.PROTECT, verbose_name="Наименование",
                                default=1)
    request_about = models.CharField(blank=True, null=True, verbose_name="Комментарий")
    request_quantity = models.PositiveIntegerField(blank=True, null=True, verbose_name="Количество", default=1)
    responsible_employee = models.ForeignKey(CustomUser, on_delete=models.PROTECT, blank=True, null=True,
                                             verbose_name="Ответственный")
    delivery_location = models.CharField(max_length=30, verbose_name="Куда везем?", choices=[
        ('Склад', 'Склад'), ('Офис', 'Офис'), ('Цех', 'Цех'), ('Монтаж', 'Монтаж'),
        ('Подрядчик', 'Подрядчик'), ('Заказчик', 'Заказчик')
    ], default=('Склад', 'Склад'))
    delivery_address = models.CharField(blank=True, null=True, verbose_name="Адрес")
    deadline_delivery_date = models.DateField(blank=True, null=True, verbose_name="Требуемая дата поставки")

    class Meta:
        verbose_name = "запрос на закуп"
        verbose_name_plural = "Запросы на закуп"

    def __str__(self):
        return f"Заявка на {self.product.name}"


class Orders(models.Model):
    order_date = models.DateField(auto_now_add=True, verbose_name="Дата заказа")
    product_request = models.ForeignKey('ProductRequest', on_delete=models.PROTECT, blank=True, null=True,
                                 verbose_name="Заявка на закуп")
    manager = models.ForeignKey(CustomUser, on_delete=models.PROTECT, blank=True, null=True,
                                verbose_name="Ответственный")
    accounted_in_1c = models.BooleanField(blank=True, null=True, verbose_name="Учтено в 1С")
    invoice_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Номер счета")
    delivery_status = models.CharField(max_length=50, verbose_name="Статус заказа", choices=[
        ('Ожидаем', 'Ожидаем'), ('Доставлено', 'Доставлено'), ('Склад', 'Склад'), ('Неполная', 'Неполная'),
        ('Частичный возврат', 'Частичный возврат'), ('Полный возврат', 'Полный возврат')
    ])
    documents = models.CharField(max_length=50, verbose_name="Документы", choices=[
        ('Нет', 'Нет'), ('УПД/СФ', 'УПД/СФ'), ('TTH/TH/AKT', 'TTH/TH/AKT'), ('ИП', 'ИП')
    ], default=('Нет', 'Нет'))
    document_flow = models.CharField(max_length=50, verbose_name="Документооборот", choices=[
        ('Нет', 'Нет'), ('ИП', 'ИП'), ('ЭДО', 'ЭДО'), ('Бумага', 'Бумага')
    ], default=('Нет', 'Нет'))
    waiting_date = models.DateField(blank=True, null=True, verbose_name="Ожидаемая дата поставки")

    class Meta:
        verbose_name = "заказ в закупку"
        verbose_name_plural = "Заказы в закупку"

    def __str__(self):
        return f"Заявка на закуп №{self.ProductRequest.id}"


class ProductMovies(models.Model):
    record_date = models.DateField(auto_now_add=True, verbose_name="Дата записи")
    process_type = models.CharField(max_length=50, choices=[
        ('warehouse', 'Прием на склад'), ('distribute', 'Выдача со склада'),
        ('return', 'Возврат на склад'), ('sup_return', 'Возврат поставщику'),
        ('move', 'Перемещение из ячейки'), ('none', 'Выбрать')
    ], verbose_name="Тип перемещения", default=('none', 'Выбрать'))
    return_to_supplier_reason = models.CharField(max_length=50, choices=[
        ('Несоответствие заказу', 'Несоответствие заказу'), ('Дефекты материалов', 'Дефекты материалов'),
        ('Дефекты изделий', 'Дефекты изделий'), ('Излишек', 'Излишек'),
        ('Нарушение сроков поставки', 'Нарушение сроков поставки')
    ], blank=True, null=True, verbose_name="Причина возврата поставщику", default=('Дефекты изделий', 'Дефекты изделий'))
    new_cell = models.ForeignKey('StorageCells', on_delete=models.PROTECT, blank=True, null=True,
                                 verbose_name="Адрес ячейки")
    product = models.ForeignKey(Products, on_delete=models.PROTECT, null=True, verbose_name="Товар")
    movie_quantity = models.PositiveIntegerField(blank=True, null=True, verbose_name="Количество", default=1)
    reason = models.CharField(max_length=200, blank=True, null=True, verbose_name="Источник перемещения")

    class Meta:
        verbose_name = "запись о перемещении товара"
        verbose_name_plural = "Перемещения по складу"

    def __str__(self):
        return str(self.id)


class StorageCells(models.Model):
    cell_address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Адрес ячейки")
    info = models.CharField(max_length=255, blank=True, null=True, verbose_name="Информация о ячейке")

    class Meta:
        verbose_name = "адресную ячейку"
        verbose_name_plural = "Адресные ячейки"

    def __str__(self):
        return str(self.cell_address)


class PivotTable(models.Model):
    product = models.ForeignKey(Products, on_delete=models.PROTECT, verbose_name="Товар")
    product_request = models.ForeignKey(ProductRequest, on_delete=models.PROTECT, verbose_name="Заявка")
    project = models.ForeignKey(Projects, on_delete=models.PROTECT, verbose_name="Проект")
    order = models.ForeignKey(Orders, on_delete=models.PROTECT, verbose_name="Заказ")
    supplier = models.ForeignKey(Suppliers, on_delete=models.PROTECT, verbose_name="Поставщик")
    has_on_storage = models.PositiveIntegerField(verbose_name="Наличие на складе, кол-во", default=0)
    storage_cell = models.ForeignKey(StorageCells, on_delete=models.PROTECT, verbose_name="Ячейка хранения")
    order_complete = models.BooleanField(verbose_name="Заказ оформлен")
    not_delivered_pcs = models.PositiveIntegerField(verbose_name="Не доставлено, кол-во")
    document_flow = models.CharField(max_length=255, verbose_name="Документооборот")
    supply_date = models.DateField(verbose_name="Дата фактического поступления")
    supply_quantity = models.PositiveIntegerField(verbose_name="Факт поставки, кол-во", default=1)
    given_quantity = models.PositiveIntegerField(verbose_name="Выдано, кол-во", default=1)
    given_employee = models.CharField(max_length=255, verbose_name="Выдано кому")
    given_date = models.DateField(verbose_name="Дата выдачи")
    refund_quantity = models.PositiveIntegerField(verbose_name="Возврат поставщику, кол-во", default=1)
    refund_reason = models.CharField(max_length=255, verbose_name="Причина возврата")

    @property
    def product_name(self):
        return self.product.name

    @property
    def product_link(self):
        return self.product.product_link

    @property
    def request_about(self):
        return self.product_request.request_about


    @property
    def packaging_unit(self):
        return self.product.packaging_unit

    @property
    def request_quantity(self):
        return self.product_request.request_quantity

    @property
    def project_code(self):
        return self.project.project_code

    @property
    def detail_name(self):
        return self.project.detail_name

    @property
    def detail_code(self):
        return self.project.detail_code

    @property
    def product_image(self):
        return self.product.product_image

    @property
    def request_date(self):
        return self.product_request.request_date

    @property
    def responsible_employee(self):
        return self.product_request.responsible_employee

    @property
    def delivery_location(self):
        return self.product_request.delivery_location

    @property
    def deadline_delivery_date(self):
        return self.product_request.deadline_delivery_date

    @property
    def waiting_date(self):
        return self.order.waiting_date

    @property
    def supplier_name(self):
        return self.supplier.name

    @property
    def invoice_number(self):
        return self.order.invoice_number

    @property
    def delivery_status(self):
        return self.order.delivery_status

    @property
    def documents(self):
        return self.order.documents

    @property
    def cell_address(self):
        return self.storage_cell.cell_address

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "позицию"
        verbose_name_plural = "Все закупки"


class ModelAccessControl(models.Model):
    model_name = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name="Правило для формы")
    groups = models.ManyToManyField(Group, verbose_name="Группы редакторов")
    fields_to_disable = models.JSONField(verbose_name="Отключаемые поля", blank=True, null=True, default=list)

    class Meta:
        verbose_name = "Правило блокировки полей формы"
        verbose_name_plural = "Управление доступом"

    def __str__(self):
        return f"{self.model_name} - {', '.join(group.name for group in self.groups.all())}"

    def display_groups(self):
        return ", ".join(group.name for group in self.groups.all())
    display_groups.short_description = "Группы редакторов"


