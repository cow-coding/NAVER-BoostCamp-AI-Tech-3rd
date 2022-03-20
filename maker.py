import argparse
import os
import re

from urllib.request import urlopen, Request
from urllib import parse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service


def argument_setting():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", required=True, help='start hex code')
    parser.add_argument("-e", required=False, help='end hex code')
    parser.add_argument("-l", required=False, help='post category link')
    parser.add_argument("-n", required=False, help='name')
    parser.add_argument("-logo", required=False, help='logo')
    parser.add_argument("--count", required=False, default=-1, type=int)
    args = parser.parse_args()

    return args


def color_code_getter(start, end, counts):
    options = webdriver.ChromeOptions()

    # headless 옵션 설정
    options.add_argument('headless')
    options.add_argument("no-sandbox")

    options.add_argument("disable-gpu")  # 가속 사용 x
    options.add_argument("lang=ko_KR")  # 가짜 플러그인 탑재
    options.add_argument(
        'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')  # user-agent 이름 설정

    url = f"https://colordesigner.io/gradient-generator/?mode=lch#{start}-{end}"
    ser = Service("./chromedriver")
    driver = webdriver.Chrome(service=ser, options=options)
    # driver.implicitly_wait(3)

    driver.get(url)
    driver.find_elements(by=By.CLASS_NAME, value='input-group__input')[1].send_keys(Keys.COMMAND + 'a')
    driver.find_elements(by=By.CLASS_NAME, value='input-group__input')[1].send_keys(counts)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    textarea = soup.findAll('div', {'title':'Copy color'})

    ret_list = []
    for i in range(0, len(textarea, ), 3):
        ret_list.append(textarea[i].text[6:])

    return ret_list


def get_post_count(url):
    req = Request('https://'+parse.quote(url[8:]))
    response = urlopen(req)
    page = response.read()
    bsobj = BeautifulSoup(page, 'html.parser')

    posts = bsobj.find('ul', {'class': 'post-content pl-0'})
    links = posts.findAll('a')
    urls = []
    for post in links:
        urls.append(base_url+post.attrs['href'])
    return urls, len(links)


def make_badges(urls, colors, name, logo):
    strs = ''
    urls.reverse()

    for i in range(len(colors)):
        badge_link = f'https://img.shields.io/badge/{name}%20|%20{i+1}-{colors[i]}?style=flat&logo={logo.lower()}&logoColor=ffffff'
        str = f"[![]({badge_link})]({urls[i]})"
        strs += (str + ' ')

    return strs


if __name__ == '__main__':
    args = argument_setting()

    print("Get post counts and links...")
    # https://cow-coding.github.io/categories/python/
    urls, counts = get_post_count(args.l)
    print("Making gradient hex color codes...")
    # 3766AB, 0b4193
    if args.count != -1:
        counts = args.count
    hex_list = color_code_getter(args.s, args.e, counts)
    print("Making full badge lists...")
    strs = make_badges(urls, hex_list, args.n, args.logo)
    print(strs)
