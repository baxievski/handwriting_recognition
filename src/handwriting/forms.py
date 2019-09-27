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
        self.helper.form_id = 'agreement_form'
        self.helper.form_method = 'post'
        super().__init__(*args, **kwargs)

    def image(self):
        data_url_pattern = re.compile('data:image/(png|jpeg);base64,(.*)$')

        image_data = self.cleaned_data['image_data']
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
        resized = Image.new('RGBA', dimmensions, (255, 255, 255, 0))
        resized.paste(data, (2, 2), mask=data)

        self.data = resized

        return self

    def flatten(self):
        flattened = Image.new('RGB', (max(self.data.size), max(self.data.size)), (255, 255, 255))
        flattened.paste(
            self.data,
            ((max(self.data.size) - self.data.size[0]) // 2, (max(self.data.size) - self.data.size[1]) // 2),
            mask=self.data)
        flattened = flattened.convert('L')

        self.data = flattened

        return self
    
    def convert(self):
        data = self.data.convert('L')
        data = np.array(data) / 255

        self.data = data.reshape(data.shape[0] * data.shape[1])

        return self

    def process_image(self, data):
        cropped = data.crop(data.getbbox())

        white_bg = Image.new('RGB', (max(cropped.size), max(cropped.size)), (255, 255, 255))
        white_bg.paste(
            cropped,
            ((max(cropped.size) - cropped.size[0]) // 2, (max(cropped.size) - cropped.size[1]) // 2),
            cropped)
        white_bg = white_bg.resize((24, 24), Image.BICUBIC)

        resized = Image.new('RGB', (28, 28), (255, 255, 255))
        resized.paste(white_bg, (2, 2))
        resized = resized.convert('L')

        processed_array = np.array(resized) / 255
        processed_array = processed_array.reshape(processed_array.shape[0] * processed_array.shape[1])

        return processed_array

    def save_rotated(self, label, dataset_path, digit_id, angles=list(range(-20, 24, 4))):
        try:
            with open(dataset_path, 'rb') as npz:
                npz_file_content = np.load(npz)
                dataset = npz_file_content['dataset']
                labels = npz_file_content['labels']
                ids = npz_file_content['ids']
        except OSError:
            pass

        data = self.image()

        # disable rotation for now
        # rotated = [data.rotate(angle, resample=Image.BICUBIC, expand=True) for angle in angles]
        rotated = [data, ]

        processed_images = [self.process_image(r) for r in rotated]

        for img in processed_images:
            try:
                dataset = np.vstack((dataset, img))
                labels = np.append(labels, label)
                ids = np.append(ids, digit_id)
            except NameError:
                dataset = img
                labels = np.array(label)
                ids = np.array(digit_id)

        with open(dataset_path, 'wb') as npz:
            np.savez(npz, dataset=dataset, labels=labels, ids=ids)
