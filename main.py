
import sys 
import os
import json
import requests


def requestGet(url,params):
	result = []
	success = True
	try:
		r = requests.get(url, params= params)
	except requests.exceptions.HTTPError as err:
		print (err)
		success = False
		sys.exit(1)
	except:
		print ('Unexpected Error')
		success = False
		sys.exit(1)

	result.append(r)
	result.append(success)
	return result

def requestPost(url,headers,data):
	result = []
	success = True
	try:
		r = requests.post(url, headers=headers, data=json.dumps(data))
	except requests.exceptions.HTTPError as err:
		print (err)
		success = False
		sys.exit(1)
	except:
		print ('Unexpected Error')
		success = False
		sys.exit(1)

	result.append(r)
	result.append(success)
	return result

#取得token
url = 'https://api2.ifeel.com.tw/pro/auth'
loginKey = {'member_account':'iiidsi_sa','client_secretkey':'daa75a16f538c13be9e97cf91acdd9c8'} 

result = requestGet(url,loginKey)[0]
success = requestGet(url,loginKey)[1]

if success:
	print ('Get token Successfully.')
	tokenData = result.json()
	print ('Token type:' + tokenData['token_type'] + '\nToken:' + tokenData['access_token'])
	tokenForTest = tokenData['token_type'] + ' ' + tokenData['access_token']
	print (tokenForTest)


#驗證token有效性
url = 'https://api2.ifeel.com.tw/pro/auth'
headers = {'Authorization': tokenForTest}
result = requestPost(url,headers,data=None)[0]
success = requestPost(url,headers,data=None)[1]

if success:
	jsonData = result.json()
	print (json.dumps(jsonData,indent=2))
	if jsonData['_status'] == 'Success':
		print ('Token is accessible')
	else:
		print ('Token not accessible')

#取得文章內容
url = 'https://api2.ifeel.com.tw/pro/document/news/all'
headers = {'Authorization': tokenForTest,'Content-Type': 'application/json'}
data = {'date': '2018-04-20','keyword': '麻疹'}
result = requestPost(url,headers,data=data)[0]
success = requestPost(url,headers,data=data)[1]

if success:
	#print (result.text)
	jsonData = result.json()
	if jsonData['_status'] == 'Success':
		print (json.dumps(jsonData['data'][0]['content']))
		print (len(jsonData['data']))
		for i in range(len(jsonData['data'])):
			
	else:
		print ('Get news unsuccessfully')




