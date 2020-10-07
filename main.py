import io
import os
try:
    import Image
except ImportError:
    from PIL import Image,ImageEnhance,ImageGrab
import pytesseract
import webbrowser
from googleapiclient.discovery import build
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time
import re
import sys, tty, termios
from PIL import ImageFile
import pyscreenshot

from google.cloud import vision
from google.cloud.vision import types

def retrieve_q_and_a(text):
	question_answers = text.split('?')
	if len(question_answers) > 2:
		corrString = ''
		for x in range(len(question_answers) - 1):
			corrString += question_answers[x]
		question_answers = [corrString, question_answers[len(question_answers) - 1]]
	question = question_answers[0].replace('\n', ' ')
	answers = question_answers[1].split('\n')
	answers = [ans.strip() for ans in answers]
	answers = [x for x in answers if x != '']
	#print(answers)
	return question, answers

g_cse_api_key = 'google custom search engine api'
g_cse_id = 'google custom search engine id'
#

def notify(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))

def approach1(question):
    url = "https://www.google.com.tr/search?q={}".format(question)
    webbrowser.open(url)

def google_search(query, start):
	service = build("customsearch", "v1", developerKey=g_cse_api_key)
	res = service.cse().list(q=query, cx=g_cse_id, start=start).execute()
	return res
#
#
def approach2(question, answers):
    met1 = [0, 0, 0]
    res = google_search(question,None)
    items = str(res['items']).lower()
    # print items
    met1[0] = items.count(answers[0].lower())
    met1[1] = items.count(answers[1].lower())
    met1[2] = items.count(answers[2].lower())
    return met1

def approach3(question, answers):
    met2 = [0, 0, 0]
    res0 = google_search(question + ' ' + answers[0], None)
    res1 = google_search(question + ' ' + answers[1], None)
    res2 = google_search(question + ' ' + answers[2], None)
    return [int(res0['searchInformation']['totalResults']), int(res1['searchInformation']['totalResults']), int(res2['searchInformation']['totalResults'])]

def predict(metric1, metric2, answers):
    max1 = metric1[0]
    max2 = metric2[0]
    for x in range(1, 3):
        if metric1[x] > max1:
            max1 = metric1[x]
        if metric2[x] > max2:
            max2 = metric2[x]
    if metric1.count(0) == 3:
        return answers[metric2.index(max2)]
    elif metric1.count(max1) == 1:
        if metric1.index(max1) == metric2.index(max2):
            return answers[metric1.index(max1)]
        else:
            percent1 = max1 / sum(metric1)
            percent2 = max2 / sum(metric2)
            if percent1 >= percent2:
                return answers[metric1.index(max1)]
            else:
                return answers[metric2.index(max2)]
    elif metric1.count(max1) == 3:
        return answers[metric2.index(max2)]
    else:
        return answers[metric2.index(max2)]



startTime = datetime.now()
vision_client = vision.ImageAnnotatorClient()
file_name = ImageGrab.grab(bbox=(1650, 380, 2450, 1200))
file_name.show()
file_name.save('screenshot.png')
file_name1='screenshot.png'
with io.open(file_name1,'rb') as image_file:
    content = image_file.read()
    image = types.Image(content=content)

response = vision_client.document_text_detection(image=image)
labels = response.full_text_annotation

# print type(labels.text)
ocr_output=str(labels.text)
ocr_output=ocr_output.replace('-','?')
ocr_output=ocr_output.replace('Q?','')
ocr_output=ocr_output.replace('S 32.5K','')
ocr_output=ocr_output.replace('TIME UP','')
print ocr_output
question, answers = retrieve_q_and_a(ocr_output)
question=question.replace('ELIMINATED', '')
ans = []
for i in range(len(answers)):
    ans.append(str(answers[i]))
res1 = approach2(question, ans)
res2 = approach3(question, ans)
print(res1)
print(res2)
print predict(res1, res2, ans)
notify(question, predict(res1, res2, answers))
print(datetime.now() - startTime)

# print ocr_output
