-- MySQL dump 10.13  Distrib 5.6.17, for Win32 (x86)
--
-- Host: awsdbinstance.cz5m3w6kwml8.us-east-1.rds.amazonaws.com    Database: comment_iq
-- ------------------------------------------------------
-- Server version	5.6.19-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `articles`
--

DROP TABLE IF EXISTS `articles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `articles` (
  `articleID` int(11) NOT NULL AUTO_INCREMENT,
  `pubDate` datetime DEFAULT NULL,
  `headline` text,
  `full_text` text,
  PRIMARY KEY (`articleID`)
) ENGINE=InnoDB AUTO_INCREMENT=131 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `comments`
--

DROP TABLE IF EXISTS `comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `comments` (
  `commentID` int(11) NOT NULL AUTO_INCREMENT,
  `commentBody` text,
  `creationDate` datetime DEFAULT NULL,
  `commentDate` datetime DEFAULT NULL,
  `recommendationCount` int(11) DEFAULT NULL,
  `username` text,
  `location` text,
  `articleID` int(11) DEFAULT NULL,
  `editorsSelection` int(11) DEFAULT NULL,
  `ArticleRelevance` text,
  `ConversationalRelevance` text,
  `PersonalXP` text,
  `Readability` text,
  `CommentLength` text,
  PRIMARY KEY (`commentID`),
  KEY `new index` (`articleID`)
) ENGINE=InnoDB AUTO_INCREMENT=5066 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vocab_comments`
--

DROP TABLE IF EXISTS `vocab_comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vocab_comments` (
  `commentID` int(11) NOT NULL AUTO_INCREMENT,
  `commentBody` text,
  `approveDate` datetime DEFAULT NULL,
  `recommendationCount` int(11) DEFAULT NULL,
  `display_name` text,
  `location` text,
  `commentSequence` int(11) DEFAULT NULL,
  `status` text,
  `articleURL` varchar(200) DEFAULT NULL,
  `editorsSelection` int(11) DEFAULT NULL,
  PRIMARY KEY (`commentID`),
  KEY `new_index` (`articleURL`)
) ENGINE=InnoDB AUTO_INCREMENT=358339 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-05-01 20:45:02
