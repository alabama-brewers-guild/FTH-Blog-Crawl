from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib import parse
from urllib.error import HTTPError
import xml.etree.ElementTree as ET

authors_set = []

def ParseMonth(url, data):
    prev_link = url
    
    while prev_link is not None:
        try:
            page = urlopen(prev_link)
        except:
            print('Could not open ' + prev_link)
            break
        soup = BeautifulSoup(page, 'lxml')
        posts = soup.find_all('div', 'hentry')

        for post in posts:
            permalink = post.find('h2', class_ = 'entry-title').a['href']
            
            title = post.find('h2', class_ = 'entry-title').a.text
            author = post.find('span', class_ = 'author').a.text
            pub_date = post.find('abbr', class_ = 'published').text
            post_content = str(post.find('div', class_ = 'entry-content'))
            try:
                post_page = urlopen(permalink)
                post_soup = BeautifulSoup(post_page, 'lxml')
                if post_soup.find(id='playback') is not None:
                    post_page = urlopen(str(post_soup.find(id='playback')['src']))
                    post_soup = BeautifulSoup(post_page, 'lxml')
                    print("Going into iframe of " + title + " from " + pub_date)
                post_content = str(post_soup.find('div', class_ = 'entry-content'))
                print("! Got full post of " + title + " from " + pub_date)
            except Exception as e:
                print("X Failed to open full post of " + title + " from " + pub_date + "Error: " + str(e))

            if author not in authors_set:
                authors_set.append(author)

            item = ET.SubElement(data, 'item')

            item.set('title', title)
            if author == 'Dan Roberts':
                item.set('author', 'droberts')
            elif author == 'Gabe Harris':
                item.set('author', 'gabeharris')
            elif author == 'Nick Hudson':
                item.set('author', 'nickhudson')
            else:
                item.set('author', author)
            item.set('pub_date', pub_date)
            item.text = post_content

        prev_div = soup.find('div', class_ = 'nav-previous')
        if prev_div == None or prev_div.a == None:
            print("No prev link at " + prev_link)
            break
        prev_link = prev_div.a['href']

start_url = 'http://web.archive.org/web/20170704135959/http://www.freethehops.org/blog/'

page = urlopen(start_url)
soup = BeautifulSoup(page, 'lxml')
archive_widget_li = soup.find(id='archives')
archive_links = [start_url]
for li in archive_widget_li.ul.find_all('li'):
    archive_links.append(li.a.get('href'))

data = ET.Element('posts')

for link in archive_links:
    ParseMonth(link, data)

mydata = ET.tostring(data)
myfile = open('items.xml', 'wb')
myfile.write(mydata)
myfile.close()

print(authors_set)

    