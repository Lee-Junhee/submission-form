from flask import Flask, flash, render_template, redirect, session, request
import subprocess, csv

app = Flask(__name__)
app.secret_key = "hi" 

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
    attempt(request.form['url'],request.form['id'])
    flash("Sucessfully Created Submodule!")
    return redirect('/')

def attempt(sub, repo):
    error = None
    subprocess.run(['git','clone', work[repo]])
    subprocess.run(['git', 'submodule', 'add', sub, session['user']], cwd="./"+repo+"/"+session['pd'])
    subprocess.run(['git', 'commit', '-am', "added submodule"], cwd="./"+repo+"/"+session['pd'])
    subprocess.run(['git', 'push'], cwd="./"+repo+"/"+session['pd'])
    subprocess.run(['rm', '-rf', repo])
    

if __name__ == "__main__":
    app.debug = True
    app.run()
