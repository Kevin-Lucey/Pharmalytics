from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb
import re

app = Flask(__name__)
app.secret_key = 'your secret key'


# Establishing a connection to the MySQL database
conn = MySQLdb.connect(
    host='localhost',
    user='root',
    passwd='CHANGE ME',
    db='Pharmalytics'
)

print(conn)

@app.route("/", methods=['GET'])
def index():
    msg = "Welcome! Please log in!"
    return render_template('index.html', msg=msg)

@app.route("/patientlogin", methods=['GET', 'POST'])
def patientlogin():
    print('in patient login')
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        try:
            username = request.form['username']
            password = request.form['password']

            if conn:
                cursor = conn.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM patientOnlyLogin WHERE username = %s AND usr_pwd = %s', (username, password))
                account = cursor.fetchone()

                if account:
                    session['loggedin'] = True
                    session['username'] = account['username']
                    session['password'] = account['usr_pwd']
                    cursor.execute("""SELECT * FROM patientInfo WHERE username = %s
                                   AND usr_pwd = %s""", (session['username'], session['password']))
                    account = cursor.fetchone()
                    cursor.close()
                    
                    if not account:
                        return redirect(url_for('index'), msg="An error occured! ")
                    msg = 'Logged in successfully!'
                    
                    return redirect(url_for('patient', msg=msg, account=account))  
                else:
                    msg = 'Incorrect username/password!'
            else:
                msg = 'No connection to the database!'
        except Exception as e:
            print(type(e), e)
            return render_template('patientlogin.html', msg="An error occured! ")
    return render_template('patientlogin.html', msg=msg)

@app.route("/doctorlogin", methods=['GET', 'POST'])
def doctorlogin():
    print('in doctor login')
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        try:
            username = request.form['username']
            password = request.form['password']

            if conn:
                cursor = conn.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM doctorOnlyLogin WHERE username = %s AND usr_pwd = %s', (username, password))
                account = cursor.fetchone()
                if account:
                    session['loggedin'] = True
                    session['username'] = account['username']
                    session['password'] = account['usr_pwd']
                    msg = 'Logged in successfully!'
                    

                    cursor.execute("""
                        SELECT * FROM doctorInfo WHERE username = %s AND usr_pwd = %s
                        """, (username, password))
                    account = cursor.fetchone()
                    cursor.close()
                    return redirect(url_for('doctor', msg=msg, account=account))  
                else:
                    msg = 'Incorrect username/password!'
            else:
                msg = 'No connection to the database!'
        except Exception as e:
            print(type(e), e)
            return render_template('doctorlogin.html', msg="An error occured! ")
    return render_template('doctorlogin.html', msg=msg)


@app.route("/pharmacylogin", methods=['GET', 'POST'])
def pharmacylogin():
    print('in pharmacy login')
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        try:
            username = request.form['username']
            password = request.form['password']

            if conn:
                cursor = conn.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM pharmacyOnlyLogin WHERE username = %s AND usr_pwd = %s', (username, password))
                account = cursor.fetchone()
                if account:
                    session['loggedin'] = True
                    session['username'] = account['username']
                    session['password'] = account['usr_pwd']
                    msg = 'Logged in successfully!'
                    cursor.execute("""
                        SELECT * FROM pharmacyInfo WHERE username = %s AND usr_pwd = %s
                        """, (username, password))
                    account = cursor.fetchone()
                    cursor.close()  

                    return redirect(url_for('pharmacy', msg=msg, account=account))  
                else:
                    msg = 'Incorrect username/password!'
            else:
                msg = 'No connection to the database!'
        except:
            return render_template('pharmacylogin.html', msg="An error occured! ")
    return render_template('pharmacylogin.html', msg=msg)



@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'personaCode' in request.form :
        username = request.form['username']
        password = request.form['password']
        personaCode = request.form['personaCode']
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM userLoginInfo WHERE username = % s', (username, ))
        account = cursor.fetchone()
        cursor.close()
        if account:
            msg = 'Account already exists !'
        elif not username or not password or not personaCode:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO userLoginInfo VALUES (% s, % s, % s)', (username, password, personaCode, ))
            conn.commit()
            msg = 'You have successfully registered !'
            return redirect(url_for("index", msg=msg, ))
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

@app.route("/patient")
def patient():
    print("in patient")
    if 'loggedin' in session:
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT * FROM patientInfo WHERE username = %s AND usr_pwd = %s 
            """, (session['username'], session['password']))
        account = cursor.fetchone()
        cursor.close()
        return render_template("patient.html", account=account)   
    return render_template("index.html", msg='Something went wrong, try to login again')

@app.route("/doctor")
def doctor():
    print('in doctor')
    if 'loggedin' in session:
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM doctorInfo WHERE username = %s and usr_pwd = %s', (session['username'], session['password']))
        account = cursor.fetchone()
    
        cursor.execute('doctorSpecificPatients(%s)', (account['doctorID'],))
        res = cursor.fetchall()

        print("res: ", res)
        return render_template('doctor.html', res=res)
    return redirect(url_for('index.html'))

@app.route('/pharmacy')
def pharmacy():
    print("in pharmacy")
    if 'loggedin' in session:
        return render_template('pharmacy.html')
    return render_template('index.html')

@app.route('/AddPatient', methods=['GET', 'POST'])
def AddPatient():
	if request.method == 'POST' and 'Name' in request.form and 'DateOfBirth' in request.form and 'gender' in request.form and 'insuranceid' in request.form:
		Name = request.form['Name']
		DateOfBirth = request.form['DateOfBirth'] 
		gender = request.form['gender'] 
		insuranceid = request.form['insuranceid'] 
		cursor = conn.cursor()
		try:
			cursor.execute('INSERT INTO AddP (Name,DateOfBirth,gender,insuranceid) VALUES (%s, %s, %s,%s)',
						   (Name, DateOfBirth,gender,insuranceid))
			conn.commit()
			msg = 'You have successfully added patient!'
		except Exception as e:
			msg = f'An error occurred: '
		finally:
			cursor.close()
		
		return render_template('AddPatient.html', msg=msg)

	return render_template('AddPatient.html')

@app.route('/insurance', methods=['GET', 'POST'])
def insurance():
	if request.method == 'POST':
		insurance_info = request.form['insurance_info']
		if insurance_info == 'Anthem':
			result = "Accepted to the pharmacy"
		else:
			result = "Not Accepted to the pharmacy"
		return render_template('insurance.html', result=result)
	return render_template('insurance.html', result=None)

@app.route('/Inventory', methods=['GET', 'POST'])
def Inventory():
	if request.method == 'POST' and 'DrugName' in request.form and 'Strength' in request.form and 'Manufacture' in request.form:
		DrugName = request.form['DrugName']
		Strength = request.form['Strength']
		Manufacture = request.form['Manufacture']
		
		cursor = conn.cursor()
		try:
			cursor.execute('INSERT INTO inventory (DrugName, Strength, Manufacture) VALUES (%s, %s, %s)',
						   (DrugName, Strength, Manufacture))
			conn.commit()
			msg = 'You have successfully added!'
		except Exception as e:
			msg = f'An error occurred'
		finally:
			cursor.close()
		
		return render_template('Inventory.html', msg=msg)

	return render_template('Inventory.html')

@app.route("/listpatient")
def listpatient():
	cursor = conn.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT Name, DateOfBirth, Gender, insuranceid FROM AddP')
	patients = cursor.fetchall() 
	cursor.close()
	return render_template("listpatient.html", patients=patients)

@app.route('/sendpre', methods=['GET', 'POST'])
def sendpre():
	if request.method == 'POST' and all(key in request.form for key in ['patientName', 'patientDateOfBirth', 'gender', 'insuranceid', 'medication', 'strength', 'quantity', 'instructions']):
		patientName = request.form['patientName']
		patientDateOfBirth = request.form['patientDateOfBirth']
		gender = request.form['gender']
		insuranceid = request.form['insuranceid']
		medication = request.form['medication']
		strength = request.form['strength']
		quantity = request.form['quantity']
		instructions = request.form['instructions']
		
		cursor = conn.cursor()
		try:
			cursor.execute('INSERT INTO prescription (patientName, patientDateOfBirth, gender, insuranceid, medication, strength, quantity, instructions) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
						   (patientName, patientDateOfBirth, gender, insuranceid, medication, strength, quantity, instructions))
			conn.commit()
			msg = 'Prescription sent successfully!'
		except Exception as e:
			msg = 'An error occurred while sending the prescription.'
			print(e) 
		finally:
			cursor.close()
		
		return render_template('sendprescription.html', msg=msg)


@app.route('/prescriptionRequests', methods=['GET', 'POST'])
def prescriptionRequests():
    print('in prescription requests')
    if 'loggedin' in session:
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        print('before cursor')
        cursor.execute('SELECT * FROM doctorInfo WHERE username = %s and usr_pwd = %s', (session['username'], session['password']))
        print("after cursor")
        account = cursor.fetchone()
        
        print("before pend")
        pend = cursor.callproc("doctorSpecificPendingScripts",  (account['doctorID'],))
        print(pend)
        cursor.close()
        return render_template('prescriptionRequests.html', account=account, pend=pend)


@app.route("/logout", methods=['GET',"POST"])
def logout():
    session.pop('username')
    session.pop('password')
    session.pop('loggedin')
    return redirect(url_for('index'))

if __name__ == "__main__":
	app.run(host="localhost", port=int("5000"), debug=True)