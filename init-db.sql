CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL UNIQUE,
    money_amount REAL NOT NULL,
    card_number TEXT NOT NULL,
    status INTEGER NOT NULL CHECK (status IN (0, 1))
);

CREATE TABLE IF NOT EXISTS user_passwords (
    user_id INTEGER PRIMARY KEY,
    password TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);


INSERT INTO users (login, money_amount, card_number, status) VALUES
('admin', 2346.50, '4539538763621046', 1),
('marta03', 1230.75, '4912335606082832', 1),
('crisss', 236.25, '4556727586609355', 1),
('alex_cool', 6000.00, '45263461174327802', 0),
('princess Diana', 7653.30, '40240076199391209', 0);

INSERT INTO user_passwords (user_id, password) VALUES
(1, 'admin123'),
(2, 'qwerty9271'),
(3, 'cruuss'),
(4, 'mycoolselforever'),
(5, 'secretinfo');