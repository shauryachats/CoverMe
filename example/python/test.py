# test_sample.py
import sample
import unittest
 
class TestAdd(unittest.TestCase):
    """
    Test the add function from the sample library
    """
 
    def test_add_integers(self):
        """
        Test that the addition of two integers returns the correct total
        """
        result = sample.add(1, 2)
        self.assertEqual(result, 3)
 
    def test_add_floats(self):
        """
        Test that the addition of two floats returns the correct result
        """
        result = sample.add(10.5, 2)
        self.assertEqual(result, 12.5)
 
    def test_add_strings(self):
        """
        Test the addition of two strings returns the two string as one
        concatenated string
        """
        result = sample.add('abc', 'def')
        self.assertEqual(result, 'abcdef')
 
 
if __name__ == '__main__':
    unittest.main()