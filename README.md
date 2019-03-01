# ZeroJudge_Exporter
## 一鍵匯出您在高中生解題系統上所有 **AC** 的程式碼

---

在高中生解題系統上寫了好多程式，但是有的有的用電腦寫，有的用手機寫，還有的在學校電腦寫。想要分享傳承給學弟們，卻發覺整理實在有夠麻煩？

所以，「ZeroJudge Exporter」誕生了！

---

## 需求
- Python 3
- selenium
- beautifulsoup4
- chromedriver

## 功能
### 登入
因為 ZeroJudge 不提供 API 且登入時必須通過 reCAPTCHA，故使用 selenium + chromedriver 讓使用者手動登入後將 jsessionid 保存後再以 requests 把程式碼抓下來。

不曉得是不是由於使用 selenium 所以感覺人跡驗證特別難過。也可以用 Google 登入，只是我的 Google 有 2FA。

亦支援從已登入的瀏覽器中提出 jsessionid 快速登入。請按 F12 叫出開發者工具。Chrome 在 Application 分頁中 有個 cookies，找到長度為 32 的 hex 字串的 jsessionid 複製並選擇自訂 cookies。