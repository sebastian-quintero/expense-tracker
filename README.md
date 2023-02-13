# expense-tracker

Track family expenses.

## Run locally

Required environment variables (with sensible defaults):

* `DDBB_USER`=`root`
* `DDBB_PASSWORD`=`your-unique-password`
* `DDBB_HOST`=`localhost`
* `DDBB_PORT`=`3306`

Run the server:

```bash
uvicorn main:app --reload
```

Perform a health check:

```bash
curl --location --request GET 'localhost:8000' \
--header 'Content-Type: application/json'
```

Record an expense. Please note that the path param can be either:

* `ess`: essential
* `non`: non-essential

```bash
curl --location --request POST 'localhost:8000/expense/ess' \
--header 'Content-Type: application/json' \
--data-raw '{
    "date": "2023-02-28 13:00:56",
    "description": "An essential expense",
    "value": 303456
}'
```

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

You can follow the logs of the container.

```bash
docker logs -f expense-tracker
```

Now you can make requests to `0.0.0.0:8000`.
