USE traveloop;

ALTER TABLE users ADD COLUMN IF NOT EXISTS tagline VARCHAR(150) DEFAULT NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS location VARCHAR(150) DEFAULT NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT DEFAULT NULL;

ALTER TABLE cities ADD COLUMN IF NOT EXISTS currency_code CHAR(3) DEFAULT 'INR';
ALTER TABLE cities ADD COLUMN IF NOT EXISTS emergency_police VARCHAR(50) DEFAULT NULL;
ALTER TABLE cities ADD COLUMN IF NOT EXISTS emergency_ambulance VARCHAR(50) DEFAULT NULL;
ALTER TABLE cities ADD COLUMN IF NOT EXISTS emergency_fire VARCHAR(50) DEFAULT NULL;
ALTER TABLE cities ADD COLUMN IF NOT EXISTS emergency_tourist_helpline VARCHAR(50) DEFAULT NULL;

UPDATE cities SET currency_code='EUR', emergency_police='112', emergency_ambulance='112', emergency_fire='112', emergency_tourist_helpline='112' WHERE name='Paris';
UPDATE cities SET currency_code='JPY', emergency_police='110', emergency_ambulance='119', emergency_fire='119', emergency_tourist_helpline='050-3816-2787' WHERE name='Tokyo';
UPDATE cities SET currency_code='USD', emergency_police='911', emergency_ambulance='911', emergency_fire='911', emergency_tourist_helpline='311' WHERE name='New York';
UPDATE cities SET currency_code='IDR', emergency_police='110', emergency_ambulance='118', emergency_fire='113', emergency_tourist_helpline='+62 361 222387' WHERE name='Bali';
UPDATE cities SET currency_code='GBP', emergency_police='999', emergency_ambulance='999', emergency_fire='999', emergency_tourist_helpline='101' WHERE name='London';
UPDATE cities SET currency_code='EUR', emergency_police='112', emergency_ambulance='112', emergency_fire='112', emergency_tourist_helpline='039039039' WHERE name='Rome';
UPDATE cities SET currency_code='THB', emergency_police='191', emergency_ambulance='1669', emergency_fire='199', emergency_tourist_helpline='1672' WHERE name='Bangkok';
UPDATE cities SET currency_code='AED', emergency_police='999', emergency_ambulance='998', emergency_fire='997', emergency_tourist_helpline='8004438' WHERE name='Dubai';
UPDATE cities SET currency_code='EUR', emergency_police='112', emergency_ambulance='112', emergency_fire='112', emergency_tourist_helpline='010' WHERE name='Barcelona';
UPDATE cities SET currency_code='AUD', emergency_police='000', emergency_ambulance='000', emergency_fire='000', emergency_tourist_helpline='131444' WHERE name='Sydney';
UPDATE cities SET currency_code='INR', emergency_police='100', emergency_ambulance='108', emergency_fire='101', emergency_tourist_helpline='1363' WHERE name='Mumbai';
UPDATE cities SET currency_code='ZAR', emergency_police='10111', emergency_ambulance='10177', emergency_fire='10177', emergency_tourist_helpline='0861322223' WHERE name='Cape Town';
