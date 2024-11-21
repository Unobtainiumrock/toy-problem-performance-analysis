from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
import logging
import os
from dotenv import load_dotenv
from pydantic import Field

logging.basicConfig(level=logging.ERROR)
load_dotenv()

app = FastAPI()

# Connection pool
pool = None
try:
    pool = SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )
    if pool:
        logging.info("Database connection pool created successfully.")
except Exception as e:
    logging.error(f"Failed to create connection pool: {e}")
    raise HTTPException(status_code=500, detail="Database connection pool creation failed.")


# Get connection from pool
def get_db_connection():
    try:
        if not pool:
            raise HTTPException(status_code=500, detail="Connection pool is not initialized.")
        return pool.getconn()
    except psycopg2.Error as e:
        logging.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Unable to connect to the database.")


# Release connection back to pool
def release_db_connection(conn):
    if pool and conn:
        pool.putconn(conn)


# Data model
class Problem(BaseModel):
    spreadsheet_row_id: int = Field(..., gt=0, description="Row ID must be a positive integer")
    problem_name: str
    problem_type: str
    difficulty_level: str
    problem_link: str
    problem_html_link: str = None
    solution_link: str = None
    completion_time_minutes: int = Field(None, ge=0, description="Completion time must be non-negative")
    solution_runtime_complexity: str = None
    solution_space_complexity: str = None
    complexity_explanation: str = None


@app.post("/problems/")
def add_problem(problem: Problem):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO problems 
            (spreadsheet_row_id, problem_name, problem_type, difficulty_level, problem_link, 
             problem_html_link, solution_link, completion_time_minutes, 
             solution_runtime_complexity, solution_space_complexity, complexity_explanation)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (
                problem.spreadsheet_row_id,
                problem.problem_name,
                problem.problem_type,
                problem.difficulty_level,
                problem.problem_link,
                problem.problem_html_link,
                problem.solution_link,
                problem.completion_time_minutes if problem.completion_time_minutes is not None else 0,
                problem.solution_runtime_complexity,
                problem.solution_space_complexity,
                problem.complexity_explanation,
            )
        )
        problem_id = cur.fetchone()[0]
        conn.commit()
        return {"id": problem_id}
    except Exception as e:
        conn.rollback()
        logging.error(f"Error occurred in POST /problems/: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        release_db_connection(conn)


@app.get("/problems/")
def list_problems(difficulty_level: str = None, problem_type: str = None):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        query = "SELECT * FROM problems WHERE 1=1"  # Base query
        params = []
        if difficulty_level:
            query += " AND difficulty_level = %s"
            params.append(difficulty_level)
        if problem_type:
            query += " AND problem_type = %s"
            params.append(problem_type)

        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        return rows
    except Exception as e:
        logging.error(f"Error occurred in GET /problems/: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve problems.")
    finally:
        cur.close()
        release_db_connection(conn)


@app.get("/problems/{problem_id}")
def get_problem(problem_id: int):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT * FROM problems WHERE id = %s;", (problem_id,))
        row = cur.fetchone()
        if row:
            return row
        else:
            raise HTTPException(status_code=404, detail="Problem not found")
    except Exception as e:
        logging.error(f"Error occurred in GET /problems/{problem_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        release_db_connection(conn)


@app.get("/problems/search/")
def search_problems(problem_name: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(
            """
            SELECT * FROM problems
            WHERE problem_name ILIKE %s;
            """,
            (f"%{problem_name}%",)
        )
        rows = cur.fetchall()
        if rows:
            return rows
        else:
            raise HTTPException(status_code=404, detail="Problem not found")
    except Exception as e:
        logging.error(f"Error occurred in GET /problems/search/: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        release_db_connection(conn)
