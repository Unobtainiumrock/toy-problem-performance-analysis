# Problem Tracker Table Schema

| Column Name                 | Data Type | Constraints                                 | Description                                                                          |
| --------------------------- | --------- | ------------------------------------------- | ------------------------------------------------------------------------------------ |
| id                          | SERIAL    | PRIMARY KEY                                 | Unique identifier for each problem.                                                  |
| spreadsheet_row_id          | INT       | UNIQUE, NOT NULL                            | Unique identifier for the corresponding row in the spreadsheet.                      |
| problem_name                | TEXT      | NOT NULL, DEFAULT 'Unknown Problem'         | Title of the problem.                                                                |
| problem_type                | TEXT      | NOT NULL, DEFAULT 'General'                 | Type of problem (e.g., array, sorting).                                              |
| difficulty_level            | TEXT      | NOT NULL, DEFAULT 'medium'                  | Difficulty level (easy, medium, hard).                                               |
| problem_link                | TEXT      | NOT NULL, DEFAULT 'https://www.google.com'  | URL link to the problem.                                                             |
| problem_html_link           | TEXT      | NOT NULL, DEFAULT 'https://www.google.com'  | HTML representation of the problem description and constraints.                      |
| solution_link               | TEXT      | NOT NULL, DEFAULT 'https://www.google.com'  | Link to your coded solution.                                                         |
| completion_time_minutes     | INTEGER   | NOT NULL, DEFAULT 0                         | Time it took to solve the challenge in minutes.                                      |
| solution_runtime_complexity | TEXT      | NOT NULL, DEFAULT 'Unknown'                 | Runtime complexity of your coded solution (e.g., O(n)).                              |
| solution_space_complexity   | TEXT      | NOT NULL, DEFAULT 'Unknown'                 | Space complexity of your coded solution (e.g., O(1)).                                |
| complexity_explanation      | TEXT      | NOT NULL, DEFAULT 'No explanation provided' | What each lettered parameter of the runtime and space complexity functions refer to. |
| found_optimal_solution      | INTEGER   | NOT NULL, DEFAULT 0                         | Boolean flag indicating if an optimal solution was found (1 for true, 0 for false).  |
| created_at                  | TIMESTAMP | NOT NULL, DEFAULT NOW()                     | Timestamp when the problem was added to the database.                                |
