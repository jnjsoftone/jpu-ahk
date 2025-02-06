"""
네오보감 실행
"""
import time
import os
import json
import random
from ahk import AHK
from PIL import ImageGrab
import argparse

ahk = AHK()
ahk.set_coord_mode('Mouse', 'Screen')

# # monitor 좌표
# [min_x1, min_y1, max_x1, max_y1] = [0, 0, 2559, 1439] # monitor1(QHD) [top, left, right, bottom]
# [min_x2, min_y2, max_x2, max_y2] = [2560, 104, 4479, 1183] # monitor2(FHD) [top, left, right, bottom]

# # OBS, Chrome 좌표
# [obs_x, obs_y] = [100, 100] # top-left
# [obs_w, obs_h] = [1280, 720] # size(width, height)
# [chrome_x, chrome_y] = [2680, 200] # top-left
# [chrome_w, chrome_h] = [1280, 720] # size(width, height)

# monitor 좌표
[min_x1, min_y1, max_x1, max_y1] = [0, 0, 1919, 1079] # monitor1(QHD) [top, left, right, bottom]
[min_x2, min_y2, max_x2, max_y2] = [1920, 0, 3839, 1079] # monitor2(FHD) [top, left, right, bottom]

# OBS, Chrome 좌표
[obs_x, obs_y] = [100, 100] # top-left
[obs_w, obs_h] = [1280, 720] # size(width, height)
[chrome_x, chrome_y] = [2020, 100] # top-left
[chrome_w, chrome_h] = [1280, 720] # size(width, height)


def get_random_number(min_val=10, max_val=100) -> int:
    """min_val과 max_val 사이의 랜덤 숫자 반환"""
    return random.randint(min_val, max_val)



def before_start_video(profileNum=2):
    """영상 재생 전 준비 작업"""
    # OBS 실행
    ahk_script = rf"""
    Run, C:/Program Files/obs-studio/bin/64bit/obs64.exe, C:/Program Files/obs-studio/bin/64bit
    WinWait, OBS 
    WinMove, OBS,, {obs_x}, {obs_y}, {obs_w}, {obs_h}
    """

    # print(ahk_script)

    ahk.run_script(ahk_script)

    time.sleep(5)

    # Chrome 실행
    ahk_script = rf"""
    Run, "C:/Program Files/Google/Chrome/Application/chrome.exe" --profile-directory="Profile {profileNum}"
    WinWait, ahk_exe chrome.exe
    WinMove, ahk_exe chrome.exe,, {chrome_x}, {chrome_y}, {chrome_w}, {chrome_h}
    """

    print(ahk_script)

    ahk.run_script(ahk_script)

    time.sleep(2)


# 해상도 설정
def set_resolution(resolution="1080", platform="class101"):
    """해상도 설정"""
    if platform == "class101":
        ahk.click(x=3705, y=1040)
        time.sleep(2)
        ahk.click(x=3705, y=875)
        time.sleep(2)
        ahk.click(x=3695, y=835)
        time.sleep(2)
        # ahk.click(x=2562, y=1070)
        # time.sleep(2)
        print("### 해상도 설정 완료")
    print("### 마우스 이동")
    ahk.click(x=min_x2 + 600, y=max_y2 - 50)


# 파일 저장 설정
# C:\Users\jungsam\Videos\class101
def set_save_file(path):
    path_split = path.replace("\\", "/").split("/")
    dir = "/".join(path_split[:-1])
    # dir = "C:/Users/jungsam/Videos/class101"
    name = path_split[-1].split(".")[0]
    # name = "test001"
    """파일 저장 설정"""
    # '설정' 클릭
    ahk.click(x=obs_x+1150, y=obs_y+615)
    time.sleep(2)
    # '출력' 클릭
    ahk.click(x=obs_x+200, y=obs_y+130)
    time.sleep(2)
    # '녹화 저장 경로' 변경
    ahk.click(x=obs_x+600, y=obs_y+380)
    time.sleep(0.2)
    ahk.key_down('Control')
    ahk.send("a")
    ahk.key_up('Control')
    ahk.send(dir)
    # '적용' 클릭
    ahk.click(x=obs_x+1070, y=obs_y+700)
    time.sleep(2)
    # '고급' 클릭
    ahk.click(x=obs_x+200, y=obs_y+300)
    time.sleep(2)
    # '파일명 형식' 변경
    ahk.click(x=obs_x+600, y=obs_y+415)
    time.sleep(0.2)
    ahk.key_down('Control')
    ahk.send("a")
    ahk.key_up('Control')
    ahk.send(name)
    # '확인' 클릭
    ahk.click(x=obs_x+950, y=obs_y+700)
    time.sleep(1)
    ahk.click(x=obs_x+950, y=obs_y+700)
    time.sleep(1)


def goto_url(url, *, delay=10, dx=200, dy=60):
    # print(f"goto_url: {url}, delay: {delay}, dx: {dx}, dy: {dy}")
    # chrome 주소창에 url 입력
    ahk.click(x = chrome_x + dx, y = chrome_y + dy) # chrome 주소창
    time.sleep(0.2)
    ahk.key_down('Control')
    ahk.send("a")
    ahk.key_up('Control')
    time.sleep(0.3)

    ahk.send(url)
    ahk.send("{Enter}")
    time.sleep(delay)


# [2680, 200] dx = 700, 530
def full_screen(*, dx=715, dy=535, delay=3):
    # 전체 화면으로
    ahk.click(x=chrome_x+dx, y=chrome_y+dy)
    time.sleep(delay)


# def pause_video(*, heights=8, dx=32, dy=28, color="0xD1D7DC"):
#     """영상 재생 상태를 확인하는 함수"""
#     # print("#####영상 재생 상태 확인")
#     # play/pause 콘트롤이 생기도록 커서 이동
#     # ahk.mouse_move(x=min_x2 + dx + 10, y=max_y2 - dy)
#     # ahk.click(x=min_x2 + dx + 10, y=max_y2 - dy)
#     # ahk.mouse_move(x=min_x2 + 600, y=max_y2 - 50)
#     # ahk.click(x=min_x2 + 600, y=max_y2 - 50)
#     ahk.click()
#     time.sleep(1)

#     # 전체 스크린샷 캡처 (모든 모니터)
#     screenshot = ImageGrab.grab(all_screens=True)
#     # print(f"Screenshot size: {screenshot.size}")
#     is_playing = True


#     # !!
#     # 두 번째 모니터 영역만 확인
#     # for i in range(heights):
#     #     pause_x = min_x2 + dx
#     #     pause_y = max_y2 - dy + i
        
#     #     rgb_color = screenshot.getpixel((pause_x, pause_y))
#     #     # print(f"0x{rgb_color[0]:02X}{rgb_color[1]:02X}{rgb_color[2]:02X}")
#     #     if color != f"0x{rgb_color[0]:02X}{rgb_color[1]:02X}{rgb_color[2]:02X}":
#     #         is_playing = False
#     #         break

#     if is_playing:
#         print("!!!!!영상 재생중 !!!!")
#         ahk.send("{Space}")  # 자동 재생시(영상 재생 중지)
    
#     time.sleep(1)
#     ahk.click()

#     # 커서 원래 위치로 이동
#     # ahk.mouse_move(x=10, y=10)


def pause_video(*, heights=8, dx=32, dy=28, color="0xD1D7DC"):
    ahk.send("{Space}")  # 자동 재생시(영상 재생 중지)


def start_record():
    """녹화 시작"""
    # !! 
    # dx = 91
    # dy = 45
    # # play/pause 콘트롤이 생기도록 커서 이동
    # ahk.mouse_move(x=min_x2 + dx + 20, y=max_y2 - dy)
    # time.sleep(2)
    # OBS 녹화 버튼 클릭
    # time.sleep(10)
    ahk.click(x=obs_x+60, y=obs_y+15)
    time.sleep(0.5)
    ahk.key_down('Control')
    ahk.send("s")
    ahk.key_up('Control')
    time.sleep(0.1)
    # print("OBS 녹화 버튼 클릭")

    # time.sleep(60)
    # 영상 재생 시작
    # ahk.mouse_move(x=chrome_x+10, y=chrome_y+300)
    # ahk.click(x=chrome_x+10, y=chrome_y+300)
    # time.sleep(40)
    ahk.mouse_move(x=min_x2 + 10, y=max_y2 - 300)
    ahk.click(x=min_x2 + 10, y=max_y2 - 300)
    ahk.mouse_move(x=min_x2 - 50, y=max_y2 - 300)
    # print("Player 녹화 시작")


def done_record():
    """녹화 완료"""
    ahk.click(x=obs_x+60, y=obs_y+15)
    ahk.key_down('Control')
    ahk.send("q")
    ahk.key_up('Control')
    time.sleep(2)

    # chrome 축소 화면으로 돌아가기
    ahk.click(x=chrome_x+800, y=chrome_y+600)
    time.sleep(2)
    ahk.send("{F11}")
    time.sleep(2)


def seconds_to_hhmmss(seconds: int) -> str:
    """초를 HH:mm:ss 형식으로 변환"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


# ** class101 **
def record_video_class101(url, duration, path):
    """녹화"""
    # print(f"녹화 시작: {url} ({seconds_to_hhmmss(duration)})")
    if duration == 0:
        return
    # 파일 저장 설정
    # path의 directory 생성
    os.makedirs(os.path.dirname(path), exist_ok=True)
    set_save_file(path)
    time.sleep(2)

    # # chrome 주소창에 url 입력
    goto_url(url)
    time.sleep(3)

    # 전체/축소 화면(chrome 축소 화면)
    # 전체 화면으로
    # full_screen(dx=715, dy=535, delay=3)
    full_screen(dx=710, dy=530, delay=3)
    time.sleep(1)
    ahk.click(x=min_x2 + 600, y=max_y2 - 50)

    # 해상도 설정
    # set_resolution(resolution="1080", platform="class101")

    # # 영상이 재생되고 있는지 확인!!
    # time.sleep(3)
    pause_video(heights=8, dx=91, dy=45, color="0xFFFFFF")
    time.sleep(2)
    # time.sleep(10)
    # print("처음으로...")

    # 처음으로
    # ahk.key_down('Control')
    # slider 이동
    # ahk.click(x=min_x2 + 50, y=max_y2 - 80)
    # !! 1분 정도 동영상에서는 영상 중지가 안되는 에러
    ahk.click(x=min_x2 + 30, y=max_y2 - 75)
    time.sleep(1)
    # ahk.click(x=min_x2 + 50, y=max_y2 - 75)
    # time.sleep(1)
    # ahk.mouse_move(x=min_x2 + 80, y=max_y2 - 300)
    # time.sleep(1)
    for _ in range(10):
        ahk.key_press("Left")
        time.sleep(0.1)
    # ahk.key_up('Control')
    time.sleep(5)

    # # start_record() 함수를 사용하면 '처음으로'시에 재생이 계속되는 버그
    start_record()
    # # OBS 녹화 시작
    # ahk.click(x=obs_x+60, y=obs_y+15)
    # time.sleep(0.5)
    # ahk.key_down('Control')
    # ahk.send("s")
    # ahk.key_up('Control')
    # time.sleep(0.1)
    # print("OBS 녹화 버튼 클릭")

    # # time.sleep(60)
    # # 영상 재생 시작
    # ahk.mouse_move(x=min_x2 + 10, y=max_y2 - 300)
    # ahk.click(x=min_x2 + 10, y=max_y2 - 300)
    # print("Player 녹화 시작")
    # # time.sleep(1)

    # OBS 녹화
    # 영상 재생 시간 확인
    time.sleep(duration)

    # OBS 녹화 완료
    done_record()

    # time.sleep(100000)

# ** main (record videos)

def record_videos_class101(classId, include_sns=[], errorLectures=[]):
    root_path = r"C:\JnJ-soft\Projects\internal\@jnjsoft\jnj-learn\_repo\class101"
    json_path = rf"{root_path}\json\classes\{classId}.json"

    with open(json_path, "r", encoding="utf-8") as f:
        videos = json.load(f)

    """녹화 여러 동영상"""
    # 영상 재생 전 준비 작업(chrome, OBS)
    # before_start_video()

    # * video 중에서 video가 없거나, 비어있는 것(hasVideo=True & downVideo)
    # _videos = [video for video in videos if video.get("lectureId") and len(video.get("subtitles")) > 0 and not video.get("downVideo")]

    # 이미 녹화된 파일이 있는 video 제외
    if len(include_sns) > 0:
        _videos = [video for video in videos if video['sn'] in include_sns]
    else:
        _videos = [video for video in videos if not os.path.exists(rf"{root_path}\video\{classId}\{str(video['sn']).zfill(3)}_{video['lectureId']}.mp4")]

    # _videos = [
    #     video for video in _videos 
    #     if not os.path.exists(rf"{root_path}\video\{classId}\{str(video['sn']).zfill(3)}_{video['lectureId']}.mp4")
    #     and not any(
    #         el['classId'] == classId 
    #         and el['sn'] == video['sn'] 
    #         and el['lectureId'] == video['lectureId'] 
    #         for el in errorLectures
    #     )
    # ]

    # 에러 강의 제외
    _videos = [video for video in _videos if not any(el['classId'] == classId and el['sn'] == video['sn'] for el in errorLectures)]

    # _video_sns = [video['sn'] for video in _videos]
    # not_recorded_sn = [str(video['sn']) for video in videos if video['sn'] not in _video_sns]  # int를 str로 변환
    # not_recorded_sn_str = ', '.join(not_recorded_sn)
    # print(f"녹화되지 않은 영상: {not_recorded_sn_str}")
    
    log = ""  # log 초기화 위치 변경
    # if not_recorded_sn_str:
    #     log += f"녹화되지 않은 영상: {not_recorded_sn_str}\n"

    # * Loop: 녹화
    for video in _videos:
        try:
            url = f"https://class101.net/ko/classes/{classId}/lectures/{video['lectureId']}"
            duration = video["duration"]
            if duration == 0:
                continue
            path = rf"{root_path}\video\{classId}\{str(video['sn']).zfill(3)}_{video['lectureId']}.mp4"
            # print(url, duration, path)
            print(f"### {video['sn']}번째 {video['title']} {seconds_to_hhmmss(duration)}")
            record_video_class101(
                url, 
                duration, 
                path
            )
            log += f"{video['sn']} {video['lectureId']}\n"

            # with open(f"./log_{classId}.txt", 'w', encoding='utf-8') as f:
            #     f.write(log)

            # ! 에러 다운로드 후, 일괄적으로 변경
            # TODO: 디버그 후 실행
            # # 원본 videos에서 해당 video 찾아서 업데이트
            # target_video = next(v for v in videos if v["lectureId"] == video["lectureId"])
            # target_video["downVideo"] = True
            
            # # JSON 파일 저장
            # with open(json_path, "w", encoding="utf-8") as f:
            #     json.dump(videos, f, indent=2, ensure_ascii=False)
            time.sleep(5)
        except Exception as e:
            print(f"Error recording video: {e}")
            continue
    
    return log


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--url', required=True, help='강의 URL')
    # parser.add_argument('--duration', type=int, required=True, help='녹화 시간(초)')
    # args = parser.parse_args()

    # record_video_class101(args.url, args.duration)

    # before_start_video(profileNum=2)
    # # path = "C:/Users/jungsam/Videos/_class101/test002.mp4"
    # # set_save_file(path)

    # url = "https://class101.net/ko/classes/6447ca8e5566230015b352ef/lectures/64914feee0d83f000f4510d8"
    # duration = 10
    # path = r"C:\Users\jungsam\Videos\_class102\test003.mp4"
    # record_video_class101(url, duration, path)

    # ** video 다운로드
    # classId = "60dd9a6bc531190014d360c4"
    # record_videos_class101(classId)

    before_start_video()

    # # !! 다시 녹화
    # !! 확인요: 632bbd5e6d337d000ffcbabe 1, 26 (2분 미만, 제대로 녹화되었는지)
    redowns = [
        # ["5f5f12977ee30d00073383f0", [13, 24]],  // !! 12, 23도 확인 필요
        # ["5d0b3a236a3bd1095630cee7", list(range(4, 35))],
        # ["5e71ab3edd13f46aa1bbe1fe", list(range(18, 47))],
        # ["5e71ab3edd13f46aa1bbe1fe", [19, 31]],
        # ["5c514d81d30c532c44694761", list(range(21, 23))],
        # ["621870c8d29df1000d3c1d82", list(range(1, 24))],
        # ["621870c8d29df1000d3c1d82", [7, 8, 9]],
        # ["5d31bb48125d26d5fb37241a", [9, 44, 45, 46, 47]],
        # ["5d91826171dcdf0c19dd4486", [17, 18, 19]], # !! 재확인 필요
        # ["606e2ce995f580000e2da438", [11, 12, 26, 28]], # !! 재확인 필요
        # ["606e2ce995f580000e2da438", list(range(27, 54))],
        # ["5fd5b0e9d56d4e001538b829", list(range(1, 46))],
        # ["6215cf62578efc000e314d83", list(range(21, 43))],
        # ["5f43f9a392236b001bf1eb40", [3, 16]],  # !! 재확인 필요(24, 25)
        # ["5f434c3699b841001331f601", list(range(23, 41))], # !! 재확인 필요(38, 39)
        # ["625d61ccc55f71000e78df26", list(range(19, 27))], # !! 재확인 필요(38, 39)
        # ["5f434c3699b841001331f601", [39, 40]],
        # ["5f43f9a392236b001bf1eb40", [25, 26]],
        # ["5d91826171dcdf0c19dd4486", [17, 18, 55]],
        # ["5d31bb48125d26d5fb37241a", [23, 24]],
        # ["5e71ab3edd13f46aa1bbe1fe", [30, 31]],
        # ["5f434c3699b841001331f601", list(range(23, 39))]
        ["62e0b928c519a9000ed8ac9e", list(range(1, 12))],
        ["61d29382c469320014395fa7", list(range(20, 24))]
    ]


    # errorLectures = json.loads(open(r"C:\JnJ-soft\Projects\internal\@jnjsoft\jnj-learn\_repo\class101\json\errorLectures.json", "r", encoding="utf-8").read())

    # # print(errorLectures)
    # # !! 중복 강의 있는 강좌 제외
    # errorClassIds = json.loads(open(r"C:\JnJ-soft\Projects\internal\@jnjsoft\jnj-learn\_repo\class101\json\overlappedClassIds.json", "r", encoding="utf-8").read())

    for classId, sns in redowns:
        print(f"========== {classId} 녹화 시작 ==========")
        record_videos_class101(classId, sns)
        time.sleep(get_random_number(min_val=5, max_val=30))

    # # !! 전체 녹화
    # myclassIds_path = "C:/JnJ-soft/Projects/internal/@jnjsoft/jnj-learn/_repo/class101/json/myclassIds.json"
    # with open(myclassIds_path, "r", encoding="utf-8") as f:
    #     # print(f.read())
    #     classIds = json.load(f)
    #     classIds.reverse()
    #     # classList = []
    #     log = ""
    #     for i, classId in enumerate(classIds):
    #         if classId in errorClassIds:
    #             continue
    #         # classList.append(f"[{i}] {classId}")
    #         # !! i = 4 다운로드 여부 확인요 "621870c8d29df1000d3c1d82"
    #         if i < 27:
    #             continue
    #         print(f"========== [{i}] {classId} 녹화 시작 ==========")
    #         log += f"[{i}] {classId}\n"

    #         log += record_videos_class101(classId)

    #         with open('./log.txt', 'a', encoding='utf-8') as f:
    #             f.write(log)

    #         time.sleep(get_random_number(min_val=5, max_val=30))
