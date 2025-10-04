# Spy Cat Agency
 
The system manages **spy cats**, their **missions**, and assigned **targets**, including business logic for validation and mission control.

---

## 🚀 Features

- CRUD for **Spy Cats**
- CRUD for **Missions** and **Targets**
- Assign cats to missions (one active mission per cat)
- Auto-complete mission when all targets are done
- Prevent editing notes when target/mission is complete
- Breed validation using [TheCatAPI](https://thecatapi.com/)

---

## ⚙️ Tech Stack

- **Python 3.13+**
- **Django 5**
- **Django REST Framework**
- **SQLite** (default)
- **Pytest** for testing

---

## 🧠 Setup & Run

Clone the repository and install dependencies:
```bash
git clone https://github.com/<your_username>/spy_cat_agency.git
cd spy_cat_agency
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Run migrations and start the server:
```bash
python manage.py migrate
python manage.py runserver
```

Visit: 
- API root: http://127.0.0.1:8000/api/
- Admin panel: http://127.0.0.1:8000/admin/

---

## API Overview: 

Endpoints:
	•	POST /api/cats/ — create a new spy cat
	•	GET /api/cats/ — list all cats
	•	PATCH /api/cats/{id}/ — update a cat’s salary
	•	DELETE /api/cats/{id}/ — remove a cat
	•	POST /api/missions/ — create a new mission (with 1–3 targets)
	•	POST /api/missions/{id}/assign-cat/ — assign a cat to a mission
	•	PATCH /api/targets/{id}/ — update notes or mark a target as completed
	•	GET /api/missions/ — list all missions

### Breed validation:
Cat breeds are validated via TheCatApi. 
API URL: https://api.thecatapi.com/v1/breeds

### Quick tests
```bash
pytest -v
```

### Postman Collection, how to use

To simplify testing, the repository includes a ready-to-import Postman collection:
postman_collection.json (located in the project root).

How to use:
- open Postman
- click import -> File, then select file postman_collection.json
- the collection will appear in your workspace
- expand the collection and click Send on any request to test the endpoints. 