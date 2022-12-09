<br />

<p align="center">
  <img src="./api/static/favicon/android-chrome-192x192.png" />
</p>


<h3 align="center">SummonerStats</h3>

<p align="center">
  <a href="https://github.com/FuzzyGrim/SummonerStats/issues">Report Bug</a>
  ·
  <a href="https://github.com/FuzzyGrim/SummonerStats/issues">Request Feature</a>
</p>


<!-- ABOUT THE PROJECT -->
## About The Project

![screenshot](./api/static/assets/screenshot.png)

SummonerStats is a site that provides League of Legends summoner's stats.

### Built With

* [Django](https://djangoproject.com), a high-level Python Web framework.
* [Bootstrap](https://getbootstrap.com), a free and responsive framework for faster and easier web development.
* [Sqlite3](https://www.sqlite.org/index.html), a small, fast, self-contained SQL database engine.
* [JQuery](https://jquery.com), a fast, small, and feature-rich JavaScript library.


<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple example steps.

### Installation

1. Install [Python 3](https://www.python.org/downloads/)
1. Get a free API Key at [Riot Developer Portal](https://developer.riotgames.com/)
2. Clone the repo
   ```sh
   git clone https://github.com/FuzzyGrim/SummonerStats.git
   ```
3. Install Python dependencies
   ```sh
   pip install -r requirements.txt
   ```
4. Create `.env` file and add your API Key
   ```env
   API = 'ENTER YOUR API';
   ```
5. Generate a Django secret key
    ```sh
    python -c "import secrets; print(secrets.token_urlsafe())"
    ```
6. Add the secret key to the `.env` file
    ```env
    SECRET = 'ENTER YOUR SECRET';
    ```
7. Apply migrations
    ```sh
    python manage.py migrate
    ```
8. Run server
   ```sh
   python manage.py runserver
   ```
9. Now that the server’s running, visit http://127.0.0.1:8000/ with your Web browser

<!-- LICENSE -->
## License

Distributed under the GPLv3 License. See `LICENSE` for more information.