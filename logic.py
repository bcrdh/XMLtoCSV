import os
import pandas as pd
from bs4 import BeautifulSoup
import glob
import datetime
import re
from mappings import mappings
from mappings import reset


def get_mods_files(input_folder):
    return \
        sorted([filename for filename in glob.iglob(os.path.join(input_folder, '**', '*.xml'), recursive=True)])


def multi_hdg_mkr(pt1, num, pt2):
    """
    Helper method for things like Contributor1_Given, Creator1_Given, etc.
    :param pt1: part 1 (e.g. Contributor, Creator, etc.)
    :param num: the number to add (e.g. Contributor2, Creator1, etc.)
    :param pt2: part 2 (e.g. Family, Given, etc.)
    :return:
    """
    return pt1 + str(num) + '_' + pt2


def convert_date(dt_str, letter_date):
    """
    Converts an invalid formatted date into a proper date for ARCA Mods
    Correct format:  Y-m-d
    Fixes:
    Incorrect format: m-d-Y
    Incorrect format (letter date): m-d e.g. Jun-17
    :param dt_str: the date string
    :param letter_date: whether the string is a letter date. Letter date is something like Jun-17
    :return: the correctly formatted date
    """
    if letter_date:
        rev_date = datetime.datetime.strptime(dt_str, '%b-%y').strftime('%Y-%m')  # convert date to yymm string format
        rev_date_pts = rev_date.split("-")
        year_num = int(rev_date_pts[0])
        if year_num > 1999:
            year_num = year_num - 100
        year_str = str(year_num)
        rev_date_pts[0] = year_str
        revised = "-".join(rev_date_pts)

    else:
        revised = datetime.datetime.strptime(dt_str, '%d-%m-%Y').strftime(
            '%Y-%m-%d')  # convert date to YY-mm string format

    return revised


def save(df, path):
    """
    Saves dataframe to given path
    :param df: the dataframe to save
    :param path: the save path
    :return: None
    """
    df.to_csv(path, encoding='utf-8', index=False)


def is_newspaper_issue(filename):
    """
    Identifies whether a file is a newspaper MODS
    :param filename: the MODS XML file name
    :return: a boolean indicating whether it is a newspaper
    """
    with open(filename, "r", encoding="utf8") as infile:
        contents = infile.read()

    # Load contents into beautifulsoup to parse xml
    soup = BeautifulSoup(contents, 'xml')
    return soup.find('detail', {'type': 'volume'})


def convert_newspapers_to_csv(files, output_folder, output_file):
    news_col_names = [
        'key', 'Filename', 'Identifier', 'IssueTitle', 'DateCreated', 'Volume', 'Issue',
        'Rights', 'CreativeCommons_URI', 'RightsStatement'
    ]

    # Create data frame
    df = pd.DataFrame(columns=news_col_names)
    df.append(pd.Series(dtype=float), ignore_index=True)

    i = 0  # Keep track of row number in df
    for filename in files:
        # Read file contents
        with open(filename, "r", encoding="utf8") as infile:
            contents = infile.read()

        # Load contents into beautifulsoup to parse xml
        soup = BeautifulSoup(contents, 'xml')

        # Set custom attrs
        soup.i = i
        soup.filename = filename

        # Set cols
        for col in news_col_names:
            if col not in mappings:
                continue
            val = mappings[col](soup)
            if val:
                df.at[i, col] = val
        i += 1
        reset()  # Reset mappings for next file

    save(df, os.path.join(output_folder, output_file))


def convert_to_csv(input_folder, output_folder, output_file):
    """
    Converts a folder of XML files into a single CSV file
    :param input_folder: the input folder containing XML files
    :param output_folder: the output folder to output the CSV
    :param output_file: the name of the CSV file to save content in
    :return: None
    """
    # updated for **Rev 18.5 of the Master Metadata Sheet**

    col_names = [
        'key', 'imageLink', 'PID', 'Filename', 'Directory', 'child_key', 'Title', 'AlternativeTitle', 'Creator1_Given',
        'Creator1_Family', 'CorporateCreator', 'Contributor1_Given', 'Contributor1_Family', 'Contributor2_Given',
        'Contributor2_Family', 'CorporateContributor',
        'Publisher_Original', 'DateCreated', 'Description', 'Extent', 'Subject1_Topic', 'Subject2_Topic',
        'Subject3_Topic',
        'Subject4_Topic', 'Subject5_Topic', 'Subject_Geographic', 'Coordinates', 'Subject1_Given', 'Subject1_Family',
        'Subject2_Given', 'Subject2_Family', 'Subject3_Given', 'Subject3_Family', 'CorporateSubject_1',
        'CorporateSubject_2', 'DateRange', 'Genre', 'GenreAuthority', 'Type', 'internetMediaType', 'Language1',
        'Language2', 'Notes', 'AccessIdentifier', 'LocalIdentifier', 'ISBN', 'Classification', 'URI', 'Source',
        'Rights',
        'CreativeCommons_URI', 'RightsStatement', 'relatedItem_Title', 'relatedItem_PID', 'recordCreationDate',
        'recordOrigin'
    ]

    # Sort the file names in order to make CSV more organized and also easier
    # for unit tests
    files = get_mods_files(input_folder)

    # Check newspaper
    if is_newspaper_issue(files[0]):
        convert_newspapers_to_csv(files, output_folder, output_file)
        return  # Don't continue

    # Create data frame
    df = pd.DataFrame(columns=col_names)
    df.append(pd.Series(dtype=float), ignore_index=True)

    # Used to keep track of row number in data frame
    i = 0
    for filename in files:
        # Read file contents
        with open(filename, "r", encoding="utf8") as infile:
            contents = infile.read()

        # Load contents into beautifulsoup to parse xml
        soup = BeautifulSoup(contents, 'xml')

        # Set custom attrs
        soup.i = i
        soup.filename = filename

        # Set cols
        for col in col_names:
            if col not in mappings:
                continue
            val = mappings[col](soup)
            if val:
                df.at[i, col] = val
        i += 1
        reset()  # Reset mappings for next file

    save(df, os.path.join(output_folder, output_file))
