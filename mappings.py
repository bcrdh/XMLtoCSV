import os
import re


def generic_find(soup, field: str):
    """
    Generic find on the soup
    :param soup: the bs4 object
    :param field: the tag name to search for
    :return: the value stripped if found, else None
    """
    value = soup.find(field)
    return value.getText().strip() if value else None


def generic_select(soup, selector: str):
    """
    Generic select on the soup
    :param soup:  the bs4 object
    :param selector: the selector string (css selectors)
    :return: the FIRST value stripped if found, else None
    """
    result = soup.select(selector)
    return result[0].getText().strip() if len(result) > 0 else None


def date_created(soup):
    """
    Generates CSV->XML DateCreated mapping
    :param soup: the bs4 object
    :return: date value as str
    """
    pattern1 = r'^[A-Z][a-z]{2}-\d{2}$'  # %b-%Y date (e.g. Jun-17)
    pattern2 = r'^\d{2}-\d{2}-[1-2]\d{3}$'  # %d-%m-%Y date (e.g. 21-01-1917)
    if soup.find('dateIssued'):
        date_cr = soup.find('dateIssued').getText().strip()
    else:
        date_cr = "n.d."

    from logic import convert_date  # For checking dates

    # Fix badly formatted dates (either of the two patterns declared above will be fixed)
    if re.match(pattern1, date_cr):
        date_cr = convert_date(date_cr, True)
    elif re.match(pattern2, date_cr):
        date_cr = convert_date(date_cr, False)

    return date_cr


def key(i: int):
    """
    The key (basically row num) of current MODS in CSV
    :param i: the for loop index int i
    :return: the appropriate key to put in CSV
    """
    return str(i + 1)


def get_repo_num(filename: str):
    """
    Gets the repo and num from the filename
    :param filename: the filename
    :return: repo, num as tuple
    """
    # Identify the repo and num from the filename in the path
    path_splitted = filename.split(os.sep)
    # Get last index of split (i.e. the filename) and split
    obj_i_dpts = path_splitted[-1].rstrip('.xml').split("_")
    repo = obj_i_dpts[0]
    num = obj_i_dpts[1]

    return repo, num


def pid(filename: str):
    """
    Generates CSV->XML key mapping
    :param soup: the bs4 object
    :param filename: the MODS XML filename
    :return: the pid of the MODS
    """
    repo, num = get_repo_num(filename)
    return '%s_%s' % (repo, num)


def image_link(filename: str):
    """
    Generates the imagelink given the filename
    :param filename: the MODS XML filename
    :return: the image link
    """
    repo, num = get_repo_num(filename)
    return "https://doh.arcabc.ca/islandora/object/" + repo + "%3A" + num


def alternative_title(soup):
    """
    Generates alternative title for given MODS XML
    :param soup: the bs4 object
    :return: str if exists, else None
    """
    alt_title = soup.select('titleInfo[type="alternative"] > title')
    if len(alt_title) > 0:
        at = alt_title[0].getText()
        return at.strip()
    else:
        return None


def title(soup):
    """
    Generates title from MODS XML
    :param soup: the bs4 object
    :return: the title as str
    """
    _title = soup.find('title').get_text().strip()
    date_cr = date_created(soup)
    if (soup.find('dateIssued', {'qualifier': 'Estimated'}) is not None or
        soup.find('dateIssued', {'qualifier': 'approximate'}) is not None) and \
            _title.find("ca. ") == -1 and date_cr != "n.d.":
        _title = _title.strip() + ", ca. " + date_cr

    return _title


def description(soup):
    """
    Gets the description from the MODS XML file
    :param soup: the bs4 object
    :return: str if found, else None
    """
    _description = soup.find('abstract')
    return _description.getText().strip() if _description else None


def extent(soup):
    """
    Gets the extent from MODS XML file
    :param soup: the bs4 object
    :return: str if found, else None
    """
    ext = soup.find('extent')
    if ext:
        ext = ext.get_text().strip()
        semicol = ext.find(";")
        ext = ext[:semicol-1] if semicol > -1 else ext
        return ext
    else:
        return None


subject_topic_store = {}  # Store subject topics to avoid searching again


def subject_topic(soup, field: str):
    """
    Gets the subject topic from the MODS XML file
    :param soup: the bs4 object
    :param field: the field e.g. Subject1_Topic, Subject2_Topic, ..., Subject5_Topic
    :return: the field value if it exists, else None
    """
    if len(subject_topic_store) == 0:
        top_tags = soup.find_all('topic')
        tsc = 0  # topical subject count
        if len(top_tags) > 0:
            for top in top_tags:
                tsc += 1
                field_name = 'Subject%d_Topic' % tsc
                subject_topic_store[field_name] = top.getText().strip()

    return subject_topic_store[field] if field in subject_topic_store else None


def subject1_topic(soup):
    return subject_topic(soup, 'Subject1_Topic')


def subject2_topic(soup):
    return subject_topic(soup, 'Subject2_Topic')


def subject3_topic(soup):
    return subject_topic(soup, 'Subject3_Topic')


def subject4_topic(soup):
    return subject_topic(soup, 'Subject4_Topic')


def subject5_topic(soup):
    return subject_topic(soup, 'Subject5_Topic')


corporate_subject_store = {}  # Store corporate subjects to avoid searching again


def corporate_subject(soup, field: str):
    """
    Gets the corporate subject from the MODS XML file
    :param soup: the bs4 object
    :param field: the field e.g. CorporateSubject_1, CorporateSubject_2
    :return: the field value if it exists, else None
    """
    if len(corporate_subject_store) == 0:
        corp_sub = soup.select('subject > name[type=corporate]')
        if len(corp_sub) > 0:
            for x in range(len(corp_sub)):
                corporate_subject_store['CorporateSubject_%d' % (x+1)] = \
                    corp_sub[x].getText().strip()

    return corporate_subject_store[field] if field in corporate_subject_store else None


def corporate_subject_1(soup):
    return corporate_subject(soup, 'CorporateSubject_1')


def corporate_subject_2(soup):
    return corporate_subject(soup, 'CorporateSubject_2')


def corporate_finder(soup, role_term: str):
    """
    Finds either a corporate creator or contributor depending on role term
    :param soup: the bs4 object
    :param role_term: the role term ("creator" or "contributor")
    :return: str if found, else None
    """
    corp_cc = soup.select('mods > name[type=corporate]')
    result = None
    for corp in corp_cc:
        if corp.find('roleTerm', string=role_term):
            result = corp.find('namePart').getText().strip()

    return result


def corporate_creator(soup):
    return corporate_finder(soup, "creator")


def corporate_contributor(soup):
    return corporate_finder(soup, "contributor")


def subject_geographic(soup):
    """
    Finds the geographic field in MODS XML
    :param soup: the bs4 object
    :return: str if found, else None
    """
    geog_elems = soup.find_all('geographic')
    geog_sub = None
    for el in geog_elems:
        # Make sure its not the <geographic> tag from Coordinates
        if len(el.findChildren('cartographics')) == 0:
            geog_sub = el
            break

    return geog_sub


def publisher_original(soup):
    """
    Finds the publisher from the MODS XML file
    :param soup: the bs4 object
    :return: str if found, else None
    """
    return generic_find(soup, 'publisher')


def date_range(soup):
    """
    Finds the daterange from the MODS XML file
    :param soup: the bs4 object
    :return: str if found, else None
    """
    return generic_find(soup, 'temporal')


def notes(soup):
    """
    Finds the notes from the MODS XML file
    :param soup: the bs4 object
    :return: str if found, else None
    """
    return generic_find(soup, 'note')


def isbn(soup):
    """
    Finds the ISBN from the MODS XML file
    :param soup: the bs4 object
    :return: str if found, else None
    """
    return generic_select(soup, 'identifier[type="isbn"]')


def classification(soup):
    """
    Finds classification from the MODS XML file
    :param soup: the bs4 object
    :return: str if found, else None
    """
    return generic_find(soup, 'classification')


def uri(soup):
    """
    Finds URI from the MODS XML file
    :param soup: the bs4 object
    :return: str if found, else None
    """
    return generic_select(soup, 'identifier[type="uri"]')


def record_origin(soup):
    """
    Finds the record creation date in the MODS XML file
    :param soup: the bs4 object
    :return: str if found, else None
    """
    return generic_find(soup, 'recordOrigin')


def record_creation_date(soup):
    """
    Finds the record creation date from the MODS XML file
    :param soup: the bs4 object
    :return: str if found, else None
    """
    return generic_find(soup, 'recordCreationDate')


def coordinates(soup):
    """
    Finds the coordinates from the MODS XML file
    :param soup: the bs4 object
    :return: str if found, else None
    """
    return generic_find(soup, 'cartographics')


creator_family_store = {}  # store to avoid searching again
creator_given_store = {}  # store to avoid searching again


def populate_creators(soup):
    """
    Finds creator families and given and puts into store
    :param soup: the bs4 object
    :return: None
    """
    pers = soup.select('mods > name[type=personal]')
    if pers is not None:
        x = 1
        for p in pers:
            if p.find('roleTerm', string="creator"):
                # p_creators.append(p)
                given = p.find('namePart', {'type': 'given'})
                family = p.find('namePart', {'type': 'family'})

                if given and family:
                    creator_given_store['Creator%d_Given' % x] = \
                        given.getText().strip()
                    creator_family_store['Creator%d_Family' % x] = \
                        family.getText().strip()
                    x += 1


def creator_family(soup, field):
    """
    Finds creator family given the field
    :param soup: the bs4 object
    :param field: the field e.g. Creator1_Family, Creator2_Family, etc.
    :return: the str if found, else None
    """
    if len(creator_family_store) == 0:
        populate_creators(soup)

    return creator_family_store[field] if field in creator_family_store else None


def creator1_family(soup):
    return creator_family(soup, 'Creator1_Family')


def creator2_family(soup):
    return creator_family(soup, 'Creator2_Family')


def creator3_family(soup):
    return creator_family(soup, 'Creator3_Family')


def creator_given(soup, field):
    """
    Finds the creator given given the field
    :param soup: the bs4 object
    :param field: the field e.g. Creator1_Given, Creator2_Given, etc.
    :return: str if found, else None
    """
    if len(creator_given_store) == 0:
        populate_creators(soup)

    return creator_given_store[field] if field in creator_given_store else None


def creator1_given(soup):
    return creator_given(soup, 'Creator1_Given')


def creator2_given(soup):
    return creator_given(soup, 'Creator2_Given')


def creator3_given(soup):
    return creator_given(soup, 'Creator3_Given')


def reset():
    """
    Resets variables for next file
    :return: None
    """
    subject_topic_store.clear()
    corporate_subject_store.clear()
    creator_family_store.clear()
    creator_given_store.clear()


mappings = {
    'DateCreated': date_created,
    'key': key,
    'PID': pid,
    'imageLink': image_link,
    'AlternativeTitle': alternative_title,
    'Title': title,
    'Description': description,
    'Extent': extent,
    'Subject1_Topic': subject1_topic,
    'Subject2_Topic': subject2_topic,
    'Subject3_Topic': subject3_topic,
    'Subject4_Topic': subject4_topic,
    'Subject5_Topic': subject5_topic,
    'CorporateSubject_1': corporate_subject_1,
    'CorporateSubject_2': corporate_subject_2,
    'CorporateCreator': corporate_creator,
    'CorporateContributor': corporate_contributor,
    'Subject_Geographic': subject_geographic,
    'Publisher_Original': publisher_original,
    'DateRange': date_range,
    'Notes': notes,
    'ISBN': isbn,
    'Classification': classification,
    'URI': uri,
    'recordOrigin': record_origin,
    'recordCreationDate': record_creation_date,
    'Coordinates': coordinates,
    'Creator1_Family': creator1_family,
    'Creator1_Given': creator1_given,
    'Creator2_Family': creator2_family,
    'Creator2_Given': creator2_given,
    'Creator3_Family': creator3_family,
    'Creator3_Given': creator3_given
}
