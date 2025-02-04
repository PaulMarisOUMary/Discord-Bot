START TRANSACTION;


CREATE TABLE IF NOT EXISTS `table_birthday`
(
    `guild_id`          BIGINT UNSIGNED NOT NULL,
    `user_id`           BIGINT UNSIGNED NOT NULL,
    `user_birth`        DATE NOT NULL,
CONSTRAINT `me_per_guild` UNIQUE (`guild_id`, `user_id`)
)
ENGINE = InnoDB,
DEFAULT CHARACTER SET utf8mb4,
COLLATE utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS `table_croissants`
(
    `user_id`           BIGINT UNSIGNED NOT NULL,
    `user_count`        SMALLINT UNSIGNED,
UNIQUE(`user_id`)
)
ENGINE = InnoDB,
DEFAULT CHARACTER SET utf8mb4,
COLLATE utf8mb4_unicode_ci;


-- CREATE TABLE IF NOT EXISTS `table_fridaycake`
-- (
--   `user_isin` tinyint(1) NOT NULL,
--   `user_id` bigint(20) UNSIGNED NOT NULL,
--   `user_name` VARCHAR(32) NOT NULL
-- UNIQUE(`user_id`)
-- )
-- ENGINE = InnoDB,
-- DEFAULT CHARACTER SET utf8mb4,
-- COLLATE utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS `table_invite`
(
    `guild_id`           BIGINT UNSIGNED NOT NULL,
    `channel_id`         BIGINT UNSIGNED NOT NULL,
    `custom_message`     VARCHAR(4096),
UNIQUE(`guild_id`)
)
ENGINE = InnoDB,
DEFAULT CHARACTER SET utf8mb4,
COLLATE utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS `table_me`
(
    `guild_id`          BIGINT UNSIGNED NOT NULL,
    `user_id`           BIGINT UNSIGNED NOT NULL,
    `user_me`           VARCHAR(1024),
CONSTRAINT `me_per_guild` UNIQUE (`guild_id`, `user_id`)
)
ENGINE = InnoDB,
DEFAULT CHARACTER SET utf8mb4,
COLLATE utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS `table_metrics`
(
    `command_name`      VARCHAR(32) NOT NULL,
    `command_count`     MEDIUMINT UNSIGNED NOT NULL,
    `command_type`      VARCHAR(64) NOT NULL,
UNIQUE(`command_name`)
)
ENGINE = InnoDB,
DEFAULT CHARACTER SET utf8mb4,
COLLATE utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS `table_prefix`
(
    `guild_id`           BIGINT UNSIGNED NOT NULL,
    `guild_prefix`       VARCHAR(256),
UNIQUE(`guild_id`)
)
ENGINE = InnoDB,
DEFAULT CHARACTER SET utf8mb4,
COLLATE utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS `table_starboard`
(
    `reference_message`   VARCHAR(100) NOT NULL,
    `display_message`     VARCHAR(100) NOT NULL,
    `star_count`          SMALLINT UNSIGNED NOT NULL,
UNIQUE(`reference_message`)
)
ENGINE = InnoDB,
DEFAULT CHARACTER SET utf8mb4,
COLLATE utf8mb4_unicode_ci;


COMMIT;