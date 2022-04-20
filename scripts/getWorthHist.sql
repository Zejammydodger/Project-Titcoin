SET @CID = {};
SELECT created , worth FROM WorthHistory WHERE CID = @CID LIMIT 30;