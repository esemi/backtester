CREATE TABLE `telemetry` (
  `bot_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `tick_number` int unsigned NOT NULL,
  `tick_timestamp` int unsigned NOT NULL,
  `bid` decimal(40,20) NOT NULL,
  `ask` decimal(40,20) NOT NULL,
  `buy_price` decimal(40,20) DEFAULT NULL,
  `sell_price` decimal(40,20) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`bot_name`,`tick_number`),
  KEY `bot_name_tick_timestamp` (`bot_name`,`tick_timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;