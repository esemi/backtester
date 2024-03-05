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


CREATE TABLE `stats` (
  `bot_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `start_date` datetime NOT NULL,
  `min_open_position_amount_usd` decimal(40,20) NOT NULL,
  `min_open_position_amount_btc` decimal(40,20) NOT NULL,
  `max_open_position_amount_usd` decimal(40,20) NOT NULL,
  `max_open_position_amount_btc` decimal(40,20) NOT NULL,
  `first_open_position_amount_usd` decimal(40,20) NOT NULL,
  `first_open_position_amount_btc` decimal(40,20) NOT NULL,
  `last_rate` decimal(40,20) NOT NULL,
  `buy_total_amount_usd` decimal(40,20) NOT NULL,
  `buy_total_amount_btc` decimal(40,20) NOT NULL,
  `buy_total_qty` decimal(40,20) NOT NULL,
  `buy_without_current_opened_amount_usd` decimal(40,20) NOT NULL,
  `buy_without_current_opened_amount_btc` decimal(40,20) NOT NULL,
  `buy_without_current_opened_qty` decimal(40,20) NOT NULL,
  `sell_without_current_opened_amount_usd` decimal(40,20) NOT NULL,
  `sell_without_current_opened_amount_btc` decimal(40,20) NOT NULL,
  `sell_without_current_opened_qty` decimal(40,20) NOT NULL,
  `dirty_pl_amount_usd` decimal(40,20) NOT NULL,
  `dirty_pl_amount_btc` decimal(40,20) NOT NULL,
  `dirty_pl_percent` decimal(40,20) NOT NULL,
  `account_balance_qty` decimal(40,20) NOT NULL,
  `liquidation_amount_usd` decimal(40,20) NOT NULL,
  `liquidation_amount_btc` decimal(40,20) NOT NULL,
  `liquidation_qty` decimal(40,20) NOT NULL,
  `pl_amount_usd` decimal(40,20) NOT NULL,
  `pl_amount_btc` decimal(40,20) NOT NULL,
  `pl_percent` decimal(40,20) NOT NULL,
  `onhold_amount_usd` decimal(40,20) NOT NULL,
  `onhold_amount_btc` decimal(40,20) NOT NULL,
  `onhold_qty` decimal(40,20) NOT NULL,
  `onhold_tick_number` int unsigned NOT NULL,
  `count_buy_transactions` int unsigned NOT NULL,
  `count_sell_transactions` int unsigned NOT NULL,
  `count_unsuccessful_deals` int unsigned NOT NULL,
  `count_success_deals` int unsigned NOT NULL,
  `max_sell_percent` decimal(40,20) NOT NULL DEFAULT '0.00000000000000000000',
  `max_sell_tick` int unsigned NOT NULL DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`bot_name`),
  KEY `bot_name_created_at` (`bot_name`,`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE `stats` ADD `exchange_balance_qty` decimal(40,20) NOT NULL DEFAULT '0.00000000000000000000' AFTER `account_balance_qty`;
ALTER TABLE `stats` ADD `open_position_average_rate` decimal(40,20) NOT NULL DEFAULT '0.00000000000000000000' AFTER `exchange_balance_qty`;
ALTER TABLE `stats` ADD `xirr` decimal(40,20) NOT NULL DEFAULT '0.00000000000000000000' AFTER `open_position_average_rate`;
ALTER TABLE `stats` ADD `liquidation_qty_left` decimal(40,20) NOT NULL DEFAULT '0.00000000000000000000' AFTER `open_position_average_rate`;