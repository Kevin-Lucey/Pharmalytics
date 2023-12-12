from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb
import re

app = Flask(__name__)
app.secret_key = 'your secret key'


#Connect to the MySQL database
conn = MySQLdb.connect(
	host='localhost',
	user='root',
	passwd='CHANGEME',
	db='Pharmalytics'
)

## If no mysqldb object is printed, connection was not established
print(conn)

@app.route("/", methods=['GET'])
def index():
	msg = "Welcome! Please log in!"
	return render_template('index.html', msg=msg)

@app.route("/patientlogin", methods=['GET', 'POST'])
def patientlogin():
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

@app.route("/patient", methods=["GET", "POST"])
def patient():
	print("in patient")
	if 'loggedin' in session:
		
		cursor = conn.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute("""
			SELECT * FROM patientInfo WHERE username = %s AND usr_pwd = %s 
			""", (session['username'], session['password']))
		account = cursor.fetchone()
		
		cursor.execute("CALL patientPrescriptions(%s)", (account['patientID'],))
		prescriptions = cursor.fetchall()
		if request.method == 'POST' and 'medication' in request.form and 'quantity' in request.form:
			cursor.execute("INSERT INTO prescriptionInfo (prescriptionName, prescriptionDosage, prescriptionDate, patientID, doctorID, quantity, approved, filled) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",(request.form['medication'], request.form['dosage'], '2023-07-25', account['patientID'], account['doctorID'], request.form['quantity'], 0,0))
			conn.commit()
		
		cursor.execute("CALL patientPrescriptions(%s)", (account['patientID'],))
		prescriptions = cursor.fetchall()
		cursor.close()
		return render_template("patient.html", account=account, prescriptions=prescriptions)   
	return render_template("index.html", msg='Something went wrong, try to login again')

@app.route("/doctor", methods=['GET', "POST"])
def doctor():
	print('in doctor')
	if 'loggedin' in session:
		cursor = conn.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM doctorInfo WHERE username = %s and usr_pwd = %s', (session['username'], session['password']))
		account = cursor.fetchone()
	
		cursor.execute('CALL doctorSpecificPatients(%s)', (account['doctorID'],))
		res = cursor.fetchall()
		print(res)
		return render_template('doctor.html', res=res)
	return redirect(url_for('index.html'))

@app.route('/pharmacy', methods=['GET',"POST"])
def pharmacy():
	print("in pharmacy")
	if 'loggedin' in session:
		return render_template('pharmacy.html')
	return render_template('index.html')



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

@app.route('/inventory', methods=['GET'])
def inventory():
	print('in inventory')
	cursor = conn.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute("SELECT * from Inventory")
	inv = cursor.fetchall()

	return render_template('inventory.html', inv = inv)

@app.route("/listpatient")
def listpatient():
	cursor = conn.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute("SELECT patientName, doctorName FROM patientInfo INNER JOIN doctorInfo WHERE patientInfo.doctorID = doctorInfo.doctorID")
	patients = cursor.fetchall() 
	cursor.close()
	return render_template("listpatient.html", patients=patients)

@app.route('/fillPrescription', methods=['GET', 'POST'])
def fillPrescription():
	cursor = conn.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute("SELECT * from needToBeFilled")
	need = cursor.fetchall()
	if request.method == 'POST' and 'prescription_id' in request.form:	
		try:
			cursor.execute("UPDATE prescriptionInfo SET filled = 1 WHERE prescriptionID = %s",(request.form['prescription_id'],))
			conn.commit()
			msg = 'Prescription sent successfully! Refresh page to update..'
		except Exception as e:
			msg = 'An error occurred while filling the prescription.'
		finally:
			cursor.close()
		
		return render_template('fillPrescription.html',need=need, msg=msg)
	return render_template('fillPrescription.html', need=need)

@app.route('/prescriptionRequests', methods=['GET', 'POST'])
def prescriptionRequests():
	print('in prescription requests')
	msg = ''
	if 'loggedin' in session:
		cursor = conn.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM doctorInfo WHERE username = %s and usr_pwd = %s', (session['username'], session['password']))
		account = cursor.fetchone()
		
		cursor.execute("CALL doctorSpecificPendingScripts(%s)",  (account['doctorID'],))
		pend = cursor.fetchall()
		

		return render_template('prescriptionRequests.html', account=account, pend=pend)

@app.route("/accept", methods=["GET", "POST"])
def accept():
	msg = ''
	if request.method == "POST" and 'prescription_id' in request.form:
		cursor = conn.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM doctorInfo WHERE username = %s and usr_pwd = %s', (session['username'], session['password']))
		account = cursor.fetchone()
		
		cursor.execute("CALL doctorSpecificPendingScripts(%s)",  (account['doctorID'],))
		pend = cursor.fetchall()

		pending_ids = [p['prescriptionID'] for p in pend] 
		print(type(request.form['prescription_id'][0]))
		for i in range(len(pending_ids)):
			if int(request.form['prescription_id'][0]) == pending_ids[i]:
				cursor.execute("CALL approveScript(%s)", (request.form['prescription_id'],))
				cursor.close()
	
		else:
			msg="Invalid prescription ID entered, try again"
			cursor.close()
			return render_template("accept.html", msg=msg)
	return render_template("accept.html", msg=msg)

@app.route("/logout", methods=['GET',"POST"])
def logout():
	session.pop('username')
	session.pop('password')
	session.pop('loggedin')
	return redirect(url_for('index'))

if __name__ == "__main__":
	app.run(host="localhost", port=int("5000"), debug=True)