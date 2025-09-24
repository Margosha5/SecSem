import sqlite3
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import html
from pathlib import Path


class UserHandler(BaseHTTPRequestHandler):
    TEMPLATES_DIR = Path(__file__).with_name("templates")

    def connect_to_db(self):
        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row
        return con

    def send_html_response(self, status_code, content):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

    def send_static_file(self, file_path, content_type):
        with open(file_path, 'rb') as file:
            content = file.read()
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(content)

    def render_template(self, title, body):
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <link rel="stylesheet" href="/static/css/style.css">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body>
            <div class="container">
                {body}
            </div>
        </body>
        </html>
        '''
    
    def render_file(self, name: str, **ctx):
        html = (self.TEMPLATES_DIR / name).read_text(encoding="utf-8")
        return html.format(**ctx)

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)

        if path.startswith('/static/'):
            self.handle_static(path)
        elif path == '/':
            self.index()
        elif path == '/users':
            self.users()
        elif path == '/by-login':
            self.by_login(query_params)
        elif path == '/by-id':
            self.by_id(query_params)
        else:
            body = '<h1>Error</h1><div class="navbar"><a href="/">Home</a></div><p class="error">Page not found</p>'
            self.send_html_response(404, self.render_template('Error', body))

    def handle_static(self, path):
        safe_path = path.lstrip('/')
        if not os.path.exists(safe_path):
            self.send_error(404, "File not found")
            return

        content_types = {
            '.css': 'text/css',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
        }

        ext = os.path.splitext(safe_path)[1].lower()
        content_type = content_types.get(ext, 'text/plain')

        self.send_static_file(safe_path, content_type)

    def index(self):
        body = self.render_file("index.html")
        self.send_html_response(200, self.render_template('Home', body))

    def users(self):
        con = self.connect_to_db()
        users = con.execute('''
            SELECT id, login, money_amount, card_number 
            FROM users 
            WHERE status = 1
            ORDER BY id
        ''').fetchall()
        con.close()

        if users:
            user_items = ''
            for user in users:
                user_items += f'''
                <li class="user-item">
                    <strong>ID:</strong> {user['id']} | 
                    <strong>Login:</strong> {html.escape(user['login'])} | 
                    <strong>Money:</strong> ${user['money_amount']:.2f} | 
                    <strong>Card:</strong> {user['card_number']}
                </li>
                '''

            users_list = f'''
            <ul class="users-list">
                {user_items}
            </ul>
            '''
        else:
            users_list = '<p>No active users found.</p>'

        body = f'''
        <h1>Current Active Users</h1>
        <div class="navbar">
            <a href="/">Home</a>
        </div>
        {users_list}
        '''
        self.send_html_response(200, self.render_template('Active Users', body))

    def by_login(self, query_params):
        login = query_params.get('login', [''])[0]

        if not login:
            body = '<h1>Error</h1><div class="navbar"><a href="/">Home</a></div><p class="error">Please provide a login parameter</p>'
            self.send_html_response(400, self.render_template('Error', body))
            return

        con = self.connect_to_db()
        user = con.execute('''
            SELECT id, login, money_amount, card_number 
            FROM users 
            WHERE login = ? AND status = 1
        ''', (login,)).fetchone()
        con.close()

        if user:
            user_info = f'''
            <div class="user-info">
                <p><strong>ID:</strong> {user['id']}</p>
                <p><strong>Login:</strong> {html.escape(user['login'])}</p>
                <p><strong>Money Amount:</strong> ${user['money_amount']:.2f}</p>
                <p><strong>Card Number:</strong> {user['card_number']}</p>
            </div>
            '''
            body = f'''
            <h1>User Info</h1>
            <div class="navbar">
                <a href="/">Home</a> | 
                <a href="/users">View Active Users</a>
            </div>
            {user_info}
            '''
            self.send_html_response(200, self.render_template('User Info', body))
        else:
            body = f'<h1>Error</h1><div class="navbar"><a href="/">Home</a></div><p class="error">No active user found with login: {html.escape(login)}</p>'
            self.send_html_response(404, self.render_template('Error', body))

    def by_id(self, query_params):
        try:
            user_id = int(query_params.get('id', ['0'])[0])
        except ValueError:
            body = '<h1>Error</h1><div class="navbar"><a href="/">Home</a></div><p class="error">Invalid ID parameter</p>'
            self.send_html_response(400, self.render_template('Error', body))
            return

        con = self.connect_to_db()
        user = con.execute('''
            SELECT id, login, money_amount, card_number 
            FROM users 
            WHERE id = ? AND status = 1
        ''', (user_id,)).fetchone()
        con.close()

        if user:
            user_info = f'''
            <div class="user-info">
                <p><strong>ID:</strong> {user['id']}</p>
                <p><strong>Login:</strong> {html.escape(user['login'])}</p>
                <p><strong>Money Amount:</strong> ${user['money_amount']:.2f}</p>
                <p><strong>Card Number:</strong> {user['card_number']}</p>
            </div>
            '''
            body = f'''
            <h1>User Info</h1>
            <div class="navbar">
                <a href="/">Home</a> | 
                <a href="/users">View All Active Users</a>
            </div>
            {user_info}
            '''
            self.send_html_response(200, self.render_template('User Info', body))
        else:
            body = f'<h1>Error</h1><div class="navbar"><a href="/">Home</a></div><p class="error">No active user found with ID: {user_id}</p>'
            self.send_html_response(404, self.render_template('Error', body))


def init_db():
    if not os.path.exists('database.db'):
        con = sqlite3.connect('database.db')
        with open('init-db.sql', 'r') as f:
            con.executescript(f.read())
        con.commit()
        con.close()
        print("Database initialized successfully")


if __name__ == '__main__':
    init_db()

    port = 8000
    server = HTTPServer(('localhost', port), UserHandler)

    print(f"Server running on http://localhost:{port}")
    print("Press Ctrl+C to stop the server")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()
