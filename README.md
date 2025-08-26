# flowdesk

## Short Description
**Flowdesk** is a web application for organizing team collaboration, managing workspaces, boards, lists, tasks, and tags. The system allows you to create workspaces, invite members, assign roles, manage boards with tasks, comment, and track progress.

## Features
- Workspace management (create, update, delete, invite members)
- Flexible role system (owner, admin, member, guest)
- Lists and tasks with drag-and-drop support
- Task comments
- Task dependency graph
- Account activation, password change, user profile

## Installation & Launch
1. **Clone the repository:**
	```sh
	git clone https://github.com/yagginov/flowdesk.git
	cd flowdesk
	```
2. **Create and activate a virtual environment:**
	```sh
	python -m venv venv
	.\venv\Scripts\activate
	```
3. **Install dependencies:**
	```sh
	pip install -r requirements.txt
	```
4. **Apply migrations:**
	```sh
	python manage.py migrate
	```
5. **Create a superuser (optional):**
	```sh
	python manage.py createsuperuser
	```
6. **Run the server:**
	```sh
	python manage.py runserver
	```
7. **Open in browser:**
	http://127.0.0.1:8000/

