from flask import Flask, send_from_directory, send_file, request
from datetime import datetime
import requests
import json
import pandas as pd
import os
import urllib.request
import ssl
import subprocess
import re
import io
import math

app = Flask(__name__)

#notes

def getCreds():
    p = subprocess.Popen('node scrape.js', shell=True)
    p
    return p
    

def getJson():
    with open('./creds.json', 'r') as creds:
        return json.load(creds)
def head():
    access=getJson()['accessToken']
    token=getJson()['dtToken']
    auth= 'Bearer '+ access
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'Authorization': auth,
        'Ocp-Apim-Subscription-Key': '3abfb6b50e7140cfafc89e1d28030710',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
        'DTToken': token,
        'Content-Type': 'application/json; charset=utf-8',
        'Sec-GPC': '1',
        'Origin': 'https://d-tools.cloud',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://d-tools.cloud/',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    return headers

paramsOpps = (
    ('stageIds', ['1502', '1503', '1504', '1505', '1506', '1509','1691', '1510']),
    ('ownerIds', ['3322', '3875', '3939', '1159', '3486', '3482', '5048', '4931']),
    ('resourceId', 'null'),
    ('datePeriod', 'undefined'),
    ('archived', 'null'),
    ('siManaged', 'null'),
    ('search', ''),
    ('fields', 'id, client, name, number, stage, stageId, stateId, budget, price, probability, estCloseDate, owner, ownerId, ownerImageUrl, resourceIds, archived, tasksCount, siManaged, siImported, siImportedOn'),
    ('sort', 'EstCloseDate DESC'),
    ('page', '1'),
    ('pageSize', '1000'),
    )
quotes = (
        ('quoteId', 'quoteId'),
        ('page', '1'),
        ('pageSize', '1000'),
        ('fields', 'id,typeId,name,shortName,quantity,shortDescription,image,imageUrl,unitCost,unitPrice,laborTime,category,categoryId,laborPrice,locationId,location,systemId,system,itemId,parentId,parentQuantity,hasAccessories,clientSupplied,discontinued,computedPrice,deleted,packageId,package,packageQuantity,packageItemId,synchronize,billable,lengthBased,length,dtin,phaseId,phase,productPrice,productCost,laborCost,uniqueId,alternateSet,alternateSetId,categoryId,supplierId,supplier,laborTypeId,taxable'),
        ('sort', 'LocationOrder,SystemOrder,name'),
        ('search', ''),
        ('includeAccessories', 'true'),
        ('locationIds', 'locations'),
    )

###################################################################################################

@app.route('/api/opportunities', methods=['GET'])
def opportunities():
    print(getJson()['dtToken'])
    print(getJson()['accessToken'])
    headers = head()
    getOpportunities = requests.get('https://api.d-tools.cloud/Opportunity/api/v1/Opportunities/GetOpportunitiesByStages', headers=headers, params=paramsOpps).json()
    return json.dumps(getOpportunities)

###################################################################################################

@app.route('/api/getOpps/<oppId>', methods=['GET'])
def oppQuotes(oppId):
    
    headers = head()
    getOpps = requests.get('https://api.d-tools.cloud/Quote/api/v1/Quotes/GetQuotes?opportunityId='+oppId+'&stateIds=1&stateIds=2&stateIds=3',headers=headers).json()
    return json.dumps(getOpps)
    print(oppId)

###################################################################################################

@app.route('/api/getCreds', methods=['GET'])
def gettingCreds():
    
    getCreds()
    return 'Done'

###################################################################################################

@app.route('/api/getCatalog/<getSearch>', methods=['GET'])
def gettingCatalog(getSearch):
    
    headers = head()
    dt=pd.DataFrame()
    s=getSearch
    if s == 'initial':
        search = 'scope'
    else:
        search = getSearch
    page = 1
    m=True
    prod = 'https://api.d-tools.cloud/Catalog/api/v1/Products/GetProducts'
    date = datetime.now().strftime('%m%d%H%M%S')
    while m:
        params = (
        ('minPrice', 'null'),
        ('maxPrice', 'null'),
        ('amazon', 'null'),
        ('discontinued', 'null'),
        ('active', 'true'),
        ('search', search),
        ('facets', 'false'),
        ('fields', '*'),
        ('sort', 'brand'),
        ('page', page),
        ('pageSize', '1000'),
        )
        p = requests.get(prod,headers=headers, params=params).json()
        m = p['hasMoreProducts']      
        df = pd.DataFrame(p['products'])
        dt = pd.concat([dt,df], ignore_index=True)
    dt = dt.drop(['id','name','shortName','brandId','categoryId','imageUrl','lengthBased','length','msrpSetTypeId','unitCostSetTypeId','unitPriceSetTypeId','margin','markup','supplierId','supplier','dtin','imageUrl','createdOn','modifiedOn'], axis=1)
    dt.to_csv('/home/bill/Desktop/'+"DT-Export_"+date+".csv", index=False)
    out={}
    out[0]=date
    return out

###################################################################################################

@app.route('/api/getQuote/<quoteId>', methods=['GET'])
def index(quoteId):
    
    headers = head()
    loc = requests.get('https://api.d-tools.cloud/Quote/api/v1/QuoteLocations/GetQuoteLocations?quoteId='+quoteId, headers=headers).json()
    locs=pd.DataFrame(loc)
    locs = locs['id'].tolist() 


    quotes = (
            ('quoteId', quoteId),
            ('page', '1'),
            ('pageSize', '1000'),
            ('fields', 'id,typeId,name,shortName,quantity,shortDescription,image,imageUrl,unitCost,unitPrice,laborTime,category,categoryId,laborPrice,locationId,location,systemId,system,itemId,parentId,parentQuantity,hasAccessories,clientSupplied,discontinued,computedPrice,deleted,packageId,package,packageQuantity,packageItemId,synchronize,billable,lengthBased,length,dtin,phaseId,phase,productPrice,productCost,laborCost,uniqueId,alternateSet,alternateSetId,categoryId,supplierId,supplier,laborTypeId,taxable'),
            ('sort', 'LocationOrder,SystemOrder,name'),
            ('search', ''),
            ('includeAccessories', 'true'),
            ('locationIds', locs),
        )
    
    response = requests.get('https://api.d-tools.cloud/Quote/api/v1/QuoteItems/GetQuoteItems', headers=headers, params=quotes).json()
    df=pd.DataFrame(response['items'])
    df['brand']=df['itemId']
    df['part']=df['itemId']
    df['model']=df['itemId']
    lookP={}
    lookB={}
    lookM={}
    m=True
    page=1
    items=[]
    while m:
        params = (
        ('page', page),
        ('pageSize', '1000'),
        )
        p = requests.get('https://api.d-tools.cloud/Catalog/api/v1/Products/GetProducts',headers=headers, params=params).json()
        li=len(p['products'])
        i=0
        while i < li:
            prod=p['products'][i]
            itemId=prod['id']
            lookP[itemId]=prod['partNumber']
            lookB[itemId]=prod['brand']
            lookM[itemId]=prod['model']
            i +=1
        m = p['hasMoreProducts']
        page +=1
    df=df.replace(to_replace={'part':lookP,'model':lookM,'brand':lookB}, value=None)
    getQuoteInfo = requests.get('https://api.d-tools.cloud/Quote/api/v1/Quotes/GetQuoteData?id='+str(quoteId),headers=headers).json()
    
    clientName=getQuoteInfo['quote']['client']
    quoteName=getQuoteInfo['quote']['name']
    phases=False
    phaseName=''

    date = datetime.now().strftime('%m%d%H%M%S')
    convertPhases(df, locs, quoteId, lookP, lookB, lookM, phaseName, clientName, quoteName, headers, phases,date)
    out={}
    out[0]=date
    return out
    
###################################################################################################

@app.route('/api/getPhases/<quoteId>', methods=['GET'])
def phases(quoteId):
    
    headers = head()
    loc = requests.get('https://api.d-tools.cloud/Quote/api/v1/QuoteLocations/GetQuoteLocations?quoteId='+quoteId, headers=headers).json()
    locs=pd.DataFrame(loc)
    locs = locs['id'].tolist() 

    quotes = (
            ('quoteId', quoteId),
            ('page', '1'),
            ('pageSize', '1000'),
            ('fields', 'id,typeId,name,shortName,quantity,shortDescription,image,imageUrl,unitCost,unitPrice,laborTime,category,categoryId,laborPrice,locationId,location,systemId,system,itemId,parentId,parentQuantity,hasAccessories,clientSupplied,discontinued,computedPrice,deleted,packageId,package,packageQuantity,packageItemId,synchronize,billable,lengthBased,length,dtin,phaseId,phase,productPrice,productCost,laborCost,uniqueId,alternateSet,alternateSetId,categoryId,supplierId,supplier,laborTypeId,taxable'),
            ('sort', 'LocationOrder,SystemOrder,name'),
            ('search', ''),
            ('includeAccessories', 'true'),
            ('locationIds', locs),
        )
    
    response = requests.get('https://api.d-tools.cloud/Quote/api/v1/QuoteItems/GetQuoteItems', headers=headers, params=quotes).json()
    df=pd.DataFrame(response['items'])
    df['brand']=df['itemId']
    df['part']=df['itemId']
    df['model']=df['itemId']
    lookP={}
    lookB={}
    lookM={}
    m=True
    page=1
    items=[]
    while m:
        params = (
        ('page', page),
        ('pageSize', '1000'),
        )
        p = requests.get('https://api.d-tools.cloud/Catalog/api/v1/Products/GetProducts',headers=headers, params=params).json()
        li=len(p['products'])
        i=0
        while i < li:
            prod=p['products'][i]
            itemId=prod['id']
            lookP[itemId]=prod['partNumber']
            lookB[itemId]=prod['brand']
            lookM[itemId]=prod['model']
            i +=1
        m = p['hasMoreProducts']
        page +=1
        
    df=df.replace(to_replace={'part':lookP,'model':lookM,'brand':lookB}, value=None)
    phaseNames = df['phase'].unique()

    getQuoteInfo = requests.get('https://api.d-tools.cloud/Quote/api/v1/Quotes/GetQuoteData?id='+str(quoteId),headers=headers).json()
    clientName=getQuoteInfo['quote']['client']
    quoteName=getQuoteInfo['quote']['name']
    phases=True
    date = datetime.now().strftime('%m%d%H%M%S')
    out={}
    out[0]=date
    phaseNumber=1
    for phase in phaseNames:
        phaseName = phase
        df1= df[df.phase == phase]
        out[phaseNumber]=phaseName
        convertPhases(df1,locs,quoteId, lookP, lookB, lookM, phaseName,clientName,quoteName,headers,phases,date)
        phaseNumber+=1
    print(out)
    return out
    #return json.dumps(phaseNames.tolist())

###################################################################################################

app.config["DOWNLOAD"] = "/home/bill/Desktop"
@app.route('/api/download/<quoteId>', methods=['GET'])
def download(quoteId):
    return send_from_directory(app.config["DOWNLOAD"], filename=quoteId, as_attachment=True)

###################################################################################################
@app.route('/api/updatePricebook', methods=['POST'])
def updatepricebook():
    data = request.get_json()
    dt = data['dt']
    tp = data['tp']
    new = data['new']
    if not dt:
        out = {'error':'No D-Tools Pricing'}
        return out
    elif not tp:
        out = {'error':'No TigerPaw Pricing'}
        return out
    elif not new:
        out = {'error':'No New Pricing'}
        return out
    else:
        download = '&download=1'
        getDT = requests.get(dt+download)
        getTP = requests.get(tp+download)
        getNEW = requests.get(new+download)
        dtools = pd.read_csv(io.StringIO(getDT.text))
        new = pd.read_csv(io.StringIO(getNEW.text))
        with io.BytesIO(getTP.content) as fh:
            tigerpaw = pd.io.excel.read_excel(fh)
        name = dtools['brand'][0]
        date = datetime.now().strftime('%m%d%H%M%S')
        filename = f'{name}_{date}.csv'
        out = {'download':filename, 'name':name}

        price(filename,dtools, new, tigerpaw)
        


        return out
###################################################################################################

def price(filename,dtools, new, tigerpaw):
    def roundup(x):
        if x == 0:
            return 0
        elif x < 5:
            return 5
        else:
            return int(math.ceil((x -.99)/ 10.0)) * 10-1

    dtools[['PB Category','PB Subcategory']] = dtools.category.str.split(' > ', expand=True)
    dtools.drop(['category','quantity', 'msrp','partNumber'], axis=1, inplace=True)
    dtools['PB Item ID'] = dtools['brand']+ ':'+ dtools['model']
    tigerpaw[['PB Manufacturer','PB Part No.']] = tigerpaw['PB Item ID'].str.split(':',expand=True)
    tigerpaw['PB Part No.'] = tigerpaw['PB Part No.'].str.upper()


    dtools.rename({'brand':'PB Manufacturer', 'model':'PB Part No.', 'shortDescription':'PB Key Description',
                    'unitCost':'PB Standard Cost', 'unitPrice':'PB Mfg. List',
                'discontinued':'PB Inactive', 'active':'PB Item Status'}, axis=1, inplace=True)   

    new['PB Item ID'] = new['PB Manufacturer'] + ':' + new['PB Part No.']
    dtools['PB Part No.'] = dtools['PB Part No.'].str.upper()
    new['PB Part No.'] = new['PB Part No.'].str.upper()

    tigerpawParts= tigerpaw['PB Part No.']
    dtoolsParts = dtools['PB Part No.']
    newParts = new['PB Part No.']

    #D-Tools parts not in TigerPaw
    dtNotInTp = dtools[~dtools['PB Part No.'].isin(tigerpawParts)]

    #TigerPaw parts not in D-Tools
    tpNotInDt = tigerpaw[~tigerpaw['PB Part No.'].isin(dtoolsParts)]

    # update TigerPaw with D-Tools Matching 

    for i, row in tigerpaw.iterrows():
        tpPart = row['PB Part No.']
        for x, rowDt in dtools.iterrows():
            dtPart = rowDt['PB Part No.']
            dtDesc = rowDt['PB Key Description']
            dtPrice = rowDt['PB Mfg. List']
            dtCost = rowDt['PB Standard Cost']
            dtCat = rowDt['PB Category']
            dtSubCat = rowDt['PB Subcategory']
            if tpPart == dtPart:
                tigerpaw.loc[i,'PB Mfg. List'] = dtPrice
                tigerpaw.loc[i,'PB Key Description'] = dtDesc
                tigerpaw.loc[i,'PB Standard Cost'] = dtCost
                tigerpaw.loc[i,'PB Category'] = dtCat
                tigerpaw.loc[i,'PB Subcategory'] = dtSubCat

    #Add new D-Tools parts to TigerPaw
    tpNew = pd.concat([tigerpaw,dtNotInTp],sort=False)
    tpNew = tpNew.reset_index(drop=True)
    #Check if part is in new pricelist
    tpNew['PB Inactive'] = True
    tpNew['PB Item Status'] = 'Discontinued'
    for x, rowNew in new.iterrows():
        newPart1 = rowNew['PB Part No.']
        for i, row in tpNew.iterrows():
            tpNewPart = row['PB Part No.']        
            if newPart1 == tpNewPart:
                #print(tpNewPart)
                tpNew.loc[i,'PB Inactive'] = False
                tpNew.loc[i,'PB Item Status'] = 'Active'

    # update TigerPaw with New Matching 
    tpNew['PB Key Description'] = tpNew['PB Key Description'].fillna(' ')
    for i, row in tpNew.iterrows():
        tpPart = row['PB Part No.']
        tpDesc = row['PB Key Description']
        tpPrice = row['PB Mfg. List']
        tpCost = row['PB Standard Cost']
        for x, rowNew in new.iterrows():
            newPart = rowNew['PB Part No.']
            newDesc = rowNew['PB Key Description']
            newPrice = rowNew['PB Mfg. List']
            newCost = rowNew['PB Standard Cost']
            newUOM = rowNew['PB UOM']
            if tpPart == newPart:
                tpNew.loc[i,'PB Mfg. List'] = newPrice
                tpNew.loc[i,'PB Standard Cost'] = newCost
                tpNew.loc[i,'PB UOM'] = newUOM
                if tpDesc == ' ':
                    tpNew.loc[i,'PB Key Description'] = newDesc

    #TigerPaw parts not in D-Tools
    tigerpawCombinedParts= tpNew['PB Part No.']
    newNotInTp = new[~new['PB Part No.'].isin(tigerpawCombinedParts)]
    for i, row in new.iterrows():
        part=row['PB Part No.']
        for x, row in newNotInTp.iterrows():
            noPart = row['PB Part No.']
            if part == noPart:
                new.loc[i,'PB Inactive'] = False
                new.loc[i,'PB Item Status'] = 'Active'
    newNotInTp = new[~new['PB Part No.'].isin(tigerpawCombinedParts)]

    #Add new Items to Tigerpaw
    tpFinal = pd.concat([tpNew,newNotInTp],sort=False)
    tpFinal = tpFinal.reset_index(drop=True)

    tpFinal['PB Mfg. List'] = tpFinal['PB Mfg. List'].str.replace('$','')
    tpFinal['PB Mfg. List'] = tpFinal['PB Mfg. List'].str.replace(',','')
    tpFinal['PB Mfg. List'] = tpFinal['PB Mfg. List'].fillna(0)
    tpFinal['PB Mfg. List'] = tpFinal['PB Mfg. List'].astype(float)
    for i, row in tpFinal.iterrows():
        price = row['PB Mfg. List']
        part = row['PB Part No.']
        newPrice = roundup(price)
        tpFinal.loc[i,'PB Mfg. List'] = newPrice

    tpFinal['PB Item Type'] = 'Material'
    tpFinal['PB Hot Item'] = False
    tpFinal['PB G/L Receipts'] = 'Materials Received'
    tpFinal['PB Taxable'] = True
    tpFinal['PB Update Std. Cost '] = True
    tpFinal['PB Update Vendor Cost'] = True
    for i, row in tpFinal.iterrows():
        inactive = row['PB Inactive']
        if inactive:
            tpFinal.loc[i,'PB Add to Assets'] = False
        else:
            tpFinal.loc[i, 'PB Add to Assets'] = True
    tpFinal['PB Key Description'] = tpFinal['PB Key Description'].str.replace("''",'in.')
    tpFinal['PB Key Description'] = tpFinal['PB Key Description'].str.replace('"','in.')

    tpFinal.to_csv(f'~/Desktop/{filename}',index=False, line_terminator='\r\n')

###################################################################################################

def convertPhases(df,locs,quoteId, lookP, lookB, lookM, phaseName,clientName,quoteName,headers,phases,date):

    df['packageDescription']=df['packageItemId']
    df['packageItemId'] = df['packageItemId'].astype('Int32')
  
    df['type']='M'
    df['locationId'] = df['locationId'].astype(str)
    x={}
    locDesc={}
    n=1
    for i in locs:
        x[str(i)]=n
        n+=1
        desc=requests.get(f'https://api.d-tools.cloud/Quote/api/v1/QuoteLocations/GetQuoteLocation?id={i}',headers=headers).json() ############################################ Added Get Description
        descs=desc['description']
        rm=desc['name']
        locDesc[str(i)]=descs

    #df=df.replace(to_replace={'locationId':x}, value=None)


    pack=df['packageItemId'].unique().dropna()  
    lookPack={}
    for i in pack:
        item = requests.get('https://api.d-tools.cloud/Catalog/api/v1/Packages/GetPackage?id='+str(i), headers=headers).json()
        lookPack[i]=item['shortDescription']
    df=df.replace(to_replace={'packageDescription':lookPack}, value=None)


    df['parentQuantity']=df['parentQuantity'].fillna(1)
    df['packageQuantity']=df['packageQuantity'].fillna(1)

    for i,row in df.iterrows():
        brand = row['brand']
        q=row['quantity']
        p=row['parentQuantity']
        l=row['laborPrice']
        pa=row['packageQuantity']
        if brand == 'LAB':
            df.loc[i,'unitPrice'] = l/q
            df.loc[i,'order'] = 7
        else:
            df.loc[i,'order'] = 5    
        df.loc[i,'quantity']=q*pa*p
        if brand == 'Accessory':
            df.loc[i,'order'] = 6
            df.loc[i, 'type'] = 'S'

    #df.order = 5
    for i,row in df.iterrows():
        accessory=row['hasAccessories']
        if accessory == True:
            df.loc[i,'order'] = 4
            df.loc[i,'parentId']=df.loc[i,'id']
    
    #def cd(path):
    #    os.chdir(os.path.expanduser(path))

    for i, row in df.iterrows():
        short=row['shortDescription']
        if "SCOPE" in row['brand']:
            df.loc[i, 'type'] = 'S'
            df.loc[i,'brand'] = 'SCOPE'
            df.loc[i,'shortDescription'] = '>>> '+short
        if row['brand'] =='LAB':
            df.loc[i, 'type'] = 'L'
        elif row['brand'] == 'Customer Supplied':
            df.loc[i, 'type'] = 'S'
        elif row['brand'] == 'Rental':
            df.loc[i, 'type'] = 'S'
        elif row['brand'] == 'Wiring':
            df.loc[i, 'type'] = 'S'
        elif row['brand'] == 'Monitoring':
            df.loc[i, 'type'] = 'S'

    ssl._create_default_https_context = ssl._create_unverified_context
    url = 'https://docs.google.com/spreadsheets/d/1SxIpBg_hNnX8shTlaWBJ0YlccXuczHPpi18oxoAmmqQ/export?format=csv&gid=0'
    # Set working directory to Current User Home
    #cd('~'+'/') 
    path = 'lookup.csv'
    # Download and setup Lookup Table from Google Sheets as a dictionary
    urllib.request.urlretrieve(url, path)
    df5 = pd.read_csv(path, usecols=[0, 1])
    lookup = df5.set_index('D-Tools Name').T.to_dict('records')[0]

    # Replace brand names based on lookup table
    df['brand'] = df['brand'].replace(lookup)

    for i in df.index:
        cs = df.loc[i, 'clientSupplied']
        part = df.loc[i, 'model']
        if cs == True:
            df.loc[i, 'brand'] = 'Customer Supplied'
            df.loc[i, 'shortDescription'] = 'Customer Supplied '+ part
            df.loc[i, 'model'] = 'Device'
            df.loc[i, 'type'] = 'S'       
    
    df['itemId'] = df['brand'] + ':' + df['model']

    # Replace Sonance Model# with Part Number
    for i in df.index:
        brand = df.loc[i, 'brand']
        part = df.loc[i, "part"]
        if brand == 'SCOPE':
            df.loc[i,'itemId'] = 'SCOPE'
        if brand == "Sonance":
            df.loc[i, 'itemId'] = brand + ':' + part
        if brand == "iPort":
            df.loc[i, 'itemId'] = brand + ':' + part
        if brand == 'Customer Supplied':
            df.loc[i, 'itemId'] = 'Customer Supplied'
        if brand == 'Monitoring':
            df.loc[i, 'itemId'] = 'Monitoring'

 ############# add system names    
    rooms = df.drop_duplicates(subset=['location', 'system'])
    for index, row in rooms.iterrows():
            sys = row['system']
            loca = row['location']
            lid=row['locationId']
            phase = row['phase']  # changed Name and Short Description to System
            df = df.append({'shortDescription':str(sys).upper(),
                            'location': str(loca), 'system': str(sys), 'quantity': 1, 'laborPrice': ' ',
                            'itemId': 'System', 'type': 'S', 'order': 2,'packageItemId':0 , 'brand': ' ', 'parentId':1,'locationId':lid}, ignore_index=True)
            df = df.append({'shortDescription': '---',
                            'location': str(loca), 'quantity': 1, 'system':  str(sys), 'itemId': 'COMMENT:DIVIDER','packageItemId':0 ,
                            'type': 'S', 'order': 1, 'parentId':1,'locationId':lid}, ignore_index=True)

    sortPackage = df.drop_duplicates(subset=['packageId'])
    sortPackage = sortPackage[sortPackage.packageId.notnull()]
 ############# add package name and dividers
    for i, row in sortPackage.iterrows():
            pId=row['packageId']
            pIId=row['packageItemId']
            value=row['location']
            short=row['packageDescription']
            name=row['package']
            sys=row['system']
            location=row['locationId']
            parent=row['parentId']
            df = df.append({'shortDescription': str(short).upper(),'system':sys,
                            'location': str(value), 'quantity': 1, 'itemId': 'Package',
                            'type': 'S', 'order': 3,'packageId':pId ,'packageItemId':pIId, 'parentId':1,'locationId':location}, ignore_index=True)

            df = df.append({'shortDescription': '^^^^^^^^^^^^^^^^^^^^^^^^^^^^','system':sys,
                            'location': str(value), 'quantity': 1, 'itemId': 'COMMENT:DIVIDER',
                            'type': 'S', 'order': 9,'packageId':pId ,'packageItemId':pIId,'parentId':9999999,'locationId':location}, ignore_index=True)
            df = df.append({'shortDescription': 'vvvvvvvvvvvvvvvvvvvvvvvvvvvv','system':sys,
                            'location': str(value), 'quantity': 1, 'itemId': 'COMMENT:DIVIDER',
                            'type': 'S', 'order': 1,'packageId':pId ,'packageItemId':pIId,'parentId':0,'locationId':location}, ignore_index=True)
 
    sys = df.drop_duplicates(subset=['location'])
 ############# add room names and dividers
    for i, row in sys.iterrows():
            lid=row['locationId']
            value=row['location']
            df = df.append({'shortDescription': '[' + str(value).upper() + ']',
                            'location': str(value), 'quantity': 1, 'system': ' ', 'itemId': 'Room',
                            'type': 'S', 'order': 2, 'parentId':0,'locationId':lid}, ignore_index=True)
            df = df.append({'shortDescription': '----------------------------',
                            'location': str(value), 'quantity': 1, 'system': ' ', 'itemId': 'COMMENT:DIVIDER',
                            'type': 'S', 'order': 1, 'parentId':0,'locationId':lid}, ignore_index=True)
            ########## add room description
            df = df.append({'shortDescription': str(lid),
                            'location': str(value), 'quantity': 1, 'system': ' ', 'itemId': 'Description',
                            'type': 'S', 'order': 3, 'parentId':0,'locationId':lid}, ignore_index=True)
    
 ################ replace locationID with Description for room description
    #df['shortDescription'] = df['shortDescription'].replace(locDesc)
    df=df.replace(to_replace={'shortDescription':locDesc}, value=None)
    df=df.replace(to_replace={'locationId':x}, value=None)##################################################

    df = df.sort_values(['locationId','system','packageItemId','parentId','order','unitPrice'],ascending=[True,True,True,True,True,False]) #
    for i, row in df.iterrows():

        if 'White Glove' in str(row['itemId']):
            df.loc[i,'itemId'] = df.loc[i,'itemId'].replace('LAB:','')
    
    df['Vendor Part #'] = df['model']

    # Create Total Price with Calculation
    df['totalPrice'] = df['unitPrice']*df['quantity']
    df['List Price'] = df['unitPrice']
    # Define Unit of Measure
    df['UOM'] = 'EA'
    df['supplier'] = ''

    df = df[['itemId', 'shortDescription', 'quantity', 'unitPrice', 'unitCost', 'totalPrice', 'type', 'List Price',
             'UOM', 'supplier', 'Vendor Part #', 'phase', 'location']]

    df['shortDescription'] = df['shortDescription'].str.replace("''",'in.')
    #df['shortDescription'] = df['shortDescription'].str.replace('<p>','')
    #df['shortDescription'] = df['shortDescription'].str.replace('</p>','')
    df['shortDescription'] = df['shortDescription'].str.replace('"','in.')
    df['Vendor Part #'] = df['Vendor Part #'].str.replace("''",'in.')
    df['Vendor Part #'] = df['Vendor Part #'].str.replace('"','in.')
    df['itemId'] = df['itemId'].str.replace("''",'in.')
    df['itemId'] = df['itemId'].str.replace('"','in.')
    df['location'] = df['location'].str.replace("''",'in.')
    df['location'] = df['location'].str.replace('"','in.')
    quoteName = re.sub('[^A-Za-z0-9.,& ]+', '-',quoteName)
 ##################### write text file  
    p='/home/bill/Desktop/'
    if phases:
        txt=open(f'{p}{clientName}-{quoteName}-{str(phaseName)}({date}).txt', "a")
    else:
        txt=open(f'{p}{clientName}-{quoteName}({date}).txt', "a")
    
 ######################## Write Project Description    
    par = (('quoteId', quoteId),)
    resp = requests.get('https://api.d-tools.cloud/Quote/api/v1/QuoteScopeOfWorks/GetQuoteScopeOfWork', headers=headers, params=par).json()
    html1 = resp['content']
    if html1:
        html1 = re.sub(r'</.*?>', '\n', html1)
        html1 = re.sub(r'<ul.*?>', '', html1)
        html1 = re.sub(r'<br.*?>', '\n', html1)
        html1 = re.sub(r'<p.*?>', '    ', html1)
        html1 = re.sub(r'<li>', '      *', html1)
        html1 = re.sub(r'<li class.*?>', '        *', html1)
        txt.write('Project Description: \n' + html1)
 ######################## Write Scopes and Descriptions
    for i, row in df.iterrows():
        if 'Room' in row['itemId']:

            txt.write('\n' + row['shortDescription']+'\n')
        if 'Description' in row['itemId']:
            if row['shortDescription']:
                html = row['shortDescription']
                html = re.sub(r'</.*?>', '\n', html)
                html = re.sub(r'<ul.*?>', '', html)
                html = re.sub(r'<br.*?>', '\n', html)
                html = re.sub(r'<p.*?>', '    ', html)
                html = re.sub(r'<li>', '      *', html)
                html = re.sub(r'<li class.*?>', '        *', html)
                txt.write('Description: \n' + html+'\n')
        if 'System' in row['itemId']:
            txt.write('\n' + row['shortDescription']+'\n')
        if 'SCOPE' in row['itemId']:
            txt.write(row['shortDescription']+'\n')
        txt.close
 ####################### drop Description
    filt= df['itemId'] == 'Description'
    df = df.drop(index=df[filt].index)
    #for i, row in df.iterrows():
    #    if 'SCOPE' in row['itemId']:
    #        df = df.drop(index=i)

    if phases:
        output = '~/Desktop/'+clientName+'-'+quoteName +'-'+str(phaseName)+'('+date+')'+'.csv'
    else:
        output = '~/Desktop/'+clientName+'-'+quoteName+'('+date+')'+'.csv'
    df.to_csv(output, index=False, header=None, line_terminator='\r\n')

###################################################################################################

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0')
   