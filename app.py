from flask import Flask, render_template, request, redirect
import statistics, json, os

app = Flask(__name__)

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

etudiants = load_data()

def calcul_stats(etudiants):
    if len(etudiants) < 2:
        return 0, 0, 0

    x = [e['heures'] for e in etudiants]
    y = [e['moyenne'] for e in etudiants]

    mx = statistics.mean(x)
    my = statistics.mean(y)

    cov = sum((xi-mx)*(yi-my) for xi, yi in zip(x,y))
    varx = sum((xi-mx)**2 for xi in x)

    if varx == 0:
        return 0,0,0

    a = cov / varx
    b = my - a*mx

    vary = sum((yi-my)**2 for yi in y)
    r = 0 if varx*vary == 0 else cov / ((varx*vary)**0.5)

    return round(r,2), round(a,2), round(b,2)

# 🧠 CONSEILS INTELLIGENTS
def generer_conseils(data, r):
    if not data:
        return ["Ajoute des étudiants pour voir les conseils"]

    conseils = []

    if r > 0.7:
        conseils.append("Augmenter les heures améliore fortement les résultats")
    elif r > 0.3:
        conseils.append("Les heures influencent modérément la moyenne")
    else:
        conseils.append("Les heures seules n'expliquent pas les résultats")

    for e in data:
        if e['heures'] < 3 and e['moyenne'] >= 12:
            conseils.append(f"{e['nom']} réussit bien avec peu d'effort 👍")
        elif e['heures'] > 6 and e['moyenne'] < 10:
            conseils.append(f"{e['nom']} travaille beaucoup mais doit changer de méthode ⚠️")
        elif e['heures'] < 3 and e['moyenne'] < 10:
            conseils.append(f"{e['nom']} doit étudier plus 📚")

    return conseils

@app.route('/', methods=['GET','POST'])
def index():
    global etudiants

    if request.method == 'POST':
        etudiants.append({
            'nom': request.form['nom'],
            'filiere': request.form['filiere'],
            'heures': float(request.form['heures']),
            'moyenne': float(request.form['moyenne'])
        })
        save_data(etudiants)
        return redirect('/')

    search = request.args.get('search','').lower()
    filiere = request.args.get('filiere','')

    data = etudiants

    if search:
        data = [e for e in data if search in e['nom'].lower()]

    if filiere:
        data = [e for e in data if e['filiere'] == filiere]

    heures = [e['heures'] for e in data]
    moyennes = [e['moyenne'] for e in data]
    noms = [e['nom'] for e in data]

    if data:
        moyenne = round(statistics.mean(moyennes),2)
        meilleur = max(data, key=lambda x:x['moyenne'])
        pire = min(data, key=lambda x:x['moyenne'])
        r,a,b = calcul_stats(data)
    else:
        moyenne = 0
        meilleur = None
        pire = None
        r,a,b = 0,0,0

    conseils = generer_conseils(data, r)

    filieres = list(set([e['filiere'] for e in etudiants]))

    return render_template(
        "index.html",
        etudiants=data,
        moyenne=moyenne,
        meilleur=meilleur,
        pire=pire,
        r=r,a=a,b=b,
        heures=heures,
        moyennes=moyennes,
        noms=noms,
        filieres=filieres,
        conseils=conseils
    )

if __name__ == "__main__":
    app.run()
