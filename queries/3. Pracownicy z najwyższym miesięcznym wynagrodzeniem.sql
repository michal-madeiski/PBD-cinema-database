SELECT w._id, u.name || ' ' || u.surname , w.salary_month as salary
FROM worker w
JOIN "user" u ON w._id = u._id
ORDER BY salary DESC
LIMIT 10; 