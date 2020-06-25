import requests, time, re, os, configparser, sys

def main(threadid):
  if threadid==None:
    threadid='3908778' # it's the D&D Politoons thread, this is for the author's convenience
  print(f"Fetching from thread {threadid}.")
  if not os.path.isdir("archive"):
    os.mkdir("archive")
  if not os.path.isdir(f"archive/{threadid}"):
    os.mkdir(f"archive/{threadid}")
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

  if f"lastpage{threadid}" in config["DEFAULT"] and config["DEFAULT"][f"lastpage{threadid}"] != "":
    lastpage = int(config["DEFAULT"][f"lastpage{threadid}"])
  else:
    lastpage = 1

  i = lastpage
  while True:
    time.sleep(0.1)
    payload = {'threadid': threadid, 'pagenumber': str(i)}
    r = s.get("https://forums.somethingawful.com/showthread.php", params=payload)
    if "The page number you requested" in r.text:
      i -= 1
      break
    print(f"Fetching page {i} in thread {threadid}.")
    with open(f"archive/{threadid}/page{i}.html", "w+", encoding="utf-8") as file:
      file.write(r.text)
    i += 1

  config["DEFAULT"][f"lastpage{threadid}"] = str(i)
  with open("config.ini", "w") as file:
    config.write(file)

if __name__ == "__main__":
  threadid=None
  if len(sys.argv) > 1:
    threadid = sys.argv[1]
  main(threadid)
