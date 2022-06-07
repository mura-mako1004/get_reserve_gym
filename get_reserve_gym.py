import itertools
import random
import time

import gspread
import requests
import yaml
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

# 変数格納yml
with open('get_reserve_gym/param.yml') as file:
    config = yaml.safe_load(file)


# seleniumで体育館の空き情報データを取得する
def get_values():
    # 1～3秒の間ランダムな数値を取得
    sec = random.uniform(1, 3)
    # seleniumのdriverを設定
    options = webdriver.ChromeOptions()
    with webdriver.Chrome(ChromeDriverManager().install(), options=options) as driver:
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        # e-kanagawaのURL
        driver.get('https://yoyaku.e-kanagawa.lg.jp/Ebina/Web/Wg_ModeSelect.aspx')
        driver.implicitly_wait(60)
        # 施設予約システムメニュー
        driver.find_element_by_name("btnNormal").click()
        time.sleep(sec)
        driver.implicitly_wait(30)
        # 1. 空き照会・抽選申込・予約申込
        driver.find_element_by_name("rbtnYoyaku").click()
        time.sleep(sec)
        driver.implicitly_wait(30)
        # 次頁
        driver.find_element_by_name("btnNextPage").click()
        time.sleep(sec)
        driver.implicitly_wait(30)
        # 次頁
        driver.find_element_by_name("btnNextPage").click()
        time.sleep(sec)
        driver.implicitly_wait(30)
        # えびな市民活動Ｃ　ビナスポ
        driver.find_element_by_name("dgTable$ctl03$chkShisetsu").click()
        time.sleep(sec)
        # 次へ >>
        driver.find_element_by_name("ucPCFooter$btnForward").click()
        time.sleep(sec)
        driver.implicitly_wait(30)
        # 1ヶ月
        driver.find_element_by_name("rbtnMonth").click()
        time.sleep(sec)
        # 土
        driver.find_element_by_name("chkSat").click()
        time.sleep(sec)
        # 日
        driver.find_element_by_name("chkSun").click()
        time.sleep(sec)
        # 祝
        driver.find_element_by_name("chkHol").click()
        time.sleep(sec)
        # 次へ >>
        driver.find_element_by_name("ucPCFooter$btnForward").click()
        time.sleep(sec)
        driver.implicitly_wait(30)
        # tableのxpathを格納するための変数
        xpath1 = '//*[@id="dlRepeat_ctl00_tpItem_dgTable"]/tbody/tr['
        xpath2 = ']/td['
        xpath3 = ']'
        count = 0
        # 大多目的室・小多目的室の△をクリック
        for i in range(3, 15):
            try:
                for j in range(3, 6):
                    xpath = xpath1 + str(j) + xpath2 + str(i) + xpath3
                    value = driver.find_element_by_xpath(xpath)
                    text = value.text
                    if "△" in text:
                        count += 1
                        if count <= 20:
                            driver.find_element_by_xpath(xpath).click()
                            time.sleep(1)
            except:
                break
        # △が1つ以上存在した場合の処理
        if count > 0:
            #  次へ >>
            driver.find_element_by_name("ucPCFooter$btnForward").click()
            time.sleep(sec)
            driver.implicitly_wait(30)
            # tableのxpathを格納するための変数
            xid1 = '//*[@id="dlRepeat_ctl0'
            xid2 = '_tpItem_dgTable"]/tbody/tr['
            xid3 = ']/td['
            xid4 = ']'
            # 情報格納用list
            list1 = [['\n', '', '', '', '']]
            # 送信用のlistを作成
            for i in range(0, 10):
                try:
                    xid = xid1 + str(i) + xid2 + str(1) + xid3 + str(1) + xid4
                    # 日時
                    datevalue = driver.find_element_by_xpath(xid).text
                    datevalue = datevalue.replace('\n', '')
                    xid = xid1 + str(i) + xid2 + str(2) + xid3 + str(1) + xid4
                    # 場所
                    placevalue = driver.find_element_by_xpath(xid).text
                    # 時間
                    timelist = ""
                    # 20時までの連続で空いている時間を一つにまとめる
                    for j in range(3, 14):
                        xid = xid1 + str(i) + xid2 + str(2) + \
                            xid3 + str(j) + xid4
                        value = driver.find_element_by_xpath(xid).text
                        if "○" in value:
                            xid = xid1 + str(i) + xid2 + str(1) + \
                                xid3 + str(j) + xid4
                            timevalue = driver.find_element_by_xpath(xid).text
                            timevalue = timevalue.replace('\n', '')
                            hantei = timevalue[0:5]
                            if hantei in timelist:
                                timeindex = timelist.find(hantei)
                                timelist = timelist[0:timeindex] + \
                                    timevalue[6:]
                            else:
                                timelist += '\n' + timevalue
                    if len(timelist) > 0:
                        list2 = [datevalue, "\n", placevalue, timelist, "\n"]
                        list1.append(list2)
                except:
                    break
        else:
            # 20時までの空きがなかった場合
            list1 = [[]]
    return list1


# スプレッドシートに値を書き込む
def write_spread(values):
    # スプレッドシートのscope
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    # 認証情報
    credential = {
        "type": "service_account",
        "project_id": config['project_id'],
        "private_key_id": config['private_key_id'],
        "private_key": config['private_key'],
        "client_email": config['client_email'],
        "client_id": config['client_id'],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": config['client_x509_cert_url']
    }
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        credential, scope)
    # スプレッドシート情報
    gc = gspread.authorize(credentials)
    sheet = gc.open_by_key(config['ssid']).sheet1
    # スプレッドシートの値を取得
    list_row = sheet.get_all_values()
    # 値を比較して変更点を確認する
    if(list_row != values):
        # スプレッドシートのクリア
        sheet.clear()
        # スプレッドシートの値を更新
        sheet.update('A1', values)
        return True
    else:
        return False


# lineAPIでメッセージを送信
def post_line(values):
    text = ''.join(list(itertools.chain.from_iterable(values)))
    # 発行されたトークン
    headers = {"Authorization": f"Bearer {config['token']}"}
    # 送信するデータ
    data = {
        "message": text
    }
    # post
    requests.post(
        "https://notify-api.line.me/api/notify",
        headers=headers,
        data=data,
    )


# スクリプトの実行
def main():
    values = get_values()
    if write_spread(values):
        post_line(values)


if __name__ == '__main__':
    main()
