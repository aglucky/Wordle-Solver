import cv2
from functools import cmp_to_key
import numpy as np
import pytesseract
import re


def contour_sort(a, b):
    br_a = cv2.boundingRect(a)
    br_b = cv2.boundingRect(b)
    if abs(br_a[1] - br_b[1]) <= 15:
        return br_a[0] - br_b[0]
    return br_a[1] - br_b[1]

#Get contours with wordle information
img = cv2.imread('wordle.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
thresh = cv2.adaptiveThreshold(gray, 255,
	cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 21, 10)
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
sortedCountours = sorted(contours, key=cmp_to_key(contour_sort))
filteredCountours = []
boxError = 15
for cnt in sortedCountours:
    x, y, w, h = cv2.boundingRect(cnt)
    if cv2.contourArea(cnt)>10000 and abs(w-h)<boxError:
        filteredCountours.append(cnt)

#Get Wordle Data
data = []
for cnt in filteredCountours:
    x, y, w, h = cv2.boundingRect(cnt)
    ROI = img[y:y+h, x:x+w]
    #Resize
    scale = 2
    width = int(ROI.shape[1] * scale)
    height = int(ROI.shape[0] * scale)
    dim = (width, height)
    ROI = cv2.resize(ROI, dim, interpolation = cv2.INTER_AREA)

    # Get Color
    average_color_row = np.average(ROI, axis=0)
    average_color = np.average(average_color_row, axis=0)

    # Get Letter
    grayROI = cv2.cvtColor(ROI, cv2.COLOR_BGR2GRAY)
    ret,threshROI = cv2.threshold(grayROI, 0, 255, cv2.THRESH_OTSU)
    threshROI = np.invert(threshROI)
    rawLetter = pytesseract.image_to_string(threshROI, lang='eng', config = '--psm 10')
    if len(rawLetter.strip())>0:
        letter = rawLetter.strip()[0]
        if letter == '|':
            letter = 'I'
        if letter == 'a':
            letter = 'V'
        data.append((average_color, letter, x))

# Make sure contourncorrectly
cv2.drawContours(img, filteredCountours, -1, (0,255,0), 3)
cv2.imwrite('test.png', img)

# Get true position key
positions = list(set(pos[2] for pos in data))
positions.sort()
pMap = {}
for i,p in enumerate(positions):
    pMap[p] = i

# Process data into letters w position and categories 
correct = []
exists = []
incorrect = []
error = 10
for line in data:
    color = line[0]
    letData = (line[1], pMap[line[2]])
    if abs(color[0]-color[1])<error and abs(color[2]-color[1])<error:
        incorrect.append(letData)
    elif color[0] < color[1] and color[2]<color[1]:
        correct.append(letData)
    else:
        exists.append(letData)


# Open wordbank
with open("words.txt", "r") as dict:
    words = dict.readlines()
solutions = [word.strip().upper() for word in words]

# Filter impossible words
correctPass = []
for word in solutions:
    possible = True
    for letter in correct:
       if not word[letter[1]] == letter[0]:
            possible = False
    if possible:
        correctPass.append(word)
    
existsPass = []
for word in correctPass:
    possible = True
    for letter in exists:
        if not letter[0] in word or  word[letter[1]] == letter[0]:
            possible = False
    if possible:
        existsPass.append(word)

finalPass = []
for word in existsPass:
    possible = True
    for letter in incorrect:
        if  letter[0] in word:
            possible = False
    if possible:
        finalPass.append(word)

# Function to perform sorting
def countDistinct(s):
    m = {}
    for i in range(len(s)):
        if s[i] not in m:
            m[s[i]] = 1
        else:
            m[s[i]] += 1
    return len(m)
def compare(a, b):
    return (countDistinct(b) - countDistinct(a))

# Print up to 5 best guesses
guesses = sorted(finalPass, key = functools.cmp_to_key(compare))
print('Top Guesses:')
for i, word in enumerate(guesses):
    if i > 4:
        break
    print(word)