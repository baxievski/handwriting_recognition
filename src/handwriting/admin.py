import numpy as np
from django.contrib import admin
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from PIL import Image
from .models import RawInputData, Character


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('get_image', 'rotation_angle', 'resized_image_dimmensions', 'is_discarded' )
    list_filter = ("rotation_angle", "raw_input_data__label", "raw_input_data__discarded", )
    readonly_fields = ("resized_image_dimmensions", "rotation_angle")
    exclude = ("image_data", )

    def get_image(self, obj):
        fk_id = obj.raw_input_data.id
        angle = obj.rotation_angle
        width = obj.resized_image_dimmensions[0]
        height = obj.resized_image_dimmensions[1]
        label = obj.raw_input_data.label
        img_src = f'<img src="/images/{fk_id}/{angle}" width="{width}" height="{height}" /> Label: "{label}"'
        return mark_safe(img_src)
    
    def is_discarded(self, obj):
        return obj.raw_input_data.discarded


@admin.register(RawInputData)
class RawInputDataAdmin(admin.ModelAdmin):
    readonly_fields = ("original_image_dimmensions", "bounding_box")
    exclude = ('image_data',)
