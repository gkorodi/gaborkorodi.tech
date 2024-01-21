"""Python Flask WebApp Auth0 integration example
"""

import json
from datetime import datetime as datetime
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from bson import ObjectId
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__, static_url_path='/public', static_folder='public')
app.secret_key = env.get("APP_SECRET_KEY")


def time_ago(epoch_value):
    if not epoch_value:
        return 'n/a'
    print(int(epoch_value.strftime('%s')) + 2)
    # print(datetime.strptime(epoch_value,'%s'))

    from_date = datetime.now()
    to_date = epoch_value  # int(epoch_value.strftime('%s')) #datetime.fromtimestamp(1000 / 1000)
    print(f"{from_date} {epoch_value}")
    dtdiff = abs(from_date - to_date)
    print(dtdiff)

    days = dtdiff.days
    seconds = dtdiff.seconds
    minutes = int(dtdiff.seconds / 60)
    hours = int(minutes / 60)

    # return f"{days} days and {hours} hours and {minutes} minutes and {seconds} seconds ago"

    if dtdiff.days <= 0:
        if hours <= 0:
            if minutes <= 0:
                return "now"
            else:
                return f"{minutes} minutes"
        else:
            return f"{hours} hours"
    else:
        return f"{days} days"


app.jinja_env.filters['time_ago'] = time_ago

oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

db_host = env.get('DB_HOST')
db_password = env.get('DB_PASSWORD')
# Source IP needs to be enabled on the MongoDB Atlas connection
uri = f"mongodb+srv://gkorodi:{db_password}@{db_host}/?retryWrites=true&w=majority"
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
link_rows = []
try:
    """Connect to the database, and query the main table"""
    db = client['links']
    links = db['links']

    randos = links.aggregate([{'$sample': {'size': 100}}])
    #
    # // Get
    # one
    # random
    # document
    # matching
    # {a: 10}
    # from the mycoll
    #
    # collection.
    # db.mycoll.aggregate([
    #     { $match: {a: 10}},
    # { $sample: {size: 1}}
    # ])

    for lr in randos:
        lr['host'] = lr['canonicalUrl'].split('/')[2]
        link_rows.append(lr)

except Exception as e:
    print(e)


def getSettings():
    return {'db': {'host': db_host}, }


# Controllers API
@app.route("/")
def home():
    # if session.get('user') is None:
    #     return redirect('/public/index.html', 302)

    return render_template(
        "dashboard.html",
        session=session.get("user"),
    )


@app.route("/dashboard")
def dashboard():
    return render_template(
        "dashboard.html",
        session=session.get("user"),
    )


@app.route("/stats")
def stats():
    dbcollection = client['links']['links']
    levelsStatSummary = dbcollection.aggregate([{'$group': {'_id': '$level', 'count': {'$sum': 1}}}])
    # Notable: https://medium.com/codex/10-python-one-liners-for-lambda-functions-4643bc5a9ea2
    # Notes: https://www.atatus.com/blog/python-converting-lsts-to-dictionaries/
    # Notes; https://medium.com/@BetterEverything/python-one-liner-to-transform-and-filter-lists-382b9c0b85d2
    levelList = [(f"L{e['_id']}", e['count']) for e in levelsStatSummary if e['_id'] is not None]
    levelList.sort()
    data = {
        'readCount': 0,
        'acknowledged': 0,
        'inserted_ids': [],
        'total': dbcollection.count_documents({}),
        '_with_level': dbcollection.count_documents({'level': {'$exists': True}}),
        '_missing_canonicalUrl': dbcollection.count_documents({'canonicalUrl': {'$exists': False}}),
        '_missing_unread': dbcollection.count_documents({'unread': {'$exists': False}}),
        '_unread': dbcollection.count_documents({'unread': True}),
        'levels': levelList,
        # dict(map(lambda x: (f"L{x['_id']}", x['count']) if x['_id'] is not 'None' else None , )),
    }
    return data


@app.route("/settings")
def settings():
    return render_template(
        "settings.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
        settings=getSettings()
    )


@app.get("/links/<id>")
def links_byId(id: str):
    dbcollection = client['links']['links']
    return render_template('details.html', session=session.get("user"),
                           doc=dbcollection.find_one({'_id': ObjectId(id)}))

def auditLog(msg) -> bool:
    auditDoc = {"type": "audit", "message": msg, "timestamp": datetime.utcnow().isoformat()}
    resp = client['links']['audits'].insert_one(auditDoc)
    return resp.acknowledged


@app.get("/links/delete/<id>")
def links_deleteById(id: str):
    dbcollection = client['links']['links']

    doc = dbcollection.find_one({'_id': ObjectId(id)})
    res = dbcollection.delete_one({'_id': ObjectId(id)})

    if res.deleted_count > 0:
        # Record has successfully been deleted.
        # Redirect to list page
        auditLog(f"Document with id: {doc['_id']} and title:'{doc['title']}' has been deleted")
        return redirect(url_for('list'))
    else:
        # There was an error with deleting.
        return render_template('details.html', errors=['Could not delete document from db'],
                               session=session.get("user"),
                               doc=dbcollection.find_one({'_id': ObjectId(id)}))


@app.route("/profile")
def profile():
    if session.get('user') is None:
        return redirect(url_for('login'), 302)

    return render_template(
        "profile.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
    )


@app.route("/list")
def list():
    print(f"showing a 100 row out of {len(link_rows)}")
    return render_template(
        "list.html",
        session=session.get("user"),
        links=link_rows[1:100]
    )


@app.route("/notifications")
def notifications():
    return render_template(
        "notifications.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
    )


@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")


@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))
