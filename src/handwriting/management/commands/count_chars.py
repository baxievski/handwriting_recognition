import collections
import numpy as np
import pickle
import random
from django.db.models import Count
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from pathlib import Path
from sklearn.preprocessing import OneHotEncoder
from handwriting.models import RawInputData, Character
from handwriting.neural_network import NeuralNetwork


class Command(BaseCommand):
    help = 'Counts the inserted characters'

    def handle(self, *args, **kwargs):
        self.raw_ids_for_labels([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.split_train_test_validate()
        self.train()

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

    def split_train_test_validate(self, training_ratio=0.8):
        test_ratio = (1 - training_ratio) * 0.6
        random.shuffle(self.raw_ids)

        train_end = int(len(self.raw_ids)*training_ratio)
        test_start = int(len(self.raw_ids)*training_ratio)
        test_end = int(len(self.raw_ids)*(training_ratio+test_ratio)) 
        validate_start = int(len(self.raw_ids)*(training_ratio+test_ratio))

        training_ids = self.raw_ids[:train_end]
        test_ids = self.raw_ids[test_start:]
        validate_ids = self.raw_ids[validate_start:]

        test_set = Character\
            .objects\
            .filter(raw_input_data__pk__in=test_ids)
        test_data = np.vstack([np.array(x.image_data) for x in test_set])
        test_labels = test_set\
            .values_list("raw_input_data__label", flat=True)\
            .all()
        test_labels = np.array(test_labels)

        training_set = Character\
            .objects\
            .filter(raw_input_data__pk__in=training_ids)
        training_data = np.vstack([np.array(x.image_data) for x in training_set])
        training_labels = training_set\
            .values_list("raw_input_data__label", flat=True)\
            .all()
        training_labels = np.array(training_labels)

        validation_set = Character\
            .objects\
            .filter(raw_input_data__pk__in=validate_ids)
        validation_data = np.vstack([np.array(x.image_data) for x in validation_set])
        validation_labels = validation_set\
            .values_list("raw_input_data__label", flat=True)\
            .all()
        validation_labels = np.array(validation_labels)

        self.training_labels = training_labels
        self.training_data = training_data
        self.test_labels = test_labels
        self.test_data = test_data
        self.validation_labels = validation_labels
        self.validation_data = validation_data

        self.stdout.write(f"Train:\t\t{self.training_data.shape}\t{self.training_labels.shape}")
        self.stdout.write(f"Test:\t\t{self.test_data.shape}\t{self.test_labels.shape}")
        self.stdout.write(f"Validation:\t{self.validation_data.shape}\t{self.validation_labels.shape}")

        return True
    
    def train(self):
        print(f"Start train()")
        nn_digits = NeuralNetwork(
            input_nodes=784,
            hidden_nodes=256,
            output_nodes=10,
            learning_rate=3.2
        )

        mnist_ohc = OneHotEncoder(sparse=False)

        training_results = nn_digits.train(
            X=self.training_data,
            y=mnist_ohc.fit_transform(self.training_labels.reshape(-1, 1)),
            X_test=self.test_data,
            y_test=mnist_ohc.fit_transform(self.test_labels.reshape(-1, 1)),
            learning_rate_decay=0.94,
            iterations=3000,
            batch_size=30,
            verbose=True
        )

        J = training_results['J_history']
        training_accuracy = training_results['train_acc_history']
        test_accuracy = training_results['test_acc_history']

        self.stdout.write(self.style.SUCCESS(f"Training accuracy:\t{training_accuracy[-1]:.3f}"))
        self.stdout.write(self.style.SUCCESS(f"Test accuracy:\t\t{test_accuracy[-1]:.3f}"))

        digits_trained = "nn_digits_trained.pkl"

        with open(digits_trained, 'wb') as f:
            pickle.dump(nn_digits, f)

        return True
