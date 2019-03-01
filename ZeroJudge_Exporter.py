import html
import json
import os
import os.path
import pickle
import sys
import tkinter
from tkinter import filedialog, messagebox, simpledialog, ttk

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def foo(event):
    i = tree.focus()
    text.delete(1.0, tkinter.END)
    text.insert(tkinter.END, d[tree.item(i)['text']]['code'])


def bar():
    lang = {'C': '.c', 'CPP': '.cpp', 'PYTHON': '.py'}
    path = filedialog.askdirectory()
    for i in d:
        x = 1
        name = path + '/' + i[:4]
        while os.path.exists(name + lang[d[i]['lang']]):
            name = '{}/{}-{}'.format(path, i[:4], x)
            x += 1
        name += lang[d[i]['lang']]
        with open(name, 'w') as f:
            f.write(d[i]['code'])
    messagebox.showinfo("Info", '儲存成功')

try:
    browser = webdriver.Chrome()  # 初始化瀏覽器
except WebDriverException:
    messagebox.showerror("Error", "找不到 Chrome Driver")
    sys.exit()
tk = tkinter.Tk()  # 初始化視窗
tk.title('ZeroJudge 匯出下載工具')
tree = ttk.Treeview(tk, columns=('num', 'date', 'result', 'lang'))
tree.heading('#0', text='title')
tree.heading('#1', text='num')
tree.heading('#2', text='date')
tree.heading('#3', text='result')
tree.heading('#4', text='lang')
tree.column('#0')
tree.column('#1', width=100)
tree.column('#2', width=100)
tree.column('#3', width=100)
tree.column('#4', width=100)
tree.bind('<<TreeviewSelect>>', foo)
tree.pack(padx=10, pady=10, fill='y', side='left')
text = tkinter.Text(tk)
text.pack(padx=10, pady=10, fill='y', side='right')
btn = tkinter.Button(tk, text='一鍵儲存', command=bar)
btn.pack(fill="none", expand=True, side='bottom')

# 詢問是否使用存在的 cookie 直接登入
if messagebox.askyesno("快速登入", "自訂 Cookies？"):
    jsessionid = simpledialog.askstring("Cookies", "JSESSIONID: ", parent=tk)
    if jsessionid is not None:
        browser.get("https://zerojudge.tw/")
        browser.execute_script(
            '''$('head').append('<link rel="stylesheet" href="https://bootswatch.com/3/cyborg/bootstrap.css" type="text/css" / > ');''')
        browser.add_cookie({'name': 'JSESSIONID', 'value': jsessionid})
# 尋找目錄是否有存在的 cookie 直接登入
elif os.path.exists("cookies.pkl"):
    browser.get("https://zerojudge.tw/")
    browser.execute_script(
        '''$('head').append('<link rel="stylesheet" href="https://bootswatch.com/3/cyborg/bootstrap.css" type="text/css" / > ');''')
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        browser.add_cookie(cookie)
browser.get("https://zerojudge.tw/Login")
browser.execute_script(
    '''$('head').append('<link rel="stylesheet" href="https://bootswatch.com/3/cyborg/bootstrap.css" type="text/css" / > ');''')
# 如果還未登入
while not browser.current_url in ["https://zerojudge.tw/#", "https://zerojudge.tw/"]:
    if browser.current_url == "https://zerojudge.tw/Login":
        # 等待使用者登入
        btn = browser.find_element_by_xpath(
            "/html/body/div[4]/div[2]/div[2]/form/button[1]")
        WebDriverWait(browser, timeout=1000, poll_frequency=1).until(
            EC.staleness_of(btn))
browser.get("https://zerojudge.tw/UserStatistic")  # 進入使用者解題統計葉面
browser.execute_script(
    '''$('head').append('<link rel="stylesheet" href="https://bootswatch.com/3/cyborg/bootstrap.css" type="text/css" / > ');''')
a = browser.find_element_by_xpath(
    "/html/body/div[3]/div/div[1]/div/div[2]/p/a[1]")
user = browser.find_element_by_xpath(
    '/html/body/div[3]/div/div[1]/div/div[2]/h4/span[1]/a').get_attribute("title")
url = a.get_attribute("href")
# 保存 cookie
cookies = browser.get_cookies()
pickle.dump(cookies, open("cookies.pkl", "wb"))
browser.close()  # 關閉瀏覽器

d = dict()
s = requests.Session()
for cookie in cookies:
    s.cookies.set(cookie['name'], cookie['value'])
while True:
    lst = s.get(url)
    soup = BeautifulSoup(lst.text, 'html.parser')
    if '沒有發現任何資料!!' in soup.select_one('body > div.container > div > table > tr:nth-child(2) > td').text:
        break
    for i in soup.findAll('tr'):
        if i.has_attr("solutionid"):
            tds = i.findAll('td')
            title = tds[2].text.lstrip().replace(
                '\r', '').replace('\n', '').split(' -- #')[0]
            num = tds[0].getText().lstrip().replace('\r', '').replace('\n', '')
            date = tds[5].getText().lstrip().replace(
                '\r', '').replace('\n', '')
            result = tds[3].select_one('#summary').text
            lang = tds[4].select_one('#btn_SolutionCode').text
            if title in d:
                x = 1
                while "{}-{}".format(title, x) in d:
                    x += 1
                title = "{}-{}".format(title, x)
            tree.insert('', 'end', text=title, values=(
                num, date, result, lang))
            d[title] = {'num': num, 'date': date, 'lang': lang, 'result': result, 'code': html.unescape(s.get(
                'https://zerojudge.tw/Solution.json?data=Code&solutionid=' + tds[0].text).json()['code'])}
    url = 'https://zerojudge.tw/Submissions' + \
        soup.select_one('#pagging').find('a', title='lastpage=')['href']
with open('zj.json', 'w') as f:
    json.dump(d, f)
tk.mainloop()
