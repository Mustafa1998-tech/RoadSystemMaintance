# Road Maintenance Management System

A comprehensive web-based solution for managing road maintenance issues, built with Django and modern frontend technologies.

## 🚀 Features

### Core Functionality
- 🚧 **Issue Management**: Full CRUD operations for road maintenance issues
- 📍 **Interactive Map**: Leaflet.js integration for issue location mapping
- 📂 **File Attachments**: Upload and manage multiple attachments per issue
- 💬 **Comments**: Add comments to issues for better collaboration
- 🔍 **Search & Filter**: Advanced search and filtering capabilities
- 📊 **Dashboard**: Overview of key metrics and statistics

### User Experience
- 🌓 **Dark/Light Mode**: Automatic theme switching based on system preferences
- 📱 **Fully Responsive**: Optimized for all device sizes
- ⚡ **HTMX Integration**: For fast, dynamic page updates
- 🎨 **Modern UI**: Built with Tailwind CSS for a clean, professional look
- 🔔 **Real-time Updates**: Get instant notifications for issue updates

### Security & Access
- 🔒 **JWT Authentication**: Secure user authentication
- 👥 **Role-based Access Control**:
  - **Admin**: Full system access
  - **Technician**: Manage assigned issues
  - **Viewer**: Read-only access

## 🛠 Tech Stack

### Backend
- Python 3.9+
- Django 4.2+
- Django REST Framework
- SQLite (Development) / PostgreSQL (Production)
- Simple JWT for authentication

### Frontend
- HTML5, CSS3, JavaScript (ES6+)
- [Tailwind CSS](https://tailwindcss.com/) (via CDN)
- [Alpine.js](https://alpinejs.dev/) for interactivity
- [HTMX](https://htmx.org/) for dynamic content
- [Leaflet.js](https://leafletjs.com/) for maps
- [Chart.js](https://www.chartjs.org/) for data visualization

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- Node.js and npm (for frontend dependencies)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Mustafa1998-tech/RoadSystemMaintance.git
   cd road-maintenance-system
   ```

2. **Set up a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   Create a `.env` file in the project root:
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///db.sqlite3
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Main application: http://localhost:8000
   - Admin interface: http://localhost:8000/admin/

## 📂 Project Structure

```
road_maintenance/
├── apps/
│   ├── accounts/          # User authentication and profiles
│   ├── issues/            # Issue management
│   ├── media/             # File uploads
│   └── reports/           # Reporting functionality
├── road_maintenance/      # Project settings
├── static/                # Static files (CSS, JS, images)
├── templates/             # HTML templates
│   └── issues/            # Issue-related templates
│       ├── base.html      # Base template for issues
│       ├── form.html      # Create/Edit issue form
│       ├── list.html      # Issues list view
│       ├── detail.html    # Issue details
│       └── confirm_delete.html  # Delete confirmation
├── .env                   # Environment variables
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt
```

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `False` |
| `SECRET_KEY` | Django secret key | - |
| `DATABASE_URL` | Database connection URL | `sqlite:///db.sqlite3` |
| `ALLOWED_HOSTS` | Allowed hostnames | `localhost,127.0.0.1` |
| `EMAIL_BACKEND` | Email backend | `console` |

## 🛠 Development

### Available Commands

```bash
# Run development server
python manage.py runserver

# Run tests
python manage.py test

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support, please open an issue in the GitHub repository.

---

<div align="center">
  Made with ❤️ by Mustafa Ahmed
</div>
