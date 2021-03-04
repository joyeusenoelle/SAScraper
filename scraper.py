import requests, time, re, os, configparser, sys
from bs4 import BeautifulSoup

config = configparser.ConfigParser()
if not os.path.isfile('config.ini'):
  print("config.ini is missing!")
  sys.exit(0)
config.read('config.ini')

if "username" not in config["DEFAULT"] or "password" not in config["DEFAULT"] or config["DEFAULT"]["username"] == "" or config["DEFAULT"]["password"] == "":
  print("username and password must be present in config.ini.")
  sys.exit(0)

info = { "username": config["DEFAULT"]["username"],
         "password": config["DEFAULT"]["password"],
         "action": "login"
        }

# files = [f for f in os.listdir('pages') if os.path.isfile("./pages/{}".format(f))]

if not os.path.isdir('pages'):
    os.mkdir('pages', 0o755)

s = requests.Session()
q = s.post("https://forums.somethingawful.com/account.php", data=info)
# print(q.text)

if "lastpage" in config["DEFAULT"] and config["DEFAULT"]["lastpage"] != "":
  lastpage = int(config["DEFAULT"]["lastpage"])
else:
  lastpage = 1

i = lastpage
while True:
  time.sleep(0.1)
  payload = {'threadid': '3908778', 'pagenumber': str(i)}
  r = s.get("https://forums.somethingawful.com/showthread.php", params=payload) #, cookies=jar)
  # with open("pages/rawpage{}.txt".format(i), "w+") as file:
  #   file.write(r.text)
  if "The page number you requested" in r.text:
    i -= 1
    break
  matcher = re.compile(r'[g]aybie[s]? [n]om\S{0,} (.+)$', flags=re.IGNORECASE|re.MULTILINE)
  # matcher = re.compile(r'[Gg]aybie[s]? [Nn]om')
  if re.search(matcher, r.text) != None:
    print("Page {} has a nomination.".format(i))
    soup = BeautifulSoup(r.text, 'html.parser')
    for tag in soup.find_all('tr'):
      keep = False
      latestimg = ""
      for child in tag.descendants:
        #if child.name == "img":
        #  lastimg = child['src']
        res = re.search(matcher, str(child))
        if res != None:
          # out = "{}: {}".format(res.group(1), lastimg)
          # print(out)
          # with open("nominations.txt", "a") as file:
          #  file.write(out + "\n")
          keep = True
      if keep == False:
        tag.decompose()
    with open("pages/page{}.html".format(i), "w") as file:
      file.write(str(soup))
  else:
    print("Page {} has no nominations.".format(i))
  i += 1

config["DEFAULT"]["lastpage"] = str(i)
with open("config.ini", "w") as file:
  config.write(file)
