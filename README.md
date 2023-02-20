# expense-tracker

Track expenses and get a report, tallying them up monthly and classifying by
type: essential and non-essential.

This project uses [FastAPI](https://fastapi.tiangolo.com) to stand up a server
and [MySQL](https://dev.mysql.com/doc/refman/8.0/en/) as a database. Please
make sure you have `mysql` installed and there is a MySQL server available. You
can visit [this
tutorial](https://dev.mysql.com/doc/refman/8.0/en/tutorial.html).

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

Before running the app, make sure the MySQL database server is running, the
`expenses.expenses` table is created and the environment variables are set.

Run the app:

```bash
uvicorn app.main:server --reload
```

Perform a health check:

```bash
curl --location --request GET 'localhost:8000' \
--header 'Content-Type: application/json'
```

Query the docs. Go to your web browser and visit the following url:
`localhost:8000/docs`.

Record an expense. Please note that the path param can be either:

* `ess`: essential
* `non`: non-essential

```bash
curl --location --request POST 'localhost:8000/expense/ess' \
--header 'Content-Type: application/json' \
--data-raw '{
    "description": "An essential expense",
    "value": 303456
}'
```

At this point, new information has been added to the `expenses.expenses` table.
You can query the database directly to look at the recorded information.

Retrieve an expense report.

```bash
curl --location --request GET 'localhost:8000/report'
```

## Run with Docker

Build the image.

```bash
docker build -t expense-tracker .
```

Run a container using the image. Notice that a `.env.example` file is provided
with sample environment variables. You should either replace these values or
use a new file, such as a standard `.env`.

```bash
docker run -d --name expense-tracker -p 8000:8000 --env-file .env --rm expense-tracker
```

Now you can make all the same requests that were described in the previous
section. Make sure that there is a database server running in the same
container where the server is being initialized.
