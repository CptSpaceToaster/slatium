import unittest

from slatium import Dualdict


class DualdictConstruct(unittest.TestCase):
    def test_simple_construct(self):
        dd = Dualdict({'a': 1, 'b': 1})
        self.assertEqual(dd, {'a': 1, 'b': 1})


class DualdictAdd(unittest.TestCase):
    def test_add(self):
        dd = Dualdict()
        dd.add('a', 'b', 1)
        self.assertEqual(dd, {'a': 1, 'b': 1})


class DualdictDelete(unittest.TestCase):
    def test_delete_key_1(self):
        dd = Dualdict()
        dd.add('a', 'b', 1)
        del dd['a']
        self.assertEqual(dd, {})

    def test_delete_key_2(self):
        dd = Dualdict()
        dd.add('a', 'b', 1)
        del dd['b']
        self.assertEqual(dd, {})


class DualdictAccess(unittest.TestCase):
    def test_access_key_1(self):
        dd = Dualdict()
        dd.add('a', 'b', [])
        self.assertEqual(dd, {'a': [], 'b': []})
        dd['a'].append(1)
        self.assertEqual(dd, {'a': [1], 'b': [1]})

    def test_access_key_2(self):
        dd = Dualdict()
        dd.add('a', 'b', [])
        self.assertEqual(dd, {'a': [], 'b': []})
        dd['b'].append(1)
        self.assertEqual(dd, {'a': [1], 'b': [1]})


class DualdictUpdate(unittest.TestCase):
    def test_update_key_1(self):
        dd = Dualdict()
        dd.add('a', 'b', 1)
        self.assertEqual(dd, {'a': 1, 'b': 1})
        dd.update('a', 'c')
        self.assertEqual(dd, {'a': 1, 'c': 1})

    def test_update_key_2(self):
        dd = Dualdict()
        dd.add('a', 'b', 1)
        self.assertEqual(dd, {'a': 1, 'b': 1})
        dd.update('b', 'c')
        self.assertEqual(dd, {'b': 1, 'c': 1})


class DualdictExceptions(unittest.TestCase):
    def test_add_existing_key(self):
        with self.assertRaises(KeyError) as context:
            dd = Dualdict()
            dd.add('a', 'b', 1)
            dd.add('a', 'c', 2)
        self.assertEqual(str(context.exception), "'a'")

    def test_del_missing_key(self):
        with self.assertRaises(KeyError) as context:
            dd = Dualdict()
            dd.add('a', 'b', 1)
            dd.add('c', 'b', 2)
        self.assertEqual(str(context.exception), "'b'")


if __name__ == '__main__':
    unittest.main()
