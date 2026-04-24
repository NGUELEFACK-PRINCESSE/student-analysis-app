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
        json.dump(data, f, indent=4)

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

# 🔥 LONG + SOLID + MOTIVATING ADVICE
def generer_conseils(data, r):
    if not data:
        return ["Start by adding students. The system will then generate a complete and personalized study strategy."]

    conseils = []

    # ===== GLOBAL ANALYSIS =====
    if r > 0.7:
        conseils.append(
            "There is a strong relationship between study time and performance. "
            "Students who study more tend to perform better. However, this only works if the study time is used effectively. "
            "Consistency is essential: studying every day, even for a short time, is far more effective than studying many hours only before exams."
        )
    elif r > 0.3:
        conseils.append(
            "There is a moderate relationship between study time and performance. "
            "This means that study time helps, but the method used is also very important. "
            "Students should focus not only on studying more, but on studying better using active techniques."
        )
    else:
        conseils.append(
            "There is a weak relationship between study time and performance. "
            "This means that studying more is not enough. Students must improve their learning strategy by practicing, understanding deeply, "
            "and avoiding passive reading."
        )

    # ===== INDIVIDUAL ANALYSIS =====
    for e in data:
        nom = e['nom']
        h = e['heures']
        m = e['moyenne']

        conseils.append(f"----- {nom} -----")
        conseils.append(f"Current level: {m}/20 with {h} hours of study.")

        if m >= 14:
            conseils.append(
                "You are already performing very well. To go even further, you should challenge yourself with harder exercises and past exam questions. "
                "Try to explain lessons to others, as teaching improves understanding. Stay consistent and avoid becoming overconfident."
            )

        elif h >= 6 and m < 10:
            conseils.append(
                "You study a lot, but your results are still low. This usually means your study method is not effective. "
                "Instead of just reading, you should practice exercises, test yourself without notes, and focus on topics you do not understand. "
                "Quality of study is more important than quantity."
            )

        elif h < 3 and m < 10:
            conseils.append(
                "Your study time is too low to achieve good results. You need to increase your study time gradually, for example by adding 1–2 hours per day. "
                "Create a fixed schedule and study every day. Start with difficult subjects when your concentration is highest."
            )

        elif h < 3 and m >= 12:
            conseils.append(
                "You achieve good results with little study time, which shows efficiency. However, this can be risky in the long term. "
                "To maintain your level, you should study more regularly and review lessons consistently."
            )

        else:
            conseils.append(
                "Your performance is average. To improve, increase your study time slightly and use active learning methods. "
                "Review lessons after class, practice regularly, and focus on your weak areas."
            )

    # ===== GENERAL STUDY STRATEGY =====
    conseils.append(
        "GENERAL STRATEGY: Create a weekly study plan and follow it consistently. "
        "Study at the same time every day to build discipline."
    )

    conseils.append(
        "STUDY METHOD: Avoid passive reading. Practice exercises, summarize lessons, and test yourself regularly."
    )

    conseils.append(
        "FOCUS: Study in sessions of 45–60 minutes with short breaks. Remove distractions like phones and social media."
    )

    conseils.append(
        "MEMORY: Review lessons multiple times (after 1 day, 3 days, and 1 week) to improve retention."
    )

    conseils.append(
        "EXAMS: Practice past exams and analyze your mistakes carefully to improve faster."
    )

    conseils.append(
        "MINDSET: Success comes from consistency and discipline. Small daily efforts lead to big results over time."
    )

    return conseils

@app.route('/', methods=['GET','POST'])
def index():

    etudiants = load_data()

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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
