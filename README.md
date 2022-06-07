# get_reserve_gym  
体育館の予約空き状況をLINEで送信するスクリプト  
  
# DEMO  
![image](https://user-images.githubusercontent.com/98931080/172421527-3d547ee7-6369-4864-bd73-80c01d9ad4aa.png)
  
# Requirement  
gspread              5.1.1  
requests             2.27.1  
PyYAML               6.0  
oauth2client         4.1.3  
selenium             4.1.0  
webdriver-manager    3.5.4  
  
# Installation  
```bash
pip install gspread  
pip install requests  
pip install pyyaml  
pip install oauth2client  
pip install selenium  
pip install webdriver_manager  
```
# Usage
```bash
cd get_reserve_gym  
python get_reserve_gym.py  
```
# Note  
変数格納先：`param.yml`   
### gspreadの認証情報  
project_id: ''  
private_key_id: ''  
private_key: ''  
client_email: ''  
client_id: ''  
client_x509_cert_url: ''  
### スプレッドシートのID
ssid: ''
### LINE APIのトークン
token: ''
