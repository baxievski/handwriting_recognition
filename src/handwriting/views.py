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


# TODO: add django-debug-toolbar:
# https://django-debug-toolbar.readthedocs.io/en/stable/installation.html#getting-the-code
def index(request):
    return render(request, "index.html")


def show_dataset_image(request, fk_id, angle):
    normalized_data = (
        Character.objects.filter(raw_input_data__id=fk_id)
        .filter(rotation_angle=angle)
        .first()
    )

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
        return render(request, "create_dataset.html", context={"label": label})

    form = PostImageForm(request.POST)

    if not form.is_valid():
        return render(request, "create_dataset.html", context={"label": label})

    raw_input_data = RawInputData(
        label=label,
        image_data=form.image().crop().flatten().convert().data,
        original_image_dimmensions=form.image().data.size,
        bounding_box=form.image().data.getbbox(),
        insertion_date=timezone.now(),
    )
    raw_input_data.save()

    for angle in range(-18, 19, 6):
        rotated_data = Character(
            raw_input_data=raw_input_data,
            rotation_angle=angle,
            resized_image_dimmensions=(28, 28),
            image_data=form.image()
            .rotate(angle)
            .crop()
            .resize((28, 28))
            .flatten()
            .convert()
            .data,
        )
        rotated_data.save()

    return render(request, "create_dataset.html", context={"label": label})


def predict(request, dataset):
    if dataset not in ("digits", "cyrillic_lowercase"):
        # FIXME: don't just render the same page
        return render(request, "predict.html", context={})

    if dataset == "digits":
        labels = "0123456789"
    elif dataset == "cyrillic_lowercase":
        labels = "абвгдѓежзѕијклљмнњопрстќуфхцчџш"

    labels = sorted(labels)
    labels = "".join(labels)
    
    if not request.POST:
        return render(request, "predict.html", context={"labels": labels, })

    trained_nn_path = Path.cwd() / "mounted" / f"nn_{dataset}_trained.pkl"
    if not Path.is_file(trained_nn_path):
        return render(request, "predict.html", context={"labels": labels, })

    with open(trained_nn_path, "rb") as f:
        trained_nn = pickle.load(f)

    form = PostImageForm(request.POST)

    if not form.is_valid():
        # FIXME: don't just render the same page
        return render(request, "predict.html", context={"labels": labels, })

    img = form.image().crop().resize((28, 28)).flatten().convert().data

    output_weights = trained_nn.predict(img)

    probabilities = output_weights * 100 / np.sum(output_weights)
    [probabilities] = probabilities.tolist()
    probabilities = [(labels[n], prob) for (n, prob) in enumerate(probabilities)]

    context = {
        "probabilities": sorted(probabilities, key=itemgetter(1), reverse=True),
        "labels": labels,
    }

    return render(request, "predict.html", context=context)