CREATE TABLE `LogHeader` (
  `id` int PRIMARY KEY,
  `device_id` int,
  `ip` varchar(255),
  `api_version` float
);

CREATE TABLE `LogDetail` (
  `id` int PRIMARY KEY,
  `headerid` int,
  `user_agent` varchar(255),
  `resolution` varchar(255),
  `current_url` varchar(255),
  `referrer_url` varchar(255),
  `utm_source` varchar(255),
  `utm_medium` varchar(255),
  `collection` varchar(255),
  `email_address` varchar(255),
  `product_id` int,
  `price` float(8,2),
  `currency` varchar(255),
  `recommendation_product_id` int,
  `timestamp` int,
  `local_time` timestamp,
  `is_paypal` boolean,
  `is_added_to_cart` boolean,
  `cart_id` int
);

CREATE TABLE `Product` (
  `product_id` integer PRIMARY KEY
);

CREATE TABLE `Option` (
  `option_id` integer PRIMARY KEY,
  `option_label` varchar(255)
);

CREATE TABLE `ProductOption` (
  `product_id` int,
  `option_id` int,
  PRIMARY KEY (`product_id`, `option_id`)
);

CREATE TABLE `Diamond` (
  `diamond_id` int PRIMARY KEY,
  `diamond_name` varchar(255) COMMENT 'Lấy Value_Labe có toption_labe <> alloy'
);

CREATE TABLE `OptionDiamond` (
  `option_id` int,
  `diamond_id` int,
  PRIMARY KEY (`option_id`, `diamond_id`)
);

CREATE TABLE `Color` (
  `color_id` int PRIMARY KEY,
  `color` varchar(255) COMMENT 'Tách ra từ Alloy Text -> yellow-585 -> Màu Vàng'
);

CREATE TABLE `Metal` (
  `metal_id` int PRIMARY KEY,
  `metal_text` varchar(255) COMMENT 'Tách ra từ Alloy Text -> yellow-585 ->585: Vàng 585 - 14K'
);

CREATE TABLE `OptopnAlloy` (
  `option_id` int,
  `color_id` int,
  `metal_id` int,
  `alloy_text` varchar(255) COMMENT 'Lấy Value_Labe có toption_labe = alloy',
  PRIMARY KEY (`option_id`, `color_id`, `metal_id`)
);

CREATE TABLE `Cart` (
  `cart_id` int,
  `product_id` int,
  `amount` int,
  `price` float(8,2),
  PRIMARY KEY (`cart_id`, `product_id`)
);

ALTER TABLE `LogDetail` ADD FOREIGN KEY (`headerid`) REFERENCES `LogHeader` (`id`);

ALTER TABLE `LogDetail` ADD FOREIGN KEY (`recommendation_product_id`) REFERENCES `Product` (`product_id`);

ALTER TABLE `LogDetail` ADD FOREIGN KEY (`product_id`) REFERENCES `Product` (`product_id`);

ALTER TABLE `ProductOption` ADD FOREIGN KEY (`product_id`) REFERENCES `Product` (`product_id`);

ALTER TABLE `ProductOption` ADD FOREIGN KEY (`option_id`) REFERENCES `Option` (`option_id`);

ALTER TABLE `Cart` ADD FOREIGN KEY (`product_id`) REFERENCES `Product` (`product_id`);

ALTER TABLE `LogDetail` ADD FOREIGN KEY (`cart_id`) REFERENCES `Cart` (`cart_id`);

ALTER TABLE `OptionDiamond` ADD FOREIGN KEY (`option_id`) REFERENCES `Option` (`option_id`);

ALTER TABLE `OptionDiamond` ADD FOREIGN KEY (`diamond_id`) REFERENCES `Diamond` (`diamond_id`);

ALTER TABLE `OptopnAlloy` ADD FOREIGN KEY (`option_id`) REFERENCES `Option` (`option_id`);

ALTER TABLE `OptopnAlloy` ADD FOREIGN KEY (`color_id`) REFERENCES `Color` (`color_id`);

ALTER TABLE `OptopnAlloy` ADD FOREIGN KEY (`metal_id`) REFERENCES `Metal` (`metal_id`);