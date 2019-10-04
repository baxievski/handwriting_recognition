import random
from django.db.models import Count
from django.core.management.base import BaseCommand, CommandError
from handwriting.models import RawInputData, Character, Dataset


class Command(BaseCommand):
    help = 'Counts the inserted characters'

    def handle(self, *args, **kwargs):
        try:
            labels = RawInputData.objects.order_by('label').values_list('label', flat=True).distinct()
        except RawInputData.DoesNotExist:
            raise CommandError(f"RawInputData does not exist")
        
        # TODO: get undiscarded
        undiscarded = RawInputData.objects.filter(discarded=False)

        # TODO: print entries per label
        label_counts = {l: undiscarded.filter(label=l).count() for l in labels}
        for l, c in label_counts.items():
            self.stdout.write(f"Label '{l}': {c}")

        # char_0 = Character.objects.filter(raw_input_data__label="0")[:200]
        # for c in char_0:
        #     self.stdout.write(f"{c}")
        
        # TODO: get ids for RawInputData per label
        label_with_least_entries = min(label_counts, key=label_counts.get)
        min_entries = label_counts[label_with_least_entries]

        r = RawInputData.objects
        raw_ids_by_label = {l: r.filter(label=l).values_list('id', flat=True)[:min_entries] for l in labels}
        raw_ids = []
        for k, v in raw_ids_by_label.items():
            raw_ids.extend(v)

        # TODO: split ids into training/test/validation sets
        random.shuffle(raw_ids)
        random.shuffle(raw_ids)
        training_ids = raw_ids[:int(len(raw_ids)*0.98)]
        test_ids = raw_ids[len(training_ids):int(len(raw_ids)*0.99)]
        validation_ids = raw_ids[len(training_ids)+len(test_ids):]
        print(f"all: {len(raw_ids)}\ntraining: {len(training_ids)}\ntesting: {len(test_ids)}\nvalidation: {len(validation_ids)}")
            
        # TODO: querysets for Character training/test/validation sets
        # TODO: https://codereview.stackexchange.com/questions/194906/cleanest-way-to-get-list-of-django-objects-that-have-same-foreign-key-and-displa
        # TODO: check old implementation from /Users/bojan/Projects/personal/handwriting_bak/data_bak/balanced_dataset.npz
        test_set = Character.objects.filter(raw_input_data__pk__in=test_ids).filter(rotation_angle=0)
        print(f"test_set: {test_set.count()}")
        for t in test_set:
            print(f"{t}")
