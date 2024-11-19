from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver


@receiver(pre_delete)
def preserve_related_field_names(sender, instance, **kwargs):
    """
    Обработчик для сохранения связанных данных в поля *_old
    перед удалением записи.
    """
    print(f"удаление объекта: {instance} модель: {sender.__name__}")

    # Получаем все связанные объекты
    for related_object in instance._meta.related_objects:
        if not isinstance(related_object, models.ManyToOneRel):  # Проверяем тип связи
            continue

        related_model = related_object.related_model  # Модель, связанная через ForeignKey
        related_field_name = related_object.field.name  # Поле связи в связанной модели
        related_field_old_name = f"{related_field_name}_old"  # Поле для сохранения старого значения

        print(f"Поле: {related_field_old_name} в модели {related_model.__name__}")

        # Проверяем, что поле *_old существует в связанной модели
        if not hasattr(related_model, related_field_old_name):
            print(f"Поле {related_field_old_name} отсутствует в модели {related_model.__name__}")
            continue

        # Ищем все записи, связанные с удаляемой моделью
        accessor_name = related_object.get_accessor_name()
        related_queryset = getattr(instance, accessor_name).all()
        for related_instance in related_queryset:
            # Сохраняем строковое представление удаляемой записи
            setattr(related_instance, related_field_old_name, str(instance))
            related_instance.save(update_fields=[related_field_old_name])
            print(f"Сохранил '{str(instance)}' в поле {related_field_old_name} модели {related_model.__name__}")
