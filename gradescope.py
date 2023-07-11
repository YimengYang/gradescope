import conda 
import mechanize
import http.cookiejar
import html2text
from bs4 import BeautifulSoup
import os
# Browser
br = mechanize.Browser()

# Cookie Jar
cj = http.cookiejar.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

br.addheaders = [('User-agent', 'Chrome')]

# The site we will navigate into, handling it's session
br.open('https://gradescope.com/login')
base_url = "https://gradescope.com"
#br.open('https://github.com/login')
# View available forms

for f in br.forms():
    #print(f)

    # Select the second (index one) form (the first form is a search query box)
    br.select_form(nr=0)

    # User credentials
    br.form['session[email]'] = "aaparvat@ucsd.edu" #TODO: Fill in email
    br.form['session[password]'] = "Sunandanavya123$" #TODO: Fill in password

    # Login
    br.submit()

    # should click older courses here
    soup = BeautifulSoup(br.response().read(), 'html.parser')
    older_courses_button = soup.find('button', {'class': 'tiiBtn tiiBtn-primaryLink js-viewInactive'})

    if older_courses_button:
        # Submit the form associated with the button
        br.select_form(nr=0)  # Assuming it's the first form
        br.submit()
    #
    soup = BeautifulSoup(br.open('https://gradescope.com/account').read())
    
    courseBoxes = soup.find_all('a', {'class':'courseBox'})
    links = {}
    for c in courseBoxes:
        n = c.find("h3").text
        n = n.replace("/", " ")
        links[n] = c.get("href")
    
    for k,v in links.items():
        try:
            print("making dir {}".format(k))
        except:
            print("error with dir name")
        if not os.path.exists(k):
            os.mkdir(k)
        else:
            print("dir exists, skipping")
            continue
        course_soup = BeautifulSoup(br.open(base_url+ v).read())
        os.chdir(k)
        assignment_table = course_soup.find('table', {'class':'table'})
        assignment_links = {}
        for head in assignment_table.find_all("th"):
            a_res = head.find("a")
            if a_res:
                assignment_links[a_res.get("aria-label")] = a_res.get("href")

        print("found assignment links: {}".format(assignment_links))
        for name, l in assignment_links.items():
            assignment_soup = BeautifulSoup(br.open(base_url+l).read())
            a_res = assignment_soup.find_all("a", {"class": "actionBar--action"})
            download_link = base_url + l + ".pdf"
            for a in a_res:
                tmp = a.get("href")
                if tmp:
                    download_link = base_url + tmp
                    break
            print("{} download link: {}".format(name, download_link))
            orig_filename = download_link.split("/")[-1]
            extension = orig_filename.split(".")[-1]
            name = name.replace("/", " ") 
            br.retrieve(download_link,'{}.{}'.format(name, extension))[0]
        os.chdir("../")
