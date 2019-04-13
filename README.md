# Auth service for MoinMoin

A simple auth provider for the MoinMoin wiki.


## Installation

1. Copy the ```authService.py``` file to your MoinMoin plugins (in actions) directory. E.g. ```/var/lib/wiki/data/plugin/action```.
1. Add the psk into the wiki configuration: ```auth_service_token = 'your secret toekn'```

## API

Every request must be a the http method `POST`. For authentication you must provide the header 'Auth-Token' with the correct psk (defined in `auth_service_token`). If you send data, you must use the content-type `application/json`.

Use the following URL template:
```
<wiki domain>/?action=authService&do=<action>
```
You can use any wiki page, but I recommend the main page. `<action>` must be one of the following:

* __list__ - get a list of all users. Returns:
```json
[{"login": "...", "email": "..."}, ... ]
```
* __loginCheck__ - check if a user with the given password exists.
Parameter:
```json
{
  "login": "...",
  "password": "..."
}
```
Returns:
```json
{"result": "$RESULT$"}
```
$RESULT$ is one of `ok`, `unknown_user`, `wrong_password`.
* __isInGroup__ - check if a group contains a specific user.
Parameter:
```json
{
  "login": "...",
  "group": "..."
}
```
Returns:
```json
{"inGroup": true/false}
```

### Example with curl

List user
```bash
curl -v -X POST -H 'Auth-Token: $PSK$' "https://$DOMAIN$/?action=authService&do=list"
```

Check Login
```bash
curl -v -X POST -H 'Auth-Token: $PSK$' -H 'Content-Type: application/json' -d '{"login": "...","password": "=B%r+xS5ZA$y"}' "https://$DOMAIN$/?action=authService&do=loginCheck"
```

Is in Group?
```bash
curl -v -X POST -H 'Auth-Token: $PSK$' -H 'Content-Type: application/json' -d '{"login": "...","group": "..."}' "https://$DOMAIN$/?action=authService&do=isInGroup"
```