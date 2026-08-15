-- ManagePEC - sample data.
--
-- Written with plain identifiers and standard INSERT syntax so the same file
-- loads into both SQLite and MySQL.  Statements are ordered so that every
-- foreign key already has its parent row.
--
-- The original five students, five staff and five sports from the phase-4 dump
-- are kept as-is; the rest was added so the aggregate and analysis screens have
-- something with spread in it (funds across several months, sports with nobody
-- enrolled, equipment in several maintenance states).

-- ------------------------------------------------------------------- students

INSERT INTO STUDENT_PERSONAL_DETAILS (Student_ID, First_Name, Last_Name, Date_of_Birth, Contact) VALUES
  (1,  'Ritvik',  'M', '2004-01-01', '+91-3456789012'),
  (2,  'Revanth', 'S', '2005-05-15', '+91-7654321098'),
  (3,  'Dileep',  'A', '2004-08-22', '+91-6543210987'),
  (4,  'Keshav',  'V', '2003-03-10', '+91-4567890123'),
  (5,  'Danny',   'A', '2004-11-28', '+91-5678901234'),
  (6,  'Aarti',   'N', '2005-02-14', '+91-9812345670'),
  (7,  'Farhan',  'K', '2004-06-30', '+91-9812345671'),
  (8,  'Meera',   'R', '2003-09-05', '+91-9812345672'),
  (9,  'Ishaan',  'B', '2005-12-19', '+91-9812345673'),
  (10, 'Nisha',   'P', '2004-04-02', '+91-9812345674'),
  (11, 'Tarun',   'G', '2003-07-21', '+91-9812345675'),
  (12, 'Sanya',   'D', '2005-10-11', '+91-9812345676');

-- ---------------------------------------------------------------------- staff

INSERT INTO STAFF_DETAILS (Staff_ID, First_Name, Last_Name, Contact) VALUES
  (1, 'Naga Raju', 'V', '+91-6543210123'),
  (2, 'Samuel',    'X', '+91-7654321012'),
  (3, 'Vinay',     'S', '+91-4567890987'),
  (4, 'Rohit',     'S', '+91-5678901012'),
  (5, 'Jeevesh',   'M', '+91-3456789987'),
  (6, 'Latha',     'K', '+91-9800011122'),
  (7, 'Imran',     'H', '+91-9800011133'),
  (8, 'Priya',     'T', '+91-9800011144');

-- --------------------------------------------------------------------- sports

INSERT INTO SPORTS (Sport_ID, Sport_Name, Capacity, No_of_Participants, Rules_Link) VALUES
  (1, 'Football',     100, 50, 'http://rules-football.com'),
  (2, 'Basketball',    80, 40, 'http://rules-basketball.com'),
  (3, 'Cricket',       50, 25, 'http://rules-cricket.com'),
  (4, 'Tennis',        30, 15, 'http://rules-tennis.com'),
  (5, 'Badminton',     20, 10, 'http://rules-badminton.com'),
  (6, 'Swimming',      40, 18, 'http://rules-swimming.com'),
  (7, 'Table Tennis',  24,  0, NULL);

INSERT INTO SPORTS_LOCATION (Sport_ID, Trainer, Location) VALUES
  (1, 1, 'Football Ground'),
  (2, 2, 'Basketball Court'),
  (3, 3, 'Cricket Ground'),
  (4, 4, 'Tennis Court'),
  (5, 5, 'Badminton Court'),
  (6, 6, 'Swimming Pool'),
  (7, 7, 'Indoor Hall');

-- ---------------------------------------------------------- student sub-types

INSERT INTO STUDENT_ACAD_DETAILS (Student_ID, Department, Course_Year, Credits_Done) VALUES
  (1,  'CSE', '2022', 2),
  (2,  'ECE', '2023', 3),
  (3,  'CSE', '2021', 1),
  (4,  'CSE', '2022', 4),
  (5,  'ECE', '2022', 2),
  (6,  'CND', '2023', 1),
  (7,  'CSE', '2023', 2),
  (8,  'ECE', '2021', 5),
  (9,  'CSD', '2023', 0),
  (10, 'CSE', '2022', 3),
  (11, 'CND', '2021', 4),
  (12, 'CSD', '2023', 1);

INSERT INTO STUDENT_SPORT_DETAILS (Student_ID, Assigned_Sport, Attendance) VALUES
  (1,  1,    90),
  (2,  2,    85),
  (3,  3,    92),
  (4,  4,    88),
  (5,  5,    94),
  (6,  1,    76),
  (7,  1,    68),
  (8,  2,    81),
  (9,  6,    59),
  (10, 6,    73),
  (11, 3,    97),
  (12, NULL, 0);

INSERT INTO STUDENT_HEALTH_DETAILS (Student_ID, Health_Issue) VALUES
  (1,  'Allergies'),
  (2,  'Asthma'),
  (3,  'No health issues'),
  (4,  'Vision problems'),
  (5,  'Diabetes'),
  (6,  'No health issues'),
  (7,  'Knee injury'),
  (8,  'No health issues'),
  (9,  'Asthma'),
  (10, 'No health issues'),
  (11, 'No health issues'),
  (12, 'Ankle sprain');

INSERT INTO SPORTS_SLOT (Sport_ID, Student_ID, Day, Time) VALUES
  (1, 1,  'MWF', '06:30:00'),
  (2, 2,  'MWF', '05:30:00'),
  (3, 3,  'TTS', '05:30:00'),
  (4, 4,  'MWF', '05:30:00'),
  (5, 5,  'TTS', '06:30:00'),
  (1, 6,  'MWF', '06:30:00'),
  (1, 7,  'TTS', '06:30:00'),
  (2, 8,  'TTS', '05:30:00'),
  (6, 9,  'MWF', '07:00:00'),
  (6, 10, 'TTS', '07:00:00'),
  (3, 11, 'TTS', '05:30:00'),
  (1, 1,  'TTS', '17:00:00');

-- ------------------------------------------------------------ staff sub-types

INSERT INTO STAFF_PROFESSIONAL (Staff_ID, Join_Date, Type, Total_Salary, Pending_Salary) VALUES
  (1, '2020-03-01', 'Coach',           60000, 20000),
  (2, '2021-05-15', 'Trainer',         55000, 18000),
  (3, '2019-08-22', 'Physiotherapist', 65000, 22000),
  (4, '2022-01-10', 'Manager',         70000, 25000),
  (5, '2018-11-28', 'Coordinator',     75000, 28000),
  (6, '2023-02-01', 'Trainer',         52000,     0),
  (7, '2023-06-12', 'Trainer',         48000, 12000),
  (8, '2021-09-30', 'Maintenance',     40000,  5000);

INSERT INTO STAFF_POSITION (Staff_ID, Sport_ID, Position, Supervisor) VALUES
  (1, 1,    'Head Coach',      NULL),
  (2, 2,    'Trainer',         1),
  (3, 3,    'Physiotherapist', 1),
  (4, 4,    'Manager',         NULL),
  (5, 5,    'Coordinator',     4),
  (6, 6,    'Trainer',         1),
  (7, 7,    'Trainer',         1),
  (8, NULL, 'Maintenance',     4);

INSERT INTO STAFF_TASKS (Staff_ID, Day, Time, Work) VALUES
  (1, '2023-01-05', '10:00:00', 'Team Practice'),
  (1, '2023-01-12', '10:00:00', 'Selection Trials'),
  (2, '2023-01-10', '11:30:00', 'Individual Training'),
  (3, '2023-01-15', '14:00:00', 'Rehabilitation Session'),
  (4, '2023-01-20', '16:30:00', 'Team Strategy Meeting'),
  (5, '2023-01-25', '17:45:00', 'Event Coordination'),
  (6, '2023-02-02', '07:00:00', 'Swim Drills'),
  (8, '2023-02-03', '09:00:00', 'Equipment Audit');

-- ---------------------------------------------------------- fitness challenges

INSERT INTO FITNESS_CHALLENGES (Challenge_ID, Challenge_Name) VALUES
  (1, 'Cardio Challenge'),
  (2, 'Strength Training Challenge'),
  (3, 'Yoga Challenge'),
  (4, 'Running Challenge'),
  (5, 'Flexibility Challenge'),
  (6, 'Endurance Challenge');

INSERT INTO FITNESS_CHALLENGES_DETAILS (Challenge_ID, From_Date, To_Date, Registration_Deadline) VALUES
  (1, '2023-03-01', '2023-03-31', '2023-02-15'),
  (2, '2023-04-01', '2023-04-30', '2023-03-15'),
  (3, '2023-05-01', '2023-05-31', '2023-04-15'),
  (4, '2023-06-01', '2023-06-30', '2023-05-15'),
  (5, '2023-07-01', '2023-07-31', '2023-06-15'),
  (6, '2023-08-01', '2023-08-31', '2023-07-15');

INSERT INTO FITNESS_SECTIONS (CS_REF_ID, Challenge_ID, Section_Name) VALUES
  (1, 1, 'Running'),
  (2, 2, 'Weightlifting'),
  (3, 3, 'Asanas'),
  (4, 4, 'Sprint'),
  (5, 5, 'Stretching'),
  (6, 6, 'Long Distance'),
  (7, 1, 'Cycling');

INSERT INTO FITNESS_SECTIONS_DETAILS (CS_REF_ID, Date, Location) VALUES
  (1, '2023-03-05', 'Football Ground'),
  (2, '2023-04-10', 'Gym'),
  (3, '2023-05-15', 'Yoga Hall'),
  (4, '2023-06-20', 'Football Ground'),
  (5, '2023-07-25', 'Fitness Center'),
  (6, '2023-08-08', 'Athletics Track'),
  (7, '2023-03-18', 'Campus Loop');

INSERT INTO FITNESS_CHALLENGE_MENTORS (CS_REF_ID, Mentor_ID) VALUES
  (1, 1),
  (1, 6),
  (2, 2),
  (3, 3),
  (4, 4),
  (5, 5),
  (6, 6),
  (7, 7);

INSERT INTO FITNESS_CHALLENGE_WINNERS (CS_REF_ID, Winner_ID, Prize) VALUES
  (1, 1,  'Fitness Tracker'),
  (1, 6,  'Runner Up Medal'),
  (2, 2,  'Cash Prize'),
  (3, 3,  'Yoga Mat Set'),
  (4, 4,  'Running Shoes'),
  (5, 5,  'Flexibility Workshop Pass'),
  (6, 11, 'Endurance Trophy');

-- -------------------------------------------------------------------- medical

INSERT INTO MEDICAL_HISTORY (Med_ID, Student_ID, DateTime, Type) VALUES
  (1, 1,  '2023-02-01 08:30:00', 'Injury'),
  (2, 2,  '2023-02-05 10:15:00', 'Allergy'),
  (4, 4,  '2023-02-15 16:45:00', 'Vision Issue'),
  (5, 5,  '2023-02-20 18:30:00', 'Diabetes'),
  (6, 7,  '2023-03-02 09:00:00', 'Injury'),
  (7, 12, '2023-03-11 15:20:00', 'Injury');

INSERT INTO MEDICAL_HISTORY_DETAILS (Med_ID, Severity, Recovery, Treatment) VALUES
  (1, 'Moderate', '2023-03-01', 'Physical therapy'),
  (2, 'Mild',     '2023-02-15', 'Antihistamines'),
  (4, 'Severe',   '2023-04-01', 'Prescription glasses'),
  (5, 'Moderate', '2023-03-10', 'Insulin therapy'),
  (6, 'Moderate', '2023-04-05', 'Knee brace and rest'),
  (7, 'Mild',     '2023-03-25', 'Ankle strapping');

-- --------------------------------------------------------------------- money

INSERT INTO TRANSACTIONS (Transaction_ID, Amount, Status) VALUES
  (1, 5000,  'Completed'),
  (2, 7000,  'Pending'),
  (3, 3000,  'Completed'),
  (4, 4500,  'Pending'),
  (5, 6000,  'Completed'),
  (6, 12000, 'Completed'),
  (7, 8500,  'Completed'),
  (8, 2200,  'Pending');

INSERT INTO FUNDS (Fund_ID, Transaction_ID, Date) VALUES
  (1, 1, '2023-01-11'),
  (2, 2, '2023-02-05'),
  (3, 3, '2023-02-10'),
  (4, 4, '2023-03-15'),
  (5, 5, '2023-03-20'),
  (6, 6, '2023-04-02'),
  (7, 7, '2023-05-19'),
  (8, 8, '2023-05-27');

-- ------------------------------------------------------------------ equipment

INSERT INTO EQUIPMENT (Equipment_ID, Equipment_Name, Sport_ID, Quantity) VALUES
  (1, 'Footballs',              1, 20),
  (2, 'Basketballs',            2, 15),
  (3, 'Cricket Bats',           3, 30),
  (4, 'Tennis Rackets',         4, 10),
  (5, 'Badminton Shuttlecocks', 5, 50),
  (6, 'Swim Kickboards',        6, 12),
  (7, 'Table Tennis Paddles',   7, 16),
  (8, 'First Aid Kits',      NULL,  6);

INSERT INTO EQUIPMENT_FUNDS (Transaction_ID, Equipment_ID, Quantity) VALUES
  (1, 1, 5),
  (2, 2, 8),
  (3, 3, 10),
  (4, 4, 3),
  (5, 5, 15),
  (6, 6, 12),
  (7, 7, 16),
  (8, 8, 6);

INSERT INTO EQUIPMENT_MAINTENANCE (Equipment_ID, Staff_ID, Date, Status) VALUES
  (1, 1, '2023-02-01', 'Good'),
  (2, 2, '2023-02-05', 'Under Maintenance'),
  (3, 3, '2023-02-10', 'Good'),
  (4, 4, '2023-02-15', 'Needs Repair'),
  (5, 5, '2023-02-20', 'Good'),
  (6, 8, '2023-02-20', 'Good'),
  (7, 8, '2023-03-01', 'Needs Repair'),
  (1, 8, '2023-06-01', 'Under Maintenance');

INSERT INTO EQUIPMENT_REGISTRATION (Registration_ID, Equipment_ID, Fund_ID, Expected_Approval_Date) VALUES
  (1, 1, 1, '2023-02-10'),
  (2, 2, 2, '2023-02-15'),
  (3, 3, 3, '2023-02-20'),
  (4, 4, 4, '2023-02-25'),
  (5, 5, 5, '2023-03-01'),
  (6, 6, 6, '2023-04-12'),
  (7, 7, 7, '2023-05-30'),
  (8, 8, 8, '2023-06-07');
