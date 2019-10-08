import numpy as np
import pickle
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from operator import itemgetter
from pathlib import Path
from PIL import Image
from handwriting.models import RawInputData, Character
from handwriting.forms import PostImageForm
# from handwriting.neural_network import NeuralNetwork


# TODO: add django-debug-toolbar: https://django-debug-toolbar.readthedocs.io/en/stable/installation.html#getting-the-code
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def index(request):
    return render(request, 'index.html', context={})


def show_dataset_image(request, fk_id, angle):
    normalized_data = Character.objects\
        .filter(raw_input_data__id=fk_id)\
        .filter(rotation_angle=angle)\
        .first()

    label = normalized_data.raw_input_data.label
    dimmensions = normalized_data.resized_image_dimmensions
    angle = normalized_data.rotation_angle

    image_data = np.array(normalized_data.image_data) * 255
    image_data = image_data.reshape(dimmensions)
    im = Image.fromarray(np.uint8(image_data))

    response = HttpResponse(content_type="image/png")
    im.save(response, format="png")

    return response


def create_dataset(request, label):
    if not request.POST:
        return render(request, 'create_dataset.html', context={'label': label,})

    form = PostImageForm(request.POST)

    if not form.is_valid():
        return render(request, 'create_dataset.html', context={'label': label,})
    
    raw_input_data = RawInputData(
        label=label,
        image_data=form.image().crop().flatten().convert().data,
        original_image_dimmensions=form.image().data.size,
        bounding_box=form.image().data.getbbox(),
        insertion_date=timezone.now(),
        ip_address=get_client_ip(request)
    )
    raw_input_data.save()

    for angle in range(-18, 19, 6):
        rotated_data = Character(
            raw_input_data=raw_input_data,
            rotation_angle=angle,
            resized_image_dimmensions=(28, 28),
            image_data=form.image().rotate(angle).crop().resize((28, 28)).flatten().convert().data,
        )
        rotated_data.save()

    return render(request, 'create_dataset.html', context={'label': label,})


def digits(request):
    if not request.POST:
        return render(request, 'digits.html', context={})

    digits_trained = Path.cwd() / "mounted" / 'nn_digits_trained.pkl'
    if not Path.is_file(digits_trained):
        return render(request, 'digits.html', context={"prediction": "Neural Network is not trained", "predictions": ""})

    with open(digits_trained, 'rb') as f:
        nn_digits = pickle.load(f)

    form = PostImageForm(request.POST)

    if not form.is_valid():
        # FIXME: don't just render the same page
        return render(request, 'digits.html', context={})

    img = form.image().crop().resize((28, 28)).flatten().convert().data

    output_weights = nn_digits.predict(img)

    probabilities = output_weights * 100 / np.sum(output_weights)
    [probabilities] = probabilities.tolist()
    probabilities = [(n, prob) for (n, prob) in enumerate(probabilities)]


    context = {
        'probabilities': sorted(probabilities, key=itemgetter(1), reverse=True),
    }

    return render(request, 'digits.html', context=context)
