# AWD Final — eLearning Platform (Django, DRF, Channels)

A modular eLearning platform with role-based accounts (student/teacher), course management (create, enroll, block/remove, materials, feedback), real‑time course chat via WebSockets, user status updates, and a REST API for user data. The system follows Django’s MVT pattern and is split into focused apps (**accounts**, **courses**, **chat**) to keep the codebase maintainable and extensible.

---

## Live Demo

- **App (Render):** `https://awdfinal.onrender.com/`  
  > Free tiers may sleep after a period of inactivity; the first request can take a little longer.

---

## Features

- **Accounts & Profiles**  
  Custom user model (extends `AbstractUser`) with `role` (student / teacher), `real_name`, and `photo`. Login, logout, registration, public profiles, and personal home pages with **status updates**.

- **Courses**  
  Teacher‑owned courses; students can **enroll** and leave **feedback**; teachers can upload **materials** and **block/remove** students. Notifications are created (e.g., on enrollment/material upload) via signals.

- **Real‑Time Chat**  
  Course‑scoped chat rooms using **Django Channels** + **Daphne**, with access control limited to the **teacher** and **enrolled students**. Messages persist in `ChatMessage`.

- **REST API (Users)**  
  Django REST Framework (`ModelViewSet` + serializer) exposes user data (list/retrieve/update/delete) with standard JSON responses.

- **Testing**  
  Unit tests across apps, including Channels tests for WebSocket behavior.

---

## Tech Stack

- **Backend:** Django (MVT), Django REST Framework  
- **Realtime:** Django Channels + Daphne, Channels Redis  
- **Database:** SQLite (local); swap to PostgreSQL for production  
- **Frontend:** Django Templates (HTML/CSS)  
- **Infra:** Redis (local at `127.0.0.1:6379`; managed store on Render)  
- **Python:** 3.13 (project is compatible with 3.10+)  
- **Packaging:** `requirements.txt` includes `Django`, `channels`, `channels_redis`, `daphne`, `djangorestframework`, `redis`, `whitenoise`, etc.

---

## Architecture

- **apps/accounts** — Auth, registration, login/logout, profiles, **StatusUpdate**, notifications; DRF viewset/serializer for `CustomUser`.
- **apps/courses** — Course CRUD, enroll/block/remove students, **Material** uploads, **Feedback**, notifications via signals.
- **apps/chat** — Channels consumer per course (`CourseChatConsumer`), persistence via **ChatMessage**, access checks for teacher / enrolled students.
- **project/** — Root settings, ASGI setup for Channels, URLs (including DRF router).

The data model is normalized with clear relationships and avoids duplication.

---

## Data Model (high level)

- **CustomUser**: extends `AbstractUser`; fields include `role`, `real_name`, `photo`. Relations to `StatusUpdate`, `Course` (as teacher), enrolled/blocked courses, `ChatMessage`, `Feedback`, `Notification`.
- **Course**: `title`, `description`, `teacher`; M2M `enrolled_students`, M2M `blocked_students`; related `Material`, `Feedback`, `ChatMessage`.
- **StatusUpdate**: short user posts with timestamps (shown on home & public profile).
- **Material**: uploaded file per course with timestamp and owner.
- **Feedback**: comment + student + course + timestamp.
- **Notification**: message + recipient + timestamps + read flag (often created via signals).
- **ChatMessage**: course + sender + message + timestamp.

---

## REST API (Users)

Implemented via DRF:
- `CustomUserSerializer`  
- `CustomUserViewSet` (list / retrieve / update / delete)

Routes are registered using a DRF `DefaultRouter` in the project URLs (e.g., `/api/users/`).

---

## WebSocket Chat

- **Per‑course room**: the consumer joins a group derived from the course ID/slug.
- **Auth & ACL**: only the **teacher** and **enrolled students** can connect and post.
- **Persistence**: messages are saved to `ChatMessage` and broadcast to the group.

---

## Local Development

1. **Clone & enter**  
   ```bash
   git clone <this-repo-url>
   cd awdfinal
   ```

2. **Python & virtualenv**  
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Environment**  
   Create a `.env` (or configure environment) with at least:
   ```
   DEBUG=True
   SECRET_KEY=change-me
   ALLOWED_HOSTS=127.0.0.1,localhost
   REDIS_URL=redis://127.0.0.1:6379/0
   ```
   For deployment, set `DEBUG=False` and a strong `SECRET_KEY`.

4. **Database**  
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Static files**  
   ```bash
   python manage.py collectstatic --noinput
   ```

6. **Run Redis locally**  
   Make sure Redis is running on `127.0.0.1:6379`.
   - macOS (Homebrew): `brew install redis && brew services start redis`
   - Linux: use your distro packages (`sudo apt install redis-server`), then `sudo service redis-server start`

7. **Run the server (ASGI)**  
   ```bash
   # Development:
   python manage.py runserver  # http://127.0.0.1:8000/

   # Or with Daphne (Channels):
   daphne -b 0.0.0.0 -p 8000 project.asgi:application
   ```

8. **Run tests**  
   ```bash
   python manage.py test
   ```

---

## Deployment Notes (Render)

- **Web service**: ASGI entrypoint `project.asgi:application` (via **Daphne**).  
- **Environment**: configure `SECRET_KEY`, `ALLOWED_HOSTS`, `REDIS_URL`, and database variables.  
- **Static**: serve with **Whitenoise** (already included) or via CDN.  
- **Redis**: use Render’s managed Redis or another provider.  
- **Cold starts**: free tiers may sleep and take time to wake up.

---

## Demo Accounts (example)

> Change or remove these in production.

- **Django admin**: `admin` / `admin`  
- **Teacher (local)**: `teacher` / `teachtest123`  
- **Student (local)**: `student` / `stutest123`  
- **Hosted teacher (web)**: `testweb` / `teacher12345`

---

## Project Structure (example)

```
awdfinal/
  apps/
    accounts/
    courses/
    chat/
  project/
    settings.py
    urls.py
    asgi.py
  templates/
  static/
  manage.py
  requirements.txt
```

---

## License

This project is for academic/demo purposes. If you plan to publish or reuse it, add an explicit license (e.g., MIT) and remove demo credentials.

---

## Acknowledgements

Built with Django, DRF, Channels, and Redis.
