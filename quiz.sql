create table quiz (
id serial primary key,
question varchar(255) not null unique,
options varchar(255) array not null,
correct_answer varchar(255) not null,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX if not exists idx_quiz__question ON quiz(question);

create table quiz_state (
user_id bigint primary key,
quiz_id integer not null default 0,
correct_answers_count INTEGER DEFAULT 0,
total_questions_count INTEGER NOT NULL,
started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX if not exists idx_quiz_state_updated ON quiz_state(updated_at);

insert into quiz (question, options, correct_answer) values
('Как читается ひらがな "あ"?',
 ARRAY['a', 'i', 'u', 'e'],
 'a'),

('Как читается ひらがな "か"?',
 ARRAY['ka', 'ki', 'ko', 'ke'],
 'ka'),

('Как переводится слово ねこ (neko)?',
 ARRAY['собака', 'кошка', 'птица', 'рыба'],
 'кошка'),

('Как переводится слово みず (mizu)?',
 ARRAY['вода', 'огонь', 'земля', 'воздух'],
 'вода'),

('Как читается ひらがな "さ"?',
 ARRAY['sa', 'shi', 'su', 'so'],
 'sa'),

('Как переводится слово ありがとう?',
 ARRAY['привет', 'пока', 'спасибо', 'извини'],
 'спасибо'),

('Как читается ひらがな "た"?',
 ARRAY['ta', 'chi', 'tsu', 'to'],
 'ta'),

('Как переводится слово いぬ (inu)?',
 ARRAY['кошка', 'собака', 'лошадь', 'тигр'],
 'собака'),

('Как читается ひらがな "な"?',
 ARRAY['na', 'ni', 'nu', 'ne'],
 'na'),

('Как переводится слово ほん (hon)?',
 ARRAY['книга', 'ручка', 'дом', 'машина'],
 'книга');
