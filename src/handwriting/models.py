import numpy as np
from django.db import models
from django.contrib import admin
from django.contrib.postgres.fields import ArrayField



class NumpyArrayField(ArrayField):
    def __init__(self, base_field, size=None, **kwargs):
        super(NumpyArrayField, self).__init__(base_field, size, **kwargs)

    @property
    def description(self):
        return "Numpy array of {}".format(self.base_field.description)

    def get_db_prep_value(self, value, connection, prepared=False):
        return super(NumpyArrayField, self).get_db_prep_value(list(value), connection, prepared)

    def deconstruct(self):
        name, path, args, kwargs = super(NumpyArrayField, self).deconstruct()
        kwargs.update({
            'base_field': self.base_field,
            'size': self.size,
        })
        return name, path, args, kwargs

    def to_python(self, value):
        return super(NumpyArrayField, self).to_python(np.array(value))

    def value_to_string(self, obj):
        return super(NumpyArrayField, self).value_to_string(list(obj))


class RawInputData(models.Model):
    label = models.CharField(max_length=1)
    image_data = NumpyArrayField(base_field=models.FloatField())
    original_image_dimmensions = ArrayField(
        base_field=models.IntegerField(),
        default=None,
        blank=True,
        null=True
    )
    bounding_box = ArrayField(
        base_field=models.IntegerField(),
        default=None,
        blank=True,
        null=True
    )
    insertion_date = models.DateTimeField('date inserted')
    ip_address = models.GenericIPAddressField(
        default=None,
        blank=True,
        null=True
    )
    discarded = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Label: {self.label}, id: {self.id}"


class Character(models.Model):
    image_data = NumpyArrayField(base_field=models.FloatField())
    resized_image_dimmensions = ArrayField(
        base_field=models.IntegerField(),
        default=None,
        blank=True,
        null=True
    )
    rotation_angle = models.IntegerField()
    raw_input_data = models.ForeignKey(
        RawInputData,
        related_name="characters",
        on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"Label: {self.raw_input_data.label}, id: {self.raw_input_data.id}, rotated: {self.rotation_angle}°"

# class Dataset(models.Model):
#     KIND = (
#        ("digits", "Numbers (0-9)"),
#        ("cyrillic", "Macedonian cyrillic characters (А-Ш, а-ш)"),
#        ("latin", "Latin characters (A-Z, a-z)"),
#    )

#     kind = models.CharField(max_length=32, choices=KIND, default="digits")
#     created_on = models.DateTimeField("dataset created")
#     training_ids = ArrayField(base_field=models.IntegerField())
#     training_labels = NumpyArrayField(base_field=models.CharField(max_length=1))
#     training_data = NumpyArrayField(
#         base_field=NumpyArrayField(
#             base_field=models.IntegerField()
#         )
#     )
#     test_ids = ArrayField(base_field=models.IntegerField())
#     test_labels = NumpyArrayField(base_field=models.CharField(max_length=1))
#     test_data = NumpyArrayField(
#         base_field=NumpyArrayField(
#             base_field=models.IntegerField()
#         )
#     )
#     validation_ids = ArrayField(base_field=models.IntegerField())
#     validation_labels = NumpyArrayField(base_field=models.CharField(max_length=1))
#     validation_data = NumpyArrayField(
#         base_field=NumpyArrayField(
#             base_field=models.IntegerField()
#         )
#     )