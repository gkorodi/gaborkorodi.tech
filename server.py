"""Python Flask WebApp Auth0 integration example
"""

import json
import datetime
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from bson import ObjectId
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app: Flask = Flask(__name__, static_url_path='/public', static_folder='public')
app.secret_key = env.get("APP_SECRET_KEY")


def time_ago(epoch_value):
    """Jinja filter to display intelligent/user-friendly time"""
    if not epoch_value:
        return 'n/a'
    print(int(epoch_value.strftime('%s')) + 2)
    # print(datetime.strptime(epoch_value,'%s'))

    from_date = datetime.datetime.now()
    to_date = epoch_value  # int(epoch_value.strftime('%s')) #datetime.fromtimestamp(1000 / 1000)
    print(f"{from_date} {epoch_value}")
    dtdiff = abs(from_date - to_date)
    print(dtdiff)

    days = dtdiff.days
    # seconds = dtdiff.seconds
    minutes = int(dtdiff.seconds / 60)
    hours = int(minutes / 60)

    # return f"{days} days and {hours} hours and {minutes} minutes and {seconds} seconds ago"
    if dtdiff.days <= 0:
        if hours <= 0:
            if minutes <= 0:
                return "now"
            return f"{minutes} minutes"
        return f"{hours} hours"
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
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['links']

link_rows = []

# Get 100 random documents from the collection
randos = db['links'].aggregate([{'$sample': {'size': 100}}])
#
# Get one random document matching { yyy: 10} from the `xxx` collection.
# db.xxx.aggregate([{ $match: {yyy: 10}}, { $sample: {size: 1}} ])
for lr in randos:
    lr['host'] = lr['canonicalUrl'].split('/')[2]
    link_rows.append(lr)

def get_settings():
    """Create dictionary with settings data and return it."""
    return {'db': {'host': db_host}, }


# Controllers API
@app.route("/")
def home():
    """Root page for the webapp."""
    # if session.get('user') is None:
    #     return redirect('/public/index.html', 302)

    return render_template(
        "dashboard.html",
        session=session.get("user"),
    )


@app.route("/dashboard")
def dashboard():
    """Show statistics on a Dashboard"""
    return render_template(
        "dashboard.html",
        session=session.get("user"),
    )


@app.route("/stats")
def stats():
    """Return comprehensive statistics as graphs."""
    dbcollection = client['links']['links']
    levels_summary_statistics = dbcollection.aggregate([
        {'$group': {'_id': '$level', 'count': {'$sum': 1}}}
    ])

    level_list = [(f"L{levelStat['_id']}", levelStat['count'])
                  for levelStat in levels_summary_statistics if levelStat['_id'] is not None]
    level_list.sort()
    data = {
        'readCount': 0,
        'acknowledged': 0,
        'inserted_ids': [],
        'total': dbcollection.count_documents({}),
        '_with_level': dbcollection.count_documents({'level': {'$exists': True}}),
        '_missing_canonicalUrl': dbcollection.count_documents({'canonicalUrl': {'$exists': False}}),
        '_missing_unread': dbcollection.count_documents({'unread': {'$exists': False}}),
        '_unread': dbcollection.count_documents({'unread': True}),
        'levels': level_list,
        # dict(map(lambda x: (f"L{x['_id']}", x['count']) if x['_id'] is not 'None' else None , )),
    }
    return data


@app.route("/settings")
def settings():
    """Show basic settings"""
    return render_template(
        "settings.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
        settings=get_settings()
    )


@app.get("/links/<doc_id>")
def links_by_id(doc_id: str):
    """Show individual document by its _id field."""
    dbcollection = client['links']['links']
    return render_template('details.html', session=session.get("user"),
                           doc=dbcollection.find_one({'_id': ObjectId(doc_id)}))


def audit_log(msg) -> bool:
    """Record audit log message in the 'audits' collection."""
    audit_doc = {"type": "audit", "message": msg, "timestamp": datetime.datetime.now().isoformat()}
    resp = client['links']['audits'].insert_one(audit_doc)
    return resp.acknowledged


@app.get("/links/delete/<doc_id>")
def links_delete_by_id(doc_id: str):
    """Delete document by its _id field."""
    dbcollection = client['links']['links']

    doc = dbcollection.find_one({'_id': ObjectId(doc_id)})
    res = dbcollection.delete_one({'_id': ObjectId(doc_id)})

    if res.deleted_count > 0:
        # Record has successfully been deleted.
        # Redirect to list page
        audit_log(f"Document with id: {doc['_id']} and title:'{doc['title']}' has been deleted")
        return redirect(url_for('list_of_docs'))

    # There was an error with deleting.
    return render_template('details.html', errors=['Could not delete document from db'],
                           session=session.get("user"),
                           doc=dbcollection.find_one({'_id': ObjectId(doc_id)}))


@app.route("/profile")
def profile():
    """Show user profile"""
    if session.get('user') is None:
        return redirect(url_for('login'), 302)

    return render_template(
        "profile.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
    )


@app.route("/list")
def list_of_docs():
    """Show a 100 random documents"""
    print(f"showing a 100 row out of {len(link_rows)}")
    return render_template(
        "list.html",
        session=session.get("user"),
        links=link_rows[1:100]
    )


@app.route("/notifications")
def notifications():
    """Show current notifications and alerts"""
    return render_template(
        "notifications.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
    )


@app.route("/callback", methods=["GET", "POST"])
def callback():
    """Callback for Auth0 OAuth workflow"""
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")


@app.route("/login")
def login():
    """Show login page from Auth0 workflow"""
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/logout")
def logout():
    """Logout function, clearing session and redirecting through Aut0"""
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
