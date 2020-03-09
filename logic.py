import os
import pandas as pd
from bs4 import BeautifulSoup
import glob
import datetime
import re


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

    pattern1 = r'^[A-Z][a-z]{2}-\d{2}$'  # %b-%Y date (e.g. Jun-17)
    pattern2 = r'^\d{2}-\d{2}-[1-2]\d{3}$'  # %d-%m-%Y date (e.g. 21-01-1917)

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

        if soup.find('dateIssued'):
            date_cr = soup.find('dateIssued').getText().strip()
        else:
            date_cr = "n.d."

        # Fix badly formatted dates (either of the two patterns declared above will be fixed)
        if re.match(pattern1, date_cr):
            date_cr = convert_date(date_cr, True)
        elif re.match(pattern2, date_cr):
            date_cr = convert_date(date_cr, False)

        # Set DateCreated column
        df.at[i, 'DateCreated'] = date_cr

        # Identify the repo and num from the filename in the path
        path_splitted = filename.split(os.sep)
        # Get last index of split (i.e. the filename) and split
        obj_i_dpts = path_splitted[-1].rstrip('.xml').split("_")
        repo = obj_i_dpts[0]
        num = obj_i_dpts[1]

        # Key
        df.at[i, 'key'] = str(i+1)

        # Arca PID
        pid = repo + '_' + num
        df.at[i, 'PID'] = pid.strip()

        # Link to Image
        df.at[i, 'imageLink'] = "https://doh.arcabc.ca/islandora/object/" + repo + "%3A" + num

        # alternativeTitle
        #fixed: change titleinfo, type: Alternative
        #       to     titleInfo, type: alternative
        alt_title = soup.select('titleInfo[type="alternative"] > title')
        if len(alt_title) > 0:
            at = alt_title[0].getText()
            df.at[i, 'AlternativeTitle'] = at.strip()
        #     #date and title
        #     if soup.find('dateIssued'):
        #         date_cr = soup.find('dateIssued').getText().strip()
        #     else:
        #         date_cr = "n.d."
        #
        #     if (re.match(pattern1, date_cr)):
        #         date_cr = convertDate(date_cr, True)
        #     elif (re.match(pattern2, date_cr)):
        #         date_cr = datetime.datetime.strptime(date_cr,'%d-%m-%Y').strftime('%Y-%m-%d')
        #     df.at[i, 'DateCreated'] = date_cr
        title = soup.find('title').get_text().strip()
        # print(soup.find('dateIssued',{'qualifier':'Estimated'}))
        # print(soup.find('dateIssued',{'qualifier':'approximate'}))
        # print(title.find("ca."))
        # print(date_cr)

        # unsure
        if (soup.find('dateIssued', {'qualifier': 'Estimated'}) is not None or soup.find('dateIssued', {
            'qualifier': 'approximate'}) is not None) and title.find("ca. ") == -1 and date_cr != "n.d.":
            title = title.strip() + ", ca. " + date_cr

        df.at[i, 'Title'] = title

        # unsure - what about abstract for Newspaper obj?
        # description
        descr = soup.find('abstract')
        if descr:
            df.at[i, 'Description'] = descr.getText().strip()

        # extent
        ext = soup.find('extent')
        if ext:
            extent = ext.get_text().strip()
            semicol = extent.find(";")
            if semicol > -1:
                extent = extent[:semicol - 1]
            df.at[i, 'Extent'] = extent

        # topical subjects
        toptags = soup.find_all('topic')
        tsc = 0  # topical subject count
        if len(toptags) > 0:
            for top in toptags:
                tsc += 1
                fieldname = multi_hdg_mkr('Subject', tsc, 'Topic')
                df.at[i, fieldname] = top.getText().strip()

        # corporate subject
        # corpsu = soup.findAll(corpSub)
        corpsu = soup.select('subject > name[type=corporate]')
        if len(corpsu) > 0:
            df.at[i, 'CorporateSubject_1'] = corpsu[0].getText().strip()
        if len(corpsu) > 1:
            df.at[i, 'CorporateSubject_2'] = corpsu[1].getText().strip()

        corpCC = soup.select('mods > name[type=corporate]')
        cCreator = None
        cContrib = None
        for corp in corpCC:
            if corp.find('roleTerm', string="creator"):
                cCreator = corp.find('namePart').getText()
            elif corp.find('roleTerm', string="contributor"):
                cContrib = corp.find('namePart').getText()

        # corporate creator
        # cCr = soup.findAll(corpCr)
        if cCreator is not None:
            df.at[i, 'CorporateCreator'] = cCreator.strip()

        # corporate contributor
        if cContrib is not None:
            df.at[i, 'CorporateContributor'] = cContrib.strip()

        # geographic subject
        geog_elems = soup.find_all('geographic')
        geog_sub = None
        for el in geog_elems:
            # Make sure its not the <geographic> tag from Coordinates
            if len(el.findChildren('cartographics')) is 0:
                geog_sub = el
                break

        if geog_sub is not None:
            df.at[i, 'Subject_Geographic'] = geog_sub.getText().strip()

        # ADDED
        # publisher_original
        publisher = soup.find('publisher')
        if publisher is not None:
            df.at[i, 'Publisher_Original'] = publisher.getText().strip()

        # ADDED
        # dateRange
        date_range = soup.find('temporal')
        if date_range is not None:
            df.at[i, 'DateRange'] = date_range.getText().strip()

        # ADDED
        # notes
        notes = soup.find('note')
        if notes is not None:
            df.at[i, 'Notes'] = notes.getText().strip()

        # ADDED
        # isbn
        isbn = soup.select('identifier[type="isbn"]')
        if len(isbn) > 0:
            df.at[i, 'ISBN'] = isbn[0].getText().strip()

        # ADDED
        # classification
        classification = soup.find('classification')
        if classification is not None:
            df.at[i, 'Classification'] = classification.getText().strip()

        # ADDED
        # URI
        uri = soup.select('identifier[type="uri"]')
        if len(uri) > 0:
            df.at[i, 'URI'] = uri[0].getText().strip()

        # ADDED
        # recordCreationDate & recordOrigin
        record_origin = soup.find('recordOrigin')
        record_creation_date = soup.find('recordCreationDate')
        if record_origin is not None and record_creation_date is not None:
            df.at[i, 'recordCreationDate'] = record_creation_date.getText().strip()
            df.at[i, 'recordOrigin'] = record_origin.getText().strip()


        # FIXED
        # coordinates
        coords = soup.find('cartographics')
        if coords is not None:
            df.at[i, 'Coordinates'] = coords.getText().strip()

        # personal creators and contributors (can have up to 3 creators, 1 contributor)
        pers = soup.select('mods > name[type=personal]')
        pCreators = []
        if pers is not None:
            for p in pers:
                if p.find('roleTerm', string="creator"):
                    pCreators.append(p)


        # role = "creator"
        pcCount = 0  # personal creator count
        if len(pCreators) > 0:
            for nm in pCreators:
                pcCount += 1
                given = nm.find('namePart', {'type': 'given'})
                family = nm.find('namePart', {'type': 'family'})
            if given is not None:
                fld = multi_hdg_mkr("Creator", pcCount, 'Given')
                df.at[i, fld] = given.getText().strip()
            if family is not None:
                fld = multi_hdg_mkr("Creator", pcCount, 'Family')
                df.at[i, fld] = family.getText().strip()

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

    save(df, os.path.join(output_folder, output_file))
    print(df)

