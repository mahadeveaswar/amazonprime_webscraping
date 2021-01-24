from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as soup
from time import sleep
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd
import requests
import base64

'''Function Definitions'''

# Login to Prime Account
def login_prime(driver,mail,passw):
    page = requests.get('https://www.amazon.com/ap/signin?accountStatusPolicy=P1&clientContext=258-5306354-2707047&language=en_US&openid.assoc_handle=amzn_prime_video_desktop_us&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.primevideo.com%2Fauth%2Freturn%2Fref%3Dav_auth_ap%3F_encoding%3DUTF8%26location%3D%252Fref%253Ddv_auth_ret')
    driver.get(page.url)
    sleep(2)
    driver.find_element_by_id('ap_email').send_keys(mail)
    driver.find_element_by_id('ap_password').send_keys(passw, Keys.ENTER)
    sleep(2)


# Wait for authenticating incase an approval is requested
def wait_auth(driver):
    acc_links = ['https://www.primevideo.com/',
                 'https://www.primevideo.com/ref=av_auth_return_redir',
                 'https://www.primevideo.com/storefront/home/ref=atv_nb_sf_hm']
    if (driver.current_url not in acc_links):
        print('Waiting for Authentication')
        sleep(30)

# Scroll till the bottom of the page to load all the shows in the page
def page_scroll_to_bottom(driver):
    lenOfPage = driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match = False
    while (match == False):
        lastCount = lenOfPage
        sleep(2)
        lenOfPage = driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        sleep(10)
        if lastCount == lenOfPage:
            match = True
    sleep(5)

# All top shows & respective links
def tvshow_title_links(driver):
    tv_links = []
    elems = driver.find_elements_by_xpath("//a[@href]")
    for elem in elems:
        if str(elem.get_attribute("href")).__contains__('detail') & ~str(elem.get_attribute("href")).__contains__(
                'autoplay'):
            if (elem.get_attribute("href") not in tv_links):
                tv_links.append(elem.get_attribute("href"))
    ttls = driver.find_elements_by_xpath("//a[@class='av-beard-title-link']")
    titles = [i.text for i in ttls]
    return (titles,tv_links)

# Get the links of each season in a show
def get_season_links(driver):
    seas_links = []
    elems = driver.find_elements_by_xpath("//a[@href]")
    for j in elems:
        if str(j.get_attribute('href')).__contains__('season'):
            seas_links.append(j.get_attribute('href'))
    return seas_links

# No. of seasons for each show
def get_seasons(driver,Soup):
    if Soup.find('div', attrs={"class": "dv-node-dp-seasons _14YvcB _1qXS7N"}) != None:
        ss = Soup.find_all('span', attrs={"class": "_36qUej"})
        # No. of Seasons in the show
        seasons = len(set([s.get_text() for s in ss if str(s.get_text()).startswith('Season')]))
    else:
        seasons = len([Soup.find('span', attrs={"class": "_36qUej"}).get_text()])
    return seasons

# Get the genre of the show
def get_genre(driver,Soup):
    gnr = Soup.find_all('a', attrs={"class": "_1NNx6V"})
    genre = []
    for g in gnr:
        if str(g).__contains__('atv_dp_pd_gen'):
            genre.append(g.text)
    genre = [i.strip().upper() for i in genre]
    return genre

# Get the network that publishes the show
def get_show_network(network,driver):
    netw = driver.find_elements_by_xpath('//div[@id="btf-product-details"]/div[@class="_1ONDJH"]/dl')
    for k in netw:
        nm = k.get_attribute('textContent')
        if nm.__contains__('Network'):
            nwk = nm.replace('Network', '')
            network.append(nwk)
    return network

# Get details about total episodes & minutes of the episode
def get_total_episode_minutes(Soup,mins,episodes):
    epis = Soup.find_all('div', attrs={"class": "_3KIibF GoQyOY"})
    episodes += len(epis)
    # Minutes
    for m in epis:
        mm = m.find_all('div')[1].text
        try:
            if mm.__contains__('h'):
                hh = mm.split('h')[0]
                if mm.__contains__('min'):
                    mn = mm.split('h')[-1]
                    mn = float(mn[:-3])
                    mm = float(hh) * 60 + float(mn)
                else:
                    mm = float(hh) * 60
            else:
                mm = float(mm[: -3])
        except Exception as error:
            print(error)
            mm = -1
        if mm > 5:
            mins += mm
        else:
            episodes -= 1
    return (episodes,mins)

# Get details about the type of content in the show
def get_content_advisory(Soup,content_advisory):
    try:
        if len(content_advisory)==0:
            content_advisory = [i.get_text() for i in Soup.find_all('dl', attrs={"class": "_2czKtE"})[2]][1].split(',')
            content_advisory = [i.strip().lower() for i in content_advisory]
    except Exception as error:
        print("No Content Advisory")
    return content_advisory
