from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this in production

# Dummy user for demo
# USER_CREDENTIALS = {
#     'username': 'admin',
#     'password': 'pass123'
# }
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

def get_db_connection():
    conn = sqlite3.connect('evoting.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

from werkzeug.security import check_password_hash

# @app.route('/voter_login', methods=['GET', 'POST'])
# def voter_login():
#     if request.method == 'POST':
#         mobile = request.form['mobile']
#         password = request.form['password']

#         conn = get_db_connection()
#         voter = conn.execute('SELECT * FROM voters WHERE mobile = ?', (mobile,)).fetchone()
#         conn.close()

#         if voter and check_password_hash(voter['password'], password):
#             session['user'] = mobile
#             session['voter_id'] = voter['id']
#             session['role'] = 'voter'
#             return redirect(url_for('voter_dashboard'))
#         else:
#             flash('Invalid credentials. Try again.')

#     return render_template('voter_login.html')
from flask import request, session, redirect, url_for, flash, render_template
from werkzeug.security import check_password_hash

@app.route('/voter_login', methods=['GET', 'POST'])
def voter_login():
    if request.method == 'POST':
        mobile = request.form['mobile']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch voter by mobile number
        cursor.execute('SELECT * FROM voters WHERE mobile = ?', (mobile,))
        voter = cursor.fetchone()
        conn.close()

        if voter:
            # voter[5] = password_hash, voter[6] = verified (index may vary, safer to use dict if you can)
            if check_password_hash(voter['password_hash'], password):
                if voter['verified']:
                    session['user'] = voter['name']
                    session['voter_id'] = voter['id']
                    session['role'] = 'voter'
                    return redirect(url_for('voter_dashboard'))
                else:
                    flash('Your account is under verification. Please wait for approval.', 'warning')
                    return redirect(url_for('voter_dashboard'))
            else:
                flash('Invalid mobile number or password. Please try again.', 'error')
        else:
            flash('Invalid mobile number or password. Please try again.', 'error')

    return render_template('voter_login.html')


@app.route('/voter_register', methods=['GET', 'POST'])
def voter_register():
    state_region_map = {
        'Andhra Pradesh': 'AP01',
        'Arunachal Pradesh': 'AR02',
        'Assam': 'AS03',
        'Bihar': 'BR04',
        'Chhattisgarh': 'CG05',
        'Delhi': 'DL06',
        'Goa': 'GA07',
        'Gujarat': 'GJ08',
        'Haryana': 'HR09',
        'Himachal Pradesh': 'HP10',
        'Jammu and Kashmir': 'JK11',
        'Jharkhand': 'JH12',
        'Karnataka': 'KA13',
        'Kerala': 'KL14',
        'Madhya Pradesh': 'MP15',
        'Maharashtra': 'MH16',
        'Manipur': 'MN17',
        'Meghalaya': 'ML18',
        'Mizoram': 'MZ19',
        'Nagaland': 'NL20',
        'Odisha': 'OD21',
        'Punjab': 'PB22',
        'Rajasthan': 'RJ23',
        'Sikkim': 'SK24',
        'Tamil Nadu': 'TN25',
        'Telangana': 'TS26',
        'Tripura': 'TR27',
        'Uttar Pradesh': 'UP28',
        'Uttarakhand': 'UK29',
        'West Bengal': 'WB30'
    }

    if request.method == 'POST':
        voter_id = request.form['voter_id']
        name = request.form['name']
        mobile = request.form['mobile']
        password = request.form['password']
        region = request.form['region']

        if region not in state_region_map.values():
            flash('Choose a valid region code from the list.')
            return render_template('voter_register.html', state_region_map=state_region_map)

        hashed_pw = generate_password_hash(password)
        dummy_public_key = 'placeholder_public_key'

        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO voters (id, name, mobile, password_hash, region,  public_key)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (voter_id, name, mobile, hashed_pw, region, dummy_public_key))
            conn.commit()
            flash('Registration successful. You can now log in.')
            return redirect(url_for('voter_login'))
        except Exception as e:
            flash('Registration failed. That mobile number or ID might already be used.'+ str(e))
        finally:
            conn.close()

    return render_template('voter_register.html', state_region_map=state_region_map)


@app.route('/voter_dashboard')
def voter_dashboard():
    if session.get('role') != 'voter':
        return redirect(url_for('voter_login'))

    conn = get_db_connection()
    elections = conn.execute('SELECT * FROM elections').fetchall()
    conn.close()

    return render_template('voter_dashboard.html', elections=elections, user=session['user'])

@app.route('/vote/<int:election_id>', methods=['GET', 'POST'])
def vote(election_id):
    if session.get('role') != 'voter':
        return redirect(url_for('voter_login'))

    voter_id = session['voter_id']
    conn = get_db_connection()

    # Check if voter already voted
    already_voted = conn.execute(
        'SELECT * FROM votes WHERE voter_id = ? AND election_id = ?',
        (voter_id, election_id)
    ).fetchone()

    if already_voted:
        conn.close()
        flash('You have already voted in this election.')
        return redirect(url_for('voter_dashboard'))

    if request.method == 'POST':
        candidate_id = request.form['candidate_id']
        conn.execute(
            'INSERT INTO votes (voter_id, election_id, candidate_id) VALUES (?, ?, ?)',
            (voter_id, election_id, candidate_id)
        )
        conn.commit()
        conn.close()
        flash('Your vote has been recorded successfully!')
        return redirect(url_for('voter_dashboard'))

    # Get election and candidates for GET
    election = conn.execute('SELECT * FROM elections WHERE id = ?', (election_id,)).fetchone()
    candidates = conn.execute(
        'SELECT * FROM candidates WHERE election_id = ?', (election_id,)
    ).fetchall()

    conn.close()
    return render_template('vote.html', election=election, candidates=candidates)


@app.route('/auth_login', methods=['GET', 'POST'])
def auth_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        conn = get_db_connection()

        if role == 'admin':
            user = conn.execute('SELECT * FROM admins WHERE username = ?', (username,)).fetchone()
        else:
            user = conn.execute('SELECT * FROM ea WHERE username = ?', (username,)).fetchone()

        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user'] = username
            session['role'] = role
            if role == 'admin':
                return redirect(url_for('auth_dashboard'))
                return render_template('auth_dashboard.html', user=username, role=role)
            else:
                return redirect(url_for('ea_dashboard'))
                return render_template('ea_dashboard.html', user=username, role=role)
        else:
            flash('Invalid username or password.')

    return render_template('auth_login.html')

@app.route('/auth_dashboard')
def auth_dashboard():
    if not session.get('user') or session.get('role') != 'admin':
        return redirect(url_for('auth_login'))
    
    conn = get_db_connection()
    voter_count = conn.execute('SELECT COUNT(*) FROM voters').fetchone()[0]
    candidate_count = conn.execute('SELECT COUNT(*) FROM candidates').fetchone()[0]
    election_count = conn.execute('SELECT COUNT(*) FROM elections').fetchone()[0]
    print("Voters:", voter_count)
    print("Candidates:", candidate_count)
    print("Elections:", election_count)
    conn.close()


    return render_template('auth_dashboard.html',
                           user=session.get('user'),
                           role=session.get('role'),
                           voters=voter_count,
                           candidates=candidate_count,
                           elections=election_count)

@app.route('/add_eaMember', methods=['GET', 'POST'])
def add_eaMember():
    if session.get('role') != 'admin':
        flash("Access denied.")
        return redirect(url_for('auth_login'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)

        conn = get_db_connection()
        conn.execute('INSERT INTO ea (username, password) VALUES (?, ?)', (username, hashed_pw))
        conn.commit()
        conn.close()
        flash('Election Authority member added successfully!')
        return redirect(url_for('add_eaMember'))

    return render_template('add_eaMember.html')

@app.route('/add_candidates', methods=['GET', 'POST'])
def add_candidates():
    if session.get('role') != 'admin':
        flash("Access denied.")
        return redirect(url_for('auth_login'))

    conn = get_db_connection()
    elections = conn.execute('SELECT id, name FROM elections').fetchall()

    if request.method == 'POST':
        name = request.form['name']
        party = request.form['party']
        election_id = request.form['election_id']

        conn.execute('INSERT INTO candidates (name, party, election_id) VALUES (?, ?, ?)',
                     (name, party, election_id))
        conn.commit()
        conn.close()
        flash('Candidate added successfully!')
        return redirect(url_for('add_candidates'))

    return render_template('add_candidates.html', elections=elections)


@app.route('/add_elections', methods=['GET', 'POST'])
def add_elections():
    if session.get('role') != 'admin':
        flash("Access denied.")
        return redirect(url_for('auth_login'))

    if request.method == 'POST':
        name = request.form['name']
        region = request.form['region']
        date = request.form['date']

        conn = get_db_connection()
        conn.execute('INSERT INTO elections (name, region, date) VALUES (?, ? ,?)', (name, region, date))
        conn.commit()
        conn.close()
        flash('Election added successfully!')
        return redirect(url_for('add_elections'))

    return render_template('add_elections.html')


@app.route('/ea_dashboard')
def ea_dashboard():
    if not session.get('user') or session.get('role') != 'ea_authority':
        return redirect(url_for('auth_login'))
    
    conn = get_db_connection()
    unverified_voters = conn.execute('SELECT COUNT(*) FROM voters WHERE verified = 0').fetchone()[0]
    unsigned_votes = conn.execute("SELECT COUNT(*) FROM blinded_votes WHERE status = ?", ('signed',)).fetchone()[0]
    conn.close()

    return render_template('ea_dashboard.html',
                           user=session.get('user'),
                           role=session.get('role'),
                           unverified_voters=unverified_voters,
                           unsigned_votes=unsigned_votes)


@app.route('/verify_voters', methods=['GET', 'POST'])
def verify_voters():
    if not session.get('user') or session.get('role') != 'ea_authority':
        return redirect(url_for('ea_login'))  # Adjust this to your EA login route

    conn = get_db_connection()

    if request.method == 'POST':
        voter_id = request.form.get('voter_id')
        conn.execute('UPDATE voters SET verified = 1 WHERE id = ?', (voter_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('verify_voters'))  # ⬅️ Redirect after POST to avoid resubmission

    voters = conn.execute('SELECT id, name, mobile, region FROM voters WHERE verified = 0').fetchall()
    conn.close()

    return render_template('verify_vote.html', voters=voters)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    #flash('Logged out successfully.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
