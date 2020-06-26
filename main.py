import requests, time, re, os, configparser, sys, argparse
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

css_to_change = ["https://www.somethingawful.com/css/main.css?12",
                 "https://forums.somethingawful.com/css/bbcode.css?1456974408",
                 "https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.4/themes/redmond/jquery-ui.min.css",
                 "https://www.somethingawful.com/css/globalmenu.css",
                 "https://www.somethingawful.com/css/forums.css?1545838155"
                ]
css_to_change_to = ["main.css",
                    "bbcode.css",
                    "jquery-ui.min.css",
                    "globalmenu.css",
                    "forums.css"
                   ]

scripts_to_change = ["https://ajax.googleapis.com/ajax/libs/jquery/2.2.2/jquery.min.js",
                     "https://cdnjs.cloudflare.com/ajax/libs/jquery-migrate/1.4.0/jquery-migrate.min.js",
                     "https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.4/jquery-ui.min.js",
                     "https://forums.somethingawful.com/js/vb/forums.combined.js?1476414227",
                     "https://twemoji.maxcdn.com/2/twemoji.min.js",
                    ]
scripts_to_change_to = ["jquery.min.js",
                        "jquery-migrate.min.js",
                        "jquery-ui.min.js",
                        "forums-combined.js",
                        "twemoji.min.js"
                       ]


def main(args):
  print(f"Fetching from thread {args.thread}.")
  if not os.path.isdir("archive"):
    print("First-time setup...")
    os.mkdir("archive")
  if not os.path.isdir("archive/css"):
    print("Setting up CSS...")
    os.mkdir("archive/css")
    for f in range(len(css_to_change)):
      r = requests.get(css_to_change[f])
      with open(f"archive/css/{css_to_change_to[f]}", "w+") as file:
        file.write(r.text)
  if not os.path.isdir("archive/scripts"):
    print("Setting up scripts...")
    os.mkdir("archive/scripts")
    for f in range(len(scripts_to_change)):
      r = requests.get(scripts_to_change[f])
      with open(f"archive/scripts/{scripts_to_change_to[f]}", "w+") as file:
        file.write(r.text)
    
  if not os.path.isdir(f"archive/{args.thread}"):
    print(f"Creating directory for {args.thread}...")
    os.mkdir(f"archive/{args.thread}")
  if not os.path.isdir(f"archive/{args.thread}/images"):
    print(f"Creating directory for {args.thread}/images...")  
    os.mkdir(f"archive/{args.thread}/images")
  config = configparser.ConfigParser(interpolation=None)
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

  s = requests.Session()
  q = s.post("https://forums.somethingawful.com/account.php", data=info)

  if f"lastpage{args.thread}" in config["DEFAULT"] and config["DEFAULT"][f"lastpage{args.thread}"] != "":
    lastpage = int(config["DEFAULT"][f"lastpage{args.thread}"])
  else:
    lastpage = 1

  i = lastpage
  parse_ok = True
  while True:
    time.sleep(0.05)
    payload = {'threadid': args.thread, 'pagenumber': str(i)}
    r = s.get("https://forums.somethingawful.com/showthread.php", params=payload)
    if "Specified thread was not found in the live forums." in r.text:
      print("That thread does not exist or is not accessible to you.")
      parse_ok = False
      break
    if "The page number you requested" in r.text:
      i -= 1
      break
    print(f"Fetching page {i} in thread {args.thread}.")
    with open(f"archive/{args.thread}/page{i}.html", "w+", encoding="utf-8") as file:
      soup = BeautifulSoup(r.text, "html.parser")
      for tag in soup.find_all("link",{"href":True}):
        if tag["href"] in css_to_change:
          tag["href"] = "../css/" + css_to_change_to[css_to_change.index(tag["href"])]
      for tag in soup.find_all("script",{"src":True}):
        if tag["src"] in scripts_to_change:
          tag["src"] = "../scripts/" + scripts_to_change_to[scripts_to_change.index(tag["src"])]
      for tag in soup.find_all("a",{"title":True}):
        if tag["title"] == "Next page":
          tag["href"] = f"page{i+1}.html"
        if tag["title"] == "Previous page":
          tag["href"] = f"page{i-1}.html"
      if args.images:
        for tag in soup.find_all("img",{"src":True}):
          src = tag["src"]
          if src[:4] != "http":
            src = "https:" + src
          imgname = src.split("/")[-1]
          fullpath = f"archive/{args.thread}/images/{imgname}"
          if not os.path.isfile(fullpath):
            img = s.get(src, stream=True)
            if img.status_code == 200:
              try:
                theimage = Image.open(BytesIO(img.content))
                print(f"\tSaving {fullpath}.")
                theimage.save(fullpath)
                tag["src"] = f"images/{imgname}"
              except:
                print(f"\tImage {src} not available.")
            else:
              print(f"Image {src} not available.")
      file.write(soup.prettify())
    i += 1

  print("Finished fetching thread.")

  config["DEFAULT"][f"lastpage{args.thread}"] = str(i)
  with open("config.ini", "w") as file:
    config.write(file)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("thread", action="store", help="The threadid from the thread's URL")
  parser.add_argument("-i", "--images", action="store_true", help="Set this flag to download images as well as HTML.\nNOTE: This may be VERY bandwidth and disk intensive!")
  args = parser.parse_args()
  main(args)
