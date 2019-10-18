from flask import Flask, flash, render_template, redirect, session, request
import subprocess, csv, time

app = Flask(__name__)
app.secret_key = "super secret key"

pdlist={
        "systems":['04','05','10'],
        "softdev":['01','02','09']
        }

@app.route("/")
def root():
    return "root"
#systems
@app.route("/systems/")
def syhome():
    return home('systems')

#softdev
@app.route("/softdev/")
def sdhome():
    return home('softdev')

#base
def home(site):
    session['mode'] = site
    if not 'submodule' in session:
        print("Anon@{}: access {}".format(request.remote_addr, site))
        return render_template("login.html",
                pds=pdlist[site])
    with open(site + "Repos.csv", newline='') as csvfile:
        session['work']={}
        reader = csv.DictReader(csvfile)
        for row in reader:
            session['work'][row['name']] = row['ssh']
        print("{}@{}: access {}".format(session['submodule'], request.remote_addr, site))
    return render_template("submission.html",
            assignments=session['work'].keys(),
            submodule=session['submodule'])

@app.route("/auth", methods=['POST'])
def login():
    session['user'] = request.form['user']
    session['email'] = request.form['email']
    if session['user'] == '' or session['email'] == '':
        session['user'] = "Lee-Junhee"
        session['email'] = "junhee.lee002@gmail.com"
    session['submodule'] = request.form['submodule']
    session['pd'] = request.form['pd']
    return redirect('/' + session['mode'])

@app.route('/logout')
def logout():
    print("{}@{}: logout".format(session['submodule'], request.remote_addr))
    del session['submodule']
    return redirect('/' + session['mode'])

@app.route('/submit', methods=['POST'])
def submit():
    if session['submodule'] == "obamaBar":
        msg = "Please change submodule name from default"
    elif not request.form['url'].startswith("https://github.com/"):
        msg = "Please use the HTTPS clone url from github"
    else:
        err = attempt(request.form['url'],request.form['id'])
        print(session['user'] + " created submodule in " + session['pd'] +" linked to "+request.form['url'])
        if err == 0:
            msg = "Sucessfully Created Submodule!"
            with open("log.csv", "a") as log:
                t = time.strftime("%Y-%b-%d %h:%M:%S", localtime())
                log.write("\n" + t +","+ str(request.remote_addr) +","+ session['submodule'] +','+ request.form['id'])
        if err == 1:
            msg = "Submodule failed to create, check information and try again."
        if err == 2:
            msg = "Bad timing, try again"
    print("{}@{}: as {} recieved message \"{}\"".format(session['submodule'], request.remote_addr, session['user'], msg))
    flash(msg)
    return redirect('/' + session['mode'])

def attempt(sub, repo):
    subprocess.run(['git', 'config', '--global', 'user.name', session['user']])
    subprocess.run(['git', 'config', '--global', 'user.email', session['email']])
    subprocess.run(['git','clone', session['work'][repo], repo])
    add = subprocess.run(['git', 'submodule', 'add', sub, session['submodule']], cwd="./"+repo+"/"+session['pd'])
    subprocess.run(['git', 'commit', '-am', "added submodule " + session['submodule']], cwd="./"+repo+"/"+session['pd'])
    push = subprocess.run(['git', 'push'], cwd="./"+repo+"/"+session['pd'])
    subprocess.run(['rm', '-rf', repo])
    if add.returncode != 0:
        return 1
    if push.returncode != 0:
        return 2
    return 0

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
