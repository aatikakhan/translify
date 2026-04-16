# ERD and SQL Notes

## ERD (Text)

- One `users` record can have many `documents` records.
- Each `documents.user_id` references `users.id`.

## SQL (MySQL Compatible)

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(200) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    source_language VARCHAR(80) NOT NULL DEFAULT 'auto',
    status VARCHAR(40) NOT NULL DEFAULT 'uploaded',
    original_s3_key VARCHAR(500) NOT NULL,
    translated_s3_key VARCHAR(500),
    translated_filename VARCHAR(255),
    error_message TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_documents_user FOREIGN KEY (user_id) REFERENCES users(id)
);
```
