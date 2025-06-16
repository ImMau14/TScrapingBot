CREATE TABLE public.Chat Types (
  chat_type_id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  chat_type character varying NOT NULL UNIQUE,
  CONSTRAINT Chat Types_pkey PRIMARY KEY (chat_type_id)
);

CREATE TABLE public.Chats (
  chat_id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  chat_tg_id bigint NOT NULL UNIQUE,
  chat_type_id bigint,
  CONSTRAINT Chats_pkey PRIMARY KEY (chat_id),
  CONSTRAINT Chats_chat_type_id_fkey FOREIGN KEY (chat_type_id) REFERENCES public.Chat Types(chat_type_id)
);

CREATE TABLE public.Languages (
  lang_id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  lang_name character varying NOT NULL UNIQUE,
  CONSTRAINT Languages_pkey PRIMARY KEY (lang_id)
);

CREATE TABLE public.Messages (
  msg_id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  user_id bigint NOT NULL,
  chat_id bigint,
  msg character varying,
  datetime timestamp without time zone,
  ia_response text,
  is_cleared boolean NOT NULL DEFAULT false,
  CONSTRAINT Messages_pkey PRIMARY KEY (msg_id),
  CONSTRAINT Messages_chat_id_fkey FOREIGN KEY (chat_id) REFERENCES public.Chats(chat_id),
  CONSTRAINT Messages_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.Users(user_id)
);

CREATE TABLE public.Users (
  user_id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  username character varying,
  lang_id bigint,
  tg_id bigint GENERATED ALWAYS AS IDENTITY NOT NULL UNIQUE,
  CONSTRAINT Users_pkey PRIMARY KEY (user_id),
  CONSTRAINT users_lang_id_fkey FOREIGN KEY (lang_id) REFERENCES public.Languages(lang_id)
);