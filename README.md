Lux Climate - B2B Payment Management System
A Telegram Mini App designed to streamline payment tracking and management between sellers and buyers.
📋 Overview
Lux Climate is a comprehensive payment management solution that helps businesses track transactions, manage installment plans, and monitor customer debts efficiently through a Telegram interface.
✨ Features

Transaction Management: Track all seller-buyer transactions in real-time
Installment Tracking: Manage flexible payment schedules for customers
Debt Monitoring: Monitor outstanding balances and payment history
Automated Reminders: Send payment notifications to customers automatically
Reporting Dashboard: Generate detailed financial reports and analytics
User Authentication: Secure JWT-based authentication system

🛠️ Tech Stack

Backend: Python 3.x, Django, Django REST Framework
Database: PostgreSQL
Authentication: JWT (JSON Web Tokens)
Containerization: Docker, Docker Compose
Bot Framework: python-telegram-bot

📦 Installation
Prerequisites

Docker and Docker Compose
Python 3.13
PostgreSQL

Setup

Clone the repository

bashgit clone https://github.com/TulqinUrinov/Lux_Climate.git
cd Lux_Climate

Create environment file

bashcp "env file example" .env

Configure your environment variables in .env:

BOT_TOKEN=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=
POSTGRES_PORT=

Build and run with Docker

bashdocker-compose up --build

Run migrations

bashdocker-compose exec web python manage.py migrate

Create superuser

bashdocker-compose exec web python manage.py createsuperuser

📁 Project Structure
Lux_Climate/
├── config/          # Django settings and configuration
├── data/            # Data management and models
├── files/           # File uploads and storage
├── tg_bot/          # Telegram bot integration
├── manage.py        # Django management script
├── r.txt            # Requirements file
└── docker-compose.yml
