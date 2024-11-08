import cv2
import numpy as np
import functools
import os
import time

def get_init_state(filename):
    image = cv2.imread(filename)
    resized_image = cv2.resize(image, (image.shape[1]//2, image.shape[0]//2))  # Resize for easier processing

    gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(gray, 195, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    tuberects  = [cv2.boundingRect(c) for c in contours if cv2.contourArea(c)>10000]
    def tubesortcmp(a, b):
        if abs(a[1]-b[1])<10:
            return a[0]-b[0]
        else:
            return a[1]-b[1]
    tuberects = sorted(tuberects, key = functools.cmp_to_key(tubesortcmp))

    indexes = []
    tubecolors = np.array([(53, 32, 40)])

    for t in tuberects:
        for i in range(4):
            y = t[1] + i*t[3]//5 + t[3]//4
            x = t[0] + t[2]//2
            c = resized_image[y][x]
            d = np.sum((c-tubecolors)**2, axis=1)
            idx = np.argmin(d)
            if d[idx]>100:
                idx = tubecolors.shape[0]
                tubecolors = np.append(tubecolors, [c], axis=0)
            indexes.append(idx)
    return indexes, tuberects

def print_state(s):
    print("---------------")
    for i in range(len(s) // 4):
        print(s[i*4:i*4+4])

def find_solve(s, bt):
    N = len(s) // 4
    for j in range(N):
        if not (s[j*4] == s[j*4+1] == s[j*4+2] == s[j*4+3]):
            break
    else:
        #print("finish", bt)
        return True
    
    for j in range(N):
        if s[j*4]:
            continue
        elif s[j*4+1]:
            idx = 0
            size = 1
            color = s[j*4+1]
        elif s[j*4+2]:
            idx = 1
            size = 2
            color = s[j*4+2]
        elif s[j*4+3]:
            idx = 2
            size = 3
            color = s[j*4+3]
        else:
            idx = 3
            size = 4
            color = 0

        for i in range(N):
            # source tube can not be same as destination tube
            # and source tube can not be empty tube
            if j == i or s[i*4+3] == 0:
                continue
            
            ssame = False
            for sidx in range(4):
                if s[i*4 + sidx]:
                    scolor = s[i*4+sidx]
                    ssize = 1
                    break
            for sidx2 in range(sidx+1, 4):
                if s[i*4 + sidx2] != scolor:
                    break
                ssize += 1
            else:
                ssame = True
                
            #skip if destination tube is not empty and source top != destination top
            if color != 0 and color != scolor:
                continue
            
            #skip if destination is empty and source only has one color
            if ssame and color == 0:
                continue
            
            # skip if destination tube has not enough space
            if ssize>size:
                continue
            
            n = s[:]
            for k in range(ssize):
                n[j*4+idx-k] = scolor
                n[i*4+sidx+k] = 0
            
            bt.append((i+1,j+1))
            if find_solve(n, bt):
                return True
            bt.pop()
    return False

def get_init_state_via_adb():
    os.system("adb shell screencap /sdcard/screenshot.png")
    os.system("adb pull /sdcard/screenshot.png screenshot.png")
    state = get_init_state("screenshot.png")
    os.remove("screenshot.png")
    return state

def perform_solve_via_adb(solve, rects):
    for s in solve:

        a = s[0]-1
        r = rects[a]
        x = r[0]*2 + r[2]
        y = r[1]*2 + r[3]
        print("from:", x, y)
        os.system(f"adb shell input tap {x} {y}")
        time.sleep(0.5)

        b = s[1]-1
        r = rects[b]
        x = r[0]*2 + r[2]
        y = r[1]*2 + r[3]
        print("to  :", x*2, y*2)
        os.system(f"adb shell input tap {x} {y}")
        time.sleep(0.5)



filename = "C:\\Users\\wyao\\Pictures\\Weixin Image_20241108172102.jpg"
#filename = "C:\\Users\\wyao\\Pictures\\Weixin Image_20240731161957.jpg"
#filename = "C:\\Users\\wyao\\Pictures\\Weixin Image_20240729101038.jpg"
#filename = "C:\\Users\\wyao\\Pictures\\Weixin game1.jpg"

#state, rects = get_init_state(filename)
state, rects = get_init_state_via_adb()

print_state(state)
solve = []
find_solve(state, solve)
print(solve)
perform_solve_via_adb(solve, rects)
