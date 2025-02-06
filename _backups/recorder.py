"""
네오보감 실행
"""
import time
from ahk import AHK
from PIL import ImageGrab

ahk = AHK()
ahk.set_coord_mode('Mouse', 'Screen')

# monitor 좌표
[min_x1, min_y1, max_x1, max_y1] = [0, 0, 2559, 1439] # monitor1(QHD) [top, left, right, bottom]
[min_x2, min_y2, max_x2, max_y2] = [2560, 104, 4479, 1183] # monitor2(FHD) [top, left, right, bottom]

# OBS, Chrome 좌표
[obs_x, obs_y] = [100, 100] # top-left
[obs_w, obs_h] = [1280, 720] # size(width, height)
[chrome_x, chrome_y] = [2680, 200] # top-left
[chrome_w, chrome_h] = [1280, 720] # size(width, height)


def before_start_video(profileNum=2):
    """영상 재생 전 준비 작업"""
    # OBS 실행
    ahk_script = rf"""
    Run, C:/Program Files/obs-studio/bin/64bit/obs64.exe, C:/Program Files/obs-studio/bin/64bit
    WinWait, OBS 
    WinMove, OBS,, {obs_x}, {obs_y}, {obs_w}, {obs_h}
    """

    print(ahk_script)

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


def goto_url(url, *, delay=10, dx=200, dy=60):
    print(f"goto_url: {url}, delay: {delay}, dx: {dx}, dy: {dy}")
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

def full_screen(*, dx=715, dy=535, delay=3):
    # 전체 화면으로
    ahk.click(x=chrome_x+dx, y=chrome_y+dy)
    time.sleep(delay)

# 해상도 설정
def set_resolution(resolution="1080", platform="class101"):
    """해상도 설정"""
    if platform == "class101":
        ahk.click(x=4344, y=1143)
        time.sleep(2)
        ahk.click(x=4378, y=976)
        time.sleep(2)
        ahk.click(x=4241, y=934)
        time.sleep(2)
        ahk.click(x=2562, y=1070)
        time.sleep(2)


def pause_video(*, heights=8, dx=32, dy=28, color="0xD1D7DC"):
    """영상 재생 상태를 확인하는 함수"""
    # 전체 스크린샷 캡처 (모든 모니터)
    screenshot = ImageGrab.grab(all_screens=True)
    # print(f"Screenshot size: {screenshot.size}")
    is_playing = True
    
    # 두 번째 모니터 영역만 확인
    for i in range(heights):
        pause_x = min_x2 + dx
        pause_y = max_y2 - dy + i
        
        rgb_color = screenshot.getpixel((pause_x, pause_y))
        # print(f"0x{rgb_color[0]:02X}{rgb_color[1]:02X}{rgb_color[2]:02X}")
        if color != f"0x{rgb_color[0]:02X}{rgb_color[1]:02X}{rgb_color[2]:02X}":
            is_playing = False
            break

    if is_playing:
        print("!!!!!영상 재생중 !!!!")
        ahk.send("{Space}")  # 자동 재생시(영상 재생 중지)
        time.sleep(2)


# def check_video_paused(ahk=ahk, max_attempts=5):
#     """영상 재생 상태를 확인하는 함수"""
#     for dx in range(max_attempts):
#         # 방법 1: play 버튼 픽셀 색상 확인
#         pause_x = chrome_x + 88  # pause 버튼의 x 좌표
#         pause_y = chrome_y + 1038  # pause 버튼의 y 좌표
#         color = ahk.pixel_get_color(pause_x, pause_y)
#         # pause 버튼의 예상 색상과 비교 (실제 색상값으로 수정 필요)
#         return color != "0xFFFFFF" 

def start_record():
    """녹화 시작"""
    # OBS 녹화 버튼 클릭
    ahk.click(x=obs_x+60, y=obs_y+15)
    time.sleep(0.5)
    ahk.key_down('Control')
    ahk.send("s")
    ahk.key_up('Control')

    # 영상 재생 시작
    ahk.click(x=chrome_x+1, y=chrome_y+300)
    time.sleep(0.1)
    ahk.mouse_move(x=10, y=10)


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

# ** class101 **
def record_video_class101(url, duration):
    """녹화"""
    # chrome 주소창에 url 입력
    goto_url(url)

    # 전체/축소 화면(chrome 축소 화면)
    # 전체 화면으로
    full_screen(dx=715, dy=535, delay=5)

    # 해상도 설정
    set_resolution(resolution="1080", platform="class101")

    # # 영상이 재생되고 있는지 확인!!
    pause_video(heights=8, dx=91, dy=45, color="0xFFFFFF")

    # 처음으로
    ahk.key_down('Control')
    for _ in range(50):
        ahk.send("{Left}")
    ahk.key_up('Control')
    time.sleep(2)

    # OBS 녹화 시작
    start_record()
    # time.sleep(1)

    # OBS 녹화
    # 영상 재생 시간 확인
    time.sleep(duration)

    # OBS 녹화 완료
    done_record()


# ** udemy **
def record_video_udemy(url, duration):
    """녹화"""
    # chrome 주소창에 url 입력
    goto_url(url)

    # 전체 화면으로
    full_screen(dx=770, dy=550, delay=5)

    # # 해상도 설정
    # set_resolution_class101("1080")

    # 영상 멈춤
    pause_video(heights=8, dx=32, dy=28, color="0xD1D7DC")

    # 처음으로
    for _ in range(20):
        ahk.send("{Left}")
    ahk.key_up('Control')

    # OBS 녹화 시작
    start_record()
    # time.sleep(1)

    # OBS 녹화
    # 영상 재생 시간 확인
    time.sleep(duration)

    # OBS 녹화 완료
    done_record()


# ** main (record videos)

def record_videos_class101(videos):
    """녹화 여러 동영상"""
    # 영상 재생 전 준비 작업(chrome, OBS)
    before_start_video(ahk=ahk)

    # * Loop: 녹화
    for video in videos:
        record_video_class101(video["url"], video["duration"])


def record_videos_udemy(videos):
    """녹화 여러 동영상"""
    # 영상 재생 전 준비 작업(chrome, OBS)
    before_start_video(ahk=ahk)

    # * Loop: 녹화
    for video in videos:
        record_video_udemy(video["url"], video["duration"])


if __name__ == "__main__":
    pass
    # videos = [
    #     {"url": "https://class101.net/ko/classes/6447ca8e5566230015b352ef/lectures/6491510f13e5eb000ef75797", "duration": 40},
    #     {"url": "https://class101.net/ko/classes/6447ca8e5566230015b352ef/lectures/64915149ef85fe000e414174", "duration": 49}
    # ]
    # before_start_video(profileNum=2)
    # record_video_class101(videos[0]['url'], videos[0]['duration'])
    # record_videos_class101(videos)
    # print("hello")

    # # * record udemy
    # before_start_video(profileNum=15)
    # record_video_udemy(url="https://www.udemy.com/course/react-the-complete-guide-incl-redux/learn/lecture/39836178", duration=30)

    # for i in range(10):
    #     print(85 + i, ":============================")
    #     pause_video(heights=8, dx=85 + i, dy=45, color="0xFFFFFF")
