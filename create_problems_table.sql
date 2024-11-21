CREATE TABLE problems (
    id SERIAL PRIMARY KEY,                                                   -- Unique database identifier
    spreadsheet_row_id INT UNIQUE NOT NULL,                                  -- Row index from the spreadsheet (unique)
    problem_name TEXT NOT NULL DEFAULT 'Unknown Problem',                    -- Problem name
    problem_type TEXT NOT NULL DEFAULT 'General',                            -- Problem type (e.g., array, sorting)
    difficulty_level TEXT NOT NULL DEFAULT 'medium',                         -- Difficulty level (e.g., easy, medium)
    problem_link TEXT NOT NULL DEFAULT 'https://www.google.com',             -- Link to the problem
    problem_html_link TEXT NOT NULL DEFAULT 'https://www.google.com',        -- HTML representation of the problem
    solution_link TEXT NOT NULL DEFAULT 'https://www.google.com',            -- Link to the solution
    completion_time_minutes INTEGER NOT NULL DEFAULT 0,                      -- Time to complete the problem
    solution_runtime_complexity TEXT NOT NULL DEFAULT 'Unknown',             -- Runtime complexity of the solution
    solution_space_complexity TEXT NOT NULL DEFAULT 'Unknown',               -- Space complexity of the solution
    complexity_explanation TEXT NOT NULL DEFAULT 'No explanation provided',  -- Explanation of the complexity
    created_at TIMESTAMP NOT NULL DEFAULT NOW()                              -- Timestamp for row creation
);
