from flask import Flask, render_template, request, url_for, redirect
import sqlite3
import os

app = Flask(__name__)
result = []
profileInfo = []
profileType = ""
articleDetails = []


def convert(data, file_name):
    with open(file_name, 'wb') as file:
        file.write(data)


@app.route('/')
def index():
    global result
    result = []
    return render_template("index.html")


@app.route('/search')
def search():
    global result
    global profileType
    return render_template("Search.html", result=result, profileType=profileType)


@app.route('/searching', methods=['POST'])
def searching():
    def player(row):
        global profileType
        profileType = "player"
        global result
        result = []
        conn = sqlite3.connect('upl.db')
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM player""")
        temp = cursor.fetchall()

        for i in temp:
            if row.lower() in i[1].lower():
                result.append(i)

    def coach(row):
        global profileType
        profileType = "coach"
        global result
        result = []
        conn = sqlite3.connect('upl.db')
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM coach""")
        temp = cursor.fetchall()

        for i in temp:
            if row.lower() in i[1].lower():
                result.append(i)

    def team(row):
        global profileType
        profileType = "team"
        global result
        result = []
        conn = sqlite3.connect('upl.db')
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM team""")
        temp = cursor.fetchall()

        for i in temp:
            if row.lower() in i[1].lower():
                result.append(i)

    to_search = request.form['request']
    search_type = request.form['requestType']

    if search_type == 'players':
        player(to_search)
    elif search_type == 'coaches':
        coach(to_search)
    else:
        team(to_search)

    return redirect(url_for('search'))


@app.route('/profile')
def profile():
    global profileInfo
    if profileInfo[1] == "team":
        return render_template("profileTeam.html", profileInfo=profileInfo)

    return render_template("profilePlayer.html", profileInfo=profileInfo)


@app.route('/profileProcessing', methods=['POST'])
def profile_processing():
    global profileInfo
    profileInfo = []
    profileID = request.form['forProfile']
    temp = profileID.split()
    profileID = temp[0]
    conn = sqlite3.connect('upl.db')
    cursor = conn.cursor()
    if temp[1] == "player":
        query = """SELECT * FROM player WHERE ID = ?"""
    elif temp[1] == "coach":
        query = """SELECT * FROM coach WHERE ID = ?"""
    else:
        query = """SELECT * FROM team WHERE ID = ?"""

    cursor.execute(query, (profileID,))
    profileInfo = cursor.fetchall()

    if profileInfo[0][4]:
        convert(profileInfo[0][4], 'static/images/photo.png')
    elif os.path.exists('static/images/photo.png'):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/images/photo.png')
        os.remove(path)

    if temp[1] == "team":
        profileInfo.append("team")
        return redirect(url_for('profile'))

    cursor = conn.cursor()
    query = """SELECT Name, City, Logo FROM team WHERE ID = ?"""
    temp = cursor.execute(query, (profileInfo[0][5],))
    temp = list(temp)
    temp[0] = list(temp[0])
    if temp[0][2]:
        convert(temp[0][2], 'static/images/clubLogo.png')
    elif os.path.exists('static/images/clubLogo.png'):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/images/clubLogo.png')
        os.remove(path)

    if not (temp[0][1] in temp[0][0]):
        temp[0][0] = str(temp[0][0]) + " " + str(temp[0][1])

    profileInfo += (temp[0][0],)
    return redirect(url_for('profile'))


@app.route('/news')
def news():
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT ID, Date, Title, Preview FROM article""")
    temp = cursor.fetchall()
    temp.append(len(temp))

    cursor.execute("""SELECT Image FROM article ORDER BY ID DESC LIMIT 5""")
    temp_image = cursor.fetchall()

    for i in range(5):
        path = 'static/images/news' + str(i + 1) + '.png'
        convert(temp_image[i][0], path)

    return render_template("Novunu.html", news=temp)


@app.route('/article')
def article():
    global articleDetails
    return render_template("article.html", articleDetails=articleDetails)


@app.route('/articleProcessing', methods=['POST'])
def articleProcessing():
    global articleDetails
    articleDetails = []
    article_id = request.form['forArticle']
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()

    query = """SELECT * FROM article WHERE ID = ?"""
    cursor.execute(query, article_id)
    articleDetails = cursor.fetchall()
    convert(articleDetails[0][3], 'static/images/articleDetails.png')
    return redirect(url_for('article'))


if __name__ == "__main__":
    app.run(debug=True)
