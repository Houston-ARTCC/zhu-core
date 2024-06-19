![Houston ARTCC](https://i.imgur.com/kvyId31t.png)

# **Virtual Houston ARTCC** Django REST API

![MIT License](https://img.shields.io/badge/Python-3.9-%232D44A4?style=flat)
![MIT License](https://img.shields.io/badge/License-MIT-%232D44A4?style=flat)
![MIT License](https://img.shields.io/badge/Version-v2.0.0-%232D44A4?style=flat)

This repository contains the backend code running the various web services of the Virtual Houston Air Route Traffic Control Center on the VATSIM network. It is published publicly to encourage ARTCCs to collaborate on development and to allow webmasters to use this framework as a base for their own ARTCC websites.

This backend is running on Python 3.9 using the [Django REST Framework](https://www.django-rest-framework.org/). It is designed to be used with a separate frontend component. For an example implementation with React, see https://github.com/Houston-ARTCC/zhu-frontend.

Created by [Michael Romashov](https://romashov.dev).
## Installation
All commands assume that you are at the root of the `zhu-core` repository that you cloned.
1. Ensure you have both Python and pip up to date. (Using a `venv` is recommended)
    ```
    python -m pip install --upgrade pip
    ```

2. Install all project dependencies.
    ```
    pip install -r requirements.txt
    ```

3. Create and populate the `.env` file.
    ```
    cp .env.example .env
    ```

    <details>
    <summary>Environment Field Descriptions</summary>

    *All strings must be surrounded with double quotes. Integers and booleans must be on their own.*
    | Field                               | Description                                                          | Example                |
    | ----------------------------------- | -------------------------------------------------------------------- | ---------------------- |
    | `DEV_ENV`                           |  Enables debug mode. **Must be `False` in production**               | `True`                 |
    | `ALLOWED_HOSTS`                     |  Comma separated list of domains and IPs that the server will run on | `"api.houston.center"` |
    | `SECRET_KEY`                        |  Django secret key. Can be generated [here](https://djecrety.ir/)    |                        |
    | `SENTRY_DSN` **[Optional]**         |  Sentry DSN for error logging                                        |                        |
    | `STATIC_ROOT` **[Optional]**        |  Root directory for static files. Defaults to `./static`             | `"/home/.../static"`   |
    | `MEDIA_ROOT` **[Optional]**         |  Root directory for uploaded files. Defaults to `./media`            | `"/home/.../media"`    |
    | `VATSIM_CONNECT_CLIENT_ID`          |  Client ID for VATSIM Connect                                        |                        |
    | `VATSIM_CONNECT_CLIENT_SECRET`      |  Client Secret for VATSIM Connect                                    |                        |
    | `VATSIM_CONNECT_REDIRECT_URI`       |  Redirect URI for VATSIM Connect                                     |                        |
    | `VATUSA_API_TOKEN`                  |  Token for VATUSA API                                                |                        |
    | `AVWX_API_TOKEN` **[Optional]**     |  [AVWX](https://avwx.rest/) API token for pulling METARs             |                        |
    | `POSITION_PREFIXES`                 |  Comma separated list of all airport IATA codes                      | `"HOU,IAH,AUS"`        |
    | `EMAIL_HOST`                        |  Email server hostname                                               | `"smtp.mailtrap.io"`   |
    | `EMAIL_PORT`                        |  Email server port                                                   | `2525`                 |
    | `EMAIL_HOST_USER`                   |  Email server username                                               | `"username"`           |
    | `EMAIL_HOST_PASSWORD`               |  Email server password                                               | `"password"`           |
    | `EMAIL_USE_TLS`                     |  Use TLS for SMTP                                                    | `True`                 |
    | `EVENTS_WEBHOOK_URL` **[Optional]** |  Discord channel webhook for posting events                          |                        |
    </details>

4. Create database tables.
    ```
    python manage.py migrate
    ```

5. Populate `users_role` table with premade roles.
    ```
    python manage.py loaddata apps/users/fixtures/roles.json
    ```

6. Sync roster with VATUSA api.
    ```
    python manage.py syncroster
    ```

7. Give yourself access to the Django admin panel. (Accessible at `/admin`)
    ```
    python manage.py addadmin
    ```

## Authentication
Authentication with the REST API is done through **JSON Web Tokens**. Please note that JWTs are not encrypted and may contain sensitive information.

After redirecting the user to VATSIM connect, the user will be redirected back to your website with a code from the VATSIM API. (Refer to [VATSIM Connect Documentation](https://github.com/vatsimnetwork/developer-info/wiki/Connect) for more details). This code can be included in the body of a POST request to `/auth/token/` to receive an `access` token and a `refresh` token for the now authenticated user. You will want to keep these tokens for future use.
```ts
axios
    .post('/auth/token/', { code: authCode })
    .then(res => {
        localStorage.setItem('access', res.data.access)
        localStorage.setItem('refresh', res.data.refresh)
    })
```

To authenticate the user for future requests, set the `Authorization` header to `Bearer <access_token>` on all requests bound for the API.
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

For security, the access token will expire 24 hours after being issued. To obtain a new access token, the refresh token retrieved earlier can be included in the body of a POST request to `/auth/token/refresh/`. The refresh token is valid for 30 days after being issued. Once the refresh token expires, the user will have to log in again.
```ts
axios
    .post('/auth/token/refresh/', { refresh: refreshToken })
    .then(res => {
        localStorage.setItem('access', res.data.access)
    })
```


## License
Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

## Contact
Michael Romashov - michael.romashov@vatusa.net
