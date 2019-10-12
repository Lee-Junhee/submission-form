from flask import Flask, flash, render_template, redirect, session, request
import subprocess, csv

app = Flask(__name__)
secretkey = open("secretkey.txt", 'r')
app.secret_key =  secretkey.read()
secretkey.close()

work = {}

pdlist=['04','05','10']

@app.route("/")
def main():
    if not 'user' in session:
        return render_template("login.html",
                pds=pdlist)
    with open("assignmntRepos.csv", newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            work[row['name']] = row['ssh']
    return render_template("submission.html",
            assignments=work.keys())

@app.route("/auth", methods=['POST'])
def login():
    session['user'] = request.form['user']
    session['pd'] = request.form['pd']
    return redirect('/')

@app.route("/logout")
def logout():
    del session['user']
    return redirect('/')

@app.route("/submit", methods=['POST'])
def submit():
    err = attempt(request.form['url'],request.form['id'])
    print(session['user'] + " created submodule in " + session['pd'] +" linked to "+request.form['url'])
    if err == 0:
        flash("Sucessfully Created Submodule!")
    if err == 1:
        flash("Submodule failed to create, check information and try again.")
    if err == 2:
        flash("Bad timing, try again")
    return redirect('/')

def attempt(sub, repo):
    subprocess.run(['git','clone', work[repo]])
    add = subprocess.run(['git', 'submodule', 'add', sub, session['user']], cwd="./"+repo+"/"+session['pd'])
    subprocess.run(['git', 'commit', '-am', "added submodule"], cwd="./"+repo+"/"+session['pd'])
    push = subprocess.run(['git', 'push'], cwd="./"+repo+"/"+session['pd'])
    subprocess.run(['rm', '-rf', repo])
    if add.returncode != 0:
        return 1
    if push.returncode != 0:
        return 2
    return 0

if __name__ == "__main__":
    app.run(host='0.0.0.0')
