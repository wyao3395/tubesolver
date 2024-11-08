import cv2
import numpy as np
import functools

tubecolors = np.array([
    (40, 32, 53),  # empty 0
    (234, 2, 50),  # red 1
    (254, 206, 2), # yellow 2
    (3, 127, 199), # blue 3
    (7, 166, 3), # green 4
    (255, 122, 1), # orange 5
    (93, 42, 135), # purple 6
    (179, 75, 46), # brown 7
    (150, 203, 1), # light green 8
    (45, 228, 210), # light blue 9
    (246, 53, 220), # light purple 10
    (211, 159, 122), # light brown 11
    (0, 103, 60),  # dark green 12
    (2, 67, 151),  # dark blue 13
    (184, 207, 223), # white 14
])[:,(2,1,0)]  #convert to BGR

def get_init_state(filename):
    image = cv2.imread(filename)
    resized_image = cv2.resize(image, (image.shape[1]//2, image.shape[0]//2))  # Resize if needed for easier processing

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
    for t in tuberects:
        for i in range(4):
            y = t[1] + i*t[3]//5 + t[3]//4
            x = t[0] + t[2]//2
            c = resized_image[y][x]
            idx = np.argmin(np.sum((c-tubecolors)**2, axis=1))
            indexes.append(idx)
    return indexes

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
        print("finish", bt)
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
            
            if find_solve(n, bt + [(i+1,j+1)]):
                return True

    return False

#state = get_init_state("C:\\Users\\wyao\\Pictures\\Weixin Image_20240731161957.jpg")
state = get_init_state("C:\\Users\\wyao\\Pictures\\Weixin Image_20240729101038.jpg")
#state = get_init_state("C:\\Users\\wyao\\Pictures\\game1.jpg")
print_state(state)
find_solve(state, [])
