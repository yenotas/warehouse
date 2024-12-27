from django.contrib.auth.models import AbstractUser, Group
from django.urls import reverse
from django.utils.html import format_html
from django.db import models
from django.contrib.contenttypes.models import ContentType


class ModelColors(models.Model):
    name = models.CharField(max_length=50, verbose_name="Таблица")
    color = models.CharField(max_length=6, verbose_name="Цвет заголовка #XXXXXX")

    class Meta:
        verbose_name = "цвет заголовка"
        verbose_name_plural = "Цвета моделей"

    def __str__(self):
        return self.name


class Departments(models.Model):
    name = models.CharField(max_length=50, verbose_name="Отдел/Цех", blank=False, unique=True)
    relate_creating = True

    class Meta:
        verbose_name = "отдел/цех"
        verbose_name_plural = "Подразделения компании"

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    tg = models.CharField(max_length=255, verbose_name="Телеграм", blank=True, null=True)
    tel = models.CharField(max_length=255, verbose_name="Телефон", blank=True, null=True)
    department = models.ForeignKey(Departments, verbose_name="Отдел/Цех", on_delete=models.SET_NULL, null=True)
    department_old = models.CharField(max_length=255, blank=True, null=True)
    position_name = models.CharField(max_length=255, verbose_name="Должность", blank=True, null=True)
    groups = models.ManyToManyField(Group, verbose_name="Группы", related_name="custom_users_set")

    class Meta:
        verbose_name = "пользователя"
        verbose_name_plural = "Пользователи"

    # @property
    # def full_name(self):
    #     return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else ""

    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else f"User {self.pk}"


class Suppliers(models.Model):
    name = models.CharField(blank=False, null=True, verbose_name="Поставщик")
    inn = models.CharField(max_length=50, blank=True, null=True, verbose_name="ИНН")
    ogrn = models.CharField(max_length=50, blank=True, null=True, verbose_name="ОГРН")
    address = models.CharField(blank=True, null=True, verbose_name="Адрес")
    contact_person = models.CharField(max_length=255, blank=True, null=True, verbose_name="Контактное лицо")
    website = models.CharField(max_length=255, blank=True, null=True, verbose_name="Web")
    email = models.CharField(max_length=255, blank=True, null=True, verbose_name="Email")
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="Телефон")
    tg = models.CharField(max_length=50, blank=True, null=True, verbose_name="Телеграм")
    relate_creating = True

    class Meta:
        verbose_name = "поставщика"
        verbose_name_plural = "Поставщики"

    def __str__(self):
        return self.name or ""


class Categories(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Категория/признак", db_index=True)
    relate_creating = True

    class Meta:
        verbose_name = "категорию / признак"
        verbose_name_plural = "Категории, признаки, свойства"

    def __str__(self):
        return self.name or ""


class Products(models.Model):
    name = models.CharField(max_length=255, blank=False, verbose_name="Наименование")
    packaging_unit = models.CharField(max_length=10, verbose_name="Ед. изм.", choices=[
        ('уп', 'уп'), ('шт', 'шт'), ('кв.м', 'кв.м'),
        ('п.м', 'п.м'), ('кг', 'кг'), ('л', 'л'), ('мл', 'мл')
    ], default=('шт', 'шт'))
    product_sku = models.CharField(max_length=100, blank=True, null=True, verbose_name="SKU / Артикул")
    product_link = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ссылка")
    supplier = models.ForeignKey(Suppliers, on_delete=models.SET_NULL, blank=False, null=True, verbose_name="Поставщик")
    supplier_old = models.CharField(max_length=255, blank=True, null=True)
    categories = models.ManyToManyField(Categories, blank=True, verbose_name="Категория / признак",
                                        related_name='name_set')
    # quantity_in_package = models.PositiveIntegerField(blank=True, null=True, verbose_name="Кол-во в упаковке", default=1)
    near_products = models.ManyToManyField('self', blank=True, verbose_name="Аналоги")
    product_image = models.ImageField(upload_to="images/%Y/%m/%d/", editable=True, null=True, blank=True,
                                      verbose_name="Фото / скриншот")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def product_image_tag(self):
        if self.product_image:
            return format_html(
                '<a href="{}"><img src="{}" width="50" height="50" /></a>',
                reverse('myadmin:storage_products_change', args=[self.pk]),
                self.product_image.url
            )
        return ""

    product_image_tag.short_description = 'Фото товара'

    def __str__(self):
        return self.name or ""


class Projects(models.Model):
    creation_date = models.DateField(auto_now_add=True, verbose_name="Дата записи")
    name = models.CharField(max_length=255, blank=False, default="", verbose_name="Проект")
    detail_full_name = models.CharField(max_length=255, blank=True, default="", verbose_name="Полное название изделия")
    manager = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Менеджер")
    manager_old = models.CharField(max_length=255, blank=True, null=True)
    engineer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name='projects_engineer_set',
                                 blank=True, null=True, verbose_name="Инженер")
    engineer_old = models.CharField(max_length=255, blank=True, null=True)
    project_code = models.CharField(max_length=100, blank=True, default="", verbose_name="Шифр проекта")
    detail_name = models.CharField(max_length=255, blank=True, default="", verbose_name="Изделие")
    detail_code = models.CharField(max_length=100, blank=True, default="", verbose_name="Шифр изделия")

    class Meta:
        verbose_name = "проект"
        verbose_name_plural = "Проекты"

    def __str__(self):
        return self.detail_code or ""


class ProductRequest(models.Model):
    request_date = models.DateField(auto_now_add=True, verbose_name="Дата запроса")
    project = models.ForeignKey(Projects, on_delete=models.SET_NULL, null=True, verbose_name="Проект",
                                default=1, related_name="name_set")
    project_old = models.CharField(max_length=255, blank=True, null=True)
    product = models.ForeignKey(Products, on_delete=models.SET_NULL, null=True, verbose_name="Наименование",
                                default=1, related_name="product_set")
    product_old = models.CharField(max_length=255, blank=True, null=True)
    request_about = models.CharField(blank=True, null=True, verbose_name="Комментарий")
    request_quantity = models.PositiveIntegerField(blank=True, null=True, verbose_name="Количество", default=1)
    responsible = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True,
                                    verbose_name="Ответственный", related_name="username_set")
    responsible_old = models.CharField(max_length=255, blank=True, null=True)
    delivery_location = models.CharField(max_length=30, verbose_name="Куда везем?", choices=[
        ('Склад', 'Склад'), ('Офис', 'Офис'), ('Цех', 'Цех'), ('Монтаж', 'Монтаж'),
        ('Подрядчик', 'Подрядчик'), ('Заказчик', 'Заказчик')
    ], default=('Склад', 'Склад'))
    delivery_address = models.CharField(blank=True, null=True, verbose_name="Адрес")
    deadline_delivery_date = models.DateField(blank=True, null=True, verbose_name="Требуемая дата поставки")
    request_accepted = models.BooleanField(default=False)
    manager = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True,
                                    verbose_name="Закупщик", related_name="manager_set")

    class Meta:
        verbose_name = "заявку на закуп"
        verbose_name_plural = "Заявки на закуп"

    def __str__(self):
        return f"Заявка {self.id} на {self.product.name}" or ""


class Orders(models.Model):
    order_date = models.DateField(auto_now_add=True, verbose_name="Дата заказа")
    product_request = models.ForeignKey('ProductRequest', on_delete=models.SET_NULL, blank=True, null=True,
                                 verbose_name="Заявка на закуп", related_name="product_req_set")
    product_request_old = models.CharField(max_length=255, blank=True, null=True)
    manager = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True,
                                verbose_name="Ответственный", related_name="name_set")
    manager_old = models.CharField(max_length=255, blank=True, null=True)
    accounted_in_1c = models.BooleanField(blank=True, null=True, verbose_name="Учтено в 1С")
    invoice_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Номер счета")
    delivery_status = models.CharField(max_length=50, blank=True, null=True, verbose_name="Статус заказа", choices=[(None, ''),
        ('Ожидаем', 'Ожидаем'), ('Доставлено', 'Доставлено'), ('Склад', 'Склад'), ('Неполная', 'Неполная'),
        ('Частичный возврат', 'Частичный возврат'), ('Полный возврат', 'Полный возврат'), ('Отмена', 'Отмена'),
    ])
    documents = models.CharField(max_length=50, verbose_name="Документы", blank=True, null=True, choices=[
        (None, ''),
        ('Нет', 'Нет'), ('УПД/СФ', 'УПД/СФ'), ('TTH/TH/AKT', 'TTH/TH/AKT'), ('ИП', 'ИП')
    ])
    document_flow = models.CharField(max_length=50, verbose_name="Документооборот", blank=True, null=True, choices=[
        (None, ''), ('Нет', 'Нет'), ('ИП', 'ИП'), ('ЭДО', 'ЭДО'), ('Бумага', 'Бумага')
    ])
    waiting_date = models.DateField(blank=True, null=True, verbose_name="Ожидаемая дата поставки")
    order_accepted = models.BooleanField(default=False)

    class Meta:
        verbose_name = "заказ по заявке"
        verbose_name_plural = "Заказы по заявкам"

    def __str__(self):
        return f"По заявке №{self.product_request}" or ""


class ProductMovies(models.Model):
    record_date = models.DateField(auto_now_add=True, verbose_name="Дата записи")
    product = models.ForeignKey(Products, on_delete=models.SET_NULL, null=True, verbose_name="Наименование",
                                default=1, related_name="product_mov_set")
    product_old = models.CharField(max_length=255, blank=True, null=True)
    process_type = models.CharField(max_length=50, choices=[
        ('warehouse', 'Прием на склад'), ('distribute', 'Выдача со склада'),
        ('return', 'Возврат на склад'), ('sup_return', 'Возврат поставщику'),
        ('move', 'Перемещение из ячейки')
    ], verbose_name="Тип перемещения", default=('none', 'Выбрать'))
    return_to_supplier_reason = models.CharField(max_length=50, choices=[
        ('Несоответствие заказу', 'Несоответствие заказу'), ('Дефекты материалов', 'Дефекты материалов'),
        ('Дефекты изделий', 'Дефекты изделий'), ('Излишек', 'Излишек'),
        ('Нарушение сроков поставки', 'Нарушение сроков поставки')
    ], default=('none', 'Выбрать'), verbose_name="Причина")
    new_cell = models.ForeignKey('StorageCells', on_delete=models.SET_NULL, blank=True, null=True,
                                 verbose_name="Адрес ячейки", related_name="name_set")
    new_cell_old = models.CharField(max_length=255, blank=True, null=True)
    movie_quantity = models.PositiveIntegerField(blank=True, null=True, verbose_name="Количество", default=1)
    reason = models.CharField(max_length=200, blank=True, null=True, verbose_name="Назначение")

    class Meta:
        verbose_name = "запись о перемещении товара"
        verbose_name_plural = "Перемещения по складу"

    def __str__(self):
        return str(self.id) or "1"


class StorageCells(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Адрес ячейки")
    info = models.CharField(max_length=255, blank=True, null=True, verbose_name="Информация о ячейке")

    class Meta:
        verbose_name = "адресную ячейку"
        verbose_name_plural = "Адресные ячейки"

    def __str__(self):
        return self.name or ""


class ModelAccessControl(models.Model):
    model_name = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, verbose_name="Правило для формы")
    model_name_old = models.CharField(max_length=255, blank=True, null=True)
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


# Пока не используется
class PivotTable(models.Model):
    product_request = models.ForeignKey(ProductRequest, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Заявка на закуп')
    order = models.ForeignKey(Orders, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Заказ')
    product_movie = models.ForeignKey(ProductMovies, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Перемещение по складу')

    product_name = models.ForeignKey(Products, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Наименование товара")
    request_about = models.CharField(max_length=255, blank=True, null=True, verbose_name="Комментарий")
    responsible = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Ответственный")
    invoice_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Номер счета")
    waiting_date = models.DateField(blank=True, null=True, verbose_name="Планируемая дата поставки")
    delivery_status = models.CharField(max_length=50, blank=True, null=True, verbose_name="Статус доставки", choices=[
        ('Ожидаем', 'Ожидаем'), ('Доставлено', 'Доставлено'), ('Склад', 'Склад'), ('Неполная', 'Неполная'),
        ('Частичный возврат', 'Частичный возврат'), ('Полный возврат', 'Полный возврат'), ('Отмена', 'Отмена'),
    ])
    document_flow = models.CharField(max_length=50, blank=True, null=True, verbose_name="Документооборот", choices=[
        ('Нет', 'Нет'), ('ИП', 'ИП'), ('ЭДО', 'ЭДО'), ('Бумага', 'Бумага')
    ])
    documents = models.CharField(max_length=50, blank=True, null=True, verbose_name="Документы", choices=[
        ('Нет', 'Нет'), ('УПД/СФ', 'УПД/СФ'), ('TTH/TH/AKT', 'TTH/TH/AKT'), ('ИП', 'ИП')
    ])
    accounted_in_1c = models.BooleanField(blank=True, null=True, verbose_name="Учтено в 1С")

    # Поля для синхронизации с ProductRequest
    request_quantity = models.PositiveIntegerField(blank=True, null=True, verbose_name="Количество")
    project_code = models.CharField(max_length=100, blank=True, null=True, verbose_name="Код проекта")
    detail_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Изделие")
    detail_code = models.CharField(max_length=100, blank=True, null=True, verbose_name="Шифр изделия")
    delivery_location = models.CharField(max_length=50, blank=True, null=True, verbose_name="Куда везем?")
    deadline_delivery_date = models.DateField(blank=True, null=True, verbose_name="Требуемая дата поставки")
    request_date = models.DateField(blank=True, null=True, verbose_name="Дата запроса")

    # Поля для синхронизации с Products и ProductMovies
    sku = models.CharField(max_length=100, blank=True, null=True, verbose_name="Артикул")
    product_image = models.ImageField(upload_to="images/%Y/%m/%d/", blank=True, null=True, verbose_name="Фото товара")
    supplier = models.CharField(max_length=255, blank=True, null=True, verbose_name="Поставщик")
    product_link = models.URLField(blank=True, null=True, verbose_name="Ссылка на сайт")
    packaging_unit = models.CharField(max_length=10, blank=True, null=True, verbose_name="Единицы измерения")
    has_on_storage = models.PositiveIntegerField(blank=True, null=True, verbose_name="Остаток на складе")
    has_on_storage_near = models.PositiveIntegerField(blank=True, null=True, verbose_name="Остаток на складе по аналогам")

    # Поля для синхронизации с ProductMovies
    supply_date = models.DateField(blank=True, null=True, verbose_name="Дата фактического поступления")
    supply_quantity = models.PositiveIntegerField(blank=True, null=True, verbose_name="Факт поставки, кол-во")
    not_delivered_pcs = models.PositiveIntegerField(blank=True, null=True, verbose_name="Не доставлено, кол-во")
    storage_cell = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ячейка хранения")

    @property
    def order_complete(self):
        return all([self.invoice_number, self.waiting_date])

    def product_image_tag(self):
        if self.product_image:
            return format_html('<img src="{}" width="50" height="50" />'.format(self.product_image.url))
        return ""
    product_image_tag.short_description = 'Фото товара'

    def save(self, *args, **kwargs):
        # Синхронизируем данные с ProductRequest
        if self.product_request:
            self.product_name = self.product_request.product
            self.request_about = self.request_about or self.product_request.request_about
            self.responsible = self.responsible or self.product_request.responsible
            self.request_quantity = self.product_request.request_quantity
            self.project_code = self.product_request.project.project_code if self.product_request.project else None
            self.detail_name = self.product_request.project.detail_name if self.product_request.project else None
            self.detail_code = self.product_request.project.detail_code if self.product_request.project else None
            self.delivery_location = self.product_request.delivery_location
            self.deadline_delivery_date = self.product_request.deadline_delivery_date
            self.request_date = self.product_request.request_date

        # Синхронизируем данные с Orders
        if self.order:
            self.invoice_number = self.invoice_number or self.order.invoice_number
            self.waiting_date = self.waiting_date or self.order.waiting_date
            self.delivery_status = self.delivery_status or self.order.delivery_status
            self.document_flow = self.document_flow or self.order.document_flow
            self.documents = self.documents or self.order.documents
            self.accounted_in_1c = self.accounted_in_1c if self.accounted_in_1c is not None else self.order.accounted_in_1c

        # Синхронизируем данные с ProductMovies
        if self.product_movie:
            self.supply_date = self.product_movie.record_date
            self.supply_quantity = self.product_movie.movie_quantity
            self.not_delivered_pcs = self.request_quantity - self.supply_quantity if self.request_quantity else None
            self.storage_cell = self.product_movie.new_cell

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "заявку и заказ закупки"
        verbose_name_plural = "Все закупки"
