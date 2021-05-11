# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from dynalab.utils import list_datasets


class UtilsUnitTest(unittest.TestCase):
    def test_list_datasets(self):
        datasets = list_datasets()
        self.assertEqual(datasets, ["Hate Speech", "NLI", "QA", "Sentiment"])
