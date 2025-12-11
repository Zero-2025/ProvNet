-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: internet__provider02
-- ------------------------------------------------------
-- Server version	8.0.41

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `activitylogs`
--

DROP TABLE IF EXISTS `activitylogs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `activitylogs` (
  `LogID` int NOT NULL AUTO_INCREMENT,
  `UserID` int DEFAULT NULL,
  `UserType` enum('Admin','Client','System') COLLATE utf8mb4_unicode_ci DEFAULT 'System',
  `Action` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Description` text COLLATE utf8mb4_unicode_ci,
  `IPAddress` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `UserAgent` text COLLATE utf8mb4_unicode_ci,
  `CreatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`LogID`),
  KEY `idx_user` (`UserID`,`UserType`),
  KEY `idx_action` (`Action`),
  KEY `idx_created` (`CreatedAt`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activitylogs`
--

LOCK TABLES `activitylogs` WRITE;
/*!40000 ALTER TABLE `activitylogs` DISABLE KEYS */;
INSERT INTO `activitylogs` VALUES (1,1,'Admin','LOGIN','Вход в систему администрирования','192.168.1.1',NULL,'2025-12-11 05:39:44'),(2,1,'Client','PAYMENT','Пополнение баланса на 1000 руб.','192.168.1.100',NULL,'2025-12-11 05:39:44'),(3,NULL,'System','BACKUP','Автоматическое резервное копирование базы данных','127.0.0.1',NULL,'2025-12-11 05:39:44');
/*!40000 ALTER TABLE `activitylogs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `balancehistory`
--

DROP TABLE IF EXISTS `balancehistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `balancehistory` (
  `HistoryID` int NOT NULL AUTO_INCREMENT,
  `ClientID` int NOT NULL,
  `OldBalance` decimal(10,2) NOT NULL,
  `NewBalance` decimal(10,2) NOT NULL,
  `ChangeAmount` decimal(10,2) NOT NULL,
  `ChangeType` enum('Payment','Tariff','Service','Correction','Refund','Penalty') COLLATE utf8mb4_unicode_ci DEFAULT 'Payment',
  `Description` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `RelatedID` int DEFAULT NULL,
  `CreatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`HistoryID`),
  KEY `idx_client` (`ClientID`),
  KEY `idx_date` (`CreatedAt`),
  KEY `idx_type` (`ChangeType`),
  CONSTRAINT `balancehistory_ibfk_1` FOREIGN KEY (`ClientID`) REFERENCES `clients` (`ClientID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `balancehistory`
--

LOCK TABLES `balancehistory` WRITE;
/*!40000 ALTER TABLE `balancehistory` DISABLE KEYS */;
INSERT INTO `balancehistory` VALUES (4,2,0.00,3000.00,3000.00,'Payment','Платеж #5: Пополнение баланса на 3,000.00 руб.',5,'2025-12-11 06:10:09'),(5,2,0.00,3000.00,3000.00,'Payment','Пополнение баланса на 3,000.00 руб.',5,'2025-12-11 06:10:09');
/*!40000 ALTER TABLE `balancehistory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clients`
--

DROP TABLE IF EXISTS `clients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clients` (
  `ClientID` int NOT NULL AUTO_INCREMENT,
  `UserID` int NOT NULL,
  `Username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `PasswordHash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `FirstName` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `LastName` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `MiddleName` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `DateOfBirth` date DEFAULT NULL,
  `PassportSeries` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `PassportNumber` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `IssueDate` date DEFAULT NULL,
  `IssuedBy` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `RegistrationAddress` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ActualAddress` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `PhoneNumber` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `IsActive` tinyint(1) DEFAULT '1',
  `Balance` decimal(10,2) DEFAULT '0.00',
  `PersonalDiscount` decimal(5,2) DEFAULT '0.00',
  `CreationDate` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `Notes` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`ClientID`),
  UNIQUE KEY `Username` (`Username`),
  UNIQUE KEY `PhoneNumber` (`PhoneNumber`),
  KEY `idx_username` (`Username`),
  KEY `idx_phone` (`PhoneNumber`),
  KEY `idx_active` (`IsActive`),
  KEY `idx_user` (`UserID`),
  CONSTRAINT `clients_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clients`
--

LOCK TABLES `clients` WRITE;
/*!40000 ALTER TABLE `clients` DISABLE KEYS */;
INSERT INTO `clients` VALUES (2,3,'111','bcb15f821479b4d5772bd0ca866c00ad5f926e3580720659cc80d39c9d09802a','111','111','',NULL,'111','111',NULL,'','111','','111','111',1,3000.00,0.00,'2025-12-11 06:08:42',NULL);
/*!40000 ALTER TABLE `clients` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clientservices`
--

DROP TABLE IF EXISTS `clientservices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clientservices` (
  `ClientServiceID` int NOT NULL AUTO_INCREMENT,
  `ConnectionID` int NOT NULL,
  `ServiceID` int NOT NULL,
  `MonthlyCost` decimal(10,2) NOT NULL,
  `ActivationDate` date NOT NULL,
  `DeactivationDate` date DEFAULT NULL,
  `IsActive` tinyint(1) DEFAULT '1',
  `CreatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `UpdatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ClientServiceID`),
  KEY `idx_connection` (`ConnectionID`),
  KEY `idx_service` (`ServiceID`),
  KEY `idx_active` (`IsActive`),
  CONSTRAINT `clientservices_ibfk_1` FOREIGN KEY (`ConnectionID`) REFERENCES `connections` (`ConnectionID`) ON DELETE CASCADE,
  CONSTRAINT `clientservices_ibfk_2` FOREIGN KEY (`ServiceID`) REFERENCES `services` (`ServiceID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clientservices`
--

LOCK TABLES `clientservices` WRITE;
/*!40000 ALTER TABLE `clientservices` DISABLE KEYS */;
INSERT INTO `clientservices` VALUES (3,2,5,300.00,'2025-12-11',NULL,1,'2025-12-11 06:09:48','2025-12-11 06:09:48'),(4,2,3,150.00,'2025-12-11',NULL,1,'2025-12-11 06:09:55','2025-12-11 06:09:55');
/*!40000 ALTER TABLE `clientservices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `connections`
--

DROP TABLE IF EXISTS `connections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `connections` (
  `ConnectionID` int NOT NULL AUTO_INCREMENT,
  `ClientID` int NOT NULL,
  `TariffID` int NOT NULL,
  `ConnectionDate` date NOT NULL,
  `Status` enum('Active','Suspended','Terminated','Pending') COLLATE utf8mb4_unicode_ci DEFAULT 'Active',
  `MonthlyPayment` decimal(10,2) NOT NULL,
  `NextPaymentDate` date DEFAULT NULL,
  `TerminationDate` date DEFAULT NULL,
  `TerminationReason` text COLLATE utf8mb4_unicode_ci,
  `CreatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `UpdatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ConnectionID`),
  KEY `idx_client` (`ClientID`),
  KEY `idx_status` (`Status`),
  KEY `idx_tariff` (`TariffID`),
  CONSTRAINT `connections_ibfk_1` FOREIGN KEY (`ClientID`) REFERENCES `clients` (`ClientID`) ON DELETE CASCADE,
  CONSTRAINT `connections_ibfk_2` FOREIGN KEY (`TariffID`) REFERENCES `tariffplans` (`TariffID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `connections`
--

LOCK TABLES `connections` WRITE;
/*!40000 ALTER TABLE `connections` DISABLE KEYS */;
INSERT INTO `connections` VALUES (2,2,1,'2025-12-11','Active',300.00,'2026-01-11',NULL,NULL,'2025-12-11 06:08:42','2025-12-11 06:08:42');
/*!40000 ALTER TABLE `connections` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `equipment`
--

DROP TABLE IF EXISTS `equipment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipment` (
  `EquipmentID` int NOT NULL AUTO_INCREMENT,
  `ClientID` int NOT NULL,
  `EquipmentType` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Model` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `SerialNumber` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `MACAddress` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `IPAddress` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `InstallationDate` date DEFAULT NULL,
  `Status` enum('Active','Inactive','Maintenance','Replaced') COLLATE utf8mb4_unicode_ci DEFAULT 'Active',
  `Notes` text COLLATE utf8mb4_unicode_ci,
  `CreatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `UpdatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`EquipmentID`),
  KEY `idx_client` (`ClientID`),
  KEY `idx_status` (`Status`),
  KEY `idx_type` (`EquipmentType`),
  CONSTRAINT `equipment_ibfk_1` FOREIGN KEY (`ClientID`) REFERENCES `clients` (`ClientID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equipment`
--

LOCK TABLES `equipment` WRITE;
/*!40000 ALTER TABLE `equipment` DISABLE KEYS */;
/*!40000 ALTER TABLE `equipment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `maintenance`
--

DROP TABLE IF EXISTS `maintenance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `maintenance` (
  `MaintenanceID` int NOT NULL AUTO_INCREMENT,
  `Title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Description` text COLLATE utf8mb4_unicode_ci,
  `Type` enum('Planned','Emergency','Upgrade') COLLATE utf8mb4_unicode_ci DEFAULT 'Planned',
  `StartTime` timestamp NOT NULL,
  `EndTime` timestamp NOT NULL,
  `AffectedClients` text COLLATE utf8mb4_unicode_ci,
  `Status` enum('Scheduled','In Progress','Completed','Cancelled') COLLATE utf8mb4_unicode_ci DEFAULT 'Scheduled',
  `CreatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `UpdatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`MaintenanceID`),
  KEY `idx_status` (`Status`),
  KEY `idx_time` (`StartTime`),
  KEY `idx_type` (`Type`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `maintenance`
--

LOCK TABLES `maintenance` WRITE;
/*!40000 ALTER TABLE `maintenance` DISABLE KEYS */;
INSERT INTO `maintenance` VALUES (1,'Плановые работы на оборудовании','Профилактические работы на узловом оборудовании. Возможны кратковременные перебои в работе.','Planned','2025-12-14 05:39:44','2025-12-15 05:39:44',NULL,'Scheduled','2025-12-11 05:39:44','2025-12-11 05:39:44'),(2,'Аварийные работы','Устранение последствий грозы на линии связи','Emergency','2025-12-11 05:39:44','2025-12-11 07:39:44',NULL,'Completed','2025-12-11 05:39:44','2025-12-11 05:39:44');
/*!40000 ALTER TABLE `maintenance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `NotificationID` int NOT NULL AUTO_INCREMENT,
  `ClientID` int NOT NULL,
  `Title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Message` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `Type` enum('Payment','Service','Tariff','Promotion','System','Warning') COLLATE utf8mb4_unicode_ci DEFAULT 'System',
  `IsRead` tinyint(1) DEFAULT '0',
  `IsImportant` tinyint(1) DEFAULT '0',
  `CreatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `ReadAt` timestamp NULL DEFAULT NULL,
  `ActionURL` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`NotificationID`),
  KEY `idx_client` (`ClientID`),
  KEY `idx_type` (`Type`),
  KEY `idx_read` (`IsRead`),
  KEY `idx_created` (`CreatedAt`),
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`ClientID`) REFERENCES `clients` (`ClientID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
INSERT INTO `notifications` VALUES (5,2,'Добро пожаловать!','Спасибо за регистрацию в нашей системе! Ваш аккаунт успешно создан.','Promotion',0,0,'2025-12-11 06:08:42',NULL,NULL),(6,2,'Новая услуга подключена','Услуга \'IP-телевидение\' успешно подключена. Стоимость: 300.00 руб./мес.','Service',0,0,'2025-12-11 06:09:48',NULL,NULL),(7,2,'Новая услуга подключена','Услуга \'Антивирусная защита\' успешно подключена. Стоимость: 150.00 руб./мес.','Service',0,0,'2025-12-11 06:09:55',NULL,NULL),(8,2,'Платеж успешно проведен','Платеж на сумму 3000.00 руб. успешно проведен. Описание: Пополнение баланса на 3,000.00 руб.','Payment',0,0,'2025-12-11 06:10:09',NULL,NULL),(9,2,'Баланс пополнен на 3000.0 руб.','Ваш баланс пополнен на 3000.0 руб. Новый баланс: 3,000.00 руб.','Payment',0,0,'2025-12-11 06:10:09',NULL,NULL);
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `PaymentID` int NOT NULL AUTO_INCREMENT,
  `ClientID` int NOT NULL,
  `Amount` decimal(10,2) NOT NULL,
  `PaymentDate` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `PaymentMethod` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'Банковская карта',
  `PaymentPeriod` date DEFAULT NULL,
  `Status` enum('Pending','Completed','Failed','Refunded') COLLATE utf8mb4_unicode_ci DEFAULT 'Completed',
  `Description` text COLLATE utf8mb4_unicode_ci,
  `TransactionID` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ReceiptNumber` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `CreatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `UpdatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`PaymentID`),
  KEY `idx_client` (`ClientID`),
  KEY `idx_date` (`PaymentDate`),
  KEY `idx_status` (`Status`),
  KEY `idx_method` (`PaymentMethod`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`ClientID`) REFERENCES `clients` (`ClientID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments`
--

LOCK TABLES `payments` WRITE;
/*!40000 ALTER TABLE `payments` DISABLE KEYS */;
INSERT INTO `payments` VALUES (5,2,3000.00,'2025-12-11 06:10:09','Банковская карта',NULL,'Completed','Пополнение баланса на 3,000.00 руб.',NULL,NULL,'2025-12-11 06:10:09','2025-12-11 06:10:09');
/*!40000 ALTER TABLE `payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `services`
--

DROP TABLE IF EXISTS `services`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `services` (
  `ServiceID` int NOT NULL AUTO_INCREMENT,
  `ServiceName` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `MonthlyCost` decimal(10,2) NOT NULL,
  `Description` text COLLATE utf8mb4_unicode_ci,
  `IsActive` tinyint(1) DEFAULT '1',
  `CreatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `UpdatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ServiceID`),
  UNIQUE KEY `ServiceName` (`ServiceName`),
  KEY `idx_name` (`ServiceName`),
  KEY `idx_active` (`IsActive`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `services`
--

LOCK TABLES `services` WRITE;
/*!40000 ALTER TABLE `services` DISABLE KEYS */;
INSERT INTO `services` VALUES (1,'Статический IP',100.00,'Выделенный статический IP-адрес',1,'2025-12-11 05:39:44','2025-12-11 05:39:44'),(2,'Родительский контроль',50.00,'Ограничение доступа к нежелательным сайтам',1,'2025-12-11 05:39:44','2025-12-11 05:39:44'),(3,'Антивирусная защита',150.00,'Защита от вирусов и вредоносных программ',1,'2025-12-11 05:39:44','2025-12-11 05:39:44'),(4,'Резервное копирование',200.00,'Облачное резервное копирование данных 100 ГБ',1,'2025-12-11 05:39:44','2025-12-11 05:39:44'),(5,'IP-телевидение',300.00,'Доступ к более чем 100 каналам',1,'2025-12-11 05:39:44','2025-12-11 05:39:44'),(6,'Игровой режим',100.00,'Оптимизация для онлайн-игр',1,'2025-12-11 05:39:44','2025-12-11 05:39:44'),(7,'Облачное хранилище 1ТБ',500.00,'1 ТБ облачного пространства',1,'2025-12-11 05:39:44','2025-12-11 05:39:44'),(8,'Техническая поддержка 24/7',200.00,'Круглосуточная техническая поддержка',1,'2025-12-11 05:39:44','2025-12-11 05:39:44');
/*!40000 ALTER TABLE `services` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `supporttickets`
--

DROP TABLE IF EXISTS `supporttickets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `supporttickets` (
  `TicketID` int NOT NULL AUTO_INCREMENT,
  `ClientID` int NOT NULL,
  `Subject` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Description` text COLLATE utf8mb4_unicode_ci,
  `Category` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT 'Другое',
  `Status` enum('Open','In Progress','Resolved','Closed') COLLATE utf8mb4_unicode_ci DEFAULT 'Open',
  `Priority` enum('Низкий','Средний','Высокий','Критический') COLLATE utf8mb4_unicode_ci DEFAULT 'Средний',
  `AssignedTo` int DEFAULT NULL,
  `CreatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `UpdatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `ResolvedAt` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`TicketID`),
  KEY `idx_client` (`ClientID`),
  KEY `idx_status` (`Status`),
  KEY `idx_category` (`Category`),
  KEY `idx_priority` (`Priority`),
  CONSTRAINT `supporttickets_ibfk_1` FOREIGN KEY (`ClientID`) REFERENCES `clients` (`ClientID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `supporttickets`
--

LOCK TABLES `supporttickets` WRITE;
/*!40000 ALTER TABLE `supporttickets` DISABLE KEYS */;
/*!40000 ALTER TABLE `supporttickets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `systemsettings`
--

DROP TABLE IF EXISTS `systemsettings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `systemsettings` (
  `SettingID` int NOT NULL AUTO_INCREMENT,
  `SettingKey` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `SettingValue` text COLLATE utf8mb4_unicode_ci,
  `SettingType` enum('String','Number','Boolean','JSON','Array') COLLATE utf8mb4_unicode_ci DEFAULT 'String',
  `Category` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `CreatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `UpdatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`SettingID`),
  UNIQUE KEY `SettingKey` (`SettingKey`),
  KEY `idx_key` (`SettingKey`),
  KEY `idx_category` (`Category`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `systemsettings`
--

LOCK TABLES `systemsettings` WRITE;
/*!40000 ALTER TABLE `systemsettings` DISABLE KEYS */;
INSERT INTO `systemsettings` VALUES (1,'company_name','Интернет-Провайдер \"Скорость+\"','String','General','Название компании','2025-12-11 05:39:44','2025-12-11 05:39:44'),(2,'company_email','support@speed-plus.ru','String','General','Основной email компании','2025-12-11 05:39:44','2025-12-11 05:39:44'),(3,'company_phone','+7 (800) 123-45-67','String','General','Телефон поддержки','2025-12-11 05:39:44','2025-12-11 05:39:44'),(4,'minimum_balance','0','Number','Billing','Минимальный допустимый баланс','2025-12-11 05:39:44','2025-12-11 05:39:44'),(5,'payment_grace_period','7','Number','Billing','Льготный период для платежей (дней)','2025-12-11 05:39:44','2025-12-11 05:39:44'),(6,'late_fee_percent','0.5','Number','Billing','Процент пени за просрочку','2025-12-11 05:39:44','2025-12-11 05:39:44'),(7,'notification_enabled','true','Boolean','Notifications','Включить отправку уведомлений','2025-12-11 05:39:44','2025-12-11 05:39:44'),(8,'maintenance_mode','false','Boolean','System','Режим технического обслуживания','2025-12-11 05:39:44','2025-12-11 05:39:44'),(9,'tax_rate','20','Number','Billing','Процент НДС','2025-12-11 05:39:44','2025-12-11 05:39:44'),(10,'currency','RUB','String','Billing','Основная валюта','2025-12-11 05:39:44','2025-12-11 05:39:44');
/*!40000 ALTER TABLE `systemsettings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tariffplans`
--

DROP TABLE IF EXISTS `tariffplans`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tariffplans` (
  `TariffID` int NOT NULL AUTO_INCREMENT,
  `TariffName` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `DownloadSpeedMbps` int NOT NULL,
  `UploadSpeedMbps` int NOT NULL,
  `MonthlyCost` decimal(10,2) NOT NULL,
  `Description` text COLLATE utf8mb4_unicode_ci,
  `IsActive` tinyint(1) DEFAULT '1',
  `CreatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `UpdatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`TariffID`),
  UNIQUE KEY `TariffName` (`TariffName`),
  KEY `idx_name` (`TariffName`),
  KEY `idx_active` (`IsActive`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tariffplans`
--

LOCK TABLES `tariffplans` WRITE;
/*!40000 ALTER TABLE `tariffplans` DISABLE KEYS */;
INSERT INTO `tariffplans` VALUES (1,'Экономный',50,10,300.00,'Базовый тариф для экономных пользователей',1,'2025-12-11 05:39:44','2025-12-11 05:39:44'),(2,'Стандартный',100,30,500.00,'Популярный тариф для дома и семьи',1,'2025-12-11 05:39:44','2025-12-11 05:39:44'),(3,'Продвинутый',200,100,800.00,'Для требовательных пользователей и геймеров',1,'2025-12-11 05:39:44','2025-12-11 05:39:44'),(4,'Безлимитный',500,200,1500.00,'Максимальная скорость без ограничений',1,'2025-12-11 05:39:44','2025-12-11 05:39:44'),(5,'Бизнес',1000,500,3000.00,'Для бизнеса и корпоративных клиентов',1,'2025-12-11 05:39:44','2025-12-11 05:39:44');
/*!40000 ALTER TABLE `tariffplans` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ticketmessages`
--

DROP TABLE IF EXISTS `ticketmessages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ticketmessages` (
  `MessageID` int NOT NULL AUTO_INCREMENT,
  `TicketID` int NOT NULL,
  `SenderType` enum('Client','Support','System') COLLATE utf8mb4_unicode_ci DEFAULT 'Client',
  `SenderID` int DEFAULT NULL,
  `MessageText` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `Attachments` text COLLATE utf8mb4_unicode_ci,
  `IsRead` tinyint(1) DEFAULT '0',
  `CreatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`MessageID`),
  KEY `idx_ticket` (`TicketID`),
  KEY `idx_sender` (`SenderType`,`SenderID`),
  KEY `idx_created` (`CreatedAt`),
  CONSTRAINT `ticketmessages_ibfk_1` FOREIGN KEY (`TicketID`) REFERENCES `supporttickets` (`TicketID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ticketmessages`
--

LOCK TABLES `ticketmessages` WRITE;
/*!40000 ALTER TABLE `ticketmessages` DISABLE KEYS */;
/*!40000 ALTER TABLE `ticketmessages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` enum('admin','user','client') COLLATE utf8mb4_unicode_ci DEFAULT 'client',
  `is_active` tinyint(1) DEFAULT '1',
  `failed_attempts` int DEFAULT '0',
  `last_login` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  KEY `idx_username` (`username`),
  KEY `idx_role` (`role`),
  KEY `idx_active` (`is_active`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9','admin',1,0,'2025-12-11 06:10:32','2025-12-11 05:39:44','2025-12-11 06:10:32'),(3,'111','bcb15f821479b4d5772bd0ca866c00ad5f926e3580720659cc80d39c9d09802a','client',1,0,'2025-12-11 06:36:41','2025-12-11 06:08:42','2025-12-11 06:36:41');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-11 12:49:45
