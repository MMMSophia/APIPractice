import requests
import json
import mysql.connector as mysql


i = 0
dictionary = []
indicator = {}
sex = {}
age = {}
url = "https://stats.oecd.org/SDMX-JSON/data/GENDER_ENT1"


response = requests.get(url)
#  print(response.json())
json_str = response.content
OECDdataset = json.loads(json_str)
#  print(OECDdataset['dataSets'][0]['series'])
print(OECDdataset['structure']['dimensions']['series'])
for each_item in OECDdataset['structure']['dimensions']['series']:
    #  dictionary[each_item['keyPosition']] = each_item['name']
    print(each_item['keyPosition'])
    dictionary.insert(each_item['keyPosition'], [])
    for key in each_item['values']:
        #  print(key)
        #  value_dict = {}
        #  value_dict.setdefault(key, val)
        dictionary[each_item['keyPosition']].append(key)
        #  value.append(each_item['name'])
        #  for (key, val) in value:
        #   each_item['name'].setdefualt(key, val)
#  dictionary[each_item['keyPosition']][each_item['name']] = each_item['values']
print(dictionary)

for dataset in OECDdataset['dataSets']:
    #  print(dataset['series'])
    for single_dts in dataset['series'].keys():
        #  print(single_dts)
        column = single_dts.split(':')
        print(column)
    #for item in column:
    #   for row1 in OECDdataset['structure']['dimensions']['series']:
    #        print(row1[i])
            #item = row1[i]['values'][item]['id']
    #print(item)



'''for id in OECD['']:
    print('')

conn = mysql.connect(host="localhost", user="root", passwd="Ermengmeng3*",db="apiconnection")
cursor = conn.cursor()

cursor.execute("truncate table OECDGenderEquality")'''
