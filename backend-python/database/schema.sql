-- schema.sql
-- Creates the `customer_support` database and `orders` table,
-- then inserts sample rows from the existing SQLite DB.

CREATE DATABASE IF NOT EXISTS `customer_support`
  DEFAULT CHARACTER SET = utf8mb4
  DEFAULT COLLATE = utf8mb4_unicode_ci;

USE `customer_support`;

CREATE TABLE IF NOT EXISTS `orders` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `order_id` VARCHAR(64) NOT NULL,
  `user_id` VARCHAR(64) NOT NULL,
  `status` VARCHAR(32) NOT NULL,
  `total` DECIMAL(10,2) NOT NULL,
  `created_at` DATETIME(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_order_id` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sample data inserts (5 rows)
INSERT INTO `orders` (`order_id`, `user_id`, `status`, `total`, `created_at`) VALUES
  ('ORD-001','user123','delivered',99.99,'2026-01-14 11:54:02.017069'),
  ('ORD-002','user123','shipped',149.99,'2026-01-21 11:54:02.017069'),
  ('ORD-003','user456','processing',79.99,'2026-01-23 11:54:02.017069'),
  ('ORD-004','user123','cancelled',59.99,'2026-01-09 11:54:02.017069'),
  ('ORD-005','user789','delivered',199.99,'2026-01-04 11:54:02.017069');
