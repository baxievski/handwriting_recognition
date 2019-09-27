import numpy as np
from django.contrib import admin
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from PIL import Image
from .models import RawInputData, Character


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('get_info', )

    def get_info(self, obj):
        fk_id = obj.raw_input_data.id
        angle = obj.rotation_angle
        width = obj.resized_image_dimmensions[0]
        height = obj.resized_image_dimmensions[1]
        label = obj.raw_input_data.label
        img_src = f'<img src="/images/{fk_id}/{angle}" width="{width}" height="{height}" /> {label}; {angle}°; {width}x{height}'
        return mark_safe(img_src)


admin.site.register(RawInputData)