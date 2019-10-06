import collections
import random
import numpy as np
from django.db.models import Count
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from handwriting.models import RawInputData, Character


class Command(BaseCommand):
    help = 'Counts the inserted characters'

    def handle(self, *args, **kwargs):
        self.raw_ids_for_labels([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.split_train_test_validate()
        self.train()
        # self.save_dataset()

#         try:
#             labels = RawInputData\
#                 .objects\
#                 .filter(label__in=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9])\
#                 .order_by('label')\
#                 .values_list('label', flat=True)\
#                 .distinct()
#         except RawInputData.DoesNotExist:
#             raise CommandError(f"RawInputData does not exist")
        
#         # TODO: get undiscarded
#         undiscarded = RawInputData.objects.filter(discarded=False)

#         # TODO: print entries per label
#         label_counts = {l: undiscarded.filter(label=l).count() for l in labels}
#         self.stdout.write(f"Labels: {label_counts}")

#         # TODO: get ids for RawInputData per label
#         min_entries = label_counts[min(label_counts, key=label_counts.get)]

#         r = RawInputData.objects
#         raw_ids_by_label = {l: r.filter(label=l).values_list("id", flat=True)[:min_entries] for l in labels}
#         raw_ids = [x for (_, v) in raw_ids_by_label.items() for x in v]

#         # TODO: split ids into training/test/validation sets
#         random.shuffle(raw_ids)
#         training_set_ids = raw_ids[:int(len(raw_ids)*0.98)]
#         test_set_ids = raw_ids[int(len(raw_ids)*0.98):int(len(raw_ids)*0.99)]
#         validation_set_ids = raw_ids[int(len(raw_ids)*0.99):]
#         print(f"all: {len(raw_ids)}")
#         print(f"training: {len(training_set_ids)}")
#         print(f"testing: {len(test_set_ids)}")
#         print(f"validation: {len(validation_set_ids)}")
            
#         # TODO: querysets for Character training/test/validation sets
#    # save training_set = Character.objects.filter(raw_input_data__pk__in=training_set_ids).filter(rotation_angle=0)
#    # save training_set_images_arrays = np.vstack([np.array(x.image_data) for x in training_set])
#    # save training_set_labels = np.array(RawInputData.objects.filter(pk__in=training_set_ids).values_list("label", flat=True).all())

#    # save test_set = Character.objects.filter(raw_input_data__pk__in=test_set_ids).filter(rotation_angle=0)
#    # save test_set_images_arrays = np.vstack([np.array(x.image_data) for x in test_set])
#    # save test_set_labels = np.array(RawInputData.objects.filter(pk__in=test_set_ids).values_list("label", flat=True).all())

#    # save validation_set = Character.objects.filter(raw_input_data__pk__in=validation_set_ids).filter(rotation_angle=0)
#    # save validation_set_images_arrays = np.vstack([np.array(x.image_data) for x in validation_set])
#    # save validation_set_labels = np.array(RawInputData.objects.filter(pk__in=validation_set_ids).values_list("label", flat=True).all())
#    # save print(f"image data shape{validation_set_images_arrays.shape}")
#    # save print(f"labels data shape{validation_set_labels.shape}")

#    # save dataset = Dataset(
#    # save     created_on=timezone.now(),
#    # save     training_ids=training_set_ids,
#    # save     training_labels=training_set_labels,
#    # save     training_data=training_set_images_arrays,
#    # save     test_ids=test_set_ids,
#    # save     test_labels=test_set_labels,
#    # save     test_data=test_set_images_arrays,
#    # save     validation_ids=validation_set_ids,
#    # save     validation_labels=validation_set_labels,
#    # save     validation_data=validation_set_images_arrays
#    # save )
#    # save dataset.save()

#         ds = Dataset.objects.all()
#         for d in ds:
#             print(f"training data shape {np.array(d.training_data).shape}")
#             print(f"training labels shape {np.array(d.training_labels).shape}")
#             print(f"{collections.Counter(np.array(d.training_labels))}\n")

#             print(f"test data shape {np.array(d.test_data).shape}")
#             print(f"test labels shape {np.array(d.test_labels).shape}")
#             print(f"{collections.Counter(np.array(d.test_labels))}\n")

#             print(f"validation data shape {np.array(d.validation_data).shape}")
#             print(f"validation labels shape {np.array(d.validation_labels).shape}")
#             print(f"{collections.Counter(np.array(d.validation_labels))}")

    def raw_ids_for_labels(self, l):
        try:
            labels = RawInputData\
                .objects\
                .filter(label__in=l)\
                .order_by('label')\
                .values_list('label', flat=True)\
                .distinct()
        except RawInputData.DoesNotExist:
            raise CommandError(f"RawInputData does not exist")

        undiscarded = RawInputData.objects.filter(discarded=False)

        label_counts = {l: undiscarded.filter(label=l).count() for l in labels}
        self.stdout.write(f"Labels: {label_counts}")

        min_entries = label_counts[min(label_counts, key=label_counts.get)]

        r = RawInputData.objects
        raw_ids_by_label = {l: r.filter(label=l).values_list("id", flat=True)[:min_entries] for l in labels}
        raw_ids = [x for (_, v) in raw_ids_by_label.items() for x in v]
        self.raw_ids = raw_ids
        return True

    def split_train_test_validate(self, training_set_ratio=0.6):
        print(f"Start split_ids_train_test_validate()")
        test_set_ratio = (1 - training_set_ratio) / 2
        random.shuffle(self.raw_ids)
        training_set_ids = self.raw_ids[:int(len(self.raw_ids)*training_set_ratio)]
        test_set_ids = self.raw_ids[int(len(self.raw_ids)*training_set_ratio):int(len(self.raw_ids)*(training_set_ratio+test_set_ratio))]
        validate_set_ids = self.raw_ids[int(len(self.raw_ids)*(training_set_ratio+test_set_ratio)):]
        self.stdout.write(f"Using: {len(training_set_ids)}, {len(test_set_ids)}, {len(validate_set_ids)}")

        training_set = Character\
            .objects\
            .filter(raw_input_data__pk__in=training_set_ids)
        training_set_data = np.vstack([np.array(x.image_data) for x in training_set])
        training_set_labels = RawInputData\
            .objects\
            .filter(pk__in=training_set_ids)\
            .values_list("label", flat=True)\
            .all()
        training_set_labels = np.array(training_set_labels)

        test_set = Character\
            .objects\
            .filter(raw_input_data__pk__in=test_set_ids)
        test_set_data = np.vstack([np.array(x.image_data) for x in test_set])
        test_set_labels = RawInputData\
            .objects\
            .filter(pk__in=test_set_ids)\
            .values_list("label", flat=True)\
            .all()
        test_set_labels = np.array(test_set_labels)

        validation_set = Character\
            .objects\
            .filter(raw_input_data__pk__in=validate_set_ids)
        validation_set_data = np.vstack([np.array(x.image_data) for x in validation_set])
        validation_set_labels = RawInputData\
            .objects\
            .filter(pk__in=validate_set_ids)\
            .values_list("label", flat=True)\
            .all()
        validation_set_labels = np.array(validation_set_labels)

        self.validation_set_labels = validation_set_labels
        self.validation_set_data = validation_set_data
        self.test_set_labels = test_set_labels
        self.test_set_data = test_set_data
        self.training_set_labels = training_set_labels
        self.training_set_data = training_set_data

        print(f"Finish split_train_test_validate()")
        return True
    
    def train(self):
        pass

    # def save_dataset(self):
    #     print(f"Start save_datset()")
    #     training_set = Character\
    #         .objects\
    #         .filter(raw_input_data__pk__in=self.training_set_ids)
    #     training_set_data = np.vstack([np.array(x.image_data) for x in training_set])
    #     training_set_labels = RawInputData\
    #         .objects\
    #         .filter(pk__in=self.training_set_ids)\
    #         .values_list("label", flat=True)\
    #         .all()
    #     training_set_labels = np.array(training_set_labels)

    #     test_set = Character\
    #         .objects\
    #         .filter(raw_input_data__pk__in=self.test_set_ids)
    #     test_set_data = np.vstack([np.array(x.image_data) for x in test_set])
    #     test_set_labels = RawInputData\
    #         .objects\
    #         .filter(pk__in=self.test_set_ids)\
    #         .values_list("label", flat=True)\
    #         .all()
    #     test_set_labels = np.array(test_set_labels)

    #     validation_set = Character\
    #         .objects\
    #         .filter(raw_input_data__pk__in=self.validate_set_ids)
    #     validation_set_data = np.vstack([np.array(x.image_data) for x in validation_set])
    #     validation_set_labels = RawInputData\
    #         .objects\
    #         .filter(pk__in=self.validate_set_ids)\
    #         .values_list("label", flat=True)\
    #         .all()
    #     validation_set_labels = np.array(validation_set_labels)
    #     print(f"1 save_datset()")

    #     dataset = Dataset(
    #         created_on=timezone.now(),
    #         training_ids=self.training_set_ids,
    #         training_labels=training_set_labels,
    #         training_data=training_set_data,
    #         test_ids=self.test_set_ids,
    #         test_labels=test_set_labels,
    #         test_data=test_set_data,
    #         validation_ids=self.validate_set_ids,
    #         validation_labels=validation_set_labels,
    #         validation_data=validation_set_data
    #     )
    #     print(f"2 save_datset()")
    #     try:
    #         dataset.save()
    #     except Exception as e:
    #         print(f"{e}")
    #     print(f"Finish save_datset()")
    #     # TODO: here - save() fails...
    #     return True