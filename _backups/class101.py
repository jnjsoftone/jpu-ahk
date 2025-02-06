# -*- coding=utf-8 -*-
"""class101.py
> productId
https://class101.net/ko/products/600813c1ea24bb000dd041b4
https://class101.net/ko/products/5fbb1b1c5cd1d500137cfdca

<section id="class_description">
<section id="kit">
<section id="curriculum">
<section id="creator">
<section id="pdp_recommend">

- thumbnail / title / level, totalChapter, totalTime, Lang, audio

#__next > main > div > div.css-10g0pqe > div.css-10c2f7i > div.css-1c9ce2j


- 클래스 소개 / 준비물 / 커리큘럼 / 크리에이터 / 추천
#__next > main > div > div.css-10g0pqe > div.css-10c2f7i > div.css-wow50y

-> html 저장

class_description.html
kit.html
curriculum.html
creator.html
pdp_recommend.html




> 커리큘럼 버튼 클릭

: function get_curriculum_infos()

-> 주소창 url 저장(class_id, curriculum_id)
-> '수업자료' 클릭, 내용 저장, 'Download' 클릭(클릭시 time.sleep())
-> '소식' 클릭, 내용 저장
-> '커리큘럼' 클릭

=> for 커리큘럼 버튼(2번째부터) 클릭

"""



# & Import AREA
# &----------------------------------------------------------------------------

"""# Builtin Modules
"""
import os, sys
from urllib import parse
import time
import math
import re
import argparse

"""# Installed Modules
"""
import asyncio
import requests
import html2text


"""# Custom Modules
"""
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/utils'))

from base_builtin import find_files, load_file, load_json, load_yaml, save_file, save_json, slashed_folder, find_folders2, find_folders_recursive, find_folders_leaf, rename_file, delete_file, move_all_files, move_folder
from browser_chrome import get_profile_by_email, Chrome
from doc_html import set_file_name, prettify, _today, get_root, node_to_string, get_nodes, get_val, remove_node, _download_file

sys.path.append(os.path.join(os.path.dirname(__file__), '../helper'))
from html_markdown import save_post_markdown

# * Global
HEADLESS = True
COUNT_UNIT = 20

VIDEO_EXT = ".mp4"
DOWN_ROOT_FOLDER = "C:/JnJ-soft/Projects/internal/jnj-web-tools/jnj-web-tools-python/down/class101"
PRODUCTS_JSON_PATH = f"{DOWN_ROOT_FOLDER}/products.json"
MYCLASSES_JSON_PATH = f"{DOWN_ROOT_FOLDER}/myclasses.json"
OBSIDIAN_ROOT_FOLDER = "G:/내 드라이브/Obsidian/_Master/20_Literature_Notes/205_Class101"
# PRODUCTS_JSON_PATH = "C:/JnJ-soft/Projects/external/kmc-web-app/backend/nodejs/src/scraping/class101/json/products.json"


VIDEO_ROOT_PATH = "E:/_class"
VIDEO_ROOT_PATH2 = "E:/class101"

# ** util function
def pop_dict(data, keys):
    for key in keys:
        data.pop(key)
    return data


def search_json(data, target, current_path=None):
    if current_path is None:
        current_path = []

    if isinstance(data, dict):
        for key, value in data.items():
            new_path = current_path + [key]
            if value == target:
                return new_path
            result = search_json(value, target, new_path)
            if result:
                return result
    elif isinstance(data, list):
        for i, item in enumerate(data):
            new_path = current_path + [i]
            if item == target:
                return new_path
            result = search_json(item, target, new_path)
            if result:
                return result
    return None

def find_in_json(data, search_key, search_value):
    def search(obj, path=None):
        if path is None:
            path = []
        
        if isinstance(obj, dict):
            for k, v in obj.items():
                # if k == search_key and v == search_value:
                condition = (k == search_key and v == search_value)
                if isinstance(search_value, str):
                    condition = (k == search_key and search_value in v)
                if condition:
                    return path
                result = search(v, path + [k])
                if result:
                    return result
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                result = search(item, path + [i])
                if result:
                    return result
        return None

    return search(data)


def get_nested_value(data, nested_keys):
    result = data
    for key in nested_keys:
        result = result[key]
    return result


def frontmeta_from_dict(data):
    frontmeta_str = '---\n'
    for key, value in data.items():
        frontmeta_str += f"{key}: \"{value}\"\n"
    frontmeta_str += '---\n'
    return frontmeta_str

def sanitize_filename(filename, repl="-"):
    filename = re.sub(r'[\\\/\.:*?"<>`|%]', "-", filename)
    filename = re.sub(r' {2,}', " ", filename)
    return filename.strip()

def sanitize_obsidian(filename, repl=""):
    filename = re.sub(r'[\\\/:*?"<>|%]', "", filename)
    filename = re.sub(r' {2,}', "-", filename)
    return filename.strip()

def is_only_numbers(s):
    # 정규 표현식: 숫자와 점(.)만 포함하는 문자열
    return bool(re.match(r'^[0-9.]+$', s))

# * Playwright
def get_chrome(url="https://class101.net/ko/my-classes", email="bigwhitekmc@gmail.com", timeout=60000):
    # url = "https://class101.net/ko/my-classes"
    profile = get_profile_by_email(email=email, base_path=None)
    chrome = Chrome(url, profile=profile, headless=False)
    chrome.page.set_default_timeout(timeout)  # !! 타임아웃 시간 설정
    return chrome

def move_and_click(chrome, button):
    bounding_box = button.bounding_box()  # 요소의 위치와 크기 정보 가져오기

    if bounding_box:
        x = bounding_box['x'] + bounding_box['width'] / 2  # 요소 중심의 x 좌표
        y = bounding_box['y'] + bounding_box['height'] / 2  # 요소 중심의 y 좌표

        # 마우스를 요소의 위치로 이동하고 클릭합니다.
        chrome.page.mouse.move(x, y)  # 마우스 이동
        chrome.page.mouse.click(x, y)  # 클릭
        time.sleep(30)

        print(f"마우스를 ({x}, {y}) 위치로 이동하여 클릭했습니다.")

def go_back_pages(page, count):
    for _ in range(count):
        page.go_back()
        time.sleep(3)
        # page.wait_for_load_state('networkidle')


async def scroll_to_bottom(page, scroll_delay=1000):
    await page.evaluate("""
        async function scrollToBottom() {
            const scrollHeight = document.body.scrollHeight;
            while (window.pageYOffset + window.innerHeight < scrollHeight) {
                window.scrollBy(0, window.innerHeight);
                await new Promise(resolve => setTimeout(resolve, arguments[0]));
            }
        }
        return scrollToBottom();
    """, scroll_delay)


def scroll_bottom(page, distance=200, scroll_delay=500):
    # Continuously scroll 100 pixels at a time until the bottom is reached
    while True:
        previous_scroll_position = page.evaluate("window.scrollY")
        page.evaluate(f"window.scrollBy(0, {distance})")
        time.sleep(scroll_delay/1000)  # Pause for 1 second
        current_scroll_position = page.evaluate("window.scrollY")

        # Break the loop if the scroll position does not change
        if current_scroll_position == previous_scroll_position:
            break

def html2md(html_content):
    # * HTML 2 MARKDOWN 설정
    # html2text 객체 생성
    text_maker = html2text.HTML2Text()
    # 링크 주소 간소화 (선택 사항)
    text_maker.ignore_links = False
    # 이미지 주소 간소화 (선택 사항)
    text_maker.ignore_images = False
    # 강조 표시를 위한 마크다운 스타일 유지 (선택 사항)
    text_maker.mark_code = True

    md = text_maker.handle(html_content)
    md = re.sub(r'\n +', '\n', md)
    # return md

    return re.sub(r'\n{3,}', '\n\n', md)

# ** Function AREA
def find_productId_by_title(title):
    json_data = load_json(PRODUCTS_JSON_PATH)
    product = get_nested_value(json_data, find_in_json(json_data, "title", title))
    return product['productId']

def find_class_folder(productId):
    return f'{DOWN_ROOT_FOLDER}/classes/{productId}'

def find_class_html_path(productId):
    return f'{DOWN_ROOT_FOLDER}/classes/{productId}/home.html'
    # return f'{DOWN_ROOT_FOLDER}/html/classes/{productId}.html'


def find_class_materials_folder(productId):
    return f'{DOWN_ROOT_FOLDER}/classes/{productId}/materials'
    # return f'{DOWN_ROOT_FOLDER}/html/classes/{productId}.html'


def get_class_json_path(productId):
    return f'{DOWN_ROOT_FOLDER}/classes/{productId}/info.json'
    # return f'{DOWN_ROOT_FOLDER}/json/classes/{productId}.json'


def get_lecture_info_by_sn(productId, sn, key):
    json_data = load_json(get_class_json_path(productId))
    # print(find_in_json(json_data, "sn", sn))
    lecture = get_nested_value(json_data, find_in_json(json_data, "sn", sn))
    return lecture[key]

def find_lecture_info_by_prefix(productId, prefix):
    json_data = load_json(get_class_json_path(productId))
    # print(find_in_json(json_data, "sn", sn))
    lecture = get_nested_value(json_data, find_in_json(json_data, "prefix", prefix))
    return lecture

def find_lecture_title_by_sn(productId, sn):
    title = get_lecture_info_by_sn(productId, sn, 'title')
    parts = title.split(" ")
    if is_only_numbers(parts[0]):
        title = " ".join(parts[1:])
    return title


def get_class_html(chrome):
    # element = chrome.page.locator('#__next > main > div > div.css-10g0pqe > div.css-10c2f7i')
    # return element.inner_html()  # inner_html() 메서드로 요소의 HTML 반환
    elements = chrome.page.locator('#__next > main > div > div > div > div').all()
    # elements = chrome.page.locator('#__next > main > div > div.css-10g0pqe > div.css-10c2f7i > div').all()
    # 2번째와 4번째 요소의 outerHTML 가져오기
    second_div_html = elements[1].inner_html()
    fourth_div_html = elements[3].inner_html()
    return second_div_html + "\n" + fourth_div_html  # inner_html() 메서드로 요소의 HTML 반환


def save_class_html(chrome, productId):
    save_file(find_class_html_path(productId), get_class_html(chrome), encoding="utf-8")


def get_class_json(productId):
    html = load_file(find_class_html_path(productId), encoding="utf-8")
    # * infos
    # title = get_nodes(html, xpath='//h1')[0].text_content()
    title = get_nodes(html, xpath='//div[@class="css-1qys0c1"]/h3')[0].text_content()
    # __next > main > div > div.css-10g0pqe > div.css-4dhpus > div.css-w5dbe2 > div.css-d9x9r7 > div.css-169u1qh > div > div > div > div.css-1qys0c1 > h3
    print(title)
    class_json = {
        'title': title,
        'productId': productId,
        'classId': ""
    }

    infos = get_nodes(html, xpath='//span[@class="css-1eej1is"]')
    texts =[info.text_content() for info in infos]
    class_json['level'] = texts[0]
    [totalChapter, totalTime] = [text.strip() for text in texts[1].split('·')]
    class_json['totalChapter'] = int(totalChapter.replace('챕터 ', '').replace('개', ''))
    class_json['totalTime'] = totalTime

    if len(texts) > 3:
        class_json['lang'] = ', '.join(texts[2].replace(' ', '').split('·'))
        class_json['audio'] = texts[4].replace('오디오 ', '')
    else:
        if '오디오' in texts[2]:
            class_json['audio'] = texts[2].replace('오디오 ', '')
        else:
            class_json['lang'] = ', '.join(texts[2].replace(' ', '').split('·'))

    # * curriculum
    # print(class_json)

    # 중급

    # 챕터 4개 · 6시간 28분

    # 오디오 한국어

    # * curriculum
    # section#curriculum button.css-1hvtp3b
    chapterNodes = get_nodes(html, xpath='//section[@id="curriculum"]//div[@class="css-1d944kd"]')
    # print(len(chapters))
    chapters_json = []
    chapterCount = 0
    totalLecture = 0

    for chapterNode in chapterNodes:
        if not chapterNode.xpath('.//h2'): continue

        # print(len(chapter.xpath("//h2")))
        tag = chapterNode.xpath('.//span[@class="css-1qjkj89"]')[0].text_content()
        chapterTitle = f"{tag}_{chapterNode.xpath('.//h2')[0].text_content()}"

        lectureNodes = chapterNode.xpath('.//button[@class="css-1hvtp3b"]')
        lectures = []
        lectureCount = 0
        for lectureNode in lectureNodes:
            if not lectureNode.xpath('.//*[@data-testid="body"]'):
                continue
            lectureCount += 1
            totalLecture += 1
            # title = lectureNode.xpath('.//*[@data-testid="title"]')[0].text_content()
            # ** TODO
            # title = get_val(lectureNode, './/*[@data-testid="title"]', 'innerhtml')
            title = get_val(lectureNode, './/*[@data-testid="title"]', 'outerhtml')
            title = title.replace('<h3 data-testid="title" class="css-1q63rp6">', '').replace('</h3>', '')
            duration = lectureNode.xpath('.//*[@data-testid="body"]')[0].text_content()
            lectures.append({
                'prefix': f"{str(chapterCount).zfill(2)}_{str(lectureCount).zfill(2)}",
                'sn': totalLecture,
                'title': title,
                'duration': duration
            })

        chapterCount += 1

        chapter = {
            'title': chapterTitle,
            'lectures': lectures,
        }
    
        chapters_json.append(chapter)
    

    # * creator
    creator = get_nodes(html, xpath='//section[@id="creator"]//h2[@data-testid="title"]')[1].text_content()


    # * 
    class_json['creator'] = creator
    class_json['totalLecture'] = totalLecture
    class_json['chapters'] = chapters_json

    return class_json


def save_class_json(productId):
    save_json(get_class_json_path(productId), get_class_json(productId))


def find_lecture_paths(productId):
    lecture_paths = []
    product = load_json(get_class_json_path(productId))
    productName = sanitize_filename(product['title'])
    
    for chapter in product['chapters']:
        chapterName = sanitize_filename(chapter['title'])
        for lecture in chapter['lectures']:
            lectureName = sanitize_filename(lecture['title'])
            lecture_paths.append(f"{productName}_{chapterName}_{lectureName}")
    
    return lecture_paths


def find_lecture_category(productId, json_path=PRODUCTS_JSON_PATH):
    json_data = load_json(json_path)
    result = find_in_json(json_data, "productId", productId)

    # [12, 'subcategories', 1, 'products', 3]  / 서브카테고리 없는 경우:  [11, 'products', 0] // get_nested_value(data, find_in_json(json_data, "productId", productId))
    if not result or (len(result) < 3):
        return ''
    if len(result) < 4:
        return json_data[result[0]]['title']
    else:
        return f"{json_data[result[0]]['title']}/{json_data[result[0]]['subcategories'][result[2]]['title']}"


def find_product_info_by_productId(productId):
    json_data = load_json(PRODUCTS_JSON_PATH)
    result = find_in_json(json_data, "productId", productId)

    if not result  or (len(result) < 3):
        return {}
    if len(result) < 4:
        info = json_data[result[0]]['products'][result[2]]
        info["category"] = json_data[result[0]]['title']
        return pop_dict(info, ["instructor"])
    else:
        info = json_data[result[0]]['subcategories'][result[2]]['products'][result[4]]
        info["category"] = f"{json_data[result[0]]['title']}/{json_data[result[0]]['subcategories'][result[2]]['title']}"
        return pop_dict(info, ["instructor"])
    # {'productId': '5c81296235b52893ce45a363', 'image': 'https://cdn.class101.net/images/85eb5915-c17e-449b-9bad-e6152b93a13f', 'title': '기획에서 편집 디자인, 유통까지, 독립출판!', 'instructor': '김현경'}


def find_class_info_by_productId(productId):
    info1 = find_product_info_by_productId(productId)
    info2 = pop_dict(load_json(get_class_json_path(productId)), ["productId", "lang", "audio", "chapters"])
    # info1.update(info2)
    return {**info1, **info2}

def download_by_click(chrome, button, download_dir):
    os.makedirs(download_dir, exist_ok=True)

    try:
        with chrome.page.expect_download() as download_info: # 다운로드 이벤트를 기다림
            button.click()

        download = download_info.value
        download_path = download.path()
        file_name = download.suggested_filename

        # 파일 저장
        save_path = os.path.join(download_dir, file_name)
        download.save_as(save_path)
        print(f"save_path: {save_path}")
        time.sleep(5)
    except:
        save_file(f'{download_dir}/error.html', f'error: {download_dir}', encoding="utf-8")


def get_material(productId, chrome, i, down):
    # * 수업자료
    span_element = chrome.page.locator('span:text-is("수업자료")')
    if span_element.count() == 0:
        print('요소를 찾을 수 없습니다.')
        return

    # # 요소가 존재하는지 확인
    # if span_element.count() > 0:
    # print('요소를 찾았습니다.')
    span_element.click()
    time.sleep(5)

    # 특정 div 요소 선택
    # div_element = chrome.page.locator('div.css-1d944kd')
    div_element = chrome.page.locator('div.css-zqgvt1')

    # outerHTML 반환
    outer_html = div_element.inner_html()  # inner_html() 메서드로 요소의 HTML 반환
    # print(outer_html)
    producti_dir = f'{DOWN_ROOT_FOLDER}/classes/{productId}'
    save_file(f'{producti_dir}/materials/{i}.html', outer_html, encoding="utf-8")
    # save_file(f'{producti_dir}/material_{str(i).zfill(3)}.html', outer_html, encoding="utf-8")
    files_dir = f'{producti_dir}/files/{i}'

    # TODO: 첨부파일 다운로드
    if down:
        # downloads = chrome.page.locator('p:has-text("Download")') # <div class="css-iy28cf"><p class="css-boqaej">Download</p></div>
        downloads = chrome.page.locator('p:text-is("Download")')
        download_elements = downloads.all()  # Locator 객체를 리스트로 변환
        for download_element in download_elements:
            download_by_click(chrome, download_element, files_dir)


    # # * 소식 TODO: '소식' 클릭시 에러 페이지로 이동하는 경우 해결
    # if i == '00_01': # 첫번째 강의의 경우에만 다운로드
    #     span_element = chrome.page.locator('span:text-is("소식")')
    #     span_element.click()
    #     time.sleep(3)
    #     # div_elements = chrome.page.locator('div.css-175oi2r').all()
    #     div_elements = chrome.page.locator('div.css-11yo0b7').all()
        
    #     if len(div_elements) > 0:
    #         div_element = div_elements[0]
    #         # outerHTML 반환
    #         outer_html = div_element.inner_html()  # inner_html() 메서드로 요소의 HTML 반환
    #         # save_file(f'{producti_dir}/news/{i}.html', outer_html, encoding="utf-8")
    #         if '아직 새로운 소식이 없어요' in outer_html:
    #             print('새로운 소식이 없음!!!')
    #         else:
    #             save_file(f'{producti_dir}/news.html', outer_html, encoding="utf-8")

    # * 커리큘럼
    span_element = chrome.page.locator('span:text-is("커리큘럼")')
    span_element.click()
    time.sleep(3)


def update_lectureId(class_json, sn, lectureId):
    chapters = class_json["chapters"]
    for chapter in chapters:
        for lecture in chapter["lectures"]:
            if lecture["sn"] == sn:
                lecture["lectureId"] = lectureId
                return class_json
    
    # save_json(get_class_json_path(productId), class_json)


def get_my_classes():
    chrome = get_chrome(url="https://class101.net/ko/my-classes")
    chrome.page.wait_for_load_state('networkidle')
    time.sleep(5)
    scroll_bottom(chrome.page)

    li_elements = chrome.page.locator('ul[data-testid="grid-list"] > li')
    count = li_elements.count()
    print(f"{li_elements.count()=}")

    try:
        myclasses = load_json(MYCLASSES_JSON_PATH)
    except:
        myclasses = []

    count2 = len(myclasses)

    myclassIds = [_class['classId'] for _class in myclasses]
    print(myclassIds)

    for i in range(count):
        if count == count2:  # 
            break
        print(f'####[{i}]')
        # chrome.page.goto("https://class101.net/ko/my-classes")
        # chrome.page.wait_for_load_state('networkidle')
        # # time.sleep(5)
        # li_elements = chrome.page.locator('ul[data-testid="grid-list"] > li')
        li_element = li_elements.nth(i)
        li_element.click()
        # time.sleep(1)
        chrome.page.wait_for_url("**/classes/**")
        classId = chrome.page.url.split("/")[-3]

        if classId in myclassIds:
            print("@@@@@@이미 등록된 강좌")
            # 전 페이지로 이동
            go_back_pages(chrome.page, 1)  # 1페이지 뒤로 이동
        else:
            print("******새로운 강좌 등록")
            firstLecture = chrome.page.url.split("/")[-1]
            print(f'class lecture: {classId}')  # https://class101.net/ko/classes/624e9c23f731df00149a5734/lectures/6256ed97e705b6000e8cd8f3

            title_el = chrome.page.locator('h3[class="css-poyozc"]').nth(1)
            title = title_el.text_content().strip()
            print(f'{title=}')
            title_el.locator('../..').click()
            # time.sleep(5)
            chrome.page.wait_for_url("**/products/**")
            # 클릭: <h3 data-testid="title" class="css-poyozc">딱 1번 배워 평생 써먹는 블로그 운영법 월 300만 원 만들기</h3>
            productId = chrome.page.url.split("/")[-1]
            print(f'productId: {productId}')  # https://class101.net/ko/products/5f3666add02aee00202da554
            # time.sleep(2)
            myclass = {
                "classId": classId,
                "firstLecture": firstLecture,
                "productId": productId,
                "title": title,
            }
            myclasses.append(myclass)
            save_json(MYCLASSES_JSON_PATH, myclasses)

            # 전전 페이지로 이동
            go_back_pages(chrome.page, 2)  # 2페이지 뒤로 이동

        chrome.page.wait_for_url("**/my-classes")
        time.sleep(2)
        scroll_bottom(chrome.page)
        time.sleep(3)
        li_elements = chrome.page.locator('ul[data-testid="grid-list"] > li')

    chrome.close()


def get_class_data_by_productId(productId):
    if not productId: return

    folder = find_lecture_category(productId, json_path=PRODUCTS_JSON_PATH)

    home_url = f"https://class101.net/ko/products/{productId}"
    profile = get_profile_by_email(email="bigwhitekmc@gmail.com", base_path=None)
    chrome = Chrome(home_url, profile=profile, headless=False)
    chrome.page.set_default_timeout(60000)  # !! 타임아웃 시간 설정
    time.sleep(5)

    save_class_html(chrome, productId)
    time.sleep(1)
    save_class_json(productId)
    class_json = get_class_json(productId)

    # 첫번째 강의 버튼 클릭
    buttons = chrome.page.locator('//section[@id="curriculum"]//button[@class="css-1hvtp3b"]')  # css-1hvtp3b
    button_elements = buttons.all()  # Locator 객체를 리스트로 변환
    button_elements[0].click()
    time.sleep(5)

    # 수업자료 / 소식 html 저장
    buttons = chrome.page.locator('//button[@class="css-1hvtp3b"]')  # css-1hvtp3b
    button_elements = buttons.all()  # Locator 객체를 리스트로 변환

    lectureCount = len(button_elements)
    print(f"{lectureCount=}, {class_json['totalLecture']=}")  # 40

    first = False
    overlappedTitles = {}  # {"title___": 0, }

    # for i in range(1, 28):
    for i in range(1, class_json['totalLecture'] + 1):
        title = find_lecture_title_by_sn(productId, i)
        title = title.replace('"', '\\"')
        if "<br" in title:  # !! title에 <br>이 있는 경우
            _title = title.split("<br")[1]
            print(f"<br> 태그가 있는 제목: {title}")
            titleEl = chrome.page.locator(f'button span:text("{_title}")')
        else:
            titleEl = chrome.page.locator(f'button span:text-is("{title}")')
        if not titleEl:
            print("#########강의 제목을 찾을 수 없습니다.")
            continue
        if titleEl.count() > 1:
            if not title in overlappedTitles:
                overlappedTitles[title] = 0
            else:
                overlappedTitles[title] += 1

            titleEl = titleEl.nth(overlappedTitles[title])
            print(f"*********중복된 제목이 있습니다. [{overlappedTitles[title] + 1}] / {titleEl.count()}")

        button = titleEl.locator('../../../../..')  # css-1hvtp3b
        lectureText = button.text_content()
        # print(f"{lectureText=}")

        down = True if "첨부파일" in lectureText else False
        button.click()
        time.sleep(5)

        if not first:
            classId = chrome.page.url.split('/')[-3]
            class_json["classId"] = classId
            first = True

        prefix = get_lecture_info_by_sn(productId, i, 'prefix')
        # print(f"[{i}] {title=}, {lectureText=}, {prefix=}, {down=}")
        print(f"[{i}] {prefix} {title}, {down=}")
        get_material(productId, chrome, prefix, down)
        update_lectureId(class_json, i, chrome.page.url.split('/')[-1])

    save_json(get_class_json_path(productId), class_json)

    chrome.close()


def get_class_data_by_title(title):
    productId = find_productId_by_title(title)
    # print("productId: ", productId)
    get_class_data_by_productId(productId)

# myclasses에 있으면서 현재 다운로드 되지 않는 데이터 스크래핑(playwright)
def get_all_class_data():
    myclasses = load_json(MYCLASSES_JSON_PATH)
    myproductIds = [_class['productId'] for _class in myclasses]
    productIds = find_folders2(f"{DOWN_ROOT_FOLDER}/classes")
    print(len(productIds), " ", productIds)

    i = 0
    for productId in myproductIds:
        if productId in productIds:
        # if productId in productIds or productId == "5cbe7fcfbf084b057dbf708d":
            print(f"#### {productId}")
            continue
        i += 1
        print(f"[{i}]: {productId}")
        get_class_data_by_productId(productId)
        time.sleep(10)


def find_lecture_video_list_from_info(info):
    chapters = info["chapters"]
    video_list = []
    for chapter in chapters:
        for lecture in chapter["lectures"]:
            name = f'{lecture["prefix"]}_{lecture["lectureId"]}.mp4' # title
            title = lecture['title']
            video_list.append({"name": name, "title": title})

    return video_list


def rename_vidoes():
    # ** video 제목 변경
    folders = find_folders_leaf(VIDEO_ROOT_PATH)
    # folderNames = [folder.split('/')[-1] for folder in folders]

    myclasses = load_json(MYCLASSES_JSON_PATH)
    titles = [myclass['title'] for myclass in myclasses]
    # titles = [sanitize_filename(myclass['title']) for myclass in myclasses]
    # for folderName in folderNames:
    for folder in folders:
        folderName = folder.split('/')[-1]
        for title in titles:
            if folderName in sanitize_filename(title):
                print(f"####{folder}")
                # ** [TODO] "."으로 시작하는 파일 삭제
                for _file in [file for file in find_files(folder) if file.split("/")[-1][0] == "."]:
                    # print(f"삭제할 파일: {_file}")
                    delete_file(_file)

                fileNames = sorted([file.split("/")[-1] for file in find_files(folder) if file[-4:] == VIDEO_EXT])
                # fileNames = sorted([file.split("/")[-1] for file in find_files(folder) if not file.split("/")[-1][0] == "."])
                # ** [TODO]
                # if (fileNames[0][2] == "_" and fileNames[0][4] == "_"):
                #     print("파일이름이 이미 변경되었습니다.") # 00_00_ 형태인 경우
                #     continue
                for myclass in myclasses:
                    if myclass["title"] == title:
                        productId = myclass["productId"]
                print(fileNames)
                print(len(fileNames), productId)

                try:
                    class_info_json_path = f"{DOWN_ROOT_FOLDER}/classes/{productId}/info.json"
                    info = load_json(class_info_json_path)
                    # print(info["title"], len(info["chapters"]))  # chapters
                    video_list = find_lecture_video_list_from_info(info)
                    if len(fileNames) != len(video_list):
                        print("!!!!!!!! 파일 개수가 일치하지 않습니다.")
                        continue
                    
                    # 파일 이름 변경
                    save_json(f"{folder}/video_list.json", video_list)
                    for i in range(len(fileNames)):
                        rename_file(f"{folder}/{fileNames[i]}", f"{folder}/{video_list[i]['name']}")

                    # 폴더 이동
                    move_folder(folder, folder.replace("/_class/", "/class101/"))
                except:
                    print("강좌 정보가 없습니다.")
                print("="*70)
                break
        else:
            print(f"++++++++++Not Found: {folderName}")

    print(folders)


def move_video_folders():
    folders = find_folders_leaf(VIDEO_ROOT_PATH)
    except_folders = [
        "E:/_class/금융 재테크/주식/주식 단타 스마트폰으로 하루 단 1시간 투자해서 월 1,000만원 수익내기",
        "E:/_class/금융 재테크/주식/코딩 없이 주식 자동매매하기, 평범한 사람이 시장을 이기는 방법",
        "E:/_class/제품 기획/PM PO/개발 지식 없어도 OK, 내가 생각하는 앱 서비스 기획하기",
        "E:/_class/창업 부업/더 새로운 창업 부업/누구나 할 수 있는 워드프레스 홈페이지 만들기 - 기획부터 출시까지 한 방에 OK",
        "E:/_class/창업 부업/블로그/자동으로 매달 천만원씩 통장에 들어오는 -구글 온라인 자동화수익 만들기-",
        "E:/_class/프로그래밍/Web 프론트엔드/React 로 웹 개발의 기초부터 프로덕션까지",
        "E:/_class/프로그래밍/Web 프론트엔드/실무에 강한 웹 퍼블리셔 포트폴리오 만들기",
        "E:/_class/프로그래밍/Web 프론트엔드/입문자도 할 수 있는 나만의 메신저 웹사이트 만들기",
        "E:/_class/프로그래밍/Web 프론트엔드/풀스택 리액트 개발자 취업을 위한 핵심 커리큘럼 by 몰입코딩",
        "E:/_class/프로그래밍/Web 프론트엔드/풀스택 웹 개발로 배우는 확진자 지도 서비스 만들기",
        "E:/_class/프로그래밍/프로그래밍언어/파이썬을 이용한 비트코인 자동매매 봇 만들기 풀 패키지",
    ]
    folders = [folder for folder in folders if not folder in except_folders]
    for folder in folders:
        move_folder(folder, folder.replace("/_class/", "/class101/"))
        # move_all_files(folder, folder.replace("/_class/", "/class101/"))


if __name__ == "__main__":
    # productId = "6257b7f7a16bad000e20d491"
    # html = load_file(find_class_html_path(productId), encoding="utf-8")
    # # * infos
    # # title = get_nodes(html, xpath='//h1')[0].text_content()
    # title = get_nodes(html, xpath='//div[@class="css-1qys0c1"]/h3')[0].text_content()
    # # __next > main > div > div.css-10g0pqe > div.css-4dhpus > div.css-w5dbe2 > div.css-d9x9r7 > div.css-169u1qh > div > div > div > div.css-1qys0c1 > h3
    # print(title)
    # get_class_data_by_productId("5e2556a44ba7b950bbd46bb5")

    # # ** get class data (강좌 제목으로)
    titles = [
        # "웹 프로그래머를 위한 워드프레스 플러그인 개발!",
        # "AI 자동 투자 봇 만들기, 노트북으로 월급을 두 배 불리는 법",
        # "풀스택 리액트 개발자 취업을 위한 핵심 커리큘럼 by 몰입코딩",
        # "클론코딩, 리액트로 소셜 네트워크 서비스 만들기",
        # "개발 지식 없어도 OK, 내가 생각하는 앱 서비스 기획하기",
        # "파이썬을 이용한 비트코인 자동매매 봇 만들기 풀 패키지",
        # "블로그 기초과정 ❘ 블로그로 하루 2시간 투자해서 직장인만큼 수익내기!",
        # "블로그 심화과정 ❘ 블로그로 월 1,000만 원까지 버는 핵심 비법!",
        # "코딩부터 배포까지! 입문자도 할 수 있는 나만의 메신저 웹사이트 만들기",
        # "딱 1번 배워 평생 써먹는 블로그 운영법 월 300만 원 만들기",
        # "AI도 대체할 수 없는 돈버는 지식 관리법 (제텔카스텐&옵시디언)",
        # "월 999만원 자동수익, 경제적 자유 얻는 구체적 가이드라인",
        # "코딩 없이 주식 자동매매하기, 평범한 사람이 시장을 이기는 방법",
        # "구글 애드센스로 평생 월 100만원 만드는 방법+돈버는 핵심 키워드 패키지",  # 소식(X)
        # "노트북 하나로 평생 돈 버는 <구글 온라인 자동화수익 만들기>",  # 소식(X)
        # "돈 버는 블로그, 황금 키워드와 제목에 대한 실전 노하우",  # 소식(X)
        # "기획에서 편집 디자인, 유통까지, 독립출판!",
        # "돈 되는 글쓰기의 비밀, 브랜드 블로그의 모든 것",
        # "파워블로거가 아니여도 가능한 월 300만원 월급 버는 <돈 되는 블로그 수익화> 노하우",
        # "리베하얀의 <웹퍼블리셔를 위한 SCSS(Sass) 프로젝트>",  # class_json['audio'] = texts[4].replace('오디오 ', '')


        # "코알못을 위한 부업, 투자에 활용하는 실용주의 파이썬 코딩",
        # "세상에서 제일 쉬운 파이썬 101 - 왕초보용 스크래치부터 파이썬까지",
        # "누구나 쉽게 만드는 나만의 다이어리 앱",
        # "TypeScript를 100% 활용한 풀스택 개발 프로젝트",
        # "<UXUI 디자이너 취업>, 취업은 이걸로 끝!",
    ]

    # for title in titles:
    #     get_class_data_by_title(title)
    #     time.sleep(20)

    # get_my_classes()

    # # # ** get class data (myclasses에 있으면서 현재 다운로드 되지 않는 데이터)
    # myclasses = load_json(MYCLASSES_JSON_PATH)
    # myproductIds = [_class['productId'] for _class in myclasses]
    # productIds = find_folders2(f"{DOWN_ROOT_FOLDER}/classes")
    # print(len(productIds), " ", productIds)
    # 
    # i = 0
    # for productId in myproductIds:
    #     if productId in productIds:
    #     # if productId in productIds or productId == "5cbe7fcfbf084b057dbf708d":
    #         print(f"#### {productId}")
    #         continue
    #     i += 1
    #     print(f"[{i}]: {productId}")
    #     get_class_data_by_productId(productId)
    #     time.sleep(10)


    # productId = '5fbb1b1c5cd1d500137cfdca'
    # sn = 5
    # print(get_lecture_info_by_sn(productId, sn, 'title'))
    # print(find_lecture_title_by_sn(productId, sn))


    # # ** test
    # class_info_json_path = f"{DOWN_ROOT_FOLDER}/classes/5e2556a44ba7b950bbd46bb5/info.json"
    # info = load_json(class_info_json_path)
    # print(info["title"], len(info["chapters"]))  # chapters
    # video_list = find_lecture_video_list_from_info(info)
    # print(len(video_list), video_list)  # chapters

    # rename_vidoes()

    # move_video_folders()

    # # * html2md(html_content)
    productId = "5e2556a44ba7b950bbd46bb5"
    productId = "602a6e4f3b950d0014898495"  # JB김종봉의 2천만원으로 경제적 자유를 달성한 진짜 이야기
    class_info = find_class_info_by_productId(productId)
    class_name = sanitize_filename(class_info["title"], repl="-")
    class_info['category'] = class_info['category'].replace(" · ", " ")
    category = class_info['category']
    material_md = frontmeta_from_dict(class_info) + "\n\n" + f"![]({class_info['image']})" + "\n\n"
    note_md = frontmeta_from_dict(class_info) + "\n\n"

    materials_folder = find_class_materials_folder(productId)

    html_paths = [file for file in find_files(materials_folder) if file[-5:] == ".html"]
    for html_path in html_paths:
        prefix = html_path.replace(materials_folder + "/", "").replace(".html", "")
        lecture_info = find_lecture_info_by_prefix(productId, prefix)
        lectureId = lecture_info.pop("lectureId")
        lecture_info['video_url'] = f"https://class101.net/ko/classes/{class_info['classId']}/lectures/{lectureId}"
        lecture_info['video_path'] = f"{VIDEO_ROOT_PATH2}/{category}/{prefix}_{lectureId}.mp4"
        frontmeta_from_dict(lecture_info)
        html_content = load_file(html_path)

        md = frontmeta_from_dict(lecture_info) + "\n\n" + html2md(html_content).replace("### 수업 노트", "")
        lecture_title = f"{prefix}_{sanitize_obsidian(lecture_info['title'])}"
        save_file(f"{OBSIDIAN_ROOT_FOLDER}/{category}/{class_name}/수업자료/{lecture_title}.md", md)
        material_md += f"[[{lecture_title}]]" + "\n\n"

        sn = str(lecture_info['sn']).zfill(3)
        save_file(f"{OBSIDIAN_ROOT_FOLDER}/{category}/{class_name}/정리노트/{sn}_{lecture_title}.md", md)
        note_md += f"[[{sn}_{lecture_title}]]" + "\n\n"

        # sn = str(lecture_info['sn']).zfill(3)
        # save_file(f"{OBSIDIAN_ROOT_FOLDER}/{category}/{class_name}/강의대본/_{lecture_title}.md", md)
        # script_md += f"[[{sn}_{lecture_title}]]" + "\n\n"


    save_file(f"{OBSIDIAN_ROOT_FOLDER}/{category}/{class_name}/수업자료.md", material_md)
    save_file(f"{OBSIDIAN_ROOT_FOLDER}/{category}/{class_name}/정리노트.md", note_md)




# 5c81296235b52893ce45a363
