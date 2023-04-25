from selenium.webdriver.common.by import By
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import time
from discord import Webhook
import aiohttp
import asyncio
from discord_webhook import DiscordWebhook
import datetime
import traceback

webhook_url = "SECRET"

# async def foo(message):
#     async with aiohttp.ClientSession() as session:
#         webhook = Webhook.from_url(url=webhook_url)
#         await webhook.send(message, username='Room Alert')
opts = Options()
opts.add_argument("--headless")
# assert opts.headless  # Operating in headless mode
browser = Firefox(options=opts)

numBoxesExpected = 10
states = dict()
names = {
    1: "N/A",
    2: "N/A",
    3: "Bonham Carter House",
    4: "College Hall",
    5: "Connaught Hall",
    6: "Eleanor Rosa House",
    7: "Garden Halls",
    8: "Handel Mansions",
    9: "International Halls",
    10: "Nutford House"
}
newline_char = "\n"
def search():
    global numBoxesExpected
    global states

    paragraphs = browser.find_elements(By.CLASS_NAME, 'multiline')
    message = f"Searched {len(paragraphs)} at datetime {str(datetime.datetime.now()).split('.')[0]}\n"
    found = False
    responses = set()
    if len(paragraphs) != numBoxesExpected:
        found=True
        message += "REVIEW: Number of boxes has changed. Please review"
        numBoxesExpected = len(paragraphs)
    for i,para in enumerate(paragraphs):
        if not 'official correspondence' in para.text:
            responses.add(para.text)
        if "Academic Year" in para.text and states[i] == 0:
            states[i] = 1
            message += f"**HIT in house#{i+1}: {names[i+1]}**\n{para.text.split(newline_char)[-1]}]\n"
            found = True
        elif "Academic Year" not in para.text and states[i] == 1:
            states[i] = 0
            message += f'MISS of house#{i+1}: Rooms are gone in {names[i+1]}\n'
            found=True
    if found:
        webhook = DiscordWebhook(url=webhook_url, content=message)
        response = webhook.execute()
        print(response, f". Checked {len(paragraphs)}. Got: {responses}")
    else:
        print(f"Not found at {str(datetime.datetime.now()).split('.')[0]}. Checked {len(paragraphs)}. Got: {responses}")

def keepLooping():
    global states
    global numBoxesExpected
    browser.get('https://uol.starrezhousing.com/StarRezPortalX/A84B2D0F/29/250/Available_Rooms-Select_your_location?UrlToken=C0620AE9&DateStart=11%20September%202022&DateEnd=17%20June%202023')
    for i in range(numBoxesExpected):
        states[i] = 0
    
    while True:
        boxes = browser.find_elements(By.CLASS_NAME, 'ui-front-side')

        for box in boxes:
            box.click()

        time.sleep(5)
        search()
        time.sleep(18)
        browser.refresh()
        time.sleep(3)

try:
    keepLooping()
except Exception:
    webhook = DiscordWebhook(url=webhook_url, content="**FAILURE**: Reset required\n")
    response = webhook.execute()
    print("Final response: ", response)
    print(traceback.format_exc())