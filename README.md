<br />

<h3 align="center">SummonerStats</h3>

<p align="center">
  Sample description
  <br />
  <br />
  <a href="https://github.com/othneildrew/Best-README-Template">View Demo</a>
  ·
  <a href="https://github.com/FuzzyGrim/SummonerStats/issues">Report Bug</a>
  ·
  <a href="https://github.com/FuzzyGrim/SummonerStats/issues">Request Feature</a>
</p>


<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)

SummonerStats is a site that provides League of Legends summoner's stats.

### Built With

* [Django](https://djangoproject.com), a high-level Python Web framework.
* [Bootstrap](https://getbootstrap.com), a free and responsive framework for faster and easier web development.


<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple example steps.

### Prerequisites

* Python 3

### Installation

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


## Deployment

It is possible to deploy to Heroku or to your own server.

### Heroku

```bash
$ heroku create
$ heroku addons:add heroku-postgresql:hobby-dev
$ heroku pg:promote DATABASE_URL
$ heroku config:set ENVIRONMENT=PRODUCTION
$ heroku config:set DJANGO_SECRET_KEY=`./manage.py generate_secret_key`
```

<!-- CONTRIBUTING -->
## Contributing

Do not hesitate to open an issue or pull request. Any contributions you make are **greatly appreciated**. To open a pull request:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


<!-- LICENSE -->
## License

Distributed under the GPLv3 License. See `LICENSE` for more information.