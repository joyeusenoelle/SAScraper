# SAScraper
A thread scraper for the Something Awful forums. **It requires Python 3.6+ and the requests module.**

Make sure you run `pip3 install requests`.

Before you run the scraper, you need to give it your forums username and password in `config.ini`. Don't worry, nobody can see this but you and Something Awful.

It's simple to run:

`python3 main.py %threadid%`

where `%threadid%` is from the URL of the thread you want to scrape. For example, to scrape the D&D Politoons thread, use:

`python3 main.py 3908778`

Each thread will go in its own folder under the `/archive` directory. The scraper will keep track of the last page it scraped and only update from there in the future if you run it again. As a convenience, it re-fetches the last page each time you run it, to catch last-minute edits.

If you include the `--images` flag:

`python3 main.py 3908778`

then the script will grab each image it can from the page and store it locally, so you don't have to worry about remote sites going down. **This may require a lot of bandwidth and disk space! Tread carefully with this option.**
