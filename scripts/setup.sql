/* 
initialize the database if it isnt already initialized
*/
CREATE DATABASE IF NOT EXISTS TitCoin;
USE TitCoin;

CREATE TABLE IF NOT EXISTS Profiles(
    discordID BIGINT NOT NULL,
    PRIMARY KEY(discordID)
);

CREATE TABLE IF NOT EXISTS Companies(
    CID INT AUTO_INCREMENT,
    PID INT,
    FOREIGN KEY(PID) REFERENCES Profiles(discordID), 
    CompanyName TEXT NOT NULL,
    PRIMARY KEY(CID)
);

CREATE TABLE IF NOT EXISTS WorthHistory(
    CID INT,
    FOREIGN KEY(CID) REFERENCES Companies(CID),
    created DATETIME NOT NULL,
    worth FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS Shares(
    ShareID INT AUTO_INCREMENT NOT NULL,
    PID INT,
    CID INT,
    FOREIGN KEY(PID) REFERENCES Profiles(discordID),
    FOREIGN KEY(CID) REFERENCES Companies(CID),
    percent FLOAT NOT NULL,
    PRIMARY KEY(ShareID)
);

CREATE TABLE IF NOT EXISTS BalanceHistory(
    PID INT,
    FOREIGN KEY(PID) REFERENCES Profiles(discordID),
    balance FLOAT NOT NULL,
    created DATETIME NOT NULL
);