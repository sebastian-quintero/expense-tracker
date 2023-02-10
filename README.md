# expense-tracker

Track family expenses.

## Usage

Required environment variables:

* `DDBB_USER`=root
* `DDBB_PASSWORD`=`your-unique-password`
* `DDBB_HOST`=localhost
* `DDBB_PORT`=3306

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

* `disc`: discretionary
* `ess`: essential

```bash
curl --location --request POST 'localhost:8000/expense/disc' \
--header 'Content-Type: application/json' \
--data-raw '{
    "date": "2023-02-28 13:00:56",
    "description": "A discretionary expense",
    "value": 30.3
}'
```
