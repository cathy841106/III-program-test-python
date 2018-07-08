
import sys 
import os
import json
import requests
import jieba
from collections import Counter
import news 

#get request
def requestGet(url,params):
	result = []   #儲存request回傳值
	success = True  #是否request成功
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

#post request
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

#取得新聞資料
def getNews(date,keyword):
	url = 'https://api2.ifeel.com.tw/pro/document/news/all'
	headers = {'Authorization': tokenForTest,'Content-Type': 'application/json'}
	data = {'date': date,'keyword': keyword}
	result = requestPost(url,headers,data=data)[0]
	success = requestPost(url,headers,data=data)[1]

	if success:
		#print (result.text)
		jsonData = result.json() #result轉換成Json格式
		if jsonData['_status'] == 'Success':
			global newsList
			newsList = []   #宣告存放個別文章的list
			for i in range(len(jsonData['data'])):
				newsToAdd = news.News(jsonData['data'][i]['content']) #建立一個News物件，將文章內容存進物件裡
				newsList.append(newsToAdd)	#文章物件加進news list裡
				print (newsList[i].getNews())	
		else:
			print ('Get news unsuccessfully')

#取得token
url = 'https://api2.ifeel.com.tw/pro/auth'
loginKey = {'member_account':'iiidsi_sa','client_secretkey':'daa75a16f538c13be9e97cf91acdd9c8'} 

result = requestGet(url,loginKey)[0]
success = requestGet(url,loginKey)[1]

if success:
	print ('Get token Successfully.')
	tokenData = result.json()
	print ('Token type:' + tokenData['token_type'] + '\nToken:' + tokenData['access_token'])
	tokenForTest = tokenData['token_type'] + ' ' + tokenData['access_token']  #連接token type和token字串，並存進新變數，之後驗證、取資料會用到
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
getNews('2018-04-20','麻疹')
getNews('2018-04-21','麻疹')

#文章合併
newsAppend = ''
for i in range(len(newsList)):
	newsAppend += newsList[i].getNews() #將news list的文章依序累加進newsAppend字串

#文章斷詞
segList = jieba.cut(newsAppend, cut_all=False) #利用結巴分詞的精確模式對文章做分詞
#加载停用词
with open('stopwords.txt', encoding = 'utf8') as f:  #讀取本地端檔案stopwords.txt，讀取每一行，將每一行存進stopwords list裡
	stopwords = f.read().splitlines()
#去除停用詞
segListWithoutStop = []
for seg in segList:
	if seg not in stopwords:
		segListWithoutStop.append(seg)

#計算TF值並取出前20大
counter = Counter(segListWithoutStop).most_common(20)  #用Counter方法計算出各詞出現次數，並取出次數前20多的詞

#打包成Json格式
for i in range(len(counter)):  
    for j in range(1,len(counter[i])):
       sum += counter[i][j]  #加總次數
average = sum / len(counter) #計算次數平均
counterJson = json.dumps([{'keyword': k, 'size': (v/average)*40} for k,v in counter], indent=2,ensure_ascii=False)  #counter轉換成json特定格式
counterJson = "{" + counterJson + "}"
print (counterJson)

#匯出
with open('./website/data.json', 'w', encoding = "utf-8") as outfile:
	outfile.write(counterJson)