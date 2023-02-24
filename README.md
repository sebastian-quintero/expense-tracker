# expense-tracker

Track expenses and get a report, tallying them up monthly and classifying by
type: essential and non-essential.

This project uses [FastAPI](https://fastapi.tiangolo.com) to stand up a server,
[MySQL](https://dev.mysql.com/doc/refman/8.0/en/) as a database, and
[SQLModel](https://www.google.com/search?client=safari&rls=en&q=sql+tiangolo&ie=UTF-8&oe=UTF-8)
to interact with it. Please make sure you have `mysql` installed and there is a
MySQL server available. You can visit [this
tutorial](https://dev.mysql.com/doc/refman/8.0/en/tutorial.html) to learn more
about standing up a MySQL server.

The server is enabled to interact with [Twilio's WhatsApp
API](https://www.twilio.com/docs/whatsapp/tutorial/requesting-access-to-whatsapp).
It provides a webhook which Twilio can `POST` to, so that it may either record
an expense or create a report.

When standing up the server locally, please visit `localhost:8000/docs` to read
the docs.

## Creating the database and expenses table

In a terminal, connect to the MySQL database server. Once the `mysql>` prompt
is available, you can create the database and table.

Create the database:

```sql
mysql> CREATE DATABASE expenses;
```

Use the database you just created:

```sql
mysql> USE expenses;
```

Create the `expenses` table:

```sql
mysql> CREATE TABLE expenses (
    id INT unsigned NOT NULL AUTO_INCREMENT, 
    date DATETIME NOT NULL,
    type VARCHAR(150) NOT NULL,
    value FLOAT NOT NULL,
    description VARCHAR(150) NOT NULL,
    PRIMARY KEY (id)
);
```

## Run locally

Required environment variables (with sensible defaults):

* `DDBB_USER`=`root` || The user of the database server.
* `DDBB_PASSWORD`=`your-unique-password` || The password for the database server.
* `DDBB_HOST`=`localhost` || The host of the database server.
* `DDBB_PORT`=`3306` || The port of the database server.
* `ALLOWED_FROM`=`+123456789,+57123456789` || Comma-separated `E.164`-formatted
phone numbers allowed as senders for the `twilio` endpoint.

Before running the app, make sure the MySQL database server is running, the
`expenses.expenses` table is created and the environment variables are set.

Run the app:

```bash
uvicorn app.main:server --reload
```

Query the docs. Go to your web browser and visit the following url:
`localhost:8000/docs`.

Perform a health check:

```bash
curl --location --request GET 'localhost:8000' \
--header 'Content-Type: application/json'
```

Record an expense. Please note that the path param can be either:

* `ess`: essential
* `non`: non-essential

```bash
curl --location --request PUT 'localhost:8000/expense/non' \
--header 'Content-Type: application/json' \
--data '{
    "description": "A non-essential expense",
    "value": 45000
}'
```

At this point, new information has been added to the `expenses.expenses` table.
You can query the database directly to look at the recorded information.

Retrieve an expense report.

```bash
curl --location --request GET 'localhost:8000/report'
```

A webhook can be submitted from Twilio. The body can be of the form:

* `<expense_type> <value> <description>`. E.g.: `non 45000 dunkin'donuts`, or `ess
  3500 tax invoice`.
* `report`.

These two messages are equivalent to requesting the `expense` and `report`
endpoints, respectively.

```bash
curl --location --request POST 'localhost:8000/twilio?From=+57123456789&Body=report'
```

Note that the sender in the `From` query param must be authorized in the
`ALLOWED_FROM` environment variable.

## Run with Docker

Build the image.

```bash
docker build -t expense-tracker .
```

Run a container using the image. Notice that a `.env.example` file is provided
with sample environment variables. You should either replace these values or
use a new file, such as a standard `.env`.

```bash
docker run -d --name expense-tracker -p 80:8000 --env-file .env --rm expense-tracker
```

Now you can make all the same requests that were described in the previous
section, but to port `80`. Make sure that there is a database server running in
the same container where the server is being initialized and that the proper
table has been created.

You can see the logs of your container with `docker logs expense-tracker` or
follow them adding the `-f` flag before the container name.
