import requests
import pyodbc
import re
import os
import base64
import sys
import hashlib

env = sys.argv[1]
objectname = 'Case'
RTField_list = []
MD5Hash_list = []

#  Get Salesforce access token and use REST API
sf_params = {
    "grant_type": "password",
    "client_id": "",
    "client_secret": "",
    "username": "",
    "password": ""
}

r = requests.post("https://login.salesforce.com/services/oauth2/token",
                  headers={"Content-Type": "application/x-www-form-urlencoded"}, data=sf_params)
access_token = r.json().get("access_token")
headers = {
    'Authorization': 'Bearer ' + access_token,
}

#  Connect to Carbon database server
conn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                      r"Server=;"
                      "Database=CARBON" + env + ";"
                      "Trusted_Connection=yes;")
cursor = conn.cursor()  # connection to get all rich text fields with <img> tags

# Questions from Sophia: tried to use delta load but cannot figure out a better way to do it...
cursor.execute(r"""
    select Id, CaseNumber, 'Problem_Recreation__c' as API_Name, cast(Problem_Recreation__c as nvarchar(max)) as RichText from SFCaseLand 
    where cast(Problem_Recreation__c as nvarchar(max)) is not null and cast(Problem_Recreation__c as nvarchar(max)) like '%</img>%'
    union
    select Id, CaseNumber, 'Root_Cause_FA__c', cast(Root_Cause_FA__c as nvarchar(max)) from SFCaseLand
    where cast(Root_Cause_FA__c as nvarchar(max)) is not null and cast(Root_Cause_FA__c as nvarchar(max)) like '%</img>%'
    union
    select Id, CaseNumber, 'Most_Recent_Case_Comment__c', cast(Most_Recent_Case_Comment__c as nvarchar(max)) from SFCaseLand
    where cast(Most_Recent_Case_Comment__c as nvarchar(max)) is not null and cast(Most_Recent_Case_Comment__c as nvarchar(max)) like '%</img>%'
    union
    select Id, CaseNumber, 'HubCase_Parnter_Comments__c', cast(HubCase_Parnter_Comments__c as nvarchar(max)) from SFCaseLand
    where cast(HubCase_Parnter_Comments__c as nvarchar(max)) is not null and cast(HubCase_Parnter_Comments__c as nvarchar(max)) like '%</img>%'
    union
    select Id, CaseNumber, 'Current_Case_Status__c', cast(Current_Case_Status__c as nvarchar(max)) from SFCaseLand
    where cast(Current_Case_Status__c as nvarchar(max)) is not null and cast(Current_Case_Status__c as nvarchar(max)) like '%</img>%'
    union
    select Id, CaseNumber, 'Conditions_of_Satisfaction__c', cast(Conditions_of_Satisfaction__c as nvarchar(max)) from SFCaseLand
    where cast(Conditions_of_Satisfaction__c as nvarchar(max)) is not null and cast(Conditions_of_Satisfaction__c as nvarchar(max)) like '%</img>%'
""")

for row in cursor:
    RTField_derived = {}
    EID = row[0]
    CaseNumber = row[1]
    fieldname = row[2]
    raw_text = row[3]
    new_text = raw_text
    # find html tags with Salesforce link
    image_url_one = re.findall(
        'https://c\.na79\.content\.force\.com/servlet/rtaImage\?eid=\S+&amp;feoid=\S+&amp;refid=\S+"', row[3])
    #  find html tags with base64 encoded
    image_url_two = re.findall('data:image/[png|gif]*;base64\S+"', row[3])
    #  find html tags with local file path embedded
    image_url_three = re.findall('src="file:///C:\S+', row[3])  # remove the tag from rax text

    if image_url_one:
        for each_url_one in image_url_one:
            MD5Hash_dict = {}
            # Get each image in rich text field unique identifier
            refid = each_url_one.split(';')[-1].replace('refid=', '').replace('"', '')
            url = "https://na79.salesforce.com/services/data/v43.0/sobjects/" + objectname + '/' + EID + \
                  '/richTextImageFields/' + fieldname + '/' + refid + '/'
            response = requests.get(url, headers=headers)
            #  Define the file type
            content_type = response.headers.get('Content-Type')
            if content_type == 'image/jpeg':
                file_type = '.jpg'
            else:
                file_type = '.png'
            #  Generate the file path
            path = 'D:/App/Carbon/Salesforce/Image Attachments/' + env + '/Land/' + EID + '/'
            try:
                os.makedirs(path)
            except OSError as error:
                print("The directory already exists", EID)
            #  Download the images into local folder
            with open(path + refid + file_type, 'wb') as f:
                f.write(response.content)
            # Generate MD5 hash of each image
            with open(
                    path + refid + file_type, "rb") as md5_file:
                bytes = md5_file.read()  # read file as bytes
                readable_hash = hashlib.md5(bytes).digest()
            MD5Hash_dict['Attachment_FileHash'] = readable_hash
            MD5Hash_dict['ParentId'] = EID
            MD5Hash_dict['Name'] = refid + file_type
            MD5Hash_list.append(MD5Hash_dict)
            #  base64 encoded and transform the code into html file, for reference only
            #  with open('D:/App/Carbon/Salesforce/RT Fields Images/'+EID+'/' + refid + file_type, "rb") as image_file:
            #    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            #    print(encoded_string)
            #  with open('D:/App/Carbon/Salesforce/RT Fields Images/'+EID+'/' + refid + '.html', 'w') as html_file:
            #    image_html = '<img src="data:image/jpeg;base64,' + encoded_string +'"></img>'
            #    html_file.write(image_html)
            #    html_file.close()

            #  replace <img> html tags into explanations text
            new_text = re.sub(r'<img.+' + re.escape(each_url_one) + r'.+?</img>',
                              '(Please refer to the following case note for screenshot - ' +
                              refid + file_type + ')', new_text)
    if image_url_two:
        i = 0
        for each_url_two in image_url_two:
            MD5Hash_dict = {}
            i += 1  # file name identifier to differentiate multiple images in one field
            #  Get base64 encode
            base64_code = each_url_two.replace('data:image/png;base64,', '').replace('data:image/gif;base64,', '') \
                .replace('"', '').encode('utf-8')
            #  Define the file type
            if 'data:image/png;base64,' in each_url_two:
                filename = CaseNumber + '_' + fieldname + '_' + str(i) + '.jpg'
            elif 'data:image/gif;base64,' in each_url_two:
                filename = CaseNumber + '_' + fieldname + '_' + str(i) + '.gif'
            #  Generate the file path
            path = 'D:/App/Carbon/Salesforce/Image Attachments/' + env + '/Land/' + EID + '/'
            try:
                os.makedirs(path)
            except OSError as error:
                print("The directory already exists", EID)
            # base 64 decoded and save the image in local folder
            with open(
                    path + filename, "wb") as base64_file:
                try:
                    base64_file.write(base64.decodebytes(base64_code))
                #  Handle the error when the base64 code is invalid
                except base64.binascii.Error as decode_error:
                    print("This is an error in base64 code.")
            # Generate MD5 hash for each image
            with open(
                    path + filename, "rb") as base64_file:
                bytes = base64_file.read()  # read file as bytes
                readable_hash = hashlib.md5(bytes).digest()
            MD5Hash_dict['Attachment_FileHash'] = readable_hash
            MD5Hash_dict['ParentId'] = EID
            MD5Hash_dict['Name'] = filename
            MD5Hash_list.append(MD5Hash_dict)
            # replace <img> html tags into explanations text
            new_text = re.sub(r'<img.+' + re.escape(each_url_two) + r'.+?</img>',
                              '(Please refer to the following case note for screenshot - ' + filename + ')', new_text)
    #  Save the new text with its id and case number into a list of dictionary
    RTField_derived['CaseNumber'] = CaseNumber
    RTField_derived['Id'] = EID
    RTField_derived['APIName'] = fieldname
    RTField_derived['Rich_Text_Field_derived'] = new_text
    RTField_list.append(RTField_derived)

# Is there a good way to do upsert? I cannot figure it out so I directly use truncate and load instead...
# insert id, case number and new text into SQL table
cursor.execute("truncate table SFRTFieldStage")
for each_RTField in RTField_list:
    #  print(each_RTField)
    # cursor.execute("update SFRTFieldStage set CaseNumber=?, Id=?,APIName=?,Rich_Text_Field_derived=?",
    #               (each_RTField['CaseNumber'], each_RTField['Id'], each_RTField['APIName'], each_RTField['Rich_Text_Field_derived']))
    cursor.execute("insert into SFRTFieldStage (CaseNumber, Id, APIName, Rich_Text_Field_derived) values (?, ?, ?, ?)",
                   (each_RTField['CaseNumber'], each_RTField['Id'], each_RTField['APIName'],
                    each_RTField['Rich_Text_Field_derived']))
    cursor.commit()

# insert MD5 hash, Case Id and File name into SFImageAttachmentLand table
#  cursor.execute("truncate table SFImageAttachmentLand")
for each_MD5Hash in MD5Hash_list:
    cursor.execute("select * from SFImageAttachmentLand where ParentId=? and Name=?",
                   (each_MD5Hash['ParentId'], each_MD5Hash['Name']))
    if cursor.rowcount == 0:
        cursor.execute("insert into SFImageAttachmentLand (Attachment_FileHash, ParentId, Name) values (?, ?, ?)",
                       (each_MD5Hash['Attachment_FileHash'], each_MD5Hash['ParentId'], each_MD5Hash['Name']))
    cursor.commit()
