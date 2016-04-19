# How to configure OAuth

All OAuth integrations require that you have a "domain" configured.

In addition, you'll need to register an Application with each OAuth partner
(Provider), and update a shared secret in `config.ini`.

## GitHub

Go to Settings -> (select the relevant Organization if applicable) ->
Applications -> Developer Applications -> Register New Application.

The first three fields are public information, and the last one - "Authorization
 callback URL" - is where GitHub will send users after the login. Set it to:

    <protocol>://<domain>/oauth/github/

For example, for SpaceDock.com, it would be `https://spacedock.com/oauth/github/`.

Once you register, you'll get a "Client ID" and "Client Secret"; Set these values
in config.ini as `gh-oauth-id` and `gh-oauth-secret` respectively.

## Google

For google, the domain name has to end with ".com" or something like that, so
testing will be somewhat harder.
(Looks like it does like http://127.0.0.1:8080/, so maybe you're in luck)

Visit https://console.developers.google.com/, and create a new project.

Then:
-> Use Google API
-> (sidenav): Credentials
-> OAuth consent screen
-> Product name
-> [SAVE]
-> (sidenav): Credentials
-> Credentials
-> New Credentials -> OAuth Client ID
-> web application
-> name: spacedock
-> Authorized JavaScript origins: Leave blank
-> Authorized redirect uris: Add these two:

    <protocol>://<domain>/oauth/google/login
    <protocol>://<domain>/oauth/google/connect

Set the Client ID (something-somethingsomething.apps.googleusercontent.com) as
`google-oauth-id` and Client Secret as `google-oauth-secret` in the config.
