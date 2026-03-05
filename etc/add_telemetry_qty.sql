ALTER TABLE `telemetry`
  ADD COLUMN `buy_qty` DECIMAL(40,20) NULL AFTER `sell_price`,
  ADD COLUMN `sell_qty` DECIMAL(40,20) NULL AFTER `buy_qty`;

