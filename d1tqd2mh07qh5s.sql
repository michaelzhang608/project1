-- Adminer 4.6.3-dev PostgreSQL dump

\connect "d1tqd2mh07qh5s";

DROP TABLE IF EXISTS "comments";
DROP SEQUENCE IF EXISTS comments_id_seq;
CREATE SEQUENCE comments_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."comments" (
    "id" integer DEFAULT nextval('comments_id_seq') NOT NULL,
    "content" character varying NOT NULL,
    "user_id" integer NOT NULL,
    "zip_id" integer NOT NULL,
    "date" timestamp NOT NULL,
    CONSTRAINT "comments_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "comments_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) NOT DEFERRABLE,
    CONSTRAINT "comments_zip_id_fkey" FOREIGN KEY (zip_id) REFERENCES zips(id) NOT DEFERRABLE
) WITH (oids = false);


DROP TABLE IF EXISTS "users";
DROP SEQUENCE IF EXISTS users_id_seq;
CREATE SEQUENCE users_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."users" (
    "id" integer DEFAULT nextval('users_id_seq') NOT NULL,
    "name" character varying NOT NULL,
    "username" character varying NOT NULL,
    "password" character varying NOT NULL,
    CONSTRAINT "users_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "users_username_key" UNIQUE ("username")
) WITH (oids = false);


DROP TABLE IF EXISTS "zips";
DROP SEQUENCE IF EXISTS zips_id_seq;
CREATE SEQUENCE zips_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."zips" (
    "id" integer DEFAULT nextval('zips_id_seq') NOT NULL,
    "zipcode" character varying NOT NULL,
    "city" character varying NOT NULL,
    "state" character varying NOT NULL,
    "lat" numeric NOT NULL,
    "long" numeric NOT NULL,
    "population" integer NOT NULL,
    CONSTRAINT "zips_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "zips_zipcode_key" UNIQUE ("zipcode")
) WITH (oids = false);


-- 2018-07-12 20:39:01.931461+00
