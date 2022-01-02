import logging
import re
import string
from typing import Optional
import bs4
import requests
import sys


def getpictureurl(dinoName) -> Optional[str]:
    res = requests.get(r'https://www.nhm.ac.uk/discover/dino-directory/' + dinoName)

    if res.status_code != 200:
        logging.error(f'The dinosaur {dinoName} is not in dino-directory.')
        return None

    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    poza = soup.select(
        '#main-content > div > div > div.row2cells13.section > div > div.large-9.medium-9.columns > div > div > div > div:nth-child(2) > div > img')
    return poza[0]['src']


def downloadpicture(dinoPictureUrl, dinoName, dinoFolder):
    dinoPictureFullPath = dinoFolder + dinoName + '.jpg'
    logging.info(f'downloadpicture dinoPictureUrl="{dinoPictureUrl}" into dinoPictureFullPath="{dinoPictureFullPath}"')
    res = requests.get(dinoPictureUrl)
    file = open(dinoPictureFullPath, 'wb')
    for chunk in res.iter_content(100000):
        file.write(chunk)
    file.close()


def get_dino_name(linkHref) -> Optional[str]:
    relinkdino = re.compile(r'/discover/dino-directory/([a-z]+).html')
    linkdino = relinkdino.findall(linkHref)
    if len(linkdino) < 1:
        return None
    logging.info(f'{linkdino} is the name of the dinosaur from {linkHref}')
    return linkdino[0]


def downloadpicture_by_letter(letter: str, dinoFolder):
    res = requests.get(r'https://www.nhm.ac.uk/discover/dino-directory/name/' + letter + '/gallery.html')
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    links = soup.findAll('a')
    for link in links:
        matchedDinoName = get_dino_name(link['href'])
        if matchedDinoName != None:
            dinoPictureUrl = getpictureurl(matchedDinoName)
            downloadpicture(dinoPictureUrl, matchedDinoName, dinoFolder)

"""
This program downloads dinosaur pictures from www.nhm.ac.uk
Example usage:
dino_picture_downloader.py diplodocus C:\\dinofolder\\
dino_picture_downloader.py a C:\\dinofolder\\
dino_picture_downloader.py all C:\\dinofolder\\
"""
logging.basicConfig(level=logging.INFO)
dinoFolder = sys.argv[2]
try:
    if len(sys.argv[1]) == 1:
        downloadpicture_by_letter(sys.argv[1], dinoFolder)
    elif sys.argv[1] == 'all':
        for letter in string.ascii_letters:
            downloadpicture_by_letter(letter, dinoFolder)
    else:
        dinoPictureUrl = getpictureurl(sys.argv[1])
        if dinoPictureUrl is not None:
            downloadpicture(dinoPictureUrl, sys.argv[1], dinoFolder)
except requests.exceptions.ConnectionError:
    logging.error("Connection Error")
