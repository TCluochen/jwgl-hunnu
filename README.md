![](http://jwgl.hunnu.edu.cn/logo/logo_school.png)
教务管理系统
===================================  
由python3.5开发，仅在windows7 x64环境下测试过<br>
依赖：BeautifulSoup from bs4

3.0特性
-----------------------------------
包含3个文件：<br>
* jwgl_student.py<br>
* 教务管理系统3.0.py<br>
* jwglAccount.json<br>

###jwgl_student.py为模组
使用时可以
<pre>
from jwgl_student import *
</pre>
初始化一个教务管理系统类：
<pre>
jwgl = jwgl_student('学号', '密码', '服务器地址')
</pre>
登陆系统：
<pre>
jwgl.logIn() #成功返回True, 失败返回False
</pre>
登出系统（登出后必须重新登陆才能再次使用）：
<pre>
jwgl.logOut() #成功返回True, 失败返回False
</pre>
获取当前登陆状态：
<pre>
jwgl.isOnline() #在线返回True, 不在线返回False
</pre>
获取当前学年/学期（系统未开放则返回空）：
<pre>
jwgl.getYearTerm() #返回元祖:(当前学年，当前学期，[最近四个学年])
</pre>
获取成绩（学年和学期来自getYearTerm，条件可为'学期', '学年', '所有'）：
<pre>
jwgl.getScore(学年, 学期, 条件) #返回三维表格的成绩，即成绩查询页面的两个表格
</pre>
获取等级考试成绩：
<pre>
jwgl.getGradeExamScore() #返回三维表格的成绩
			#即为等级考试查询界面的一个表格
			#第一维长度为1
</pre>

###教务管理系统3.0.py为自己写的调用程序
书写混乱。仅供本人凭吊和引以为戒。


###jwglAccount.json为json文件
形如
<pre>
{
  "serverAddress": [
    {
      "address": "http://202.197.120.56"
    },
    {
      "address": "http://202.197.120.57"
    }
  ],
  "stduentPwd": "your password",
  "studentNumber": "your number"
}
</pre>
供 教务管理系统3.0.py 使用

2.0特性
-----------------------------------
实验版本，面向过程+函数式编程，书写混乱。仅供本人凭吊和引以为戒。