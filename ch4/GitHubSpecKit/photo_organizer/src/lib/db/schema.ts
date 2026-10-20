import { sqliteTable, integer, text, real } from 'drizzle-orm/sqlite-core';
import { sql } from 'drizzle-orm';

export const albums = sqliteTable('albums', {
  id:            integer('id').primaryKey({ autoIncrement: true }),
  name:          text('name').notNull(),
  date:          text('date').notNull(),
  display_order: real('display_order').notNull(),
  cover_photo_id: integer('cover_photo_id'),
  created_at:    text('created_at').notNull().default(sql`CURRENT_TIMESTAMP`),
});

export const photos = sqliteTable('photos', {
  id:             integer('id').primaryKey({ autoIncrement: true }),
  album_id:       integer('album_id').notNull().references(() => albums.id, { onDelete: 'cascade' }),
  filename:       text('filename').notNull(),
  filepath:       text('filepath').notNull(),
  thumbnail_path: text('thumbnail_path').notNull(),
  mime_type:      text('mime_type').notNull(),
  size_bytes:     integer('size_bytes').notNull(),
  width:          integer('width'),
  height:         integer('height'),
  display_order:  real('display_order').notNull(),
  added_at:       text('added_at').notNull().default(sql`CURRENT_TIMESTAMP`),
});
