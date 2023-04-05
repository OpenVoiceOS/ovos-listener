# Copyright 2020 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from unittest import TestCase

from ovos_listener.data_structures import CyclicAudioBuffer


class TestCyclicBuffer(TestCase):
    def test_init(self):
        buff = CyclicAudioBuffer(16, b'abc')
        self.assertEqual(buff.get(), b'abc')
        self.assertEqual(len(buff), 3)

    def test_init_larger_inital_data(self):
        size = 16
        buff = CyclicAudioBuffer(size, b'a' * (size + 3))
        self.assertEqual(buff.get(), b'a' * size)

    def test_append_with_room_left(self):
        buff = CyclicAudioBuffer(16, b'abc')
        buff.append(b'def')
        self.assertEqual(buff.get(), b'abcdef')

    def test_append_with_full(self):
        buff = CyclicAudioBuffer(3, b'abc')
        buff.append(b'de')
        self.assertEqual(buff.get(), b'cde')
        self.assertEqual(len(buff), 3)

    def test_get_last(self):
        buff = CyclicAudioBuffer(3, b'abcdef')
        self.assertEqual(buff.get_last(3), b'def')

    def test_get_item(self):
        buff = CyclicAudioBuffer(6, b'abcdef')
        self.assertEqual(buff[:], b'abcdef')
