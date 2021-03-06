
import sys 
import os
import json
import requests
import jieba
from collections import Counter
import configparser 
import news 

#讀取設定檔
cfp = configparser.ConfigParser()
cfp.readfp(open('config.ini'))

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

#取得新聞詳細資料
def getNews(date_from,date_to,keyword):
	url = cfp.get('url','get_news_detail_url')
	headers = {'Authorization': tokenForTest,'Content-Type': 'application/json'}
	data = {'date_from': date_from, 'date_to': date_to ,'keyword': keyword}
	result = requestPost(url,headers,data=data)[0]
	success = requestPost(url,headers,data=data)[1]

	if success:
		#print (result.text)
		jsonData = result.json() #result轉換成Json格式
		if jsonData['_status'] == 'Success':
			print (jsonData)
			#global newsList
			#newsList = []   #宣告存放個別文章的list
			#for i in range(len(jsonData['data'])):
			#	newsToAdd = news.News(jsonData['data'][i]['content']) #建立一個News物件，將文章內容存進物件裡
			#	newsList.append(newsToAdd)	#文章物件加進news list裡
		else:
			print ('Get news unsuccessfully')

#取得token
url = cfp.get('url','get_token_url')
loginKey = {'member_account':cfp.get('account','member_account'),'client_secretkey':cfp.get('account','client_secretkey')} 

result = requestGet(url,loginKey)[0]
success = requestGet(url,loginKey)[1]

if success:
	print ('Get token Successfully.')
	tokenData = result.json()
	tokenForTest = tokenData['token_type'] + ' ' + tokenData['access_token']  #連接token type和token字串，並存進新變數，之後驗證、取資料會用到

#驗證token有效性
url = cfp.get('url','test_token_url')
headers = {'Authorization': tokenForTest}
result = requestPost(url,headers,data=None)[0]
success = requestPost(url,headers,data=None)[1]

if success:
	jsonData = result.json()
	if jsonData['_status'] == 'Success':
		print ('Token is accessible.')
	else:
		print ('Token not accessible.')

if __name__ == "__main__":
    date_from = str(sys.argv[1])
    date_to = str(sys.argv[2])
    keyword = str(sys.argv[3])

print (date_from + date_to + keyword)
getNews('2018-04-20','2018-04-21','麻疹')

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
sumc = 0
for i in range(len(counter)):  
    for j in range(1,len(counter[i])):
       sumc += counter[i][j] #加總次數
average = sumc / len(counter) #計算次數平均
counterJson = json.dumps([{'keyword': k, 'size': (v/average)*40} for k,v in counter], indent=2,ensure_ascii=False)  #counter轉換成json特定格式
counterJson = "{" + counterJson + "}"

#匯出
with open('./website/data.json', 'w', encoding = "utf-8") as outfile:
	outfile.write(counterJson)