# Auth0 Python Web App Sample

This sample demonstrates how to add authentication to a Python web app using Auth0.

# Running the App

To run the sample, make sure you have `python3` and `pip` installed.

Rename `.env.example` to `.env` and populate it with the client ID, domain, secret, callback URL and audience for your
Auth0 app. If you are not implementing any API you can use `https://YOUR_DOMAIN.auth0.com/userinfo` as the audience.
Also, add the callback URL to the settings section of your Auth0 client.

Register `http://localhost:3000/callback` as `Allowed Callback URLs` and `http://localhost:3000`
as `Allowed Logout URLs` in your client settings.

Run `pip install -r requirements.txt` to install the dependencies and run `python server.py`.
The app will be served at [http://localhost:3000/](http://localhost:3000/).

# Running the App with Docker

To run the sample, make sure you have `docker` installed.

To run the sample with [Docker](https://www.docker.com/), make sure you have `docker` installed.

Rename the .env.example file to .env, change the environment variables, and register the URLs as explained [previously](#running-the-app).

Run `sh exec.sh` to build and run the docker image in Linux or run `.\exec.ps1` to build
and run the docker image on Windows.

## What is Auth0?

Auth0 helps you to:

* Add authentication with [multiple authentication sources](https://auth0.com/docs/identityproviders),
either social like **Google, Facebook, Microsoft Account, LinkedIn, GitHub, Twitter, Box, Salesforce, among others**,or
enterprise identity systems like **Windows Azure AD, Google Apps, Active Directory, ADFS or any SAML Identity Provider**.
* Add authentication through more traditional **[username/password databases](https://docs.auth0.com/mysql-connection-tutorial)**.
* Add support for **[linking different user accounts](https://auth0.com/docs/link-accounts)** with the same user.
* Support for generating signed [JSON Web Tokens](https://auth0.com/docs/jwt) to call your APIs and
**flow the user identity** securely.
* Analytics of how, when and where users are logging in.
* Pull data from other sources and add it to the user profile, through [JavaScript rules](https://auth0.com/docs/rules).

## Create a free account in Auth0

1. Go to [Auth0](https://auth0.com) and click Sign Up.
2. Use Google, GitHub or Microsoft Account to log in.

## Issue Reporting

If you have found a bug or if you have a feature request, please report them at this repository issues section.
Please do not report security vulnerabilities on the public GitHub issue tracker.
The [Responsible Disclosure Program](https://auth0.com/whitehat) details the procedure for disclosing security issues.

## Author

[Auth0](https://auth0.com)

## License

This project is licensed under the MIT license. 

# DevOps steps

Always run `pylint $(git ls-files '*.py')` on the code, because that is what GitHub `Pylint` action does.

# Notes

https://medium.com/codex/10-python-one-liners-for-lambda-functions-4643bc5a9ea2

https://www.atatus.com/blog/python-converting-lsts-to-dictionaries/

https://medium.com/@BetterEverything/python-one-liner-to-transform-and-filter-lists-382b9c0b85d2

## Environment

### Setup

The `.env` file stores all secret and settings information, which is not included in the repo. Needs to be created
per server and per environment.

An example `.env` file can be created from the below template

AUTH0_CLIENT_ID=<CLIENT_ID_FOR_AUTH0_APPLICATION>
AUTH0_CLIENT_SECRET=<CLIENT_SECRET_FOR_AUTH0_APPLICATION>
AUTH0_DOMAIN="<DOMAIN_FOR_AUTH0_APPLICATION>"
APP_SECRET_KEY="<FLASK_APPLICATION_SECRET_CODE>"
DB_HOST="<DB_HOST_DNS_NAME>"
DB_PASSWORD="<DB_PASSWORD>"
DB_USER="<DB_USERNAME>"

