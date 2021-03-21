from flask import Flask, send_from_directory, send_file
import requests
import json
import pandas as pd
import os
import urllib.request
import ssl
import subprocess
import re
import time

app = Flask(__name__)



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
    ('ownerIds', ['3322', '3875', '3939', '1159', '3486', '3482']),
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
    getOpportunities = requests.get('https://api.d-tools.cloud/Opportunity/api/v1/Opportunities/GetOpportunitiesForStages', headers=headers, params=paramsOpps).json()
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


    convertPhases(df, locs, quoteId, lookP, lookB, lookM, phaseName, clientName, quoteName, headers, phases)

    return '{"":""}'
    
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

    for phase in phaseNames:
        phaseName = phase
        df1= df[df.phase == phase]
        convertPhases(df1,locs,quoteId, lookP, lookB, lookM, phaseName,clientName,quoteName,headers,phases)

    return json.dumps(phaseNames.tolist())

###################################################################################################

app.config["DOWNLOAD"] = "/home/bill/Desktop"
@app.route('/api/download/<quoteId>', methods=['GET'])
def download(quoteId):
    return send_from_directory(app.config["DOWNLOAD"], filename=quoteId+'.csv', as_attachment=False)



###################################################################################################

def convertPhases(df,locs,quoteId, lookP, lookB, lookM, phaseName,clientName,quoteName,headers,phases):

    df['packageDescription']=df['packageItemId']
    df['packageItemId'] = df['packageItemId'].astype('Int32')
  
    df['type']='M'
    df['locationId'] = df['locationId'].astype(str)
    x={}
    n=1
    for i in locs:
        x[str(i)]=n
        n+=1
    df=df.replace(to_replace={'locationId':x}, value=None)


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
            df.loc[i,'order'] = 6    
        df.loc[i,'quantity']=q*pa*p

    df.order = 5
    for i,row in df.iterrows():
        accessory=row['hasAccessories']
        if accessory == True:
            df.loc[i,'order'] = 4
            df.loc[i,'parentId']=df.loc[i,'id']
    
    #def cd(path):
    #    os.chdir(os.path.expanduser(path))

    for index, row in df.iterrows():
        if "SCOPE" in row['brand']:
            df.loc[index, 'type'] = 'L'
        if row['brand'] =='LAB':
            df.loc[index, 'type'] = 'L'
        elif row['brand'] == 'Customer Supplied':
            df.loc[index, 'type'] = 'S'
    
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
        if brand == "Sonance":
            df.loc[i, 'itemId'] = brand + ':' + part
    
    rooms = df.drop_duplicates(subset=['location', 'system'])
    for index, row in rooms.iterrows():
            sys = row['system']
            loca = row['location']
            lid=row['locationId']
            phase = row['phase']  # changed Name and Short Description to System
            df = df.append({'shortDescription': '--- ' + str(sys).upper() + ' ---',
                            'location': str(loca), 'system': str(sys), 'quantity': 1, 'laborPrice': ' ',
                            'itemId': 'System:' + str(sys), 'type': 'S', 'order': 2, 'brand': ' ', 'parentId':0,'locationId':lid}, ignore_index=True)


    sortPackage = df.drop_duplicates(subset=['packageId'])
    sortPackage = sortPackage[sortPackage.packageId.notnull()]

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
                            'location': str(value), 'quantity': 1, 'itemId': name,
                            'type': 'S', 'order': 3,'packageId':pId ,'packageItemId':pIId, 'parentId':1,'locationId':location}, ignore_index=True)

            df = df.append({'shortDescription': '^^^^^^^^^^^^^^^^^^^^^^^^^^^^','system':sys,
                            'location': str(value), 'quantity': 1, 'itemId': 'COMMENT:DIVIDER',
                            'type': 'S', 'order': 9,'packageId':pId ,'packageItemId':pIId,'parentId':9999999,'locationId':location}, ignore_index=True)
            df = df.append({'shortDescription': 'vvvvvvvvvvvvvvvvvvvvvvvvvvvv','system':sys,
                            'location': str(value), 'quantity': 1, 'itemId': 'COMMENT:DIVIDER',
                            'type': 'S', 'order': 1,'packageId':pId ,'packageItemId':pIId,'parentId':0,'locationId':location}, ignore_index=True)
 
    sys = df.drop_duplicates(subset=['location'])

    for i, row in sys.iterrows():
            lid=row['locationId']
            value=row['location']
            df = df.append({'shortDescription': '--- ' + str(value).upper() + ' ---',
                            'location': str(value), 'quantity': 1, 'system': ' ', 'itemId': 'Room:' + str(value),
                            'type': 'S', 'order': 2, 'parentId':0,'locationId':lid}, ignore_index=True)
            df = df.append({'shortDescription': '----------------------------',
                            'location': str(value), 'quantity': 1, 'system': ' ', 'itemId': 'COMMENT:DIVIDER',
                            'type': 'S', 'order': 1, 'parentId':0,'locationId':lid}, ignore_index=True)
    
    df = df.sort_values(['locationId','system','packageItemId','parentId','order'])
    for i, row in df.iterrows():

        if 'White Glove' in row['itemId']:
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
    df['shortDescription'] = df['shortDescription'].str.replace('"','in.')
    quoteName = re.sub('[^A-Za-z0-9.,& ]+', '-',quoteName)
    
    if phases:
        output = '~/Desktop/'+clientName+'-'+quoteName +'-'+str(phaseName)+'.csv'
    else:
        output = '~/Desktop/'+clientName+'-'+quoteName+'.csv'
    df.to_csv(output, index=False, header=None, line_terminator='\r\n')

###################################################################################################

if __name__ == '__main__':
    app.run(debug = True)
   