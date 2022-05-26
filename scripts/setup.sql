/* 
initialize the database if it isnt already initialized
*/
CREATE DATABASE IF NOT EXISTS TitCoin;
USE TitCoin;

/* profiles of all members, along with their balances */
CREATE TABLE IF NOT EXISTS Profiles(
    discordID BIGINT NOT NULL,
    balance DOUBLE NOT NULL DEFAULT 0,
    PRIMARY KEY(discordID)
);

/* log of balance changes */
CREATE TABLE IF NOT EXISTS BalanceHistory(
    PID BIGINT,
    FOREIGN KEY(PID) REFERENCES Profiles(id),
    balance FLOAT NOT NULL,
    tag TEXT,
    timestamp DATETIME NOT NULL
);

/* all companies, along with their associated owners */
CREATE TABLE IF NOT EXISTS Companies(
    CID INT AUTO_INCREMENT,
    PID BIGINT,
    FOREIGN KEY(PID) REFERENCES Profiles(id),
    companyName TEXT NOT NULL,
    worth DOUBLE NOT NULL,
    shares INT,
    PRIMARY KEY(CID)
);

/* history of worth of companies */
CREATE TABLE IF NOT EXISTS WorthHistory(
    CID INT,
    FOREIGN KEY(CID) REFERENCES Companies(id),
    worth FLOAT NOT NULL,
    tag TEXT,
    timestamp DATETIME NOT NULL
);

/* record of share ownership */
CREATE TABLE IF NOT EXISTS Shares(
    ShareID INT AUTO_INCREMENT NOT NULL,
    PID BIGINT,
    CID INT,
    FOREIGN KEY(PID) REFERENCES Profiles(id),
    FOREIGN KEY(CID) REFERENCES Companies(id),
    numShares BIGINT NOT NULL,
    PRIMARY KEY(ShareID)
);