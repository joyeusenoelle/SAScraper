# SAScraper
A thread scraper for the Something Awful forums

Before you run the scraper, you need to give it your forums username and password in `config.ini`. Don't worry, nobody can see this but you and Something Awful.

It's simple to run:

`python3 main.py %threadid%`

where `%threadid%` is from the URL of the thread you want to scrape. For example, to scrape the D&D Politoons thread, use:

`python3 main.py 3908778`

Each thread will go in its own folder under the `/archive` directory. The scraper will keep track of the last page it scraped and only update from there in the future if you run it again.
