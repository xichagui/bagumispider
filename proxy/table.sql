CREATE TABLE if not EXISTS `proxy_ip` (
    `id` int(10) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `address` varchar (50) NOT NULL DEFAULT '0',
    `http_type` int(10) unsigned NOT NULL DEFAULT 0,
    `timeout_times` int(10) unsigned NOT NULL DEFAULT 0,
    `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;