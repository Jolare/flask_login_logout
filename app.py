from flask import Flask, render_template, request, json, redirect, session
from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "itsasecret"
mysql = MySQL()

# MySQL Config
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'alsoasecret'
app.config['MYSQL_DATABASE_DB'] = 'ToDoListe'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route("/")
def main():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("signup.html")

@app.route("/registered",methods=["POST","GET"])
def registered():
    try:
        #Abfrage aus HTML Dokument
        _name = request.form["inputName"]
        _email = request.form["inputEmail"]
        _password = request.form["inputPassword"]

        #SQL Verbindung
        if _name and _email and _password:
            conn = mysql.connect()
            cursor = conn.cursor()
            _hashed_password = generate_password_hash(_password)
            
            #Prozedur der Datenbank ordnet Daten in Tabelle ein
            cursor.callproc("sp_createUser",(_name,_email,_hashed_password))
            data = cursor.fetchall()

            #Javascript Konsolenausgaben
            if len(data) is 0:
                conn.commit()
                return json.dumps({"message":"Benutzer erfolgreich erstellt!"})
            else:
                return json.dumps({"error":str(data[0])})
        else:
            return json.dumps({"html":"<span>Bitte alle Felder ausfuellen!</span>"})
    except Exception as e:
        return json.dumps({"error":str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route("/login")
def login():
    return render_template("signin.html")

@app.route("/validateLogin",methods=["POST","GET"])
def validateLogin():
    try:
        #Abfrage der eingegebenen Daten

        _username = request.form["inputEmail"]
        _password = request.form["inputPassword"]
        
        #SQl Verbindung
        
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc("sp_validateLogin",(_username,))
        data = cursor.fetchall()

        if len(data) > 0:
            #Eingegebenes Passwort mit Hash in Datenbank vergleichen und einloggen

            if check_password_hash(str(data[0][3]), _password):
                session["user"] = data[0][0]
                return redirect("/userHome")
        
            else:
                return render_template("error.html", error = "Email Adresse oder Passwort falsch!")
        
        else: 
            return render_template("error.html", error = "Email Adresse oder Passwort falsch!")

    except Exception as e:
        return render_template("error.html", error = str(e))
        
    finally:
        cursor.close()
        conn.close()

@app.route("/userHome")
def userHome():
    if session.get("user"):
        return render_template("userHome.html")
    else:
        return render_template("error.html",error = "Unbefugter Zugang!")

@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect("/")

if __name__ == "__main__":
    app.run()
