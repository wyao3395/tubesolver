from PIL import Image

tubecolors = [
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
]
xaxis = {
    3:[280*n+259 for n in range(4)],
    4:[240*n+179 for n in range(4)],
    5:[200*n+139 for n in range(5)],
    6:[177*n+100 for n in range(6)]
}

yaxis = {
    # 92n+off for n in range(4)
    2:[822, 1374],
    3:[554, 1054, 1554], 
}

def get_init_state(im, n):
    colors = []
    lines = len(n)
    yoff = yaxis[lines]
    for k in range(lines):
        xoff = xaxis[n[k]]
        for j in range(n[k]):
            if k == lines-1 and j == n[k]-1:
                continue
            for i in range(4):
                colors.append(im.getpixel((xoff[j], yoff[k]+92*i)))
                    
    indexes = []
    for a in colors:
        for i in range(15):
            b  = tubecolors[i]
            c = (a[0]-b[0])**2 +(a[1]-b[1])**2 + (a[2]-b[2])**2
            if c < 100:
                #print(a,b,c,i)
                indexes.append(i)
                break
        else:
            print("color not found")
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

im = Image.open("game1.jpg")
state = get_init_state(im, [5,6,6])
print_state(state)
find_solve(state, [])
