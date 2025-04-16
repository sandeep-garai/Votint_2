import sqlite3
from werkzeug.security import generate_password_hash

def init_db(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    with open('schema.sql', 'r') as f:
        schema = f.read()
        c.executescript(schema)

    # Initialize admin account
    admin_username = 'admin'
    admin_password = 'pass123'
    admin_hash = generate_password_hash(admin_password)

    c.execute("INSERT OR IGNORE INTO admins (id, username, password) VALUES (1, ?, ?)", (admin_username, admin_hash))

    ea_username = 'ea_auth'
    ea_password = 'pass123'
    ea_hash = generate_password_hash(admin_password)

    c.execute("INSERT OR IGNORE INTO ea (id, username, password) VALUES (1, ?, ?)", (ea_username, ea_hash))

    voters = [
    ('9876543211', 'password1'),
    ('9123456782', 'password2'),
    ('9988776653', 'password3'),
    ('9000011124', 'password4'),
    ('9555566675', 'password5'),
    ]

    for mobile, plain_pw in voters:
        hashed_pw = generate_password_hash(plain_pw)
        c.execute('INSERT OR IGNORE INTO voters (mobile, password) VALUES (?, ?)', (mobile, hashed_pw))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    db_name = 'evoting.db'
    init_db(db_name)
    print(f"Database '{db_name}' initialized successfully.")
