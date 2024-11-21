# Problem Tracker Table Schema

| Column Name                     | Data Type | Constraints   | Description                                                                          |
| ------------------------------- | --------- | ------------- | ------------------------------------------------------------------------------------ |
| **id**                          | SERIAL    | PRIMARY KEY   | Unique identifier for each problem.                                                  |
| **spreadsheet_row_id**          | INT       | UNIQUE        | Unique identifier for the corresponding row in the spreadsheet.                      |
| **problem_name**                | TEXT      | NOT NULL      | Title of the problem.                                                                |
| **problem_type**                | TEXT      | NOT NULL      | Type of problem (e.g., warm-up, arrays, etc.).                                       |
| **difficulty_level**            | TEXT      | NOT NULL      | Difficulty level (easy, medium, hard).                                               |
| **problem_link**                | TEXT      | NOT NULL      | URL link to the problem.                                                             |
| **problem_html_link**           | TEXT      | Optional      | Extracted HTML description and constraints from the problem page.                    |
| **solution_link**               | TEXT      | Optional      | Link to your coded solution.                                                         |
| **completion_time_minutes**     | INTEGER   | Optional      | Time it took to solve the challenge in minutes.                                      |
| **solution_runtime_complexity** | TEXT      | Optional      | Runtime complexity of your coded solution (e.g., O(n)).                              |
| **solution_space_complexity**   | TEXT      | Optional      | Space complexity of your coded solution (e.g., O(1)).                                |
| **complexity_explanation**      | TEXT      | Optional      | What each lettered parameter of the runtime and space complexity functions refer to. |
| **created_at**                  | TIMESTAMP | DEFAULT NOW() | Timestamp when the problem was added to the database.                                |
