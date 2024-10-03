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