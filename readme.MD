# FastAPI Blogs Application

I made this project to get more comfortable with implementing core concepts such as middleware, jwt authentication, and database operations. Now a days, you can just use frameworks such as Django, Spring-boot, or Express to get a lot of these features out of the box. These frameworks are great and I use them all the time, but I wanted to understand how they work under the hood.

With this project I aim to implement the following features:

- [ ] User Authentication
- [ ] Blog CRUD operations
- [ ] Comment CRUD operations
- [ ] Various middleware operations
- [ ] Unit tests (probably)

## Installation

1. Clone the repository
2. Install the dependencies

```bash
pip install -r requirements/local.txt
```

3. Create database

```bash
createdb fastapi_blogs_db
```

4. Set the environment variables

```bash
export DATABASE_URL=postgresql://postgres:password@localhost/fastapi_blogs_db
```

5. Run the application

```bash
uvicorn app.main:app --reload
```

## Database

### To create tables

```bash
psql -U postgres -h localhost -d fastapi_blogs_db -f app/sql/<table_name>.sql
```
