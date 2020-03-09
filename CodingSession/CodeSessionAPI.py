import requests
import json
import mysql.connector as mysql


i = 0
structure_map = {}
observation = {}
attribute = {}
series_list = []
mapped_series_list = []



url = "https://stats.oecd.org/SDMX-JSON/data/GENDER_ENT1"
response = requests.get(url)
#  print(response.json())
json_str = response.content
OECDdataset = json.loads(json_str)
#  print(OECDdataset['dataSets'][0]['series'])
#  print(OECDdataset['structure']['dimensions']['series'])


for each_item in OECDdataset['structure']['dimensions']['series']:
    #  print(each_item['keyPosition'])
    #  structure_map.insert()
    for key in each_item['values']:
        #  print(key)
        structure_map.setdefault(each_item['keyPosition'], []).append(key['name'])

print(structure_map)

for each_attribute in OECDdataset['structure']['attributes']['series']:
    attribute[each_attribute['name']] = []
    for attribute_name in each_attribute['values']:
        attribute[each_attribute['name']].append(attribute_name['name'])
        #  each_attribute[attribute_name['name']] = attribute_name['name']
        #  attribute.setdefault(each_attribute['name'], []).append(attribute_name['name'])

print(attribute)

for each_observation in OECDdataset['structure']['dimensions']['observation']:
    for observation_name in each_observation['values']:
        observation.setdefault(each_observation['name'], []).append(observation_name['name'])

print(observation)



for each_dataset in OECDdataset['dataSets']:
    #  print(each_dataset['series'])
    for series in each_dataset['series'].keys():
        #  print(single_dts)
        series_list.append(series.split(':'))
        #  print(series_list)

for each_dataset in OECDdataset['dataSets']:
    for series in each_dataset['series'].values():
        #  print(series['attributes'])
        #  print(series['observations'].keys())
        for each_year in series['observations'].keys():
            #  print(each_year)
            a = series['attributes']
            a.append(each_year)
            #print(a)
            for each_value in series['observations'].values():
                #  print(series['attributes'])
                #  print(each_year)
                #  print(each_value)
                #  print(a)
                #a.extend(each_value)
                #  a.extend(each_value)
                #  print(a)
                b = a + each_value
                #  print(b)
        #  print(series['observations'].values())

#  print(series_list)
#  print(structure_map[0][0])
for each_series in series_list:
    i = 0
    mapped_each_num = []
    for each_num in each_series:
        #  print(each_num)
        #  print(structure_map[i][int(each_num)])
        mapped_each_num.append(structure_map[i][int(each_num)])
        i += 1
    #  print(mapped_each_num)
    mapped_series_list.append(mapped_each_num)

print(mapped_series_list)
#  print(series_list)



'''for id in OECD['']:
    print('')

conn = mysql.connect(host="localhost", user="root", passwd="Ermengmeng3*",db="apiconnection")
cursor = conn.cursor()

cursor.execute("truncate table OECDGenderEquality")'''
