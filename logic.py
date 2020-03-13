import os
import pandas as pd
from bs4 import BeautifulSoup
import glob
import datetime
import re
from mappings import mappings
from mappings import reset


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


def convert_newspapers_to_csv(files):
    news_col_names = [
        'key', 'Title', 'AlternativeTitle', 'Creator1_Given', 'Creator1_Family',
        'CorporateCreator', 'Contributor1_Given', 'Contributor1_Family',
        'CorporateContributor', 'Publisher_Original', 'DateCreated', 'Description',
        'CorporateSubject1', 'Genre', 'GenreAuthority', 'Type', 'internetMediaType',
        'Language', 'Notes', 'Source', 'Rights', 'CreativeCommons_URI', 'RightsStatement',
        'relatedItem_Title', 'relatedItem_PID', 'DateIssued_Start', 'DatedIssued_End', 'DateRange',
        'Frequency', 'Abstract', 'Publisher_Location', 'IssueTitle', 'Volume', 'Issue'
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
     'Creator1_Family', 'CorporateCreator', 'Contributor1_Given', 'Contributor1_Family', 'CorporateContributor',
     'Publisher_Original', 'DateCreated', 'Description', 'Extent', 'Subject1_Topic', 'Subject2_Topic', 'Subject3_Topic',
     'Subject4_Topic', 'Subject5_Topic', 'Subject_Geographic', 'Coordinates', 'Subject1_Given', 'Subject1_Family',
     'Subject2_Given', 'Subject2_Family', 'Subject3_Given', 'Subject3_Family', 'CorporateSubject_1',
     'CorporateSubject_2', 'DateRange', 'Genre', 'GenreAuthority', 'Type', 'internetMediaType', 'Language1',
     'Language2', 'Notes', 'AccessIdentifier', 'LocalIdentifier', 'ISBN', 'Classification', 'URI', 'Source', 'Rights',
     'CreativeCommons_URI', 'RightsStatement', 'relatedItem_Title', 'relatedItem_PID', 'recordCreationDate', 'recordOrigin'
    ]

    path = input_folder

    # Sort the file names in order to make CSV more organized and also easier
    # for unit tests
    files = sorted([filename for filename in glob.iglob(os.path.join(path, '*.xml'))])

    # Check newspaper
    if is_newspaper_issue(files[0]):
        convert_newspapers_to_csv(files)
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

        # Set DateCreated column
        df.at[i, 'DateCreated'] = mappings['DateCreated'](soup)

        # Key
        df.at[i, 'key'] = mappings['key'](i)

        # Arca PID
        df.at[i, 'PID'] = mappings['PID'](filename)

        # Link to Image
        df.at[i, 'imageLink'] = mappings['imageLink'](filename)

        alt_title = mappings['AlternativeTitle'](soup)
        if alt_title:
            df.at[i, 'AlternativeTitle'] = alt_title

        df.at[i, 'Title'] = mappings['Title'](soup)

        # unsure - what about abstract for Newspaper obj?
        # description
        description = mappings['Description'](soup)
        if description:
            df.at[i, 'Description'] = description

        # extent
        ext = mappings['Extent'](soup)
        if ext:
            df.at[i, 'Extent'] = ext

        # topical subjects
        for x in range(1, 6):
            field = 'Subject%d_Topic' % x
            result = mappings[field](soup)
            #print(result)
            if result:
                #print('Setting %s to %s' % (field, result))
                df.at[i, field] = result

        # corporate subject
        for x in range(1, 3):
            field = 'CorporateSubject_%d' % x
            result = mappings[field](soup)
            if result:
                df.at[i, field] = result

        # corpCC = soup.select('mods > name[type=corporate]')
        # cCreator = None
        # cContrib = None
        # for corp in corpCC:
        #     if corp.find('roleTerm', string="creator"):
        #         cCreator = corp.find('namePart').getText()
        #     elif corp.find('roleTerm', string="contributor"):
        #         cContrib = corp.find('namePart').getText()

        # corporate creator
        c_creator = mappings['CorporateCreator'](soup)
        if c_creator:
            df.at[i, 'CorporateCreator'] = c_creator.strip()

        c_contrib = mappings['CorporateContributor'](soup)
        # corporate contributor
        if c_contrib:
            df.at[i, 'CorporateContributor'] = c_contrib.strip()

        # geographic subject
        geog_sub = mappings['Subject_Geographic'](soup)
        if geog_sub:
            df.at[i, 'Subject_Geographic'] = geog_sub.getText().strip()

        # ADDED
        # publisher_original
        publisher = mappings['Publisher_Original'](soup)
        if publisher:
            df.at[i, 'Publisher_Original'] = publisher

        # ADDED
        # dateRange
        date_range = mappings['DateRange'](soup)
        if date_range:
            df.at[i, 'DateRange'] = date_range

        # ADDED
        # notes
        notes = mappings['Notes'](soup)
        if notes:
            df.at[i, 'Notes'] = notes

        # ADDED
        # isbn
        isbn = mappings['ISBN'](soup)
        if isbn:
            df.at[i, 'ISBN'] = isbn

        # ADDED
        # classification
        classification = mappings['Classification'](soup)
        if classification:
            df.at[i, 'Classification'] = classification

        # ADDED
        # URI
        uri = mappings['URI'](soup)
        if uri:
            df.at[i, 'URI'] = uri

        # ADDED
        # recordCreationDate & recordOrigin
        record_origin = mappings['recordOrigin'](soup)
        record_creation_date = mappings['recordCreationDate'](soup)
        if record_origin and record_creation_date:
            df.at[i, 'recordCreationDate'] = record_creation_date
            df.at[i, 'recordOrigin'] = record_origin


        # FIXED
        # coordinates
        coords = mappings['Coordinates'](soup)
        if coords:
            df.at[i, 'Coordinates'] = coords

        # personal creators and contributors (can have up to 3 creators, 1 contributor)
        for x in range(1, 4):
            field_family = 'Creator%d_Family' % x
            field_given = 'Creator%d_Given' % x
            creator_family = mappings[field_family](soup)
            creator_given = mappings[field_given](soup)
            if creator_family and creator_given:
                df.at[i, field_family] = creator_family
                df.at[i, field_given] = creator_given

        # personal contributors (max 1 per new guidelines)
        pContrib = None
        pers = soup.select('mods > name[type=personal]')
        if pers is not None:
            for p in pers:
                # print(p.has_attr('type'))
                if p.find('roleTerm', string="contributor"):
                    pContrib = p
                    break

        given = None
        family = None
        if pContrib is not None:
            given = pContrib.find('namePart', {'type': 'given'})
            family = pContrib.find('namePart', {'type': 'family'})
        if given is not None:
            fld = "Contributor1_Given"
            df.at[i, fld] = given.getText().strip()
        if family is not None:
            fld = 'Contributor1_Family'
            df.at[i, fld] = family.getText().strip()

        # personal name subjects (find number)
        psCount = 0  # personal subject count
        perSubs = soup.select('subject > name[type=personal]')
        if len(perSubs) > 0:
            for nm in perSubs:
                psCount += 1
                given = nm.find('namePart', {'type': 'given'})
                if given is not None:
                    fld = multi_hdg_mkr("Subject", psCount, 'Given')
                    df.at[i, fld] = given.getText().strip()
                family = nm.find('namePart', {'type': 'family'})
                if family is not None:
                    fld = multi_hdg_mkr("Subject", psCount, 'Family')
                    df.at[i, fld] = family.getText().strip()

        # genre
        genre = soup.find('genre')
        if genre is not None:
            gen = genre.getText().strip()
            df.at[i, 'Genre'] = gen
            auth = soup.find("td", {"valign": True})
            if genre is not None:
                genAuth = ""
                auth = soup.find("genre", {"authority": "marcgt"})
                if auth is not None:
                    genAuth = "marcgt"
                else:
                    genAuth = "aat"
                df.at[i, 'Genre'] = gen
                df.at[i, 'GenreAuthority'] = genAuth
        # type
        typ = soup.find('typeOfResource')
        if typ is not None:
            df.at[i, 'Type'] = typ.get_text().strip()

        # format
        frmat = soup.find('internetMediaType')
        if frmat is not None:
            df.at[i, 'internetMediaType'] = frmat.getText().strip()

        # FIXED - Now detects both Language1 and Language2
        # language
        lang = soup.find_all('languageTerm')
        for x in range(len(lang)):
            df.at[i, 'Language%d' % (x+1)] = lang[x].getText().strip()

        # identifiers
        ai = soup.find('identifier', {'type': 'access'})
        if ai is not None:
            df.at[i, 'AccessIdentifier'] = ai.getText().strip()
        li = soup.find('identifier', {'type': 'local'})
        if li is not None:
            df.at[i, 'LocalIdentifier'] = li.getText().strip()

        # source
        src = soup.find('physicalLocation')
        if src is not None:
            df.at[i, 'Source'] = src.getText().strip()

        # rights
        rights = soup.find('accessCondition', {'displayLabel': 'Restricted'})
        if rights is not None:
            df.at[i, 'Rights'] = rights.getText().strip()
        rightsStmt = soup.find('accessCondition', {'displayLabel': 'Rights Statement'})
        if rightsStmt is not None:
            df.at[i, 'RightsStatement'] = rightsStmt.getText().strip()
        ccl = soup.find('accessCondition', {'displayLabel': 'Creative Commons license'})
        if ccl is not None:
            df.at[i, 'CreativeCommons_URI'] = ccl.getText().strip()

        #        relatedItem
        hostTitle = soup.select('relatedItem[type=host] > titleInfo > title')
        hostPID = soup.select('relatedItem[type=host] > identifier')
        if len(hostTitle) > 0:
            df.at[i, 'relatedItem_Title'] = hostTitle[0].getText()
        if len(hostPID) > 0:
            df.at[i, 'relatedItem_PID'] = hostPID[0].getText()

        i = i + 1
        reset()  # Reset mappings for next file

    save(df, os.path.join(output_folder, output_file))
    print(df)

