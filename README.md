# Burst — Editorial News Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://hub.docker.com/)
[![Railway](https://img.shields.io/badge/Railway-Deploy-0B0D0E?logo=railway&logoColor=white)](https://railway.app/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A full-featured Django news platform for readers, journalists, editors, and publishers. Features role-based workflows, subscriptions, newsletters with cover images and sharing, OAuth (Google/Apple), REST API, RSS feeds, SEO sitemaps, and a modern editorial UI.

---

## ✨ Features

### User Roles & Workflows

| Role | Capabilities |
|------|--------------|
| **Reader** | Browse articles & newsletters, subscribe to publishers/journalists, search, RSS feed |
| **Journalist** | Create and edit articles, create newsletters with cover images, share content |
| **Editor** | Review, approve, and manage articles for their publisher |
| **Publisher** | Own publishing house, manage team (editors/journalists), view analytics |

### Core Functionality

- **Articles** — Draft → pending → approval → published workflow; hero images; categories
- **Newsletters** — Cover images, sharing (Twitter, LinkedIn, WhatsApp, copy link), public detail pages
- **Subscriptions** — Readers follow publishers and journalists; email notifications on approvals
- **Search** — Full-text search with category/publisher filters; `/` keyboard shortcut to focus
- **RSS Feed** — `/feed/` with 50 most recent published articles
- **Sitemap** — `/sitemap.xml` for SEO (static pages + published articles)

### Technical

- **Auth** — Sign in with Google & Apple (django-allauth), password reset, custom User model
- **REST API** — Token auth, articles/newsletters/subscriptions endpoints
- **Media** — Hero/cover image validation (JPEG, PNG, GIF, WebP; max 5 MB)
- **SEO** — Open Graph, Twitter Cards, sitemap, RSS discovery in HTML head
- **UI** — Responsive, accessible, Burst teal theme; styled 404/500 error pages

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Django 5.2, Python 3.11+ |
| **API** | Django REST Framework |
| **Auth** | django-allauth (Google, Apple) |
| **Database** | SQLite (dev) / MySQL·MariaDB (production) |
| **Images** | Pillow |
| **Config** | python-decouple (.env) |

---

## 📸 Screenshots

_Add screenshots of the home page, article detail, newsletter creation, and share buttons._

---

## 🚀 Quick Start

### Option A: Docker (recommended)

**Prerequisites:** Docker and Docker Compose

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/burst-news.git
cd burst-news

# Environment
cp .env.example .env
# Edit .env if needed (SQLite works by default)

# Build and run
docker compose up --build
```

Open **http://localhost:8000**. Migrations and user groups run automatically.

**Optional sample data:**
```bash
docker compose exec web python manage.py create_sample_data
```

### Option B: Local setup

**Prerequisites:** Python 3.11+, pip

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/burst-news.git
cd burst-news

# Virtual environment
python3 -m venv venv
source venv/bin/activate   # Windows: venv\\Scripts\\activate

# Dependencies
pip install -r requirements.txt

# Environment
cp .env.example .env
# Edit .env if using MySQL; SQLite works out of the box

# Database
python manage.py migrate

# Sample data & permissions
python manage.py setup_groups
python manage.py create_sample_data

# Run
python manage.py runserver
```

Open **http://127.0.0.1:8000**

### Sample Accounts (password: `testpass123`)

- `reader1` — Reader  
- `Aphiwe_tech` — Journalist  
- `editor_tech` — Editor  
- `publisher_tech` — Publisher  

---

## ⚙️ Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret | dev key (change in production) |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |
| `DB_ENGINE` | `sqlite` or `mysql` | `sqlite` |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD` | MySQL credentials | — |
| `EMAIL_HOST`, `EMAIL_PORT`, etc. | SMTP (production) | Console backend in dev |
| `TWITTER_BEARER_TOKEN` | Twitter API (optional) | — |
| `SITE_URL` | Base URL for links | `http://127.0.0.1:8000` |
| `ACCOUNT_DEFAULT_HTTP_PROTOCOL` | OAuth protocol | `http` (use `https` in prod) |

Never commit `.env`; use `.env.example` as a template.

---

## MariaDB Migration

The project supports MariaDB (and MySQL) for production. To migrate from SQLite to MariaDB:

1. **Install MariaDB** (e.g. `brew install mariadb` on macOS).

2. **Create the database:**
   ```bash
   mysql -u root -p
   CREATE DATABASE news_app_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   EXIT;
   ```

3. **Update `.env`:**
   ```
   DB_ENGINE=mysql
   DB_NAME=news_app_db
   DB_USER=root
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=3306
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   python manage.py setup_groups
   python manage.py create_sample_data
   ```

PyMySQL is used as the MySQL driver (see `requirements.txt`). The same migrations apply to both SQLite and MariaDB.

---

## 🐳 Docker

### Run from Docker Hub (no build required)

```bash
# Create a directory and .env file
mkdir burst-news && cd burst-news
curl -o .env https://raw.githubusercontent.com/YOUR_USERNAME/burst-news/main/.env.example

# Run with pre-built image (replace YOUR_DOCKERHUB_USERNAME with your Docker Hub username)
docker run -d -p 8000:8000 \
  --entrypoint sh \
  -e SECRET_KEY=your-secret-key-change-me \
  -e DEBUG=True \
  -e ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0 \
  -v burst-db:/app/data \
  --name burst-web \
  YOUR_DOCKERHUB_USERNAME/burst-news:latest \
  -c "/app/docker-entrypoint.sh python manage.py runserver 0.0.0.0:8000"
```

Open **http://localhost:8000**

### Run with Docker Compose (clone & build)

```bash
git clone https://github.com/YOUR_USERNAME/burst-news.git
cd burst-news
cp .env.example .env
docker compose up --build
```

- **Live reload** — Project is mounted at `/app`, so code changes apply instantly.
- **Database** — Named volume `db_data` persists SQLite data.
- **Media** — Stored in `./media` (inside the project mount).

### Docker Commands

| Command | Description |
|---------|-------------|
| `docker compose up` | Start the app |
| `docker compose down` | Stop (keeps data) |
| `docker compose down -v` | Stop and remove volumes |
| `docker compose exec web python manage.py createsuperuser` | Create admin user |
| `docker compose exec web python manage.py create_sample_data` | Load sample data |

### Publish to Docker Hub

1. **Log in:**
   ```bash
   docker login
   ```

2. **Build and tag** (replace `YOUR_DOCKERHUB_USERNAME` with your Docker Hub username):
   ```bash
   docker build -t YOUR_DOCKERHUB_USERNAME/burst-news:latest .
   ```

3. **Push:**
   ```bash
   docker push YOUR_DOCKERHUB_USERNAME/burst-news:latest
   ```

4. **Optional:** Create a `docker-compose.pull.yml` for running from the published image:
   ```bash
   docker compose -f docker-compose.pull.yml up
   ```

---

## 🚂 Deploy to Railway

1. **Push your code to GitHub** (if not already).

2. **Go to [railway.app](https://railway.app/)** and sign in with GitHub.

3. **New Project** → **Deploy from GitHub repo** → select `burst-news`.

4. **Add a database** (optional but recommended):
   - Click **+ New** → **Database** → **PostgreSQL**
   - Railway will set `DATABASE_URL` automatically

5. **Configure environment variables** (Project → Variables):
   | Variable | Value |
   |----------|-------|
   | `SECRET_KEY` | A random string (e.g. `python -c "import secrets; print(secrets.token_hex(32))"`) |
   | `DEBUG` | `False` |
   | `ALLOWED_HOSTS` | `.railway.app,.up.railway.app` |
   | `SITE_URL` | Your Railway URL (e.g. `https://your-app.up.railway.app`) |
   | `ACCOUNT_DEFAULT_HTTP_PROTOCOL` | `https` |

6. **Deploy** — Railway builds and deploys automatically. Get your URL from **Settings** → **Networking** → **Generate Domain**.

7. **Create admin user** (Railway dashboard → your service → **Settings** → **Custom start command** is already set, or run one-off):
   ```bash
   railway run python manage.py createsuperuser
   ```

---

## 📁 Project Structure

```
burst-news/
├── news/                    # Main application
│   ├── models.py            # User, Article, Newsletter, Publisher, Subscription
│   ├── views.py             # Web views
│   ├── api_views.py         # REST API
│   ├── serializers.py       # DRF serializers
│   ├── forms.py             # Forms (with image validation)
│   ├── feeds.py             # RSS feed
│   ├── sitemaps.py          # SEO sitemap
│   ├── signals.py           # Notifications
│   ├── adapters.py          # django-allauth adapter
│   ├── management/commands/ # setup_groups, create_sample_data
│   ├── templates/
│   └── static/
├── news_app/
│   ├── settings.py
│   └── urls.py
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── docker-compose.pull.yml    # Run from Docker Hub image
├── docker-entrypoint.sh
├── Procfile                   # Railway / Heroku
├── railway.json               # Railway config
└── .env.example
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/articles/` | List articles (filtered by role) |
| `POST` | `/api/articles/` | Create article (journalists) |
| `GET` | `/api/articles/{id}/` | Article detail |
| `PUT/PATCH` | `/api/articles/{id}/` | Update article |
| `DELETE` | `/api/articles/{id}/` | Delete article |
| `POST` | `/api/articles/{id}/approve/` | Approve article (editors) |
| `GET` | `/api/newsletters/` | List newsletters |
| `POST` | `/api/newsletters/` | Create newsletter |
| `GET` | `/api/publishers/` | List publishers |
| `GET` | `/api/categories/` | List categories |
| `GET/POST` | `/api/subscriptions/` | Manage subscriptions |

Authentication: Token (`Authorization: Token <token>`).

---

## 🌐 Key Routes

| Route | Description |
|-------|-------------|
| `/` | Home (articles + newsletters) |
| `/articles/` | Article list |
| `/articles/<id>/` | Article detail + share |
| `/newsletters/` | Newsletter list |
| `/newsletters/<id>/` | Newsletter detail + share |
| `/newsletters/create/` | Create newsletter |
| `/search/` | Search articles |
| `/feed/` | RSS feed |
| `/sitemap.xml` | SEO sitemap |
| `/subscriptions/` | Manage subscriptions |
| `/dashboard/publisher/` | Publisher dashboard |

---

## 🧪 Testing

```bash
python manage.py test
```

Covers models, views, API, auth, and notifications.

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**[Your Name]**  
- GitHub: [@yourusername](https://github.com/yourusername)  
- LinkedIn: [Your Profile](https://linkedin.com/in/yourprofile)
