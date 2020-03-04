import os
import unittest

from logic import convert_to_csv, convert_date


def get_content(file1, file2):
    """
    Reads two files as a list of sentences, each
    :param file1: the first file to read
    :param file2: the second file to read
    :return: a tuple containing 2 lists, the lines in file1 and file2
    """
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        return [line for line in f1], [line for line in f2]


"""
Test class for the convert_to_csv method
"""


class TestConversionMethod(unittest.TestCase):
    def test_conversion_arms_oral(self):
        # create test variables
        input_folder = 'test/input/arms_oralHistories'
        output_folder = 'test/test_output'
        output_file = 'test_arms_oralHistories.csv'
        # correct output file (where the manually prepared output is stored)
        test_output_file = 'test/output/arms_oralHistories.csv'
        # call function
        convert_to_csv(input_folder, output_folder, output_file)

        file1_content, file2_content = get_content(output_folder + os.sep + output_file, test_output_file)
        self.assertListEqual(file1_content, file2_content)

    def test_conversion_klhs_photographs(self):
        # create test variables
        input_folder = 'test/input/klhs_photographs'
        output_folder = 'test/test_output'
        output_file = 'test_klhs_photographs.csv'
        # correct output file (where the manually prepared output is stored)
        test_output_file = 'test/output/klhs_photographs.csv'
        # call function
        convert_to_csv(input_folder, output_folder, output_file)

        file1_content, file2_content = get_content(output_folder + os.sep + output_file, test_output_file)
        self.assertListEqual(file1_content, file2_content)

    def test_conversion_news_issues(self):
        # create test variables
        input_folder = 'test/input/news_issues'
        output_folder = 'test/test_output'
        output_file = 'test_news_issues.csv'
        # correct output file (where the manually prepared output is stored)
        test_output_file = 'test/output/news_issues.csv'
        # call function
        convert_to_csv(input_folder, output_folder, output_file)

        file1_content, file2_content = get_content(output_folder + os.sep + output_file, test_output_file)
        self.assertListEqual(file1_content, file2_content)

    def test_conversion_klhs_shino(self):
        # create test variables
        input_folder = 'test/input/klhs_shino'
        output_folder = 'test/test_output'
        output_file = 'test_klhs_shino.csv'
        # correct output file (where the manually prepared output is stored)
        test_output_file = 'test/output/klhs_shino.csv'
        # call function
        convert_to_csv(input_folder, output_folder, output_file)

        file1_content, file2_content = get_content(output_folder + os.sep + output_file, test_output_file)
        self.assertListEqual(file1_content, file2_content)

    def test_conversion_osoyoos_transportation(self):
        # create test variables
        input_folder = 'test/input/osoyoos_transportation'
        output_folder = 'test/test_output'
        output_file = 'test_osoyoos_transportation.csv'
        # correct output file (where the manually prepared output is stored)
        test_output_file = 'test/output/osoyoos_transportation.csv'
        # call function
        convert_to_csv(input_folder, output_folder, output_file)

        file1_content, file2_content = get_content(output_folder + os.sep + output_file, test_output_file)
        self.assertListEqual(file1_content, file2_content)


"""
Test class for the convertDate method
"""


class TestDateMethod(unittest.TestCase):
    def test_conversion(self):
        # Format: per list within the list, format is [dtStr, letterDate] where dtStr and letterDate are parameter names
        # from the function currently defined in Sharon's script.
        # The #number represents the test case, e.g. #1 is Test case 1.

        tests = [
            ['Jan-20', True],  # 1
            ['Jan-62', True],  # 2
            ['Jan-00', True],  # 3
            ['Dec-01', True],  # 4
            ['30-01-1989', False]  # 5
        ]

        # The answers to the corresponding tests
        answers = [
            '1920-01',
            '1962-01',
            '1900-01',
            '1901-12',
            '1989-01-30'
        ]

        # Test case 1: Jan-20 gets converted to 2020-01, but since 2020 > 1999, 2020-100 = 1920-01 (which is the correct output)
        # Test case 2: Jan-62 gets converted to 1962-01
        # Test case 3: Same as test case 1, but with the year 2000
        # Test case 4: Change from testing month Jan to Dec
        # Test case 5: Change badly formed date to correclty formed date

        result_set = [convert_date(test[0], test[1]) for test in tests]
        self.assertSequenceEqual(result_set, answers)


if __name__ == '__main__':
    unittest.main()
