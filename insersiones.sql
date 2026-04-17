INSERT INTO users (id, name, email, password, role) VALUES

('2001','Ana Torres','ana@test.com','123456','candidate'),
('2002','Luis Martínez','luis@test.com','123456','candidate'),
('2003','Camila Rojas','camila@test.com','123456','candidate'),
('2004','Diego Herrera','diego@test.com','123456','candidate'),
('2005','Valentina Castro','valentina@test.com','123456','candidate'),
('2006','Santiago Mejía','santiago@test.com','123456','candidate'),
('2007','Laura Gómez','laura.g@test.com','123456','candidate'),
('2008','Andrés Pérez','andres@test.com','123456','candidate'),
('2009','Natalia Ruiz','natalia@test.com','123456','candidate'),
('2010','Jorge Ramírez','jorge@test.com','123456','candidate');

INSERT INTO resumes (user_id, file_path, raw_text) VALUES

('2001','/cv_ana.pdf','Profesora de álgebra y cálculo'),
('2002','/cv_luis.pdf','Docente en programación y desarrollo backend'),
('2003','/cv_camila.pdf','Profesora de inteligencia artificial'),
('2004','/cv_diego.pdf','Docente de filosofía moderna'),
('2005','/cv_valentina.pdf','Profesora de física y matemáticas'),
('2006','/cv_santiago.pdf','Profesor de bases de datos'),
('2007','/cv_laura.pdf','Docente de inglés y comunicación'),
('2008','/cv_andres.pdf','Profesor de derecho laboral'),
('2009','/cv_natalia.pdf','Docente de administración de empresas'),
('2010','/cv_jorge.pdf','Profesor de machine learning');

INSERT INTO candidate_profiles 
(user_id, education, experience_years, skills, areas, languages, summary)
VALUES

-- MATEMÁTICAS
('2001',
'["Licenciada en Matemáticas","Maestría en Matemáticas"]',
6,
'["Álgebra","Cálculo","Estadística"]',
'["Matemáticas"]',
'["Español","Inglés"]',
'Profesora especializada en álgebra y cálculo'
),

-- PROGRAMACIÓN
('2002',
'["Ingeniero de Sistemas"]',
4,
'["Python","Java","Backend"]',
'["Programación"]',
'["Español"]',
'Docente en desarrollo de software'
),

-- IA
('2003',
'["Ingeniera en Sistemas","Maestría en IA"]',
7,
'["Machine Learning","Deep Learning","Python"]',
'["Inteligencia Artificial"]',
'["Español","Inglés"]',
'Profesora experta en inteligencia artificial'
),

-- FILOSOFÍA
('2004',
'["Licenciado en Filosofía"]',
10,
'["Ética","Lógica","Filosofía"]',
'["Filosofía"]',
'["Español"]',
'Docente con enfoque en filosofía moderna'
),

-- FÍSICA
('2005',
'["Física","Maestría en Física"]',
5,
'["Física","Matemáticas","Cálculo"]',
'["Física"]',
'["Español","Inglés"]',
'Profesora de física aplicada'
),

-- BASES DE DATOS
('2006',
'["Ingeniero de Sistemas"]',
8,
'["SQL","PostgreSQL","MongoDB"]',
'["Bases de Datos"]',
'["Español"]',
'Profesor experto en bases de datos'
),

-- INGLÉS
('2007',
'["Licenciada en Lenguas"]',
9,
'["Inglés","Comunicación","Writing"]',
'["Idiomas"]',
'["Inglés","Español"]',
'Docente de inglés profesional'
),

-- DERECHO
('2008',
'["Abogado","Especialización en Derecho Laboral"]',
6,
'["Derecho","Laboral","Legal"]',
'["Derecho"]',
'["Español"]',
'Profesor en derecho laboral'
),

-- ADMINISTRACIÓN
('2009',
'["Administrador de Empresas"]',
7,
'["Gestión","Finanzas","Marketing"]',
'["Administración"]',
'["Español"]',
'Docente en administración empresarial'
),

-- MACHINE LEARNING
('2010',
'["Ingeniero","Doctorado en IA"]',
12,
'["Machine Learning","Python","AI"]',
'["Inteligencia Artificial"]',
'["Español","Inglés"]',
'Profesor experto en machine learning'
);




INSERT INTO users (id, name, email, password, role) VALUES
('3001','Ana Torres','ana123@test.com','123456','employee'),
('3002','Luis Martínez','luis13@test.com','123456','employee'),
('3003','Camila Rojas','camila123@test.com','123456','employee');

INSERT INTO employees 
(user_id, name, email, position, salary, start_date, phone, address)
VALUES
('3001','Ana Torres','ana@test.com','Docente Matemáticas',4000000,'2020-01-01','3001234567','Bogotá'),
('3002','Luis Martínez','luis@test.com','Docente Programación',4200000,'2021-03-01','3009876543','Medellín'),
('3003','Camila Rojas','camila@test.com','Docente IA',5000000,'2019-06-15','3012223344','Cali');

INSERT INTO payrolls 
(employee_id, period, salary, bonuses, deductions, net_salary)
VALUES

(1,'2024-01',4000000,200000,300000,3900000),
(2,'2024-01',4200000,150000,250000,4100000),
(3,'2024-01',5000000,500000,400000,5100000);

INSERT INTO vacations 
(employee_id, start_date, end_date, days, status)
VALUES

(1,'2024-06-01','2024-06-10',10,'approved'),
(2,'2024-07-01','2024-07-05',5,'pending'),
(3,'2024-08-10','2024-08-20',10,'approved');


INSERT INTO documents 
(employee_id, name, file_path)
VALUES

(1,'Contrato','/docs/contrato_ana.pdf'),
(2,'Contrato','/docs/contrato_luis.pdf'),
(3,'Contrato','/docs/contrato_camila.pdf');

INSERT INTO requests 
(employee_id, type, description, status)
VALUES

(1,'certificado','Solicitud certificado laboral','closed'),
(2,'vacaciones','Solicitud de vacaciones','open'),
(3,'cambio','Cambio de dirección','closed');

INSERT INTO job_history 
(employee_id, position, salary, start_date, end_date)
VALUES

(1,'Docente Junior',3000000,'2018-01-01','2020-01-01'),
(2,'Developer',3500000,'2019-01-01','2021-03-01'),
(3,'Investigador IA',4500000,'2017-01-01','2019-06-15');




SELECT * FROM vacations;


