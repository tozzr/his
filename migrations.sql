CREATE TABLE public.patients (
	id uuid DEFAULT gen_random_uuid() NOT NULL,
	firstname varchar NOT NULL,
	lastname varchar NOT NULL,
	birthdate date NULL,
	CONSTRAINT patients_pk PRIMARY KEY (id)
);

CREATE TABLE public.doctors (
	id uuid DEFAULT gen_random_uuid() NOT NULL,
	firstname varchar NOT NULL,
	lastname varchar NOT NULL,
	birthdate date NULL,
	CONSTRAINT doctors_pk PRIMARY KEY (id)
);

CREATE TABLE public.users (
	id uuid DEFAULT gen_random_uuid() NOT NULL,
	email varchar NOT NULL,
	username varchar NOT NULL,
	password varchar NOT NULL,
	CONSTRAINT users_pk PRIMARY KEY (id)
);