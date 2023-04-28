import unittest
from PG_book_processing import cleaning_functions

class Test_Book_Cleaning(unittest.TestCase):
    def test_create_pattern(self):
        title = "Happiness and Marriage"
        author = "Elizabeth Towne"
        pattern = cleaning_functions.create_pattern(title,author)

        correct = "(HAPPINESS|(h|H)appiness)(\\s+|\n+)(AND|(a|A)nd)(\\s+|\n+)(MARRIAGE|(m|M)arriage)(\\s+|\n+)(By|BY|by)(\\s{1,3}|\n{1,3})(ELIZABETH|(e|E)lizabeth) (TOWNE|(t|T)owne)"

        self.assertEqual(pattern.__repr__(),correct.__repr__())
