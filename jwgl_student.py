import bs4, os, time, re, threading
from bs4 import BeautifulSoup
from urllib import request, parse, error

'''
教务管理系统类
'''
class jwgl_student():
	def __init__(self, studentNumber, studentPwd, serverAddress='http://jwgl.hunnu.edu.cn'):
		#加锁，当“刷新seesionID进程”访问本类时，获取信息等方法必须等待
		self.lock = threading.Lock()
		self.refreshSessionID_thread = refreshSessionID(self)

		#账号密码
		self.studentNumber = studentNumber
		self.studentPwd = studentPwd

		#服务器地址和会话id
		self.serverAddress = serverAddress
		self.sessionID = ''

		#查询成绩所需的__VIEWSTATE
		self.score__VIEWSTATE = ''

		self.baseHeaders = {'Host': serverAddress.replace('http://', ''),
							'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0',
							'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
							'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
							'Accept-Encoding': 'gzip, deflate',
							'Referer': '',
							'Connection': 'keep-alive'}

	#登陆
	def logIn(self):
		#判断是否已经获取到了可用的会话id
		if self.sessionID == '':
			#用get方法获取跳转链接
			startPageResp = request.urlopen(self.serverAddress)
			jumpUrl = startPageResp.geturl()
			#从跳转链接中获取会话id
			sessionID = jumpUrl[jumpUrl.find('(') + 1:jumpUrl.find(')')]
			startPage = BeautifulSoup(startPageResp.read(), 'lxml')
			#获取页面状态码
			self.logIn__VIEWSTATE = startPage.find(attrs={'name': '__VIEWSTATE'}).get('value')
			logInUrl = '%s/(%s)/default2.aspx' % (self.serverAddress, sessionID)
		else:
			#判断是否重复登陆
			if self.isOnline():
				#开始自动刷新sessionID
				if not self.refreshSessionID_thread.isAlive():
					self.refreshSessionID_thread.start()
				return True
			logInUrl = '%s/(%s)/default2.aspx' % (self.serverAddress, self.sessionID)

		#post头
		logInHeaders = dict(self.baseHeaders)
		logInHeaders['Referer'] = logInUrl

		#post数据
		data = {'__VIEWSTATE': self.logIn__VIEWSTATE,
				'TextBox1': self.studentNumber,
				'TextBox2': self.studentPwd,
				'TextBox3': '',
				'RadioButtonList1': parse.quote('学生', encoding='gbk'),
				'Button1': '',
				'lbLanguage': ''}
		decoded_data = parse.urlencode(data).replace('%25', '%').encode('gbk')

		#登陆
		req = request.Request(logInUrl, headers=logInHeaders, data=decoded_data)
		#错误处理
		try:
			resp = request.urlopen(req)
		except error.HTTPError as e:
			if e.code == 400:
				print ('程序出错！发送的数据包有误！')
			return False

		logInPage = BeautifulSoup(resp.read(), 'lxml')
		#判断是否登陆成功
		if logInPage.title.text.find('请登录') == -1:
			#登陆成功，设置会话id
			self.sessionID = sessionID
			#获取姓名
			self.name = logInPage.find('span', id='xhxm').text
			self.name = re.sub(r'\W', '', self.name)
			self.name = re.sub(r'\d', '', self.name).replace('同学', '')

			#获取所有二级界面链接
			self.subUrlList = logInPage.find_all('a', target='zhuti')

			#设置当前学年/学期
			self.__setYearTerm()

			#开始自动刷新sessionID
			if not self.refreshSessionID_thread.isAlive():
				self.refreshSessionID_thread.start()

			return True
		else:
			#登陆失败
			return False
	
	#登出
	def logOut(self, stopRefreshRessionID=True):
		#判断是否已经登出
		if not self.isOnline():
			if stopRefreshRessionID:
				if self.refreshSessionID_thread.isAlive():
					self.refreshSessionID_thread.stop()
					self.refreshSessionID_thread.join()
			#print ('你当前已经登出！')
			return True
		#设置登出url
		logOutUrl = '%s/(%s)/xs_main.aspx?xh=%s' % (self.serverAddress, self.sessionID, self.studentNumber)

		#解析主界面获取__VIEWSTATE
		mainPageResp = request.urlopen(logOutUrl)
		mainPage = BeautifulSoup(mainPageResp.read(), 'lxml')
		logOut__VIEWSTATE = mainPage.find(attrs={'name': '__VIEWSTATE'}).get('value')

		#post头
		logOutHeaders = dict(self.baseHeaders)
		logOutHeaders['Referer'] = logOutUrl

		#post数据
		data = {'__EVENTTARGET': 'likTc',
				'__EVENTARGUMENT': '',
				'__VIEWSTATE': logOut__VIEWSTATE}
		decoded_data = parse.urlencode(data).replace('%25', '%').encode('gbk')

		#注销
		req = request.Request(logOutUrl, headers=logOutHeaders, data=decoded_data)
		resp = request.urlopen(req)

		#判断是否注销成功
		if not self.isOnline():
			self.sessionID = ''
			if stopRefreshRessionID:
				if self.refreshSessionID_thread.isAlive():
					self.refreshSessionID_thread.stop()
					self.refreshSessionID_thread.join()
			return True
		else:
			#print ('注销失败！')
			return False
	
	#判断当前是否在线
	def isOnline(self):
		if self.sessionID == '':
			return False
		#解析
		logInUrl = '%s/(%s)/xs_main.aspx?xh=%s' % (self.serverAddress, self.sessionID, self.studentNumber)
		resp = request.urlopen(logInUrl)
		soup = BeautifulSoup(resp, 'lxml')
		return soup.title.text.find('请登录') == -1

	#设置当前学年/学期和最近学年列表
	def __setYearTerm(self):
		#获取成绩页面url
		scoreUrl = self.__getSubUrl('在校成绩')
		if scoreUrl == '':
			print ('查询成绩接口暂未开放！')
			return
		scoreUrl = '%s/(%s)/%s' % (self.serverAddress, self.sessionID, scoreUrl)
		#将姓名编码至gbk
		decoded_name = parse.quote(self.name, encoding='gbk')
		#替换中文
		scoreUrl = scoreUrl.replace(self.name, decoded_name)

		#post头
		scoreHeaders = dict(self.baseHeaders)
		scoreHeaders['Referer'] = scoreUrl

		req = request.Request(scoreUrl, headers=scoreHeaders)
		#解析页面获取信息
		soup = BeautifulSoup(request.urlopen(req).read(), 'lxml')
		self.score__VIEWSTATE = soup.find(attrs={'name': '__VIEWSTATE'}).get('value')
		self.currentYear, self.currentTerm = [x.text for x in soup.find_all(selected='selected')]
		self.yearList = []
		#获取学年下拉列表中的选项
		currentYear = soup.find(selected='selected')
		for i in range(4):
			currentYear = currentYear.previous_sibling.previous_sibling
			self.yearList.append(currentYear.text)

	#设置当前学年/学期和最近学年列表
	def getYearTerm(self):
		if self.score__VIEWSTATE == '':
			return ()
		else:
			return (self.currentYear, self.currentTerm, self.yearList)

	#查找二级页面
	def __getSubUrl(self, key):
		for eachSubUrl in self.subUrlList:
			if eachSubUrl.get('onclick').find(key) != -1:
				return eachSubUrl.get('href')
		return ''

	#从页面中获取所有成绩表格中的值
	def __getTableFromPage(self, soup):
		tables = soup.find_all(class_='datelist')
		allScore = []
		for eachTable in tables:
			#获取每个表格的内容
			lines = []
			for child in eachTable.children:
				if type(child) != bs4.element.Tag:
					continue
				#将所有td中的内容复制到course中
				cells = child.find_all('td')
				lines.append([cell.text for cell in cells])
			#添加进总表
			allScore.append(lines)
		return allScore

	#获取成绩
	def getScore(self, year, term, condition):
		#获取成绩页面url
		scoreUrl = self.__getSubUrl('在校成绩')
		if scoreUrl == '':
			print ('查询成绩接口暂未开放！')
			return []
		scoreUrl = '%s/(%s)/%s' % (self.serverAddress, self.sessionID, scoreUrl)
		#将姓名编码至gbk
		decoded_name = parse.quote(self.name, encoding='gbk')
		#替换中文
		scoreUrl = scoreUrl.replace(self.name, decoded_name)

		#post头
		scoreHeaders = dict(self.baseHeaders)
		scoreHeaders['Referer'] = scoreUrl
			
		#post数据
		data = {'__VIEWSTATE': self.score__VIEWSTATE,
				'ddlXN': year,
				'ddlXQ': term}
		if condition == '所有':
			data['Button2'] = parse.quote('在校学习成绩查询', encoding='gbk')
		elif condition == '学年':
			data['Button5'] = parse.quote('按学年查询', encoding='gbk')
		elif condition == '学期':
			data['Button1'] = parse.quote('按学期查询', encoding='gbk')
		else:
			print ('查询条件有错！')
			os.system('pause')
			return []
		decoded_data = parse.urlencode(data).replace('%25', '%').encode('gbk')

		#发送post
		req = request.Request(scoreUrl, headers=scoreHeaders, data=decoded_data)
		#解析页面获取成绩
		soup = BeautifulSoup(request.urlopen(req).read(), 'lxml')		
		return self.__getTableFromPage(soup)

	#获取等级考试成绩
	def getGradeExamScore(self):
		#获取等级考试成绩页面url
		gradeExamScoreUrl = self.__getSubUrl('等级考试')
		if gradeExamScoreUrl == '':
			print ('查询成绩接口暂未开放！')
			return []
		gradeExamScoreUrl = '%s/(%s)/%s' % (self.serverAddress, self.sessionID, gradeExamScoreUrl)
		#将姓名编码至gbk
		decoded_name = parse.quote(self.name, encoding='gbk')
		#替换中文
		gradeExamScoreUrl = gradeExamScoreUrl.replace(self.name, decoded_name)

		#post头
		gradeExamScoreHeaders = dict(self.baseHeaders)
		gradeExamScoreHeaders['Referer'] = gradeExamScoreUrl

		#发送post
		req = request.Request(gradeExamScoreUrl, headers=gradeExamScoreHeaders)
		#解析页面获取等级考试成绩
		soup = BeautifulSoup(request.urlopen(req).read(), 'lxml')
		return self.__getTableFromPage(soup)

'''
刷新会话id进程
'''
class refreshSessionID(threading.Thread):
	def __init__(self, jwglAccount):
		threading.Thread.__init__(self)
		self.jwglAccount = jwglAccount

	#线程开始
	def run(self):
		self.ifdo = True
		while self.ifdo:
			#每5min刷新一次
			for i in range( 5 * 60):
				if not self.ifdo:
					break
				time.sleep(1)
			if not self.ifdo:
				break
			#刷新数据中，数据加锁
			self.jwglAccount.lock.acquire()
			self.jwglAccount.logOut(stopRefreshRessionID=False)
			self.jwglAccount.logIn()
			#刷新完成，数据解锁
			self.jwglAccount.lock.release()

	#线程结束
	def stop(self):
		self.ifdo = False

'''
程序开始
'''

if __name__ == '__main__':
	serverAddressList = ['http://jwgl.hunnu.edu.cn', 'http://202.197.120.56', 'http://202.197.120.57']
	for eachServerAdress in serverAddressList:
		myAccount = jwgl_student('201430185038', 'xxxxxx', serverAddress = eachServerAdress)
		if myAccount.logIn():
			print ('登陆成功')
			print (myAccount.getScore('2014-2015', '1', '学期'))
		else:
			print ('登陆失败，请检查账号和密码')

	os.system('pause')