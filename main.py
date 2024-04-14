import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import time
import requests
import utils
import config
import sys

# 问卷链接
url = config.url

# 每题选项的比例
prob = config.prob

# 填空题答案
answerList = config.answerList

# 填写份数
epochs = config.epochs

# IP API代提取链接
api = config.api

# UA库
UA = config.UA


option = webdriver.EdgeOptions()
option.add_experimental_option('excludeSwitches', ['enable-automation'])
option.add_experimental_option('useAutomationExtension', False)


if __name__ == "__main__":

    # 一次性获取所有的 IP 地址
    iptext = requests.get(api).text
    ips = iptext.strip().splitlines()
    # 确保 ips 的数量小于 epochs
    epochs = min(epochs, len(ips))
    # 将所有IP放入一个集合中
    available_ips = set(ips)
    # 创建一个集合来存储已经选择的 IP 地址
    selected_ips = set()
    # 失败次数计数
    failed_count = 0
    # 确保 driver 在外部初始化为 None
    driver = None
    # 迭代 range(epochs)
    for epoch in range(epochs):
        try:
            # 从可用的 IP 地址集合中随机选择一个 IP
            ip = random.choice(list(available_ips - selected_ips))
            # 将选择的 IP 添加到已选择的集合中
            selected_ips.add(ip)
            # 从可用的 IP 地址中移除已选择的 IP
            available_ips.remove(ip)

            option.add_argument('--proxy-server={}'.format(ip))

            driver = webdriver.Edge(options=option)

            # 修改User-Agent
            num = random.randint(0, 2)
            driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": UA[num]})
            # 将webdriver属性置为undefined
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument',
                                {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'})

            driver.get(url)
            
            # 题号
            index = 1
            # 获取题目数量
            questions = driver.find_elements(By.CLASS_NAME, "field.ui-field-contain")
            for i in range(1, len(questions) + 1):
                xpath = '//*[@id="div{}"]'.format(i)
                question = driver.find_element(By.XPATH, xpath)
                # 获取题目类型
                flag = question.get_attribute("type")
                if flag == '2':
                    index = utils.fill_blank(driver, i, answerList, index)
                    utils.pause_random_time
                elif flag == '3':
                    index = utils.single_choice(driver, i, prob, index)
                    utils.pause_random_time
                elif flag == '4':
                    index = utils.multi_choice(driver, i, prob, index)
                    utils.pause_random_time
                elif flag == '5':
                    index = utils.single_scale(driver, i, prob, index)
                    utils.pause_random_time
                elif flag == '6':
                    xpath = '//*[@id="div{}"]/div[1]/div[2]/span'.format(i)
                    if driver.find_element(By.XPATH, xpath).text.find("【") != -1:
                        index = utils.multi_matrix_scale(driver, i, prob, index, num)
                        utils.pause_random_time
                    else:
                        index = utils.single_matrix_scale(driver, i, prob, index, num)
                        utils.pause_random_time
                elif flag == '7':
                    index = utils.select(driver, i, prob, index)
                    utils.pause_random_time
                elif flag == '8':
                    index = utils.single_slide(driver, i, prob, index)
                    utils.pause_random_time
                elif flag == '11':
                    index = utils.sort(driver, i, prob, index)
                    utils.pause_random_time
                elif flag == '12':
                    index = utils.multi_slide(driver, i, prob, index)
                    utils.pause_random_time
                else:
                    print("没有该题型")
                    sys.exit(0)
                    
            time.sleep(1)
            submit_button = driver.find_element(By.XPATH, '//*[@id="ctlNext"]')
            submit_button.click()
            time.sleep(1)

            # 请点击智能验证码进行验证！
            try:
                comfirm = driver.find_element(By.XPATH, '//*[@id="layui-layer1"]/div[3]/a')
                comfirm.click()
                time.sleep(1)
            except Exception as e:
                print(e)

            # 点击按钮开始智能验证
            try:
                button = driver.find_element(By.XPATH, '//*[@id="SM_BTN_WRAPPER_1"]')
                button.click()
                time.sleep(0.5)
            except Exception as e:
                print(e)

            # 滑块验证
            try:
                slider = driver.find_element(By.XPATH, '//*[@id="nc_1__scale_text"]/span')
                time.sleep(0.3)
                if str(slider.text).startswith("请按住滑块，拖动到最右边"):
                    width = slider.size.get('width')
                    ActionChains(driver).drag_and_drop_by_offset(slider, width, 0).perform()
                    time.sleep(1)
            except Exception as e:
                print(e)

            time.sleep(3)
        except Exception as e:
            # 如果出现异常，递增失败计数
            print(f"任务在第 {epoch + 1} 轮失败: {e}")
            failed_count += 1
        finally:
            # 使用 try-except 块确保 driver.quit() 的异常被捕获
            try:
                # 确保在每次迭代后都关闭 driver
                driver.quit()
            except Exception as e:
                # 捕获异常并输出错误信息
                print(f"Error during driver.quit(): {e}")
            # 继续执行其他后续代码
            print(f"已完成 {epoch + 1} 份")
        
    print("全部完成{}份填写".format(epochs))
    # 最后输出失败的份数
    print(f"失败 {failed_count} 份")
