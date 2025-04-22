CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ea (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);
DROP TABLE elections;
CREATE TABLE IF NOT EXISTS elections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    region TEXT NOT NULL,
    date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    party TEXT NOT NULL,
    election_id INTEGER NOT NULL,
    FOREIGN KEY (election_id) REFERENCES elections(id)
);

-- CREATE TABLE IF NOT EXISTS voters (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     mobile TEXT NOT NULL UNIQUE,
--     password TEXT NOT NULL
-- );
DROP TABLE voters;
CREATE TABLE IF NOT EXISTS voters (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    mobile TEXT UNIQUE NOT NULL,
    region TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    public_key TEXT NOT NULL,
    verified BOOLEAN DEFAULT 0,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS blinded_votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    voter_id INTEGER NOT NULL,
    election_id INTEGER NOT NULL,
    blinded_vote TEXT NOT NULL,
    signed_blind TEXT, -- Populated once EA signs
    status TEXT CHECK(status IN ('pending', 'signed', 'rejected')) DEFAULT 'pending',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (voter_id) REFERENCES voters(id),
    FOREIGN KEY (election_id) REFERENCES elections(id)
);

CREATE TABLE IF NOT EXISTS votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    election_id INTEGER NOT NULL,
    candidate_id INTEGER NOT NULL,
    ea_signature TEXT NOT NULL,  -- Signature of the unblinded vote
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (election_id) REFERENCES elections(id),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
);


