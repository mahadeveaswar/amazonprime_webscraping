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
from process_func import *

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(options=options, executable_path=r'chromedriver.exe')

# Enter user credentials for Amazon Prime account
mail = 'ENTER YOUR AMAZON USER EMAIL'
passw = 'ENTER YOUR PASSWORD'

# Login into Amazon prime account
login_prime(driver,mail,passw)

# Wait for Authentication if requested
wait_auth(driver)

# Cliking TV Shows
driver.get(r'https://www.primevideo.com/storefront/tv/ref=atv_nb_sf_tv')

# Top TV Shows
driver.get(r'https://www.primevideo.com/search/ref=atv_tv_hom_c_laptvn_7_smr?queryToken=eyJ0eXBlIjoicXVlcnkiLCJuYXYiOnRydWUsInBpIjoiZGVmYXVsdCIsInNlYyI6ImNlbnRlciIsInN0eXBlIjoic2VhcmNoIiwicXJ5IjoicF9uX2VudGl0eV90eXBlPVRWIFNob3cmaW5kZXg9ZXUtYW1hem9uLXZpZGVvLW90aGVyJmFkdWx0LXByb2R1Y3Q9MCZicT0oYW5kIHNvcnQ6J2ZlYXR1cmVkLXJhbmsnIChub3QgYXZfcHJpbWFyeV9nZW5yZTonY2hpbGRyZW4nKSkmYXZfYnlfdHlwZV9pbl90ZXJyaXRvcnk9SU46c3ZvZDpwcmltZSZzZWFyY2gtYWxpYXM9aW5zdGFudC12aWRlbyZxcy1hdl9yZXF1ZXN0X3R5cGU9NCZxcy1pcy1wcmltZS1jdXN0b21lcj0yIiwicnQiOiJsQVB0Vm5zbXIiLCJ0eHQiOiJUb3AgVFYiLCJvZmZzZXQiOjAsIm5wc2kiOjAsIm9yZXEiOiIzNzQ0NTc2NS1mMDY4LTQ3MzctYjlkZi01NzNlOTI0NmRmOWQ6MTYxMDY0MTI3NDAwMCIsInN0cmlkIjoiMToxSUFZRzBCVVQxRVZPIyNNWlFXR1pMVU1WU0VHWUxTTjUyWEdaTE0iLCJvcmVxayI6ImpzRGowUWwwenJXQllEVHlIcThQbkRxbUc3ZnJKaTM1cnh6RXpERXppckk9Iiwib3JlcWt2IjoxfQ%3D%3D&pageId=default&queryPageType=browse&ie=UTF8')
sleep(3)

# Scrolling till end of page to load all shows in the webpage
page_scroll_to_bottom(driver)

# Obtaining all the top tv show links & titles on the page
titles,tv_links = tvshow_title_links(driver)
bckup_df = pd.DataFrame({'title':titles,'show_links':tv_links})

tv_cols = ['title', 'seasons', 'start_year','imdb_rating','viewer_maturity','genre',
                                   'content_advisory','network','episodes','avg_episode_runtime']
tv_show_df = pd.DataFrame(columns=tv_cols)

try:
    for i in range(len(tv_links)):
        # Open a Tab
        print(tv_links[i])
        driver.execute_script('''window.open("'''+tv_links[i]+'''","_blank");''')
        sleep(1.5)
        driver.switch_to.window(driver.window_handles[1])
        html = driver.page_source
        Soup = soup(html,'lxml')
        # Show Title
        title = titles[i].upper()
        print(title)
        seasons = get_seasons(driver,Soup)
        # Genre
        genre = get_genre(driver,Soup)
        # Network
        network = []
        network = get_show_network(network,driver)
        episodes = 0
        mins = 0
        rating = 0
        viewer_maturity = "NR"
        content_advisory = []
        year = []
        if seasons==1:
            try:
                expansion = driver.find_element_by_xpath('//a[@data-automation-id="ep-expander"]').get_attribute('href')
                driver.get(expansion)
            except NoSuchElementException as error:
                pass
            # Get the IMBD rating if it exists else set as -1
            try:
                rating = float(driver.find_element_by_xpath('//span[@data-automation-id="imdb-rating-badge"]').text)
            except NoSuchElementException as error:
                pass
            # No. of Episodes
            html = driver.page_source
            Soup = soup(html, 'lxml')
            episodes, mins = get_total_episode_minutes(Soup, mins, episodes)
            viewer_maturity = driver.find_element_by_xpath('//span[@data-automation-id="rating-badge"]').get_attribute("title")[:-1]
            year = [int(driver.find_element_by_xpath('//span[@data-automation-id="release-year-badge"]').text)]
            # Content Advisory if exists
            content_advisory = get_content_advisory(Soup,content_advisory)
        else:
            seas_links = get_season_links(driver)
            for lnk in seas_links:
                driver.get(lnk)
                try:
                    expansion = driver.find_element_by_xpath('//a[@data-automation-id="ep-expander"]').get_attribute('href')
                    driver.get(expansion)
                except NoSuchElementException as error:
                    pass
                html = driver.page_source
                Soup = soup(html, 'lxml')
                # No. of Episodes
                episodes, mins = get_total_episode_minutes(Soup, mins, episodes)
                # Genre
                if len(genre)==0:
                    genre = get_genre(driver, Soup)
                # Network
                if len(network)==0:
                    network = get_show_network(network, driver)
                # Get the IMBD rating if it exists else set as -1
                try:
                    if rating == 0:
                        rating = float(driver.find_element_by_xpath('//span[@data-automation-id="imdb-rating-badge"]').text)
                except NoSuchElementException as error:
                    pass
                if viewer_maturity=='NR':
                    viewer_maturity = driver.find_element_by_xpath('//span[@data-automation-id="rating-badge"]').get_attribute("title")[:-1]
                else:
                    pass
                if len(year)==0:
                    year.append(int(driver.find_element_by_xpath('//span[@data-automation-id="release-year-badge"]').text))
                # Content Advisory if exists
                content_advisory = get_content_advisory(Soup,content_advisory)
        if len(year)==0:
            year = 0
        else:
            year = min(year)
        if rating == 0:
            rating=-1
        if episodes==0:
            avg_mins = 0
        else:
            avg_mins = mins/episodes
        if len(network)==0:
            network = 'NA'
        else:
            network = network[0].upper()
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        tv_df = pd.DataFrame([[title, seasons, year, rating, viewer_maturity, genre, content_advisory, network, episodes,
                            avg_mins]], columns=tv_cols)
        print(tv_df)
        tv_show_df = pd.concat([tv_show_df, tv_df])
        tv_out_df = tv_show_df.reset_index(drop=True)
        tv_out_df.to_csv('shows_data.csv',index=False)
        bckup_df.to_csv('titles_links.csv', index=False)
except Exception as error:
    print(error)
    bckup_df.to_csv('titles_links.csv',index=False)
    tv_out_df = tv_show_df.reset_index(drop=True)
    tv_out_df.to_csv('shows_data.csv',index=False)
    for handle in driver.window_handles[1:]:
        driver.switch_to.window(handle)
        driver.close()
    driver.switch_to.window(driver.window_handles[0])
