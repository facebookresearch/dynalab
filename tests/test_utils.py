# Copyright (c) Facebook, Inc. and its affiliates.

import unittest

from dynalab.utils import list_datasets


class UtilsUnitTest(unittest.TestCase):
    def test_list_datasets(self):
        datasets = list_datasets()
        self.assertEqual(datasets, ["Hate Speech", "NLI", "QA", "Sentiment"])
