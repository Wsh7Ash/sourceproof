import sqlite3


def route_upload(request):
    name = request.args["name"]
    return store_file(name)


def store_file(name):
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO files (name) VALUES ('%s')" % name)
    conn.commit()
    return True
