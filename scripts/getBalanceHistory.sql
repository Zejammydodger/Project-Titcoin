SET @PID = {};
SELECT balance , created FROM BalanceHistory WHERE PID = @PID LIMIT 30;