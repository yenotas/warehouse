from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.utils.functional import cached_property


class Departments(models.Model):
    department = models.CharField(max_length=50, verbose_name="Отдел/Цех", default='Офис')

    class Meta:
        verbose_name = "Отдел/Цех"
        verbose_name_plural = "Подразделения компании"

    def __str__(self):
        return self.department


class ModelColors(models.Model):
    model_name = models.CharField(max_length=50, verbose_name="Таблица")
    color = models.CharField(max_length=6, verbose_name="Цвет заголовка #XXXXXX")

    class Meta:
        verbose_name = "цвет"
        verbose_name_plural = "Цвета моделей"


class CustomUser(AbstractUser):
    tg = models.CharField(max_length=255, verbose_name="Телеграм", blank=True, null=True)
    tel = models.CharField(max_length=255, verbose_name="Телефон", blank=True, null=True)
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
    product_sku = models.CharField(max_length=100, blank=True, null=True, verbose_name="SKU / Артикул")
    category = models.ForeignKey(Categories, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Категория")
    supplier = models.ForeignKey(Suppliers, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Поставщик")
    packaging_unit = models.CharField(max_length=10, verbose_name="Единицы измерения", choices=[
        ('уп.', 'уп.'), ('шт.', 'шт.'), ('кв.м', 'кв.м'),
        ('п.м.', 'п.м.'), ('кг', 'кг'), ('л', 'л'), ('мл', 'мл')
    ], default=('шт.', 'шт.'))
    quantity_in_package = models.PositiveIntegerField(blank=True, null=True, verbose_name="Кол-во в упаковке", default=1)
    product_image = models.ImageField(upload_to="images/%Y/%m/%d/", editable=True, null=True, blank=True, verbose_name="Фото / скриншот")
    near_products = models.ManyToManyField('self', blank=True, verbose_name="Аналоги")

    class Meta:
        verbose_name = "наименование"
        verbose_name_plural = "Товарные наименования"

    def __str__(self):
        return f"{self.name} | {self.product_sku}"


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
    responsible = models.ForeignKey(CustomUser, on_delete=models.PROTECT, blank=True, null=True,
                                    verbose_name="Ответственный")
    delivery_location = models.CharField(max_length=30, verbose_name="Куда везем?", choices=[
        ('Склад', 'Склад'), ('Офис', 'Офис'), ('Цех', 'Цех'), ('Монтаж', 'Монтаж'),
        ('Подрядчик', 'Подрядчик'), ('Заказчик', 'Заказчик')
    ], default=('Склад', 'Склад'))
    delivery_address = models.CharField(blank=True, null=True, verbose_name="Адрес")
    deadline_delivery_date = models.DateField(blank=True, null=True, verbose_name="Требуемая дата поставки")

    class Meta:
        verbose_name = "заявка на закуп"
        verbose_name_plural = "Заявки на закуп"

    def __str__(self):
        return f"Заявка {self.id} на {self.product.name}"


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
        ('Частичный возврат', 'Частичный возврат'), ('Полный возврат', 'Полный возврат'), ('Отмена', 'Отмена'),
    ])
    documents = models.CharField(max_length=50, verbose_name="Документы", choices=[
        ('Нет', 'Нет'), ('УПД/СФ', 'УПД/СФ'), ('TTH/TH/AKT', 'TTH/TH/AKT'), ('ИП', 'ИП')
    ], default=('Нет', 'Нет'))
    document_flow = models.CharField(max_length=50, verbose_name="Документооборот", choices=[
        ('Нет', 'Нет'), ('ИП', 'ИП'), ('ЭДО', 'ЭДО'), ('Бумага', 'Бумага')
    ], default=('Нет', 'Нет'))
    waiting_date = models.DateField(blank=True, null=True, verbose_name="Ожидаемая дата поставки")

    class Meta:
        verbose_name = "заказ по заявке"
        verbose_name_plural = "Заказы по заявкам"

    def __str__(self):
        return f"Заказ по заявке №{self.product_request.id}"


class ProductMovies(models.Model):
    record_date = models.DateField(auto_now_add=True, verbose_name="Дата записи")
    product = models.ForeignKey(Products, on_delete=models.PROTECT, verbose_name="Наименование",
                                default=1)
    process_type = models.CharField(max_length=50, choices=[
        ('warehouse', 'Прием на склад'), ('distribute', 'Выдача со склада'),
        ('return', 'Возврат на склад'), ('sup_return', 'Возврат поставщику'),
        ('move', 'Перемещение из ячейки')
    ], verbose_name="Тип перемещения", default=('none', 'Выбрать'))
    return_to_supplier_reason = models.CharField(max_length=50, choices=[
        ('Несоответствие заказу', 'Несоответствие заказу'), ('Дефекты материалов', 'Дефекты материалов'),
        ('Дефекты изделий', 'Дефекты изделий'), ('Излишек', 'Излишек'),
        ('Нарушение сроков поставки', 'Нарушение сроков поставки')
    ], blank=True, null=True, verbose_name="Причина возврата поставщику")
    new_cell = models.ForeignKey('StorageCells', on_delete=models.PROTECT, blank=True, null=True,
                                 verbose_name="Адрес ячейки")
    movie_quantity = models.PositiveIntegerField(blank=True, null=True, verbose_name="Количество", default=1)
    reason_id = models.CharField(max_length=200, blank=True, null=True, verbose_name="ID источника перемещения")
    # reason_id в зависимости от типа перемещения process_type подразумевает id записи моделей:
    # warehouse => order_id,
    # distribute => customuser_id,
    # return => project_id,
    # sup_return => supplier_id,
    # move => ProductMovies_id,
    # поле return_to_supplier_reason заполняется только при process_type == sup_return

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


# models.py

class PivotTable(models.Model):
    # Связи с другими моделями
    product_request = models.ForeignKey('ProductRequest', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Заявка на закуп')
    order = models.ForeignKey('Orders', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Заказ')
    product_movie = models.ForeignKey('ProductMovies', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Перемещение по складу')

    # Поля для редактирования и синхронизации
    request_about = models.CharField(max_length=255, blank=True, null=True, verbose_name="Комментарий")
    responsible = models.ForeignKey(CustomUser, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Ответственный")
    invoice_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Номер счета")
    waiting_date = models.DateField(blank=True, null=True, verbose_name="Планируемая дата поставки")
    delivery_status = models.CharField(max_length=50, blank=True, null=True, verbose_name="Статус доставки", choices=[
        ('Ожидаем', 'Ожидаем'),
        ('Доставлено', 'Доставлено'),
        ('Склад', 'Склад'),
        ('Неполная', 'Неполная'),
        ('Частичный возврат', 'Частичный возврат'),
        ('Полный возврат', 'Полный возврат')
    ])
    document_flow = models.CharField(max_length=50, blank=True, null=True, verbose_name="Документооборот", choices=[
        ('Нет', 'Нет'),
        ('ИП', 'ИП'),
        ('ЭДО', 'ЭДО'),
        ('Бумага', 'Бумага')
    ])
    documents = models.CharField(max_length=50, blank=True, null=True, verbose_name="Документы", choices=[
        ('Нет', 'Нет'),
        ('УПД/СФ', 'УПД/СФ'),
        ('TTH/TH/AKT', 'TTH/TH/AKT'),
        ('ИП', 'ИП')
    ])
    accounted_in_1c = models.BooleanField(blank=True, null=True, verbose_name="Учтено в 1С")

    # Свойства для доступа к полям связанных моделей (только для чтения)
    @property
    def product_name(self):
        return self.product_request.product.name if self.product_request and self.product_request.product else None

    @property
    def product_id(self):
        return self.product_request.product.id if self.product_request and self.product_request.product else None

    @property
    def sku(self):
        return self.product_request.product.product_sku if self.product_request and self.product_request.product else None

    @property
    def product_image(self):
        if self.product_request and self.product_request.product and self.product_request.product.product_image:
            return self.product_request.product.product_image.url
        return None

    @property
    def responsible(self):
        return self.product_request.responsible if self.product_request else None

    @property
    def supplier(self):
        return self.product_request.product.supplier if self.product_request and self.product_request.product else None

    @property
    def product_link(self):
        return self.product_request.product.product_link if self.product_request and self.product_request.product else None

    @property
    def packaging_unit(self):
        return self.product_request.product.packaging_unit if self.product_request and self.product_request.product else None

    @property
    def has_on_storage(self):
        if self.product_request and self.product_request.product:
            total_quantity = ProductMovies.objects.filter(product=self.product_request.product).aggregate(models.Sum('movie_quantity'))['movie_quantity__sum'] or 0
            return total_quantity
        return None

    @property
    def has_on_storage_near(self):
        if self.product_request and self.product_request.product:
            near_products = self.product_request.product.near_products.all()
            total_quantity = ProductMovies.objects.filter(product__in=near_products).aggregate(models.Sum('movie_quantity'))['movie_quantity__sum'] or 0
            return total_quantity
        return None

    @property
    def request_quantity(self):
        return self.product_request.request_quantity if self.product_request else None

    @property
    def project_code(self):
        return self.product_request.project.project_code if self.product_request and self.product_request.project else None

    @property
    def detail_name(self):
        return self.product_request.project.detail_name if self.product_request and self.product_request.project else None

    @property
    def detail_code(self):
        return self.product_request.project.detail_code if self.product_request and self.product_request.project else None

    @property
    def delivery_location(self):
        return self.product_request.delivery_location if self.product_request else None

    @property
    def deadline_delivery_date(self):
        return self.product_request.deadline_delivery_date if self.product_request else None

    @property
    def supply_date(self):
        return self.product_movie.record_date if self.product_movie else None

    @property
    def supply_quantity(self):
        return self.product_movie.movie_quantity if self.product_movie else None

    @property
    def not_delivered_pcs(self):
        if self.product_request and self.product_movie:
            return self.product_request.request_quantity - self.product_movie.movie_quantity
        return None

    @property
    def storage_cell(self):
        return self.product_movie.new_cell if self.product_movie else None

    def save(self, *args, **kwargs):
        # Синхронизируем поля с моделью ProductRequest
        if self.product_request:
            self.product_request.request_about = self.request_about
            self.product_request.responsible = self.responsible
            self.product_request.save()

        # Синхронизируем поля с моделью Orders
        if self.order:
            self.order.invoice_number = self.invoice_number
            self.order.waiting_date = self.waiting_date
            self.order.delivery_status = self.delivery_status
            self.order.document_flow = self.document_flow
            self.order.documents = self.documents
            self.order.accounted_in_1c = self.accounted_in_1c
            self.order.save()

        super(PivotTable, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "заявку и заказ закупки"
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

