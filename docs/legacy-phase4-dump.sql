-- MySQL dump 10.13  Distrib 8.0.35, for Win64 (x86_64)
--
-- Host: localhost    Database: PEC
-- ------------------------------------------------------
-- Server version	8.0.35

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `EQUIPMENT`
--

DROP TABLE IF EXISTS `EQUIPMENT`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `EQUIPMENT` (
  `Equipment_ID` int NOT NULL,
  `Equipment_Name` varchar(50) NOT NULL,
  `Sport_ID` int DEFAULT NULL,
  `Quantity` int NOT NULL,
  PRIMARY KEY (`Equipment_ID`),
  KEY `Sport_ID` (`Sport_ID`),
  CONSTRAINT `equipment_ibfk_1` FOREIGN KEY (`Sport_ID`) REFERENCES `SPORTS` (`Sport_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `EQUIPMENT`
--

LOCK TABLES `EQUIPMENT` WRITE;
/*!40000 ALTER TABLE `EQUIPMENT` DISABLE KEYS */;
INSERT INTO `EQUIPMENT` VALUES (1,'Football',1,20),(2,'Basketballs',2,15),(3,'Cricket Bat',3,30),(4,'Tennis Rackets',4,10),(5,'Badminton Shuttlecocks',5,50);
/*!40000 ALTER TABLE `EQUIPMENT` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `EQUIPMENT_FUNDS`
--

DROP TABLE IF EXISTS `EQUIPMENT_FUNDS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `EQUIPMENT_FUNDS` (
  `Transaction_ID` int NOT NULL,
  `Equipment_ID` int DEFAULT NULL,
  `Quantity` int NOT NULL,
  PRIMARY KEY (`Transaction_ID`),
  KEY `Equipment_ID` (`Equipment_ID`),
  CONSTRAINT `equipment_funds_ibfk_1` FOREIGN KEY (`Transaction_ID`) REFERENCES `TRANSACTIONS` (`Transaction_ID`) ON DELETE CASCADE,
  CONSTRAINT `equipment_funds_ibfk_2` FOREIGN KEY (`Equipment_ID`) REFERENCES `EQUIPMENT` (`Equipment_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `EQUIPMENT_FUNDS`
--

LOCK TABLES `EQUIPMENT_FUNDS` WRITE;
/*!40000 ALTER TABLE `EQUIPMENT_FUNDS` DISABLE KEYS */;
INSERT INTO `EQUIPMENT_FUNDS` VALUES (1,1,5),(2,2,8),(3,3,10),(4,4,3),(5,5,15);
/*!40000 ALTER TABLE `EQUIPMENT_FUNDS` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `EQUIPMENT_MAINTENANCE`
--

DROP TABLE IF EXISTS `EQUIPMENT_MAINTENANCE`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `EQUIPMENT_MAINTENANCE` (
  `Equipment_ID` int NOT NULL,
  `Staff_ID` int DEFAULT NULL,
  `Date` date NOT NULL,
  `Status` varchar(50) NOT NULL,
  PRIMARY KEY (`Equipment_ID`),
  KEY `Staff_ID` (`Staff_ID`),
  CONSTRAINT `equipment_maintainance_ibfk_1` FOREIGN KEY (`Equipment_ID`) REFERENCES `EQUIPMENT` (`Equipment_ID`) ON DELETE CASCADE,
  CONSTRAINT `equipment_maintainance_ibfk_2` FOREIGN KEY (`Staff_ID`) REFERENCES `STAFF_DETAILS` (`Staff_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `EQUIPMENT_MAINTENANCE`
--

LOCK TABLES `EQUIPMENT_MAINTENANCE` WRITE;
/*!40000 ALTER TABLE `EQUIPMENT_MAINTENANCE` DISABLE KEYS */;
INSERT INTO `EQUIPMENT_MAINTENANCE` VALUES (1,1,'2023-02-01','Good'),(2,2,'2023-02-05','Under Maintenance'),(3,3,'2023-02-10','Good'),(4,4,'2023-02-15','Needs Repair'),(5,5,'2023-02-20','Good');
/*!40000 ALTER TABLE `EQUIPMENT_MAINTENANCE` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `EQUIPMENT_REGISTRATION`
--

DROP TABLE IF EXISTS `EQUIPMENT_REGISTRATION`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `EQUIPMENT_REGISTRATION` (
  `Registration_ID` int NOT NULL,
  `Equipment_ID` int DEFAULT NULL,
  `Fund_ID` int DEFAULT NULL,
  `Expected_Approval_Date` date NOT NULL,
  PRIMARY KEY (`Registration_ID`),
  KEY `Equipment_ID` (`Equipment_ID`),
  KEY `Fund_ID` (`Fund_ID`),
  CONSTRAINT `equipment_registration_ibfk_1` FOREIGN KEY (`Equipment_ID`) REFERENCES `EQUIPMENT` (`Equipment_ID`) ON DELETE CASCADE,
  CONSTRAINT `equipment_registration_ibfk_2` FOREIGN KEY (`Fund_ID`) REFERENCES `FUNDS` (`Fund_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `EQUIPMENT_REGISTRATION`
--

LOCK TABLES `EQUIPMENT_REGISTRATION` WRITE;
/*!40000 ALTER TABLE `EQUIPMENT_REGISTRATION` DISABLE KEYS */;
INSERT INTO `EQUIPMENT_REGISTRATION` VALUES (1,1,1,'2023-02-10'),(2,2,2,'2023-02-15'),(3,3,3,'2023-02-20'),(4,4,4,'2023-02-25'),(5,5,5,'2023-03-01');
/*!40000 ALTER TABLE `EQUIPMENT_REGISTRATION` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `FITNESS_CHALLENGE_MENTORS`
--

DROP TABLE IF EXISTS `FITNESS_CHALLENGE_MENTORS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `FITNESS_CHALLENGE_MENTORS` (
  `CS_REF_ID` int NOT NULL,
  `Mentor_ID` int DEFAULT NULL,
  PRIMARY KEY (`CS_REF_ID`),
  KEY `Mentor_ID` (`Mentor_ID`),
  CONSTRAINT `fitness_challenge_mentors_ibfk_1` FOREIGN KEY (`CS_REF_ID`) REFERENCES `FITNESS_SECTIONS` (`CS_REF_ID`) ON DELETE CASCADE,
  CONSTRAINT `fitness_challenge_mentors_ibfk_2` FOREIGN KEY (`Mentor_ID`) REFERENCES `STAFF_DETAILS` (`Staff_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `FITNESS_CHALLENGE_MENTORS`
--

LOCK TABLES `FITNESS_CHALLENGE_MENTORS` WRITE;
/*!40000 ALTER TABLE `FITNESS_CHALLENGE_MENTORS` DISABLE KEYS */;
INSERT INTO `FITNESS_CHALLENGE_MENTORS` VALUES (1,1),(2,2),(3,3),(4,4),(5,5);
/*!40000 ALTER TABLE `FITNESS_CHALLENGE_MENTORS` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `FITNESS_CHALLENGE_WINNERS`
--

DROP TABLE IF EXISTS `FITNESS_CHALLENGE_WINNERS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `FITNESS_CHALLENGE_WINNERS` (
  `CS_REF_ID` int NOT NULL,
  `Winner_ID` int DEFAULT NULL,
  `Prize` varchar(50) NOT NULL,
  PRIMARY KEY (`CS_REF_ID`),
  KEY `Winner_ID` (`Winner_ID`),
  CONSTRAINT `fitness_challenge_winners_ibfk_1` FOREIGN KEY (`CS_REF_ID`) REFERENCES `FITNESS_SECTIONS` (`CS_REF_ID`) ON DELETE CASCADE,
  CONSTRAINT `fitness_challenge_winners_ibfk_2` FOREIGN KEY (`Winner_ID`) REFERENCES `STUDENT_PERSONAL_DETAILS` (`Student_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `FITNESS_CHALLENGE_WINNERS`
--

LOCK TABLES `FITNESS_CHALLENGE_WINNERS` WRITE;
/*!40000 ALTER TABLE `FITNESS_CHALLENGE_WINNERS` DISABLE KEYS */;
INSERT INTO `FITNESS_CHALLENGE_WINNERS` VALUES (1,1,'Fitness Tracker'),(2,2,'Cash Prize'),(3,3,'Yoga Mat Set'),(4,4,'Running Shoes'),(5,5,'Flexibility Workshop Pass');
/*!40000 ALTER TABLE `FITNESS_CHALLENGE_WINNERS` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `FITNESS_CHALLENGES`
--

DROP TABLE IF EXISTS `FITNESS_CHALLENGES`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `FITNESS_CHALLENGES` (
  `Challenge_ID` int NOT NULL,
  `Challenge_Name` varchar(50) NOT NULL,
  PRIMARY KEY (`Challenge_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `FITNESS_CHALLENGES`
--

LOCK TABLES `FITNESS_CHALLENGES` WRITE;
/*!40000 ALTER TABLE `FITNESS_CHALLENGES` DISABLE KEYS */;
INSERT INTO `FITNESS_CHALLENGES` VALUES (1,'Cardio Challenge'),(2,'Strength Training Challenge'),(3,'Yoga Challenge'),(4,'Running Challenge'),(5,'Flexibility Challenge');
/*!40000 ALTER TABLE `FITNESS_CHALLENGES` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `FITNESS_CHALLENGES_DETAILS`
--

DROP TABLE IF EXISTS `FITNESS_CHALLENGES_DETAILS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `FITNESS_CHALLENGES_DETAILS` (
  `Challenge_ID` int NOT NULL,
  `From_Date` date NOT NULL,
  `To_Date` date NOT NULL,
  `Registration_Deadline` date NOT NULL,
  PRIMARY KEY (`Challenge_ID`),
  CONSTRAINT `fitness_challenges_details_ibfk_1` FOREIGN KEY (`Challenge_ID`) REFERENCES `FITNESS_CHALLENGES` (`Challenge_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `FITNESS_CHALLENGES_DETAILS`
--

LOCK TABLES `FITNESS_CHALLENGES_DETAILS` WRITE;
/*!40000 ALTER TABLE `FITNESS_CHALLENGES_DETAILS` DISABLE KEYS */;
INSERT INTO `FITNESS_CHALLENGES_DETAILS` VALUES (1,'2023-03-01','2023-03-31','2023-02-15'),(2,'2023-04-01','2023-04-30','2023-03-15'),(3,'2023-05-01','2023-05-31','2023-04-15'),(4,'2023-06-01','2023-06-30','2023-05-15'),(5,'2023-07-01','2023-07-31','2023-06-15');
/*!40000 ALTER TABLE `FITNESS_CHALLENGES_DETAILS` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `FITNESS_SECTIONS`
--

DROP TABLE IF EXISTS `FITNESS_SECTIONS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `FITNESS_SECTIONS` (
  `CS_REF_ID` int NOT NULL,
  `Challenge_ID` int DEFAULT NULL,
  `Section_Name` varchar(50) NOT NULL,
  PRIMARY KEY (`CS_REF_ID`),
  KEY `Challenge_ID` (`Challenge_ID`),
  CONSTRAINT `fitness_sections_ibfk_1` FOREIGN KEY (`Challenge_ID`) REFERENCES `FITNESS_CHALLENGES` (`Challenge_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `FITNESS_SECTIONS`
--

LOCK TABLES `FITNESS_SECTIONS` WRITE;
/*!40000 ALTER TABLE `FITNESS_SECTIONS` DISABLE KEYS */;
INSERT INTO `FITNESS_SECTIONS` VALUES (1,1,'Running'),(2,2,'Weightlifting'),(3,3,'Asanas'),(4,4,'Sprint'),(5,5,'Stretching');
/*!40000 ALTER TABLE `FITNESS_SECTIONS` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `FITNESS_SECTIONS_DETAILS`
--

DROP TABLE IF EXISTS `FITNESS_SECTIONS_DETAILS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `FITNESS_SECTIONS_DETAILS` (
  `CS_REF_ID` int NOT NULL,
  `Date` date NOT NULL,
  `Location` varchar(50) NOT NULL,
  PRIMARY KEY (`CS_REF_ID`),
  CONSTRAINT `fitness_sections_details_ibfk_1` FOREIGN KEY (`CS_REF_ID`) REFERENCES `FITNESS_SECTIONS` (`CS_REF_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `FITNESS_SECTIONS_DETAILS`
--

LOCK TABLES `FITNESS_SECTIONS_DETAILS` WRITE;
/*!40000 ALTER TABLE `FITNESS_SECTIONS_DETAILS` DISABLE KEYS */;
INSERT INTO `FITNESS_SECTIONS_DETAILS` VALUES (1,'2023-03-05','Football Ground'),(2,'2023-04-10','Gym'),(3,'2023-05-15','Yoga Hall'),(4,'2023-06-20','Football Ground'),(5,'2023-07-25','Fitness Center');
/*!40000 ALTER TABLE `FITNESS_SECTIONS_DETAILS` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `FUNDS`
--

DROP TABLE IF EXISTS `FUNDS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `FUNDS` (
  `Fund_ID` int NOT NULL,
  `Transaction_ID` int DEFAULT NULL,
  `Date` date NOT NULL,
  PRIMARY KEY (`Fund_ID`),
  KEY `Transaction_ID` (`Transaction_ID`),
  CONSTRAINT `funds_ibfk_1` FOREIGN KEY (`Transaction_ID`) REFERENCES `TRANSACTIONS` (`Transaction_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `FUNDS`
--

LOCK TABLES `FUNDS` WRITE;
/*!40000 ALTER TABLE `FUNDS` DISABLE KEYS */;
INSERT INTO `FUNDS` VALUES (1,1,'2023-02-01'),(2,2,'2023-02-05'),(3,3,'2023-02-10'),(4,4,'2023-02-15'),(5,5,'2023-02-20');
/*!40000 ALTER TABLE `FUNDS` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `MEDICAL_HISTORY`
--

DROP TABLE IF EXISTS `MEDICAL_HISTORY`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MEDICAL_HISTORY` (
  `Med_ID` int NOT NULL,
  `Student_ID` int DEFAULT NULL,
  `DateTime` datetime NOT NULL,
  `Type` varchar(100) NOT NULL,
  PRIMARY KEY (`Med_ID`),
  KEY `Student_ID` (`Student_ID`),
  CONSTRAINT `medical_history_ibfk_1` FOREIGN KEY (`Student_ID`) REFERENCES `STUDENT_PERSONAL_DETAILS` (`Student_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MEDICAL_HISTORY`
--

LOCK TABLES `MEDICAL_HISTORY` WRITE;
/*!40000 ALTER TABLE `MEDICAL_HISTORY` DISABLE KEYS */;
INSERT INTO `MEDICAL_HISTORY` VALUES (1,1,'2023-02-01 08:30:00','Injury'),(2,2,'2023-02-05 10:15:00','Allergy'),(4,4,'2023-02-15 16:45:00','Vision Issue'),(5,5,'2023-02-20 18:30:00','Diabetes');
/*!40000 ALTER TABLE `MEDICAL_HISTORY` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `MEDICAL_HISTORY_DETAILS`
--

DROP TABLE IF EXISTS `MEDICAL_HISTORY_DETAILS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MEDICAL_HISTORY_DETAILS` (
  `Med_ID` int NOT NULL,
  `Severity` varchar(50) NOT NULL,
  `Recovery` date NOT NULL,
  `Treatment` varchar(250) NOT NULL,
  PRIMARY KEY (`Med_ID`),
  CONSTRAINT `medical_history_details_ibfk_1` FOREIGN KEY (`Med_ID`) REFERENCES `MEDICAL_HISTORY` (`Med_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MEDICAL_HISTORY_DETAILS`
--

LOCK TABLES `MEDICAL_HISTORY_DETAILS` WRITE;
/*!40000 ALTER TABLE `MEDICAL_HISTORY_DETAILS` DISABLE KEYS */;
INSERT INTO `MEDICAL_HISTORY_DETAILS` VALUES (1,'Moderate','2023-03-01','Physical therapy'),(2,'Mild','2023-02-15','Antihistamines'),(4,'Severe','2023-04-01','Prescription glasses'),(5,'Moderate','2023-03-10','Insulin therapy');
/*!40000 ALTER TABLE `MEDICAL_HISTORY_DETAILS` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `SPORTS`
--

DROP TABLE IF EXISTS `SPORTS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `SPORTS` (
  `Sport_ID` int NOT NULL,
  `Sport_Name` varchar(50) NOT NULL,
  `Capacity` int NOT NULL,
  `No_of_Participants` int NOT NULL,
  `Rules_Link` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`Sport_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `SPORTS`
--

LOCK TABLES `SPORTS` WRITE;
/*!40000 ALTER TABLE `SPORTS` DISABLE KEYS */;
INSERT INTO `SPORTS` VALUES (1,'Football',100,50,'http://rules-football.com'),(2,'Basketball',80,40,'http://rules-basketball.com'),(3,'Cricket',50,25,'http://rules-Cricket.com'),(4,'Tennis',30,15,'http://rules-tennis.com'),(5,'Badminton',20,10,'http://rules-badminton.com');
/*!40000 ALTER TABLE `SPORTS` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `SPORTS_LOCATION`
--

DROP TABLE IF EXISTS `SPORTS_LOCATION`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `SPORTS_LOCATION` (
  `Sport_ID` int NOT NULL,
  `Trainer` int DEFAULT NULL,
  `Location` varchar(50) NOT NULL,
  PRIMARY KEY (`Sport_ID`),
  KEY `Trainer` (`Trainer`),
  CONSTRAINT `sports_location_ibfk_1` FOREIGN KEY (`Sport_ID`) REFERENCES `SPORTS` (`Sport_ID`) ON DELETE CASCADE,
  CONSTRAINT `sports_location_ibfk_2` FOREIGN KEY (`Trainer`) REFERENCES `STAFF_DETAILS` (`Staff_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `SPORTS_LOCATION`
--

LOCK TABLES `SPORTS_LOCATION` WRITE;
/*!40000 ALTER TABLE `SPORTS_LOCATION` DISABLE KEYS */;
INSERT INTO `SPORTS_LOCATION` VALUES (1,1,'Football Ground'),(2,2,'Basketball Court'),(3,3,'FG'),(4,4,'Tennis Court'),(5,5,'Badminton Court');
/*!40000 ALTER TABLE `SPORTS_LOCATION` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `SPORTS_SLOT`
--

DROP TABLE IF EXISTS `SPORTS_SLOT`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `SPORTS_SLOT` (
  `Sport_ID` int DEFAULT NULL,
  `Student_ID` int NOT NULL,
  `Day` varchar(5) NOT NULL,
  `Time` time NOT NULL,
  PRIMARY KEY (`Student_ID`),
  KEY `Sport_ID` (`Sport_ID`),
  CONSTRAINT `sports_slot_ibfk_1` FOREIGN KEY (`Sport_ID`) REFERENCES `SPORTS` (`Sport_ID`) ON DELETE CASCADE,
  CONSTRAINT `sports_slot_ibfk_2` FOREIGN KEY (`Student_ID`) REFERENCES `STUDENT_PERSONAL_DETAILS` (`Student_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `SPORTS_SLOT`
--

LOCK TABLES `SPORTS_SLOT` WRITE;
/*!40000 ALTER TABLE `SPORTS_SLOT` DISABLE KEYS */;
INSERT INTO `SPORTS_SLOT` VALUES (1,1,'MWF','06:30:00'),(2,2,'MWF','05:30:00'),(3,3,'TTS','05:30:00'),(4,4,'MWF','05:30:00'),(5,5,'TTS','06:30:00');
/*!40000 ALTER TABLE `SPORTS_SLOT` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `STAFF_DETAILS`
--

DROP TABLE IF EXISTS `STAFF_DETAILS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `STAFF_DETAILS` (
  `Staff_ID` int NOT NULL,
  `First_Name` varchar(50) NOT NULL,
  `Last_Name` varchar(50) NOT NULL,
  `Contact` varchar(15) NOT NULL,
  PRIMARY KEY (`Staff_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `STAFF_DETAILS`
--

LOCK TABLES `STAFF_DETAILS` WRITE;
/*!40000 ALTER TABLE `STAFF_DETAILS` DISABLE KEYS */;
INSERT INTO `STAFF_DETAILS` VALUES (1,'Naga Raju','V','+91-6543210123'),(2,'Samuel','X','+91-7654321012'),(3,'Vinay','S','+91-4567890987'),(4,'Rohit','S','+91-5678901012'),(5,'Jeevesh','M','+91-3456789987');
/*!40000 ALTER TABLE `STAFF_DETAILS` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `STAFF_POSITION`
--

DROP TABLE IF EXISTS `STAFF_POSITION`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `STAFF_POSITION` (
  `Staff_ID` int NOT NULL,
  `Sport_ID` int DEFAULT NULL,
  `Position` varchar(50) NOT NULL,
  `Supervisor` int DEFAULT NULL,
  PRIMARY KEY (`Staff_ID`),
  KEY `Sport_ID` (`Sport_ID`),
  KEY `Supervisor` (`Supervisor`),
  CONSTRAINT `staff_position_ibfk_1` FOREIGN KEY (`Staff_ID`) REFERENCES `STAFF_DETAILS` (`Staff_ID`) ON DELETE CASCADE,
  CONSTRAINT `staff_position_ibfk_2` FOREIGN KEY (`Sport_ID`) REFERENCES `SPORTS` (`Sport_ID`) ON DELETE CASCADE,
  CONSTRAINT `staff_position_ibfk_3` FOREIGN KEY (`Supervisor`) REFERENCES `STAFF_DETAILS` (`Staff_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `STAFF_POSITION`
--

LOCK TABLES `STAFF_POSITION` WRITE;
/*!40000 ALTER TABLE `STAFF_POSITION` DISABLE KEYS */;
INSERT INTO `STAFF_POSITION` VALUES (1,1,'Head Coach',NULL),(2,2,'Trainer',1),(3,3,'Physiotherapist',1),(4,4,'Manager',NULL),(5,5,'Coordinator',4);
/*!40000 ALTER TABLE `STAFF_POSITION` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `STAFF_PROFESSIONAL`
--

DROP TABLE IF EXISTS `STAFF_PROFESSIONAL`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `STAFF_PROFESSIONAL` (
  `Staff_ID` int NOT NULL,
  `Join_Date` date NOT NULL,
  `Type` varchar(50) NOT NULL,
  `Total_Salary` int NOT NULL,
  `Pending_Salary` int NOT NULL,
  PRIMARY KEY (`Staff_ID`),
  CONSTRAINT `staff_professional_ibfk_1` FOREIGN KEY (`Staff_ID`) REFERENCES `STAFF_DETAILS` (`Staff_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `STAFF_PROFESSIONAL`
--

LOCK TABLES `STAFF_PROFESSIONAL` WRITE;
/*!40000 ALTER TABLE `STAFF_PROFESSIONAL` DISABLE KEYS */;
INSERT INTO `STAFF_PROFESSIONAL` VALUES (1,'2020-03-01','Coach',60000,20000),(2,'2021-05-15','Trainer',55000,18000),(3,'2019-08-22','Physiotherapist',65000,22000),(4,'2022-01-10','Manager',70000,25000),(5,'2018-11-28','Coordinator',75000,28000);
/*!40000 ALTER TABLE `STAFF_PROFESSIONAL` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `STAFF_TASKS`
--

DROP TABLE IF EXISTS `STAFF_TASKS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `STAFF_TASKS` (
  `Staff_ID` int NOT NULL,
  `Day` date NOT NULL,
  `Time` time NOT NULL,
  `Work` varchar(100) NOT NULL,
  PRIMARY KEY (`Staff_ID`),
  CONSTRAINT `staff_tasks_ibfk_1` FOREIGN KEY (`Staff_ID`) REFERENCES `STAFF_DETAILS` (`Staff_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `STAFF_TASKS`
--

LOCK TABLES `STAFF_TASKS` WRITE;
/*!40000 ALTER TABLE `STAFF_TASKS` DISABLE KEYS */;
INSERT INTO `STAFF_TASKS` VALUES (1,'2023-01-05','10:00:00','Team Practice'),(2,'2023-01-10','11:30:00','Individual Training'),(3,'2023-01-15','14:00:00','Rehabilitation Session'),(4,'2023-01-20','16:30:00','Team Strategy Meeting'),(5,'2023-01-25','17:45:00','Event Coordination');
/*!40000 ALTER TABLE `STAFF_TASKS` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `STUDENT_ACAD_DETAILS`
--

DROP TABLE IF EXISTS `STUDENT_ACAD_DETAILS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `STUDENT_ACAD_DETAILS` (
  `Student_ID` int NOT NULL,
  `Department` varchar(50) NOT NULL,
  `Course_Year` varchar(50) NOT NULL,
  `Credits_Done` int NOT NULL,
  PRIMARY KEY (`Student_ID`),
  CONSTRAINT `student_acad_details_ibfk_1` FOREIGN KEY (`Student_ID`) REFERENCES `STUDENT_PERSONAL_DETAILS` (`Student_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `STUDENT_ACAD_DETAILS`
--

LOCK TABLES `STUDENT_ACAD_DETAILS` WRITE;
/*!40000 ALTER TABLE `STUDENT_ACAD_DETAILS` DISABLE KEYS */;
INSERT INTO `STUDENT_ACAD_DETAILS` VALUES (1,'CSE','2022',2),(2,'ECE','2023',3),(3,'CSE','2021',1),(4,'CSE','2022',4),(5,'ECE','2022',2);
/*!40000 ALTER TABLE `STUDENT_ACAD_DETAILS` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `STUDENT_HEALTH_DETAILS`
--

DROP TABLE IF EXISTS `STUDENT_HEALTH_DETAILS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `STUDENT_HEALTH_DETAILS` (
  `Student_ID` int NOT NULL,
  `Health_Issue` varchar(100) NOT NULL,
  PRIMARY KEY (`Student_ID`),
  CONSTRAINT `student_health_details_ibfk_1` FOREIGN KEY (`Student_ID`) REFERENCES `STUDENT_PERSONAL_DETAILS` (`Student_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `STUDENT_HEALTH_DETAILS`
--

LOCK TABLES `STUDENT_HEALTH_DETAILS` WRITE;
/*!40000 ALTER TABLE `STUDENT_HEALTH_DETAILS` DISABLE KEYS */;
INSERT INTO `STUDENT_HEALTH_DETAILS` VALUES (1,'Allergies'),(2,'Asthma'),(3,'No health issues'),(4,'Vision problems'),(5,'Diabetes');
/*!40000 ALTER TABLE `STUDENT_HEALTH_DETAILS` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `STUDENT_PERSONAL_DETAILS`
--

DROP TABLE IF EXISTS `STUDENT_PERSONAL_DETAILS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `STUDENT_PERSONAL_DETAILS` (
  `Student_ID` int NOT NULL,
  `First_Name` varchar(50) NOT NULL,
  `Last_Name` varchar(50) NOT NULL,
  `Date_of_Birth` date NOT NULL,
  `Contact` varchar(15) NOT NULL,
  PRIMARY KEY (`Student_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `STUDENT_PERSONAL_DETAILS`
--

LOCK TABLES `STUDENT_PERSONAL_DETAILS` WRITE;
/*!40000 ALTER TABLE `STUDENT_PERSONAL_DETAILS` DISABLE KEYS */;
INSERT INTO `STUDENT_PERSONAL_DETAILS` VALUES (1,'Ritvik','M','2004-01-01','+91-3456789012'),(2,'Revanth','S','2005-05-15','+91-7654321098'),(3,'Dileep','A','2004-08-22','+91-6543210987'),(4,'Keshav','V','2003-03-10','+91-4567890123'),(5,'Danny','A','2004-11-28','+91-5678901234');
/*!40000 ALTER TABLE `STUDENT_PERSONAL_DETAILS` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `STUDENT_SPORT_DETAILS`
--

DROP TABLE IF EXISTS `STUDENT_SPORT_DETAILS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `STUDENT_SPORT_DETAILS` (
  `Student_ID` int NOT NULL,
  `Assigned_Sport` int DEFAULT NULL,
  `Attendence` int NOT NULL,
  PRIMARY KEY (`Student_ID`),
  KEY `Assigned_Sport` (`Assigned_Sport`),
  CONSTRAINT `student_sport_details_ibfk_1` FOREIGN KEY (`Student_ID`) REFERENCES `STUDENT_PERSONAL_DETAILS` (`Student_ID`) ON DELETE CASCADE,
  CONSTRAINT `student_sport_details_ibfk_2` FOREIGN KEY (`Assigned_Sport`) REFERENCES `SPORTS` (`Sport_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `STUDENT_SPORT_DETAILS`
--

LOCK TABLES `STUDENT_SPORT_DETAILS` WRITE;
/*!40000 ALTER TABLE `STUDENT_SPORT_DETAILS` DISABLE KEYS */;
INSERT INTO `STUDENT_SPORT_DETAILS` VALUES (1,1,90),(2,2,85),(3,3,92),(4,4,88),(5,5,94);
/*!40000 ALTER TABLE `STUDENT_SPORT_DETAILS` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `TRANSACTIONS`
--

DROP TABLE IF EXISTS `TRANSACTIONS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `TRANSACTIONS` (
  `Transaction_ID` int NOT NULL,
  `Amount` int NOT NULL,
  `Status` varchar(50) NOT NULL,
  PRIMARY KEY (`Transaction_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TRANSACTIONS`
--

LOCK TABLES `TRANSACTIONS` WRITE;
/*!40000 ALTER TABLE `TRANSACTIONS` DISABLE KEYS */;
INSERT INTO `TRANSACTIONS` VALUES (1,5000,'Completed'),(2,7000,'Pending'),(3,3000,'Completed'),(4,4500,'Pending'),(5,6000,'Completed');
/*!40000 ALTER TABLE `TRANSACTIONS` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-12-02 15:57:59
