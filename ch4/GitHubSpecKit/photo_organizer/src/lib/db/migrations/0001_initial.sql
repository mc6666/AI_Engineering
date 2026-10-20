-- SQLite: foreign_keys pragma enforced at connection time; circular FK handled
-- by keeping cover_photo_id as an unconstrained integer (updated by app logic).
CREATE TABLE IF NOT EXISTS `albums` (
  `id`             integer PRIMARY KEY AUTOINCREMENT NOT NULL,
  `name`           text NOT NULL,
  `date`           text NOT NULL,
  `display_order`  real NOT NULL,
  `cover_photo_id` integer,
  `created_at`     text NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TABLE IF NOT EXISTS `photos` (
  `id`             integer PRIMARY KEY AUTOINCREMENT NOT NULL,
  `album_id`       integer NOT NULL REFERENCES `albums`(`id`) ON DELETE CASCADE,
  `filename`       text NOT NULL,
  `filepath`       text NOT NULL,
  `thumbnail_path` text NOT NULL,
  `mime_type`      text NOT NULL,
  `size_bytes`     integer NOT NULL,
  `width`          integer,
  `height`         integer,
  `display_order`  real NOT NULL,
  `added_at`       text NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

CREATE INDEX IF NOT EXISTS `albums_display_order_idx` ON `albums`(`display_order`);
CREATE INDEX IF NOT EXISTS `albums_date_idx` ON `albums`(`date`);
CREATE INDEX IF NOT EXISTS `photos_album_id_idx` ON `photos`(`album_id`);
CREATE INDEX IF NOT EXISTS `photos_album_order_idx` ON `photos`(`album_id`, `display_order`);
