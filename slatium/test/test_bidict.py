import unittest

from slatium import Bidict


class BidictConstruct(unittest.TestCase):
    def test_simple_construct(self):
        bd = Bidict({'a': 1, 'b': 2})
        self.assertEqual(bd, {'a': 1, 'b': 2})
        self.assertEqual(bd.inverse, {1: ['a'], 2: ['b']})

    def test_shared_construct(self):
        bd = Bidict({'a': 1, 'b': 1})
        self.assertEqual(bd, {'a': 1, 'b': 1})
        self.assertEqual(len(bd.inverse[1]), 2)
        self.assertTrue('a' in bd.inverse[1])
        self.assertTrue('b' in bd.inverse[1])


class BidictAdd(unittest.TestCase):
    def test_add(self):
        bd = Bidict()
        bd['a'] = 1
        self.assertEqual(bd, {'a': 1})
        self.assertEqual(bd.inverse, {1: ['a']})
        bd['b'] = 2
        self.assertEqual(bd, {'a': 1, 'b': 2})
        self.assertEqual(bd.inverse, {1: ['a'], 2: ['b']})

    def test_overwrite(self):
        bd = Bidict()
        bd['a'] = 1
        self.assertEqual(bd, {'a': 1})
        self.assertEqual(bd.inverse, {1: ['a']})
        bd['a'] = 2
        self.assertEqual(bd, {'a': 2})
        self.assertEqual(bd.inverse, {1: ['a'], 2: ['a']})


class BidictDelete(unittest.TestCase):
    def test_delete_simple_key(self):
        bd = Bidict({'a': 1, 'b': 2})
        del bd['b']
        self.assertEqual(bd, {'a': 1})
        self.assertEqual(bd.inverse, {1: ['a']})

    def test_delete_shared_key(self):
        bd = Bidict({'a': 1, 'b': 1})
        del bd['b']
        self.assertEqual(bd, {'a': 1})
        self.assertEqual(bd.inverse, {1: ['a']})

    def test_delete_simple_value(self):
        bd = Bidict({'a': 1, 'b': 2})
        del bd[2]
        self.assertEqual(bd, {'a': 1})
        self.assertEqual(bd.inverse, {1: ['a']})

    def test_delete_shared_value(self):
        bd = Bidict({'a': 1, 'b': 1})
        del bd[1]
        self.assertEqual(bd, {})
        self.assertEqual(bd.inverse, {})


class BidictAccess(unittest.TestCase):
    def test_access_simple_key(self):
        bd = Bidict({'a': 1, 'b': 2})
        self.assertEqual(bd['a'], [1])
        self.assertEqual(bd['b'], [2])

    def test_access_shared_key(self):
        bd = Bidict({'a': 1, 'b': 1})
        self.assertEqual(bd['a'], [1])
        self.assertEqual(bd['b'], [1])

    def test_access_simple_value(self):
        bd = Bidict({'a': 1, 'b': 2})
        self.assertEqual(bd[1], ['a'])
        self.assertEqual(bd[2], ['b'])

    def test_access_shared_value(self):
        bd = Bidict({'a': 1, 'b': 1})
        self.assertEqual(len(bd.inverse[1]), 2)
        self.assertTrue('a' in bd.inverse[1])
        self.assertTrue('b' in bd.inverse[1])


class BidictExceptions(unittest.TestCase):
    def test_access_missing_key(self):
        with self.assertRaises(KeyError) as context:
            bd = Bidict()
            bd['a']
        self.assertEqual(str(context.exception), "'a'")

    def test_del_missing_key(self):
        with self.assertRaises(KeyError) as context:
            bd = Bidict()
            del bd['a']
        self.assertEqual(str(context.exception), "'a'")


if __name__ == '__main__':
    unittest.main()
