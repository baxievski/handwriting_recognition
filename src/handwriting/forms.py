import copy
import re
import base64
import numpy as np
import io
from django import forms
from crispy_forms.helper import FormHelper
from PIL import Image


class PostImageForm(forms.Form):
    image_data = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_id = "handwriting_input_form"
        self.helper.form_method = "post"
        super().__init__(*args, **kwargs)

    def image(self):
        data_url_pattern = re.compile("data:image/(png|jpeg);base64,(.*)$")

        image_data = self.cleaned_data["image_data"]
        image_data = data_url_pattern.match(image_data).group(2)
        image_data = image_data.encode()
        image_data = base64.b64decode(image_data)
        image_data = Image.open(io.BytesIO(image_data))

        self.original_image_data = image_data
        self.data = copy.deepcopy(image_data)

        return self

    def rotate(self, angle):
        if angle == 0:
            return self

        self.data = self.data.rotate(angle, resample=Image.BICUBIC, expand=True)

        return self

    def crop(self):
        self.data = self.data.crop(self.data.getbbox())
        return self

    def resize(self, dimmensions):
        dimmensions = tuple(dimmensions)
        inside_dimmensions = tuple(x - 4 for x in dimmensions)

        data = self.data.resize(inside_dimmensions, Image.BICUBIC)
        resized = Image.new("RGBA", dimmensions, (255, 255, 255, 0))
        resized.paste(data, (2, 2), mask=data)

        self.data = resized

        return self

    def flatten(self):
        flattened = Image.new(
            "RGB", (max(self.data.size), max(self.data.size)), (255, 255, 255)
        )
        flattened.paste(
            self.data,
            (
                (max(self.data.size) - self.data.size[0]) // 2,
                (max(self.data.size) - self.data.size[1]) // 2,
            ),
            mask=self.data,
        )
        flattened = flattened.convert("L")

        self.data = flattened

        return self

    def convert(self):
        data = self.data.convert("L")
        data = np.array(data) / 255

        self.data = data.reshape(data.shape[0] * data.shape[1])

        return self
