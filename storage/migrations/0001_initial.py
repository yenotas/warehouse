# Generated by Django 5.1.2 on 2024-11-11 13:34

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, db_index=True, max_length=255, null=True, verbose_name='Категория товара')),
            ],
            options={
                'verbose_name': 'Категорию',
                'verbose_name_plural': 'Категории',
            },
        ),
        migrations.CreateModel(
            name='Departments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.CharField(default='Офис', max_length=50, verbose_name='Отдел/Цех')),
            ],
            options={
                'verbose_name': 'Отдел/Цех',
                'verbose_name_plural': 'Подразделения компании',
            },
        ),
        migrations.CreateModel(
            name='ModelColors',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_name', models.CharField(max_length=50, verbose_name='Таблица')),
                ('color', models.CharField(max_length=6, verbose_name='Цвет заголовка #XXXXXX')),
            ],
            options={
                'verbose_name': 'цвет',
                'verbose_name_plural': 'Цвета моделей',
            },
        ),
        migrations.CreateModel(
            name='StorageCells',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cell_address', models.CharField(blank=True, max_length=255, null=True, verbose_name='Адрес ячейки')),
                ('info', models.CharField(blank=True, max_length=255, null=True, verbose_name='Информация о ячейке')),
            ],
            options={
                'verbose_name': 'адресную ячейку',
                'verbose_name_plural': 'Адресные ячейки',
            },
        ),
        migrations.CreateModel(
            name='Suppliers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, null=True, verbose_name='Поставщик')),
                ('inn', models.CharField(blank=True, max_length=50, null=True, verbose_name='ИНН')),
                ('ogrn', models.CharField(blank=True, max_length=50, null=True, verbose_name='ОГРН')),
                ('address', models.CharField(blank=True, null=True, verbose_name='Адрес')),
                ('contact_person', models.CharField(blank=True, max_length=255, null=True, verbose_name='Контактное лицо')),
                ('website', models.CharField(blank=True, max_length=255, null=True, verbose_name='Web')),
                ('email', models.CharField(blank=True, max_length=255, null=True, verbose_name='Email')),
                ('phone', models.CharField(blank=True, max_length=50, null=True, verbose_name='Телефон')),
                ('tg', models.CharField(blank=True, max_length=50, null=True, verbose_name='Телеграм')),
            ],
            options={
                'verbose_name': 'название контрагента',
                'verbose_name_plural': 'Поставщики',
            },
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('tg', models.CharField(blank=True, max_length=255, null=True, verbose_name='Телеграм')),
                ('tel', models.CharField(blank=True, max_length=255, null=True, verbose_name='Телефон')),
                ('position_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Должность')),
                ('groups', models.ManyToManyField(related_name='custom_users', to='auth.group', verbose_name='Группы')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
                ('department', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='storage.departments', verbose_name='Отдел/Цех')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ModelAccessControl',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fields_to_disable', models.JSONField(blank=True, default=list, null=True, verbose_name='Отключаемые поля')),
                ('groups', models.ManyToManyField(to='auth.group', verbose_name='Группы редакторов')),
                ('model_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype', verbose_name='Правило для формы')),
            ],
            options={
                'verbose_name': 'Правило блокировки полей формы',
                'verbose_name_plural': 'Управление доступом',
            },
        ),
        migrations.CreateModel(
            name='ProductRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_date', models.DateField(auto_now_add=True, verbose_name='Дата запроса')),
                ('request_about', models.CharField(blank=True, null=True, verbose_name='Комментарий')),
                ('request_quantity', models.PositiveIntegerField(blank=True, default=1, null=True, verbose_name='Количество')),
                ('delivery_location', models.CharField(choices=[('Склад', 'Склад'), ('Офис', 'Офис'), ('Цех', 'Цех'), ('Монтаж', 'Монтаж'), ('Подрядчик', 'Подрядчик'), ('Заказчик', 'Заказчик')], default=('Склад', 'Склад'), max_length=30, verbose_name='Куда везем?')),
                ('delivery_address', models.CharField(blank=True, null=True, verbose_name='Адрес')),
                ('deadline_delivery_date', models.DateField(blank=True, null=True, verbose_name='Требуемая дата поставки')),
                ('responsible', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Ответственный')),
            ],
            options={
                'verbose_name': 'заявка на закуп',
                'verbose_name_plural': 'Заявки на закуп',
            },
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_date', models.DateField(auto_now_add=True, verbose_name='Дата заказа')),
                ('accounted_in_1c', models.BooleanField(blank=True, null=True, verbose_name='Учтено в 1С')),
                ('invoice_number', models.CharField(blank=True, max_length=100, null=True, verbose_name='Номер счета')),
                ('delivery_status', models.CharField(choices=[('Ожидаем', 'Ожидаем'), ('Доставлено', 'Доставлено'), ('Склад', 'Склад'), ('Неполная', 'Неполная'), ('Частичный возврат', 'Частичный возврат'), ('Полный возврат', 'Полный возврат'), ('Отмена', 'Отмена')], max_length=50, verbose_name='Статус заказа')),
                ('documents', models.CharField(choices=[('Нет', 'Нет'), ('УПД/СФ', 'УПД/СФ'), ('TTH/TH/AKT', 'TTH/TH/AKT'), ('ИП', 'ИП')], default=('Нет', 'Нет'), max_length=50, verbose_name='Документы')),
                ('document_flow', models.CharField(choices=[('Нет', 'Нет'), ('ИП', 'ИП'), ('ЭДО', 'ЭДО'), ('Бумага', 'Бумага')], default=('Нет', 'Нет'), max_length=50, verbose_name='Документооборот')),
                ('waiting_date', models.DateField(blank=True, null=True, verbose_name='Ожидаемая дата поставки')),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Ответственный')),
                ('product_request', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='storage.productrequest', verbose_name='Заявка на закуп')),
            ],
            options={
                'verbose_name': 'заказ по заявке',
                'verbose_name_plural': 'Заказы по заявкам',
            },
        ),
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Наименование')),
                ('product_link', models.CharField(blank=True, max_length=255, null=True, verbose_name='Ссылка')),
                ('product_sku', models.CharField(blank=True, max_length=100, null=True, verbose_name='SKU / Артикул')),
                ('packaging_unit', models.CharField(choices=[('уп.', 'уп.'), ('шт.', 'шт.'), ('кв.м', 'кв.м'), ('п.м.', 'п.м.'), ('кг', 'кг'), ('л', 'л'), ('мл', 'мл')], default=('шт.', 'шт.'), max_length=10, verbose_name='Единицы измерения')),
                ('quantity_in_package', models.PositiveIntegerField(blank=True, default=1, null=True, verbose_name='Кол-во в упаковке')),
                ('product_image', models.ImageField(blank=True, null=True, upload_to='images/%Y/%m/%d/', verbose_name='Фото / скриншот')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='storage.categories', verbose_name='Категория')),
                ('near_products', models.ManyToManyField(blank=True, to='storage.products', verbose_name='Аналоги')),
                ('supplier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='storage.suppliers', verbose_name='Поставщик')),
            ],
            options={
                'verbose_name': 'наименование',
                'verbose_name_plural': 'Товарные наименования',
            },
        ),
        migrations.AddField(
            model_name='productrequest',
            name='product',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='storage.products', verbose_name='Наименование'),
        ),
        migrations.CreateModel(
            name='ProductMovies',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record_date', models.DateField(auto_now_add=True, verbose_name='Дата записи')),
                ('process_type', models.CharField(choices=[('warehouse', 'Прием на склад'), ('distribute', 'Выдача со склада'), ('return', 'Возврат на склад'), ('sup_return', 'Возврат поставщику'), ('move', 'Перемещение из ячейки')], default=('none', 'Выбрать'), max_length=50, verbose_name='Тип перемещения')),
                ('return_to_supplier_reason', models.CharField(blank=True, choices=[('Несоответствие заказу', 'Несоответствие заказу'), ('Дефекты материалов', 'Дефекты материалов'), ('Дефекты изделий', 'Дефекты изделий'), ('Излишек', 'Излишек'), ('Нарушение сроков поставки', 'Нарушение сроков поставки')], max_length=50, null=True, verbose_name='Причина возврата поставщику')),
                ('movie_quantity', models.PositiveIntegerField(blank=True, default=1, null=True, verbose_name='Количество')),
                ('reason_id', models.CharField(blank=True, max_length=200, null=True, verbose_name='ID источника перемещения')),
                ('product', models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='storage.products', verbose_name='Наименование')),
                ('new_cell', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='storage.storagecells', verbose_name='Адрес ячейки')),
            ],
            options={
                'verbose_name': 'запись о перемещении товара',
                'verbose_name_plural': 'Перемещения по складу',
            },
        ),
        migrations.CreateModel(
            name='PivotTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_about', models.CharField(blank=True, max_length=255, null=True, verbose_name='Комментарий')),
                ('invoice_number', models.CharField(blank=True, max_length=100, null=True, verbose_name='Номер счета')),
                ('waiting_date', models.DateField(blank=True, null=True, verbose_name='Планируемая дата поставки')),
                ('delivery_status', models.CharField(blank=True, choices=[('Ожидаем', 'Ожидаем'), ('Доставлено', 'Доставлено'), ('Склад', 'Склад'), ('Неполная', 'Неполная'), ('Частичный возврат', 'Частичный возврат'), ('Полный возврат', 'Полный возврат'), ('Отмена', 'Отмена')], max_length=50, null=True, verbose_name='Статус доставки')),
                ('document_flow', models.CharField(blank=True, choices=[('Нет', 'Нет'), ('ИП', 'ИП'), ('ЭДО', 'ЭДО'), ('Бумага', 'Бумага')], max_length=50, null=True, verbose_name='Документооборот')),
                ('documents', models.CharField(blank=True, choices=[('Нет', 'Нет'), ('УПД/СФ', 'УПД/СФ'), ('TTH/TH/AKT', 'TTH/TH/AKT'), ('ИП', 'ИП')], max_length=50, null=True, verbose_name='Документы')),
                ('accounted_in_1c', models.BooleanField(blank=True, null=True, verbose_name='Учтено в 1С')),
                ('request_quantity', models.PositiveIntegerField(blank=True, null=True, verbose_name='Количество')),
                ('project_code', models.CharField(blank=True, max_length=100, null=True, verbose_name='Код проекта')),
                ('detail_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Изделие')),
                ('detail_code', models.CharField(blank=True, max_length=100, null=True, verbose_name='Шифр изделия')),
                ('delivery_location', models.CharField(blank=True, max_length=50, null=True, verbose_name='Куда везем?')),
                ('deadline_delivery_date', models.DateField(blank=True, null=True, verbose_name='Требуемая дата поставки')),
                ('request_date', models.DateField(blank=True, null=True, verbose_name='Дата запроса')),
                ('sku', models.CharField(blank=True, max_length=100, null=True, verbose_name='Артикул')),
                ('product_image', models.ImageField(blank=True, null=True, upload_to='images/%Y/%m/%d/', verbose_name='Фото товара')),
                ('supplier', models.CharField(blank=True, max_length=255, null=True, verbose_name='Поставщик')),
                ('product_link', models.URLField(blank=True, null=True, verbose_name='Ссылка на сайт')),
                ('packaging_unit', models.CharField(blank=True, max_length=10, null=True, verbose_name='Единицы измерения')),
                ('has_on_storage', models.PositiveIntegerField(blank=True, null=True, verbose_name='Остаток на складе')),
                ('has_on_storage_near', models.PositiveIntegerField(blank=True, null=True, verbose_name='Остаток на складе по аналогам')),
                ('supply_date', models.DateField(blank=True, null=True, verbose_name='Дата фактического поступления')),
                ('supply_quantity', models.PositiveIntegerField(blank=True, null=True, verbose_name='Факт поставки, кол-во')),
                ('not_delivered_pcs', models.PositiveIntegerField(blank=True, null=True, verbose_name='Не доставлено, кол-во')),
                ('storage_cell', models.CharField(blank=True, max_length=255, null=True, verbose_name='Ячейка хранения')),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='storage.orders', verbose_name='Заказ')),
                ('responsible', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Ответственный')),
                ('product_movie', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='storage.productmovies', verbose_name='Перемещение по складу')),
                ('product_request', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='storage.productrequest', verbose_name='Заявка на закуп')),
                ('product_name', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='storage.products', verbose_name='Наименование товара')),
            ],
            options={
                'verbose_name': 'заявку и заказ закупки',
                'verbose_name_plural': 'Все закупки',
            },
        ),
        migrations.CreateModel(
            name='Projects',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateField(auto_now_add=True, verbose_name='Дата записи')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Полное название проекта')),
                ('detail_full_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Полное название изделия')),
                ('project_code', models.CharField(blank=True, max_length=100, null=True, verbose_name='Шифр проекта')),
                ('detail_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Изделие')),
                ('detail_code', models.CharField(blank=True, max_length=100, null=True, verbose_name='Шифр изделия')),
                ('engineer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='projects_engineer_set', to=settings.AUTH_USER_MODEL, verbose_name='Инженер')),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Менеджер')),
            ],
            options={
                'verbose_name': 'проект',
                'verbose_name_plural': 'Проекты',
            },
        ),
        migrations.AddField(
            model_name='productrequest',
            name='project',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='storage.projects', verbose_name='Проект'),
        ),
    ]
