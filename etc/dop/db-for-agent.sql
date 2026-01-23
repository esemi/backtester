-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Хост: localhost
-- Время создания: Янв 09 2026 г., 11:37
-- Версия сервера: 8.0.41-0ubuntu0.22.04.1
-- Версия PHP: 8.2.17

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- База данных: `thesim`
--

-- --------------------------------------------------------

--
-- Структура таблицы `stats`
--

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
  `exchange_balance_qty` decimal(40,20) NOT NULL DEFAULT '0.00000000000000000000',
  `open_position_average_rate` decimal(40,20) NOT NULL DEFAULT '0.00000000000000000000',
  `last_24h_success_deals` int UNSIGNED NOT NULL DEFAULT '0',
  `liquidation_qty_left` decimal(40,20) NOT NULL DEFAULT '0.00000000000000000000',
  `xirr` decimal(40,20) NOT NULL DEFAULT '0.00000000000000000000',
  `liquidation_amount_usd` decimal(40,20) NOT NULL,
  `liquidation_amount_btc` decimal(40,20) NOT NULL,
  `liquidation_qty` decimal(40,20) NOT NULL,
  `pl_amount_usd` decimal(40,20) NOT NULL,
  `pl_amount_btc` decimal(40,20) NOT NULL,
  `pl_percent` decimal(40,20) NOT NULL,
  `onhold_amount_usd` decimal(40,20) NOT NULL,
  `onhold_amount_btc` decimal(40,20) NOT NULL,
  `onhold_qty` decimal(40,20) NOT NULL,
  `onhold_tick_number` int UNSIGNED NOT NULL,
  `count_buy_transactions` int UNSIGNED NOT NULL,
  `count_sell_transactions` int UNSIGNED NOT NULL,
  `count_unsuccessful_deals` int UNSIGNED NOT NULL,
  `count_success_deals` int UNSIGNED NOT NULL,
  `max_sell_percent` decimal(40,20) NOT NULL DEFAULT '0.00000000000000000000',
  `max_sell_tick` int UNSIGNED NOT NULL DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `invest_body` decimal(40,20) NOT NULL DEFAULT '0.00000000000000000000'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Триггеры `stats`
--
DELIMITER $$
CREATE TRIGGER `on_delete` AFTER DELETE ON `stats` FOR EACH ROW INSERT INTO stats_prev (bot_name, date_time, count_buy_transactions, count_sell_transactions) VALUES (old.bot_name, NOW(), old.count_buy_transactions, old.count_sell_transactions) ON DUPLICATE KEY UPDATE date_time = NOW(), count_buy_transactions=old.count_buy_transactions, count_sell_transactions=old.count_sell_transactions
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `on_insert` BEFORE INSERT ON `stats` FOR EACH ROW BEGIN
    DECLARE count_buy INT;
    DECLARE count_sell INT;
    
    SELECT count_buy_transactions, count_sell_transactions INTO count_buy, count_sell 
    FROM stats_prev 
    WHERE bot_name = NEW.bot_name;
    
    IF count_buy != NEW.count_buy_transactions OR count_sell != NEW.count_sell_transactions THEN
        INSERT INTO bot_stats
SET 
bot_name = NEW.bot_name,
date_time = NOW(),
start_date = new.start_date,
first_open_position_amount = new.first_open_position_amount_usd,
last_rate = new.last_rate,
buy_total_amount = new.buy_total_amount_usd,
buy_total_qty = new.buy_total_qty,
sell_without_current_opened_amount = new.sell_without_current_opened_amount_usd,
sell_without_current_opened_qty = new.sell_without_current_opened_qty,
dirty_pl_amount = new.dirty_pl_amount_usd,
dirty_pl_percent = new.dirty_pl_percent,
account_balance_qty = new.account_balance_qty,
exchange_balance_qty = new.exchange_balance_qty,
open_position_average_rate = new.open_position_average_rate,
last_24h_success_deals = new.last_24h_success_deals,
xirr = new.xirr,
liquidation_amount = new.liquidation_amount_usd,
liquidation_qty = new.liquidation_qty,
count_buy_transactions = new.count_buy_transactions,
count_sell_transactions = new.count_sell_transactions,
count_unsuccessful_deals = new.count_unsuccessful_deals,
count_success_deals = new.count_success_deals,
max_sell_percent = new.max_sell_percent,
invest_body = new.invest_body,
order_id = 1;
    END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Структура таблицы `stats_prev`
--

CREATE TABLE `stats_prev` (
  `bot_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `date_time` datetime NOT NULL,
  `count_buy_transactions` int UNSIGNED NOT NULL,
  `count_sell_transactions` int UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `telemetry`
--

CREATE TABLE `telemetry` (
  `id` bigint UNSIGNED NOT NULL,
  `bot_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `tick_number` int UNSIGNED NOT NULL,
  `tick_timestamp` int UNSIGNED NOT NULL,
  `bid` decimal(40,20) NOT NULL,
  `ask` decimal(40,20) NOT NULL,
  `buy_price` decimal(40,20) DEFAULT NULL,
  `sell_price` decimal(40,20) DEFAULT NULL,
  `dirty_pl_amount` decimal(40,20) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `buy_fee_qty` decimal(40,20) DEFAULT NULL,
  `buy_fee_ticker` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sell_fee_qty` decimal(40,20) DEFAULT NULL,
  `sell_fee_ticker` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `stats`
--
ALTER TABLE `stats`
  ADD PRIMARY KEY (`bot_name`),
  ADD KEY `bot_name_created_at` (`bot_name`,`created_at`),
  ADD KEY `created_at` (`created_at`);

--
-- Индексы таблицы `stats_prev`
--
ALTER TABLE `stats_prev`
  ADD PRIMARY KEY (`bot_name`),
  ADD KEY `date_time` (`date_time`);

--
-- Индексы таблицы `telemetry`
--
ALTER TABLE `telemetry`
  ADD PRIMARY KEY (`bot_name`,`tick_number`),
  ADD UNIQUE KEY `id_unique` (`id`),
  ADD KEY `bot_name_tick_timestamp` (`bot_name`,`tick_timestamp`),
  ADD KEY `tick_number` (`tick_number`),
  ADD KEY `tick_timestamp` (`tick_timestamp`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `telemetry`
--
ALTER TABLE `telemetry`
  MODIFY `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
