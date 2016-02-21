# -*- coding, utf-8 -*-
import os, bs4, msvcrt, time, re, threading
from urllib import request, parse
from bs4 import BeautifulSoup

os.system("color 70")
os.system("title 教务管理系统v2.0")

'''
获取成绩函数，接收目标url（从主页面中的菜单中获取），登陆账号姓名，页面状态码（从查询页面中获取）作为参数
另外接收学年、学期、查找条件（可为所有，学年，学期）作为查找参数
返回成绩数组
'''
def getScore(targetUrl, name, __VIEWSTATE, year, term, condition):
	global serverAddress, sessionID
	#将姓名编码至urlcode
	decoded_name = parse.quote(name, encoding = 'gbk')
	url = '%s/(%s)/%s' % (serverAddress, sessionID, targetUrl)
	#替换中文
	url = url.replace(name, decoded_name)
	sendHeaders = {'Host': 'jwgl.hunnu.edu.cn',
				   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0',
				   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
				   'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
				   'Accept-Encoding': 'gzip, deflate',
				   'Referer': url,
				   'Connection': 'keep-alive'}
	data = {'__VIEWSTATE': __VIEWSTATE,
			'ddlXN': year,
			'ddlXQ': term}
	if condition == '所有':
		data['Button2'] = parse.quote('在校学习成绩查询', encoding = 'gbk')
	elif condition == '学年':
		data['Button5'] = parse.quote('按学年查询', encoding = 'gbk')
	elif condition == '学期':
		data['Button1'] = parse.quote('按学期查询', encoding = 'gbk')
	else:
		print ('查询条件有错！')
		os.system('pause')
		return []
	decoded_data = parse.urlencode(data).replace('%25', '%').encode('gbk')

	#发送post
	req = request.Request(url, headers = sendHeaders, data = decoded_data)
	soup = BeautifulSoup(request.urlopen(req).read(), 'lxml')
	#获取所有的成绩表格，一般为2个表格，期末成绩和补考成绩
	tables = soup.find_all(class_ = 'datelist')
	allScore = []
	for eachTable in tables:
		#获取每个表格的内容
		course = []
		for child in eachTable.children:
			if type(child) != bs4.element.Tag:
				continue
			#将所有td中的内容复制到course中
			cells = child.find_all('td')
			course.append([cell.text for cell in cells])
		#添加进总表
		allScore.append(course)
	return allScore

'''
用get方法获取等级考试成绩，接收登陆账号姓名，目标url（从主页面中的菜单中获取）作为参数
返回等级考试的成绩
'''
def getGradeExamScore(targetUrl, name):
	global serverAddress, sessionID
	#将姓名编码至urlcode
	decoded_name = parse.quote(name, encoding = 'gbk')
	url = '%s/(%s)/%s' % (serverAddress, sessionID, targetUrl)
	#替换中文
	url = url.replace(name, decoded_name)
	sendHeaders = {'Host': 'jwgl.hunnu.edu.cn',
				   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0',
				   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
				   'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
				   'Accept-Encoding': 'gzip, deflate',
				   'Referer': url,
				   'Connection': 'keep-alive'}
	
	req = request.Request(url, headers = sendHeaders)
	soup = BeautifulSoup(request.urlopen(req).read(), 'lxml')
	tables = soup.find_all(class_ = 'datelist')
	gradeExamScore = []
	for eachTable in tables:
		course = []
		for child in eachTable.children:
			if type(child) != bs4.element.Tag:
				continue
			cells = child.find_all('td')
			course.append([cell.text for cell in cells])
		gradeExamScore.append(course)
	return gradeExamScore

'''
用get方法获取成绩页面源代码，接收登陆账号姓名，目标url（从主页面中的菜单中获取）作为参数
返回查成绩界面源代码（soup）
'''
def getScorePage(targetUrl, name):
	global serverAddress, sessionID
	#将姓名编码至urlcode
	decoded_name = parse.quote(name, encoding = 'gbk')
	url = '%s/(%s)/%s' % (serverAddress, sessionID, targetUrl)
	#替换中文
	url = url.replace(name, decoded_name)
	sendHeaders = {'Host': 'jwgl.hunnu.edu.cn',
				   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0',
				   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
				   'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
				   'Accept-Encoding': 'gzip, deflate',
				   'Referer': url,
				   'Connection': 'keep-alive'}

	req = request.Request(url, headers = sendHeaders)
	soup = BeautifulSoup(request.urlopen(req).read(), 'lxml')
	return soup

'''
格式化输出成绩，无返回
'''
def printScore(score):
	courseWidth = 25
	splitLine = '-' * 60
	title = ['****************期末成绩****************', '****************补考成绩****************']
	for i in range(len(score)):
		print (title[i])
		print (splitLine)
		#寻找成绩所在的列数
		for j in range(len(score[i][0])):
			if score[i][0][j] == '成绩' or score[i][0][j] == '补考成绩':
				scoreIndex = j
				break
		#判断是期末成绩还是补考成绩
		if i == 0:
			#输出科目名称的表头
			print ('%s' % score[i][0][3], end = '')
			#考虑科目名称的表头的长度，因为是中文，所以宽度需要乘以2
			print (' ' * (courseWidth - len(score[i][0][3]) * 2), end = '')
			print ('\t%s\t%s\t%s' % (score[i][0][4], score[i][0][6], score[i][0][scoreIndex]))
			for eachCourse in score[i][1:]:
				#输出科目名称
				if len(eachCourse[3]) > 12:
					eachCourse[3] = eachCourse[3][:eachCourse[3].find('（')]
				print ('%s' % eachCourse[3], end = '')
				#根据科目名称的长度输出相应空格
				space = courseWidth - len(eachCourse[3]) * 2
				for j in range(len(eachCourse[3])):
					#判断是否存在半角英文字符
					if eachCourse[3][j] < chr(255):
						space += 1
				print (' ' * space, end = '')
				print ('\t%s\t%s\t%s' % ( eachCourse[4], eachCourse[6], eachCourse[scoreIndex]))
			print ()
		else:
			print ('%s' % score[i][0][scoreIndex], end = '')
			print (' ' * (courseWidth - len(score[i][0][scoreIndex]) * 2), end = '')
			print ('\t%s' % (score[i][0][4]))
			if len(score[i]) <= 1:
				print ('一科都没挂，你是大学霸！！！\(≧▽≦)/')
			for eachCourse in score[i][1:]:
				if len(eachCourse[3]) > 12:
					eachCourse[3] = eachCourse[3][:eachCourse[3].find('（')]
				print ('%s' % eachCourse[3], end = '')
				#根据科目名称的长度输出相应空格
				space = courseWidth - len(eachCourse[3]) * 2
				for j in range(len(eachCourse[3])):
					#判断是否存在半角英文字符
					if eachCourse[3][j] < chr(255):
						space += 1
				print (' ' * space, end = '')
				print ('\t%s' % (eachCourse[scoreIndex]))
			print ()
	print ()

'''
格式化输出等级考试成绩，无返回
'''
def printGradeExamScore(gradeExamScore):
	courseWidth = 25
	splitLine = '-' * 60
	title = ['****************等级考试成绩****************']
	for i in range(len(title)):
		print (title[i])
		print (splitLine)
		for j in range(len(gradeExamScore[i][0])):
			if gradeExamScore[i][0][j].find('成绩') != -1:
				scoreIndex = j
				break
		print (gradeExamScore[i][0][2], end = '')
		print (' ' * (courseWidth - len(gradeExamScore[i][0][2]) * 2), end = '')
		print (gradeExamScore[i][0][scoreIndex])
		if len(gradeExamScore[i]) <= 1:
			print ('无等级考试成绩！')
		for eachCourse in gradeExamScore[i][1:]:
			print (eachCourse[2], end = '')
			space = courseWidth - len(eachCourse[2]) * 2
			for j in range(len(eachCourse[2])):
				if eachCourse[2][j] < chr(255):
					space += 1
			print (' ' * space, end = '')
			print (eachCourse[scoreIndex])

'''
登陆教务管理系统，接收页面状态码（从主页面获取），账号密码作为参数
返回登陆成功后的页面（soup）ps：只能登陆学生账号
'''
def login(__VIEWSTATE, studentNumber, studentPwd):
	#post主体
	global serverAddress, sessionID
	url = '%s/(%s)/default2.aspx' % (serverAddress, sessionID)
	data = {'__VIEWSTATE': __VIEWSTATE,
			'TextBox1': studentNumber,
			'TextBox2': studentPwd,
			'TextBox3': '',
			'RadioButtonList1': parse.quote('学生', encoding = 'gbk'),
			'Button1': '',
			'lbLanguage': ''}
	decoded_data = parse.urlencode(data).replace('%25', '%').encode('gbk')
	#post头
	sendHeaders = {'Host': 'jwgl.hunnu.edu.cn',
				   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0',
				   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
				   'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
				   'Accept-Encoding': 'gzip, deflate',
				   'Referer': url,
				   'Connection': 'keep-alive'}
	#登陆
	req = request.Request(url, headers = sendHeaders, data = decoded_data)
	resp = request.urlopen(req)
	#解析页面判断是否登陆成功
	soup = BeautifulSoup(resp.read(), 'lxml')
	return soup

'''
注销教务管理系统
'''
def logout(sessionID, studentNumber):
	#post主体
	global serverAddress
	url = '%s/(%s)/xs_main.aspx?xh=%s' % (serverAddress, sessionID, studentNumber)
	mainPageResp = request.urlopen(url)
	mainPage = BeautifulSoup(mainPageResp.read(), 'lxml')
	logout__VIEWSTATE = mainPage.find(attrs = {'name': '__VIEWSTATE'}).get('value')

	data = {'__EVENTTARGET': 'likTc',
			'__EVENTARGUMENT': '',
			'__VIEWSTATE': logout__VIEWSTATE}
	decoded_data = parse.urlencode(data).replace('%25', '%').encode('gbk')
	#post头
	sendHeaders = {'Host': 'jwgl.hunnu.edu.cn',
				   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0',
				   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
				   'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
				   'Accept-Encoding': 'gzip, deflate',
				   'Referer': url,
				   'Connection': 'keep-alive'}
	#注销
	req = request.Request(url, headers = sendHeaders, data = decoded_data)
	resp = request.urlopen(req)
	#解析页面判断是否登陆成功
	soup = BeautifulSoup(resp.read(), 'lxml')
	return soup

'''
刷新会话id进程
'''
class refreshSessionID(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		self.ifdo = True
		global serverAddress, sessionID
		while self.ifdo:
			#每5min刷新一次
			for i in range( 5 * 60):
				if not self.ifdo:
					break
				time.sleep(1)
			if not self.ifdo:
				break
			#获取初始页面
			startPageResp = request.urlopen(serverAddress)
			#获取跳转url
			jumpUrl = startPageResp.geturl()
			#获取会话id
			newSessionID = jumpUrl[jumpUrl.find('(') + 1:jumpUrl.find(')')]
			#分析初始页面源代码获取__VIEWSTATE
			startPage = BeautifulSoup(startPageResp.read(), 'lxml')
			__VIEWSTATE = startPage.find(attrs = {'name': '__VIEWSTATE'}).get('value')

			#更新sessionID
			oldSessionID = sessionID
			sessionID = newSessionID
			#尝试登陆
			mainPage = login(__VIEWSTATE, studentNumber, studentPwd)
			#通过页面中的提示信息判断是否登陆成功
			logout(oldSessionID, studentNumber)
			alert = mainPage.find('script').text
			if alert != '':
				print (alert[alert.index('(') + 2:alert.index(')') - 1])
				os.system('pause')
				exit()

	def stop(self):
		self.ifdo = False

'''
显示菜单
'''
def menu(title, menuList):
	selected = 0
	while True:
		print (title)
		for i in range(len(menuList)):
			if i == selected:
				print ('>>', end = '')
			else:
				print ('  ', end = '')
			print (menuList[i])
		while True:
			ch = msvcrt.getch()
			if ch == b'H':#上
				if selected > 0:
					selected -= 1
					os.system('cls')
					break
			elif ch == b'P':#下
				if selected < (len(menuList) - 1):
					selected += 1
					os.system('cls')
					break
			elif ch == b'\r':#回车
				return selected
			elif ch ==b'\x1b':#ESC
				return -1
	
'''
程序开始
'''
#设置服务器url
serverAddress = 'http://jwgl.hunnu.edu.cn'
#尝试从文件中读取账号密码，否则从input()获取
try:
	with open('jwglAccount.txt', 'r') as f:
		studentNumber = f.readline().strip()
		studentPwd = f.readline().strip()
except Exception as e:
	print ("请输入教务管理系统的账号：")
	studentNumber = input().strip()
	print ("请输入教务管理系统的密码：")
	studentPwd = input().strip()

#先用get方法获取带会话id的url
startPageResp = request.urlopen(serverAddress)
jumpUrl = startPageResp.geturl()
#获取会话id
sessionID = jumpUrl[jumpUrl.find('(') + 1:jumpUrl.find(')')]
#分析页面源代码，获取页面状态码
startPage = BeautifulSoup(startPageResp.read(), 'lxml')
__VIEWSTATE = startPage.find(attrs = {'name': '__VIEWSTATE'}).get('value')

#登陆
mainPage = login(__VIEWSTATE, studentNumber, studentPwd)
#通过页面中的提示信息判断是否登陆成功
alert = mainPage.find('script').text
if alert != '':
	print (alert[alert.index('(') + 2:alert.index(')') - 1])
	os.system('pause')
	exit()

#自动更新SessionID线程
refreshSessionID_thread = refreshSessionID()
refreshSessionID_thread.start()

#获取姓名
name = mainPage.find('span', id = 'xhxm').text
name = re.sub(r'\W', '', name)
name = re.sub(r'\d', '', name).replace('同学', '')

#获取所有二级界面链接
subUrlList = mainPage.find_all('a', target = 'zhuti')
#查找成绩页面url
key = '成绩'
for eachSubUrl in subUrlList:
	if eachSubUrl.get('onclick').find(key) != -1:
		scoreUrl = eachSubUrl.get('href')
		break
#查找等级考试成绩页面url
key = '等级'
for eachSubUrl in subUrlList:
	if eachSubUrl.get('onclick').find(key) != -1:
		gradeExamUrl = eachSubUrl.get('href')
		break

#获取查询成绩页面
scorePage = getScorePage(scoreUrl, name)
#获取查询成绩页面状态码
__VIEWSTATE = scorePage.find(attrs = {'name': '__VIEWSTATE'}).get('value')
#获取当前学年和学期
year, term = [x.text for x in scorePage.find_all(selected = 'selected')]

yearList = []
#获取学年下拉列表中的选项
currentYear = scorePage.find(selected = 'selected')
for i in range(4):
	currentYear = currentYear.previous_sibling.previous_sibling
	yearList.append(currentYear.text)

menuList = ['当前学期成绩', '当前学年成绩', '在校期间成绩', '等级考试成绩', '其他学年成绩']
orderList = ['学期', '学年', '所有']
title = '%s同学你好！你的学号为%s\n当前为%s学年 第%s学期\n请按上下键选择功能，回车键确定\n' % (name, studentNumber, year, term)
title_selectYear = '请选择需要查询的学年，请按上下键选择功能，回车键确定\n'

errorInfo = '\n身份验证失效，请重新登陆！'
while True:
	os.system('cls')
	#for i in range(60*20):
	#	print (i)
	#	time.sleep(1)
	order = menu(title, menuList)
	if order < 0 or order >= len(menuList):
		break
	elif order < len(orderList):
		os.system('cls')
		print ('%s为：' % menuList[order])
		score = getScore(scoreUrl, name, __VIEWSTATE, year, term, orderList[order])
		if len(score) == 0:
			print (errorInfo)
			break
		printScore(score)
	elif order == 3:
		os.system('cls')
		print ('%s为：' % menuList[order])
		gradeExamScore = getGradeExamScore(gradeExamUrl, name)
		if len(gradeExamScore) == 0:
			print (errorInfo)
			break
		printGradeExamScore(gradeExamScore)
	elif order == 4:
		os.system('cls')
		order = menu(title_selectYear, yearList)
		if order < 0 or order >= len(yearList):
			continue
		selectedYear = yearList[order]
		score = getScore(scoreUrl, name, __VIEWSTATE, selectedYear, term, '学年')
		if len(score) == 0:
			print (errorInfo)
			break
		os.system('cls')
		print ('%s学年的成绩为：' % selectedYear)
		printScore(score)
	os.system('pause')

print ('\n退出程序...')
refreshSessionID_thread.stop()
refreshSessionID_thread.join()
logout(sessionID, studentNumber)
os.system('pause')