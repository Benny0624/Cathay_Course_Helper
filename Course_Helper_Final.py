#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Import selenium Packages
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchWindowException

# Import other Packages
import getpass
import time
import threading

# Login 
def Login(Acnt,Pwd):
    try:
        wait = WebDriverWait(BROWSER, 30)
        # Send Key
        Acnt_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        Acnt_input.send_keys(Acnt)
        Pwd_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        Pwd_input.send_keys(Pwd)
        # Press Button
        login_btn = wait.until(EC.presence_of_element_located((By.ID, "btnLogin")))
        login_btn.click()
    except NoSuchElementException as e: 
        print('Error:', e)
        print("Can not find Elements !")
        
        
# 按到國泰學習網
def ToCourse():
    try:
        wait = WebDriverWait(BROWSER, 15)
        # window_before 
        window_before = BROWSER.window_handles[0]
        # 3 layer content
        wait.until(EC.presence_of_element_located((By.XPATH, "//a[.='行政資源']"))).click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//a[.='學習與發展']"))).click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//a[.='國泰學習網']"))).click()
        
        # window_after
        window_after = BROWSER.window_handles[1]
        BROWSER.switch_to.window(window_after)
        
        # 待修課程
        wait.until(EC.presence_of_element_located((By.XPATH, \
                                         "//mat-icon[@fonticon='icon-book-open']"))).click()        
        # 最新加入的待修(最下面)
        wait.until(EC.presence_of_element_located((By.XPATH, \
                                         "//mat-icon[.='play_arrow']"))).click()
    except NoSuchElementException as e:
        print('Error:', e)
        print("Can not find Elements !")
        
# AutoPlay
class AutoPlay:
    def __init__(self):
        # Thread control param
        self.T1 = 0
        
    # 切進學習網iframe
    def CutIn(self):
        BROWSER.switch_to.frame('content')
        BROWSER.switch_to.frame('playContent')
        BROWSER.switch_to.frame('Content')
    
    # 取得影片時間
    def GetTime(self):
        BROWSER.switch_to.default_content()
        self.CutIn()
        wait = WebDriverWait(BROWSER, 5)
        child1 = wait.until(EC.presence_of_element_located((By.XPATH, "//span[.= 'Current Time']")))
        child2 = wait.until(EC.presence_of_element_located((By.XPATH, "//span[.= 'Duration Time']")))
        return child1, child2
        
    # 取得NEXT按鈕狀態
    def GetNXT(self):
        # 切到下 banner
        BROWSER.switch_to.default_content()
        BROWSER.switch_to.frame('banner')
        wait = WebDriverWait(BROWSER, 2)
        
        # Get nextbtn
        nextbtn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@class= 'btn btn-primary'][@onclick= 'javascript:goNext()']")))
        return nextbtn
    
    # 要否續播彈出視窗處理
    def PopupCheck(self):
        while True:
            len_handles=len(BROWSER.window_handles)
            wait = WebDriverWait(BROWSER, 10)
            # T1 Not operating and has Popup
            if(self.T1 == 0 and len_handles == 4):
                try:

                    # Switch to Popup page
                    print('Swich to Popup page')
                    handles=BROWSER.window_handles
                    BROWSER.switch_to.window(handles[3])
                    # Click continue
                    print('Click continue')
                    wait.until(EC.presence_of_element_located((By.XPATH, "//button[.='繼續播放']"))).click()
                    # Switch back
                    print('Swich Back')
                    handles=BROWSER.window_handles
                    BROWSER.switch_to.window(handles[2])

                except NoSuchElementException as e:
                    print('Error:', e)
                    print('PopupCheck break')
                    break
                    
            # T1 Still operating or No Popup
            elif(self.T1 == 1 or len_handles != 4):
                pass
            # T1 already break(T1 == 2)
            else:
                print('PopupCheck break')
                break
            
            # Wait 20 sec
            time.sleep(20)
    
    # 課程是否仍在播放判別
    def IsPlayOrEnd(self):

        # Whether New to the course
        New = True

        while True:
            # Thread 1
            self.T1 = 1
            try:
                # Play
                BROWSER.switch_to.default_content()
                Play = BROWSER.find_elements_by_xpath("//iframe[@id = 'content']")
                if(Play != [] and New == True):
                    # wait 5 sec
                    time.sleep(5)
                    print('First play buttom click')
                    BROWSER.find_element_by_xpath("//iframe[@id = 'content']").click()
                    # wait 60 sec to further check time
                    time.sleep(60)

                # Store play status
                BROWSER.switch_to.default_content()
                Play = BROWSER.find_elements_by_xpath("//iframe[@id = 'content']")
           
                # Get NXT
                nextbtn = self.GetNXT()
                
                # Get time
                child1, child2 = self.GetTime()
                C1 = child1.is_displayed()
                C2 = child2.is_displayed()
                

                # Pause to check time(if time not displayed)
                Pause = False
                if(Play != [] and not (C1 and C2)):
                    BROWSER.switch_to.default_content()
                    print('Pause buttom click')
                    BROWSER.find_element_by_xpath("//iframe[@id = 'content']").click()
                    Pause = True
                    # Get time
                    child1, child2 = self.GetTime()
              
                # Error control                
                if((child1.find_element_by_xpath("..").text == '' or child2.find_element_by_xpath("..").text == '') and nextbtn != ''):
                    print('Next Buttom click')
                    nextbtn.click()
                    # New
                    New = True
                    
                    # T1 reset
                    self.T1 = 0
                    continue
                    
                elif((child1.find_element_by_xpath("..").text == '' or child2.find_element_by_xpath("..").text == '') and nextbtn == ''):
                    print('No Time')
                    self.T1 = 2
                    break
                    
                else:
                    playtime = child1.find_element_by_xpath("..").text.split('\n')[1]
                    endtime = child2.find_element_by_xpath("..").text.split('\n')[1]
                    print(playtime,endtime)

                    # Resume
                    BROWSER.switch_to.default_content()
                    Play = BROWSER.find_elements_by_xpath("//iframe[@id = 'content']")

                    if(Play != [] and Pause == True):
                        print('Resume buttom click')
                        BROWSER.find_element_by_xpath("//iframe[@id = 'content']").click()

            # Another Kind Time bar
            except NoSuchElementException as e:
                print('Error:', e)
                print('Another Kind Time bar')
                # Time
                BROWSER.switch_to.default_content()
                self.CutIn()
                wait = WebDriverWait(BROWSER, 15)
                Time = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class = 'progressbar__label \
                                                                progressbar__label_type_time']"))).get_attribute('aria-label')
                playtime = Time.strip().split(' / ')[0]
                endtime = Time.strip().split(' / ')[1] 
                print(playtime,endtime)

            # End Course
            except NoSuchWindowException as e:
                print('Error:', e)
                print('End Course !')
                self.T1 = 2
                break

            # Check if it is The End
            if playtime >= endtime:
                # 下一個
                print('Time Comparison Over, Get NXT')
                nextbtn = self.GetNXT()
                print("Next Buttom click")
                nextbtn.click()

                # New
                New = True
                
                # T1 reset
                self.T1 = 0
                continue

            # New
            New = False
            
            # T1 reset
            self.T1 = 0

            # 120秒檢查一次
            print('wait 120')
            time.sleep(120)
            
# Parameters
ACNT = input('Please enter ACNT: ')
PWD = getpass.getpass('Please enter PWD: ')
BROWSER = webdriver.Chrome()

# Main 
def Main(ACNT, PWD):
    # 瀏覽器設定
    BROWSER.get('https://cathay.elearn.com.tw/dist/#/index')
    Login(Acnt = ACNT,Pwd = PWD)
    time.sleep(1)
    ToCourse()
    # 等進去學習網
    time.sleep(30)
    # 控制播放線程
    A = AutoPlay()
    t1 = threading.Thread(target=A.IsPlayOrEnd)
    t2 = threading.Thread(target=A.PopupCheck)
    # 切到播放視窗
    handles=BROWSER.window_handles
    BROWSER.switch_to.window(handles[2])
    # 開始播放
    t1.start()
    time.sleep(10)
    t2.start()

# Run Crawler
if __name__ == "__main__":
    Main(ACNT, PWD)