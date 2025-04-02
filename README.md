# 🚀 FastHTML Todo App with AI Task Estimation

This is a **FastHTML**-based Todo application with AI-powered task estimation using **Google Gemini AI**. It supports **PostgreSQL** as the database and leverages **FastSQL** for ORM operations. The app allows users to create, categorize, and manage their tasks efficiently.

## ✨ Features
- 📌 **Task Categorization**: Automatically assigns categories based on keywords.
- ⏳ **AI-Powered Task Estimation**: Uses **Google Gemini AI** to estimate task completion time.
- ✅ **Task Management**: Create, edit, delete, and mark tasks as completed.
- 🔄 **Drag-and-Drop Sorting**: Uses **SortableJS** for reordering tasks.
- 🔐 **User Authentication**: Supports user login and session management.
- 📄 **Markdown Support**: Task details support Markdown formatting.

## 🛠 Tech Stack
- **FastHTML** for backend and frontend rendering
- **FastSQL** for database interactions
- **PostgreSQL** for storing tasks
- **Google Gemini AI** for task estimation
- **SortableJS & MarkdownJS** for enhanced UI experience

## 🚀 Installation & Setup
### 1️⃣ Clone the Repository
```sh
 git clone https://github.com/your-username/your-repo.git
 cd your-repo
```

### 2️⃣ Install Dependencies
Ensure you have Python installed, then install required packages:
```sh
 pip install fasthtml fastsql google genai
```

### 3️⃣ Set Up PostgreSQL Database
Update your **database URL** in the `DB_URL` variable inside the code:
```python
 DB_URL = "postgresql://username:password@host:port/database"
```

### 4️⃣ Run the Application
```sh
 python app.py
```
App will start on `http://localhost:8080`

## 🔧 Usage
- **Login/Register** with a username and password.
- **Add a Task** and the app will auto-assign a category and estimated time.
- **Edit/Delete Tasks** from the UI.
- **Reorder tasks** using drag-and-drop.

## 📜 API Routes
- `GET /` → Fetch all tasks
- `POST /login` → Authenticate user
- `POST /create` → Create a new task
- `POST /edit` → Edit an existing task
- `POST /remove` → Delete a task
- `POST /toggle_done` → Mark task as completed

## 🛡 Security & Authentication
- Passwords are securely hashed before storing in the database.
- User sessions are maintained using FastHTML’s session management.

## 🎯 Future Enhancements
- 🌍 Multi-user collaboration
- 📆 Due dates & reminders
- 📊 Analytics & task insights

## 🤝 Contributing
Pull requests are welcome! Please open an issue to discuss your changes before submitting a PR.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

🚀 **Happy Coding!**

