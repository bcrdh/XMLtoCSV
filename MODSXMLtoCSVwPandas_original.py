import os
import pandas as pd
from bs4 import BeautifulSoup
import glob
from numba.tests.test_types import gen
#updated for **Rev 18.5 of the Master Metadata Sheet**


col_names =  ['key','PID', 'Filename','Directory','child_key','Title', 'AlternativeTitle', 'Creator1_Given','Creator1_Family', 'Creator2_Given','Creator2_Family', 'Creator3_Given','Creator3_Family']
col_names += ['CorporateCreator','Contributor1_Given','Contributor1_Family','CorporateContributor','Publisher_Original','DateCreated','Description','Extent','Subject1_Topic','Subject2_Topic','Subject3_Topic','Subject4_Topic','Subject5_Topic']
col_names += ['Subject_Geographic','Coordinates','Subject1_Given','Subject1_Family','Subject2_Given','Subject2_Family','Subject3_Given','Subject3_Family','CorporateSubject_1','CorporateSubject_2']
col_names += ['dateRange','Genre','GenreAuthority','Type','internetMediaType','Language1','Language2','Notes','AccessIdentifier','LocalIdentifier','ISBN','Classification','URI']
col_names += ['Source','Rights','CreativeCommons_URI','RightsStatement','relatedItem_Title','relatedItem_pid','recordCreationDate','recordOrigin']

dirList = []

path = r"C:\\Users\sharo\Desktop\frak"
for i in os.scandir(path):
    if i.is_dir():
        dirList.append(i.path)
for d in dirList:
    print(d)
    repCol = d.split('/')
    beg = len(path) + 1
    repCol = d[beg:]
    print(repCol)

    repo = repCol.split("_")[0]
    df  = pd.DataFrame(columns = col_names)
    df.append(pd.Series(), ignore_index=True)
    i = 0
    for filename in glob.iglob(os.path.join(d, '*.xml')):
        
        fnames = filename.split('\\')
        objIDpts = fnames[7].split("_")
        num = objIDpts[1].split(".")[0]

        def multiHdgMkr(pt1, num, pt2):
            return(pt1 + str(num) + '_' + pt2)
       
        infile = open(filename,"r",encoding="utf8")
        contents = infile.read()
        soup = BeautifulSoup(contents,'xml')

        #Arca PID
        pid = fnames[7].replace(".xml","")
        objNum = pid.split("_")[1]
        pid = repo + ":" + objNum
        df.at[i, 'PID'] = pid.strip()
        
        #Link to Image
        df.at[i, 'ImageLink'] = "https://doh.arcabc.ca/islandora/object/" + repo + "%3A" + objNum
    
        #alternativeTitle
        if soup.find('titleinfo',{'type':'Alternative'}):
            at = soup.find('titleinfo',{'type':'Alternative'}).getText()
            df.at[i, 'AlternativeTitle']=at.strip()
        #date and title
        if soup.find('dateIssued'):
            dateCr = soup.find('dateIssued').getText().strip()
        else:
            dateCr = "n.d."
        df.at[i, 'DateCreated'] = dateCr
    
        title=soup.find('title').get_text().strip()
        print(soup.find('dateIssued',{'qualifier':'Estimated'}))
        print(soup.find('dateIssued',{'qualifier':'approximate'}))
        print(title.find("ca."))
        print(dateCr)
              
        if (soup.find('dateIssued',{'qualifier':'Estimated'}) != None or soup.find('dateIssued',{'qualifier':'approximate'}) != None) and title.find("ca. ")==-1 and dateCr != "n.d.":
            title = title.strip() + ", ca. " + dateCr
    
        df.at[i, 'Title']=title
        
    #description    
        descr = soup.find('abstract')
        if descr:
            df.at[i, 'Description'] = descr.getText().strip()
    
    #extent
        ext = soup.find('extent')
        if ext:
            extent = ext.get_text().strip()
            semicol = extent.find(";")
            if semicol > -1:
                    extent = extent[:semicol -1]
            df.at[i, 'Extent'] = extent
           
    #topical subjects
        toptags = soup.find_all('topic')
        tsc = 0 #topical subject count
        if len(toptags) > 0:
            for top in toptags:
                tsc += 1
                fieldname = multiHdgMkr('Subject', tsc, 'Topic')
                df.at[i, fieldname] = top.getText().strip()
    
    #corporate subject   
        #corpsu = soup.findAll(corpSub)
        corpsu = soup.select('subject > name[type=corporate]')
        if len(corpsu) > 0:
            df.at[i, 'CorporateSubject_1'] = corpsu[0].getText().strip()
        if len(corpsu) > 1:
            df.at[i, 'CorporateSubject_2'] = corpsu[1].getText().strip()
    
        corpCC = soup.select('mods > name[type=corporate]')
        cCreator = None
        cContrib = None
        for corp in corpCC:
            if corp.find('roleTerm',string="creator"):
                cCreator = corp.find('namePart').getText()
            elif corp.find('roleTerm',string="contributor"):
                cContrib = corp.find('namePart').getText()
            
    #corporate creator
        #cCr = soup.findAll(corpCr)
        if cCreator != None:
            df.at[i, 'CorporateCreator']  = cCreator.strip()
    
    #corporate contributor
        if cContrib != None:
            df.at[i, 'CorporateContributor'] = cContrib.strip()
    
    #geographic subject
        geogSub = soup.find('geographic')
        if geogSub != None:    
            df.at[i, 'Subject_Geographic'] = geogSub.getText().strip()
        
    #coordinates
        coords = soup.find('coordinates')
        if coords != None:
            df.at[i, 'Coordinates'] = coords.getText().strip() 
            
    #personal creators and contributors (can have up to 3 creators, 1 contributor)
        pers = soup.select('mods > name[type=personal]')
        pCreators = []
        pContrib = None
        if pers !=None:
            for p in pers:
                if p.find('roleTerm',string="creator"):
                    pCreators.append(p)
                elif p.find('roleTerm',string="contributor"):
                    pContrib = p
        #role = "creator"
        pcCount = 0 #personal creator count
        if len(pCreators)>0:
            for nm in pCreators:
                pcCount += 1
                given = nm.find('namePart',{'type':'given'})
                family = nm.find('namePart',{'type':'family'})
            if given != None:
                fld = multiHdgMkr("Creator", pcCount, 'Given')
                df.at[i, fld] = given.getText().strip()
            if family != None:
                fld = multiHdgMkr("Creator", pcCount, 'Family')
                df.at[i, fld] = family.getText().strip()
            
    #personal contributors (max 1 per new guidelines)
        given = None
        family = None
        if pContrib != None:
            given = pContrib.find('namePart',{'type':'given'})
            family = pContrib.find('namePart',{'type':'family'})
        if given != None:
            fld = "Contributor1_Given"
            df.at[i, fld] = given.getText().strip()    
        if family != None:
            fld='Contributor1_Family'
            df.at[i, fld] = given.getText().strip()
        
    #personal name subjects (find number)
        psCount = 0 #personal subject count
        perSubs = []
        perSubs = soup.select('subject > name[type=personal]')
        if len(perSubs) > 0:
            for nm in perSubs:
                psCount += 1
                given = nm.find('namePart',{'type':'given'})
                if given != None:
                    fld = multiHdgMkr("Subject", psCount, 'Given')
                    df.at[i, fld] = given.getText().strip()
                family = nm.find('namePart',{'type':'family'})
                if family != None:
                    fld = multiHdgMkr("Subject", psCount, 'Family')
                    df.at[i, fld] = family.getText().strip()
    
        #genre    
        genre = soup.find('genre')
        if genre != None:
            gen = genre.getText().strip()
            df.at[i, 'Genre'] = gen
            auth = soup.find("td", {"valign" : True})
            if genre != None:
                genAuth = ""
                auth = soup.find("genre", {"authority" : "marcgt"})
                if auth != None:
                    genAuth = "marcgt"
                else:
                    genAuth = "aat"
                df.at[i, 'Genre'] = gen
                df.at[i, 'GenreAuthority'] = genAuth
        #type
        typ = soup.find('typeOfResource')
        if typ != None:
            df.at[i, 'Type'] = typ.get_text().strip()
    
        #format
        frmat = soup.find('internetMediaType')
        if frmat != None:
            df.at[i, 'internetMediaType'] = frmat.getText().strip()
        
        #language
        lang = soup.find('languageTerm')
        if lang != None:
            df.at[i, 'Language1'] = lang.getText().strip()
    
        #identifiers
        ai = soup.find('identifier',{'type':'access'})
        if ai !=None:
            df.at[i, 'AccessIdentifier'] = ai.getText().strip()
        li = soup.find('identifier',{'type':'local'})
        if li != None:
            df.at[i, 'LocalIdentifier'] = li.getText().strip()
            
        #source
        src = soup.find('physicalLocation')
        if src != None:
            df.at[i, 'Source'] = src.getText().strip()
    
        #rights
        rights = soup.find('accessCondition',{'displayLabel':'Restricted'})
        if rights != None:
            df.at[i, 'Rights'] = rights.getText().strip()
        rightsStmt = soup.find('accessCondition',{'displayLabel':'Rights Statement'})
        if rightsStmt != None:
            df.at[i, 'RightsStatement'] = rightsStmt.getText().strip()
        ccl = soup.find('accessCondition',{'displayLabel':'Creative Commons license'})
        if ccl != None:
            df.at[i, 'CreativeCommons_URI'] = ccl.getText().strip() 
        
#        relatedItem
        hostTitle = soup.select('relatedItem[type=host] > titleInfo > title')
        if len(hostTitle) > 0:
            df.at[i, 'relatedItem_Title'] = hostTitle[0].getText()
        clcn = repCol
        df.at[i, 'relatedItem_pid'] = clcn.replace("_",":")
        lastRepCol = repCol
        i = i + 1
            
    file_name = repCol + ".csv"
    savePath = r'C:/Users/sharo/Desktop' + '/'
    dest = os.path.join(savePath,file_name)
    df.to_csv(dest, encoding='utf-8', index=False)
    print("Wrote " + file_name +".")
