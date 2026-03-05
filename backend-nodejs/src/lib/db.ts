import {createPool} from 'mysql2/promise';


const {
    MYSQL_HOST='localhost',
    MYSQL_USER='root',
    MYSQL_PASSWORD='',
    MYSQL_DATABASE,
    MYSQL_CONNECTION_LIMIT='10',
    MYSQL_PORT='3306'
} = process.env;
if(!MYSQL_DATABASE){
    throw new Error('MYSQL_DATABASE environment variable is required');
}

export const pool = createPool({
    host: MYSQL_HOST,
    user: MYSQL_USER,
    password: MYSQL_PASSWORD,
    database: MYSQL_DATABASE,
    connectionLimit: parseInt(MYSQL_CONNECTION_LIMIT, 10),
    port: Number(MYSQL_PORT),
    waitForConnections: true,
    timezone: 'Z'

});

export async function ensureSchema(){
    const adminPool = createPool({
    host: MYSQL_HOST,
    user: MYSQL_USER,
    password: MYSQL_PASSWORD,
    port: Number(MYSQL_PORT),
    waitForConnections: true,
    connectionLimit: 1,
    timezone: 'Z'
    });

    try{
        await adminPool.execute(
            `CREATE DATABASE IF NOT EXISTS ${MYSQL_DATABASE} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci`
        );
    }finally {
        await adminPool.end();
    }

    await pool.execute(
        `CREATE TABLE IF NOT EXISTS users (
            id char(36) not null PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            name VARCHAR(100),
            created_at TIMESTAMP not null DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP not null DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci`
    );
    await pool.execute(
        `CREATE TABLE IF NOT EXISTS password_reset_tokens(
            id char(36) not null PRIMARY KEY,
            user_id char(36) not null,
            token VARCHAR(255) NOT NULL UNIQUE,
            expires_at datetime NOT NULL,
            used_at datetime null,
            created_at TIMESTAMP not null DEFAULT CURRENT_TIMESTAMP,
            constraint fk_reset_user foreign key (user_id) references users(id) on delete cascade
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci`
    );


    await pool.execute(`
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
        id char(36) not null primary key,
        user_id char(36) not null,
        token VARCHAR(255) NOT NULL UNIQUE,
        expires_at datetime NOT NULL,
        used_at datetime null,
        created_at TIMESTAMP not null DEFAULT CURRENT_TIMESTAMP,
        constraint fk_reset_user foreign key (user_id) references users(id) on delete cascade
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci`
    );


    await pool.execute(`
        CREATE TABLE IF NOT EXISTS orders (
  id INT NOT NULL AUTO_INCREMENT primary key,
  order_id VARCHAR(64) NOT NULL unique key,
  user_id VARCHAR(64) NOT NULL,
  status VARCHAR(32) NOT NULL,
  total DECIMAL(10,2) NOT NULL,
  created_at DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
`);

    // Check if table is empty before inserting sample data
    const [rows] = await pool.execute<any[]>('SELECT COUNT(*) as count FROM orders');
    if (rows[0].count === 0) {
        await pool.execute(`
            INSERT INTO orders (order_id, user_id, status, total, created_at) VALUES
          ('ORD-001','user123','delivered',99.99,'2026-01-14 11:54:02.017069'),
          ('ORD-002','user123','shipped',149.99,'2026-01-21 11:54:02.017069'),
          ('ORD-003','user456','processing',79.99,'2026-01-23 11:54:02.017069'),
          ('ORD-004','user123','cancelled',59.99,'2026-01-09 11:54:02.017069'),
          ('ORD-005','user789','delivered',199.99,'2026-01-04 11:54:02.017069')
        `);
    }
}
