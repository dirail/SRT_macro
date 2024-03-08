# ##자동화 크롬 브라우저를 위한 필수 패키지
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By   ## html id활용 용이하기 위해 선언
from selenium.webdriver.support.select import Select    ## 리스트를 포함하는 Element를 다루기 위한 package선언
import time     #sleep을 위해서 time package 선언

# Chrome WebDriver 객체 생성
def open_browser():    
    driver = webdriver.Chrome()
    return driver

# 로그인 함수
def login(driver, login_id, login_pw):
    driver.get('https://etk.srail.kr/cmc/01/selectLoginForm.do')    ## SRT 로그인페이지로 연결
    driver.find_element(By.ID, 'srchDvNm01').send_keys(str(login_id))    ## 회원번호 입력
    driver.find_element(By.ID, 'hmpgPwdCphd01').send_keys(str(login_pw))    ## 비밀번호 입력
    ## 확인버튼 클릭
    driver.find_element(By.XPATH, '/html/body/div/div[4]/div/div[2]/form/fieldset/div[1]/div[1]/div[2]/div/div[2]/input').click()
    return driver

# 기차 정보 셋팅 함수
def set_train(driver, dpt_stn, arr_stn, dpt_dt, dpt_tm,  psn_num = 1, want_reserve=False):

    ## 승차권 예약으로 접속
    driver.get('https://etk.srail.kr/hpg/hra/01/selectScheduleList.do?pageId=TK0101010000')

    ## 출발지 선택
    elm_dpt_stn = driver.find_element(By.ID, 'dptRsStnCdNm')
    elm_dpt_stn.clear()     ##사전에 입력된 내용 지우기
    elm_dpt_stn.send_keys(dpt_stn)
    
    ## 도착지 선택
    elm_arr_stn = driver.find_element(By.ID, 'arvRsStnCdNm')
    elm_arr_stn.clear()
    elm_arr_stn.send_keys(arr_stn)
    
    ##출발일자 선택
    elm_dptDt = driver.find_element(By.ID, 'dptDt')    
    ##숫자로 입력 없거나 에러이면 오늘로 진행
    try:
        ##일자 리스트 중에서 출발일자 선택
        Select(elm_dptDt).select_by_value(str(dpt_dt))
    except:
        ##오늘년월일 정보 입력
        today = datetime.now().strftime('%Y%m%d')
        Select(elm_dptDt).select_by_value(str(today))
    
    ## 출발시각 선택 & 전처리 : 문자열 구성을 위해 10 미만은 문자 0을 앞에 추가
    if dpt_tm  < 10:
        dpt_tm  = '0'+ str(dpt_tm)
    else:
        dpt_tm  = str(dpt_tm)

    ##출발시각 입력을 위한 Element
    elm_dptTm  = driver.find_element(By.ID, 'dptTm')  
    try:
        Select(elm_dptTm).select_by_value(dpt_tm + '0000')      ## 타겟 시간 선택
    except:
        pass
    
    ## 기차종류 SRT만 선택 
    driver.find_element(By.ID, 'trnGpCd300').click()

    # # 알림
    print("기차를 조회합니다")
    print(f"출발역 [{dpt_stn}] / 도착역 [{arr_stn}]\n{dpt_dt[:4]}년 {dpt_dt[4:6]}월 {dpt_dt[6:]}일")

    return driver


# 조회 루프 시작
def page_stable():
    ## 대기자수 많아서 웨이팅 후 예매선택 ( 조회 성공시 나오는 열차번호? 안 나오면 계속 기다리는 원리 )
    for i in range(40):
        time.sleep(1.0)
        try:
            # driver.find_element(By.XPATH, waiting_list)
            driver.find_element(By.XPATH, '/html/body/div/div[4]/div/div[3]/div[1]/form/fieldset/div[6]/table/tbody/tr[1]/td[10]/a')
            # print('대기 끝')
            break
        except:
            print('대기 중 .... ', i)
            pass
        # time.sleep(1.5)
    time.sleep(1.5)


def start_search(first = 1, last = 10):

    #조회버튼클릭
    search_btn = "/html/body/div/div[4]/div/div[2]/form/fieldset/div[2]/input"
    driver.find_element(By.XPATH, search_btn).click()

    page_stable()

    first_train = driver.find_element(By.CSS_SELECTOR, f"#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody > tr:nth-child({first}) > td:nth-child({4})").text[-5:]
    last_train = driver.find_element(By.CSS_SELECTOR, f"#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody > tr:nth-child({last}) > td:nth-child({4})").text[-5:]
    print( f"{first_train}에서 {last_train} 사이의 기차를 조회합니다.\n" )
    
    ##예약이 될때까지 반복문수행
    n=0
    search_button_found = False
    while True:
        try:  # try 가 트루가 되면 끝나는겨
            for i in range(first, last + 1):  # 타고싶은 후보 열차 입력 (위에서 부터 1번)
                standard_seat = driver.find_element(By.CSS_SELECTOR, f"#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody > tr:nth-child({i}) > td:nth-child(7)").text
    
                if "예약하기" in standard_seat:
                    driver.find_element(By.XPATH, f"/html/body/div[1]/div[4]/div/div[3]/div[1]/form/fieldset/div[6]/table/tbody/tr[{i}]/td[7]/a/span").click()
                    print("예약 가능")
                    break
            n+=1
            print( f'재시도 ...... {n:03}' )
            # pass
    
        except:
            # 리스트 초기화 됐을때
            driver.find_element(By.XPATH, search_btn)
            # search_button_found = True
            print("열차 리스트가 초기화 되었습니다.\n")
            driver.find_element(By.XPATH, search_btn).click()
    
            page_stable()
            # time.sleep(2)
    
            ##자리나서 눌렀는데 잔여석 없다고 나올때
        try:
            # no_empty = "/html/body/div/div[4]/div/div[2]/div[7]/a"
            no_empty = "//a[@class='btn_large btn_blue val_m']/span[text()='확인']"
            no_empty_btn = driver.find_element(By.XPATH, no_empty)
            no_empty_btn
            driver.back()
            print("잔여좌석 없음")
            ## 원하는 기차정보 재셋팅 필요
            time.sleep(2)
        except:
            # print('확인 버튼을 찾을 수 없습니다.')
            pass
        search_button_found = False
        time.sleep(2.5)
        driver.refresh()

    return driver



## 지역명 예시
# ['수서','동탄','평택지제','천안아산','오송',
# '대전','김천(구미)','서대구','동대구','신경주',
# '울산(통도사)','부산','공주','익산','정읍','광주송정','나주','목포']


if __name__ == "__main__":
    driver = open_browser()
    driver = login(driver, '1986111308', 'zziny7622!')  ## 회원 번호, 비밀번호
    set_train(driver, "동대구", "수서", "20240310", 16)  ## ex) "동대구", "수서", "20240310", 16(탑승시각)
    start_search(first = 5, last = 7)  ## 화면 중 원하는 시간대 선택가능, 기본값 first = 1, last = 10
    print('예약 완료')