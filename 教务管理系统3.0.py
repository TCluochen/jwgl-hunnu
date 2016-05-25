import json, os, sys, msvcrt
from jwgl_student import *

os.system("color 70")
os.system("title 教务管理系统v3.0")

'''
显示菜单
'''
def menu(title, menuList, order=0):
    selected = order
    while True:
        print (title)
        print ('上下键选择，回车键确定，ESC键退出\n')
        for i in range(len(menuList)):
            if i == selected:
                print ('>>', end='')
            else:
                print ('  ', end='')
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
筛选表格数据
接收的数据形如
[
 [
  ['表格1头1', '表格1头2'],
  ['表格1行1数据1', '表格1行1数据2'],
  ['表格1行2数据1', '表格1行2数据2']
 ],[
  ['表格2头1', '表格2头2'],
  ['表格2行1数据1', '表格2行1数据2'],
  ['表格2行2数据1', '表格2行2数据2']
 ]
]
'''
def filterTable(tables):
    keyWords = [set(['等级考试名称', '课程名称', '学分', '成绩']),
                set(['课程名称', '补考成绩'])]
    afterFilter = []
    for tableIndex in range(len(tables)):
        table = []
        filterIndexList = set()
        for tableTitleIndex in range(len(tables[tableIndex][0])):
            if tables[tableIndex][0][tableTitleIndex] in keyWords[tableIndex]:
                filterIndexList.add(tableTitleIndex)
        for eachLine in tables[tableIndex]:
            line = []
            for eachColumn in range(len(eachLine)):
                if eachColumn in filterIndexList:
                    line.append(eachLine[eachColumn])
            table.append(line)
        afterFilter.append(table)
    return afterFilter

'''
格式化输出成绩
'''
def printScore(tables):
    if len(tables) == 2:
        title = ['************************期末成绩************************', '************************补考成绩************************']
    elif len(tables) == 1:
        title = ['**********************等级考试成绩**********************']
    #设置列宽
    columnWidth = [30, 15, 15, 10, 10, 10]
    splitLine = '-' * 60
    for tableIndex in range(len(tables)):
        #判断是否只有表头
        if len(tables[tableIndex]) <= 1:
            continue
        print (title[tableIndex])
        print (splitLine)
        for eachLine in tables[tableIndex]:
            for columnIndex in range(len(eachLine)):
                if len(eachLine[columnIndex]) > columnWidth[columnIndex] / 2:
                    try:
                        eachLine[columnIndex] = eachLine[columnIndex][:eachLine[columnIndex].find('（')]
                    except:
                        pass
                space = columnWidth[columnIndex] - len(eachLine[columnIndex]) * 2
                for ch in eachLine[columnIndex]:
                    if ch <= chr(255):
                        space += 1
                print (eachLine[columnIndex], end=' ' * space)
            print ()
        print ()
    print ()

#获取账号密码
try:
    #尝试从配置文件中读取
    with open('jwglAccount.json', 'r') as f:
        account = json.load(f)
except Exception as e:
    account = {}
    print ('请输入教务管理系统的账号：')
    account['studentNumber'] = input().strip()
    print ('请输入教务管理系统的密码：')
    account['stduentPwd'] = input().strip()
    account['serverAddress'] = []
    account['serverAddress'].append({'address': 'http://202.197.120.56'})
    account['serverAddress'].append({'address': 'http://202.197.120.57'})

#启动服务
jwgl = jwgl_student(account['studentNumber'], account['stduentPwd'], account['serverAddress'][0]['address'])
#判断是否登陆成功
if not jwgl.logIn():
    print ('登陆失败，请检查账号密码！(如有配置文件，则请检查同目录下jwglAccount.json文件)')
    os.system('pause')
    exit()
else:
    with open('jwglAccount.json', 'w') as f:
        json.dump(account, f, indent=2)

try:
    (currentYear, currentTerm, yearList) = jwgl.getYearTerm()
    title = '%s同学你好！你的学号为%s\n当前为%s学年，第%s学期' % (jwgl.name, jwgl.studentNumber, currentYear, currentTerm)
    menuList = ['等级考试成绩', '当前学期成绩', '当前学年成绩', '在校期间成绩', '其他学年成绩']
    orderList = ['', '学期', '学年', '所有']
    title_selectYear = '请选择需要查询的学年'
except:
    title = '%s同学你好！你的学号为%s\n成绩查询接口暂未开放，不能查询成绩' % (jwgl.name, jwgl.studentNumber)
    menuList = ['等级考试成绩']

errorInfo = '身份验证失效，请重新登陆！'
order = 0
orderYear = 0
#选择菜单
while True:
    os.system('cls')
    #for i in range(60*20):
    #    print (i)
    #    time.sleep(1)
    order = menu(title, menuList, order)
    if order < 0 or order >= len(menuList):
        break
    elif order == 0:
        os.system('cls')
        print ('%s为：' % menuList[order])
        gradeExamScore = jwgl.getGradeExamScore()
        if len(gradeExamScore) == 0:
            print (errorInfo)
            break
        gradeExamScore = filterTable(gradeExamScore)
        printScore (gradeExamScore)
        os.system('pause')
    elif order == 4:
        #选择学年
        while True:
            os.system('cls')
            temp =     menu(title_selectYear, yearList, orderYear)
            if temp < 0 or temp >= len(yearList):
                break
            orderYear = temp
            selectedYear = yearList[orderYear]
            os.system('cls')
            print ('%s学年成绩为：' % selectedYear)
            #获取学年成绩
            score = jwgl.getScore(selectedYear, '1', '学年')
            if len(score) == 0:
                print (errorInfo)
                break
            score = filterTable(score)
            printScore (score)
            os.system('pause')
    else:
        os.system('cls')
        print ('%s为：' % menuList[order])
        score = jwgl.getScore(currentYear, currentTerm, orderList[order])
        if len(score) == 0:
            print (errorInfo)
            break
        score = filterTable(score)
        printScore (score)
        os.system('pause')    

print ('\n退出程序...')
jwgl.logOut()
os.system('pause')
