from fasthtml.common import *
from hmac import compare_digest
from fastsql import Database  # Import FastSQL for PostgreSQL
from fastsql.core import NotFoundError
from hashlib import sha256
from google import genai
import re


API_KEY = "AIzaSyA7A4v58H24mJ4xqtuYAkG--4sqcQJP-3Y"
client = genai.Client(api_key=API_KEY)

# PostgreSQL database URL
DB_URL = "postgresql://postgres:ptJenPtGhffopTfeiYCFTUVqTIUNLaCj@centerbeam.proxy.rlwy.net:40602/railway"

# Create a database connection
try:
    db = Database(DB_URL)
    print("✅ Connected to PostgreSQL database successfully!")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    exit()

# Define User model
class User:
    name: str
    pwd: str

# Define Todo model
class Todo:
    id: int
    title: str
    done: bool = False
    name: str
    details: str = ""
    priority: int = 0
    category: str = "other"  # ✅ Add category
    estimated_time: str = "Unknown"  # ✅ Add estimated time

    def __ft__(self):
        ashow = A(self.title, hx_post=retr.to(id=self.id), target_id='current-todo')
        aedit = A('edit', hx_post=edit.to(id=self.id), target_id='current-todo')
        dt = '✅ ' if self.done else ''
        adone = CheckboxX(id=f'done-{self.id}', name='done', label='Done', checked=self.done, hx_post=toggle_done.to(id=self.id))
        category_label = Span(f"📌 Category: {self.category.capitalize()} | ⏳ {self.estimated_time} min", cls="text-sm text-gray-500")
        return Li(dt, ashow, ' | ', aedit, ' | ', adone, category_label, Hidden(id="id", value=self.id), Hidden(id="priority", value=self.priority), id=f'todo-{self.id}')

# Create tables in PostgreSQL
try:
    users = db.create(User, pk='name')
    todos = db.create(Todo)
    print("✅ Tables created successfully!")
except Exception as e:
    print(f"❌ Table creation failed: {e}")
    exit()

login_redir = RedirectResponse('/login', status_code=303)

def before(req, sess):
    auth = req.scope['auth'] = sess.get('auth', None)
    if not auth:
        return login_redir
    todos.xtra(name=auth)

def _not_found(req, exc):
    return Titled('Oh no!', Div('We could not find that page :('))

def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()




def estimate_time(task_title):
    """Estimate the time required for a task using Gemini AI."""
    prompt = f"Estimate the time (in minutes) needed to complete this task: {task_title}. Respond with only a number."
    
    response = client.models.generate_content(
        model="gemini-1.5-pro", contents=prompt
    )

    print(response.text)
    
    if response and response.text:
        match = re.search(r"\d+", response.text)  # ✅ Extract first number from response
        if match:
            return int(match.group(0))  # ✅ Return the extracted integer

    return 30  # Default fallback time (30 minutes)









hdrs = (SortableJS('.sortable'), MarkdownJS('.markdown'))

bware = Beforeware(before, skip=[r'/favicon\\.ico', r'/static/.*', r'.*\\.js', r'.*\\.css', '/login'])
app, rt = fast_app(before=bware, live=True, exception_handlers={404: _not_found}, hdrs=hdrs)

@app.get
def login():
    return Titled("Login", Form(action='/login', method='post')(
        Input(id='name', name='name', placeholder='Name'),
        Input(id='pwd', name='pwd', type='password', placeholder='Password'),
        Button('Login')
    ))

@dataclass
class Login:
    name: str
    pwd: str

@rt("/login")
def post(login: Login, sess):
    if not login.name or not login.pwd:
        return "Missing username or password."
    
    try:
        u = users[login.name]  # Try fetching the user
    except NotFoundError:
        # If user doesn't exist, create a new one
        hashed_pwd = hash_password(login.pwd)
        users.insert({"name": login.name, "pwd": hashed_pwd})
        return "New user registered. Please log in again."
    
    # Verify password
    if u.pwd != hash_password(login.pwd):
        return "Incorrect password. Try again."
    
    sess['auth'] = u.name  # Store user in session
    return RedirectResponse("/", status_code=303)


@app.get("/logout")
def logout(sess):
    del sess['auth']
    return login_redir



@rt("/")
def get(auth):
    try:
        todo_list = todos(order_by="priority ASC")  # ✅ Force sorting order
    except Exception as e:
        print(f"❌ Error fetching todos: {e}")  # ✅ Debugging
        todo_list = []  # ✅ Prevents breaking UI

    return Title(f"{auth}'s Todo List"), Container(
        Grid(H1(f"{auth}'s Todo List"),
             Div(style='text-align: right')(A('Logout', href='/logout'))),
        Card(
            Ul(Form(id='todo-list', cls='sortable', hx_post=reorder, hx_trigger="end")(
                *todo_list  # ✅ Ensures safe rendering
            )),
            header=Form(hx_post=create, target_id='todo-list', hx_swap="afterbegin")(
                Input(id="new-title", name="title", placeholder="New Todo"),
                Div(
                    Button("Add", type="submit"),
                )
            ),
            footer=Div(id='current-todo')
        )
    )



@rt
def reorder(id: list[int]):
    for i, id_ in enumerate(id):
        todos.update(priority=i, id=id_)
    return tuple(todos(order_by='priority'))

@rt
def create(todo: Todo):
    todo.estimated_time = estimate_time(todo.title)  # ✅ AI-based time estimation

    # ✅ Set priority based on keyword detection
    priority_keywords = {"urgent": 3, "important": 2, "optional": 1}
    todo.priority = next((v for k, v in priority_keywords.items() if k in todo.title.lower()), 1)

    # ✅ Improved category detection with case-insensitive regex
    category_map = {
        "work": ["meeting", "project", "deadline", "work", "task"],
        "personal": ["grocery", "shopping", "call", "birthday", "family"],
        "health": ["workout", "exercise", "doctor", "meditation", "hospital"],
        "finance": ["tax", "invoice", "budget", "payment", "salary"],
    }

    title_lower = todo.title.lower()
    detected_category = "other"  # Default category

    for category, keywords in category_map.items():
        for word in keywords:
            if re.search(word, title_lower, re.IGNORECASE):  # ✅ Case-insensitive matching
                detected_category = category
                break
        if detected_category != "other":
            break  # ✅ Exit early when a match is found

    todo.category = detected_category  # ✅ Assign detected category

    print(f"🛠 Task Title: {todo.title} → Category: {todo.category}")  # ✅ Debugging

    new_todo = todos.insert(todo)
    return new_todo, clear("new-title")


@rt
def remove(id: int):
    todos.delete(id)
    return clear(f'todo-{id}')

@rt
def edit(id: int):
    todo = todos[id]
    return fill_form(Form(hx_post=replace, target_id=f'todo-{id}', id="edit")(
        Group(Input(id="title"), Button("Save")),
        Hidden(id="id"), Hidden(priority="priority"),
        Hidden(name="done"), CheckboxX(id="done", label='Done'),
        Textarea(id="details", name="details", rows=10)
    ), todo)

@rt
def replace(todo: Todo):
    return todos.update(todo), clear('current-todo')

@rt
def retr(id: int):
    todo = todos[id]
    return Div(H2(todo.title), Div(todo.details, cls="markdown"), Button('Delete', name='id', value=id, hx_post=remove, hx_swap="outerHTML"))

@rt
def toggle_done(id: int):
    todo = todos[id]
    todos.update(done=not todo.done, id=id)
    return todos[id]

serve(
    port=8080
)
