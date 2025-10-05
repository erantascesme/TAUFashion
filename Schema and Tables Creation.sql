-- Create the schema
CREATE SCHEMA IF NOT EXISTS TAUFashion;
USE TAUFashion;

-- 1. Users table
CREATE TABLE Users (
    email VARCHAR(255) NOT NULL,
    username VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    date_of_birth DATE NOT NULL,
    faculty VARCHAR(255) NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    PRIMARY KEY (email)
);

-- 2. Products table
CREATE TABLE Products (
    catalog_number INT NOT NULL AUTO_INCREMENT,
    product_name VARCHAR(255) NOT NULL,
    amount_in_stock INT NOT NULL,
    cost DECIMAL(10, 2) NOT NULL,
    image_url VARCHAR(255),
    is_campaign BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (catalog_number)
);

-- 3. Transactions table
CREATE TABLE Transactions (
    order_id INT NOT NULL AUTO_INCREMENT,
    user_email VARCHAR(255) NOT NULL,
    order_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (order_id),
    FOREIGN KEY (user_email) REFERENCES Users(email) ON DELETE CASCADE
);

-- 4. Transaction Details table
CREATE TABLE TransactionDetails (
    order_id INT NOT NULL,
    product_catalog_number INT NOT NULL,
    quantity INT NOT NULL,
    PRIMARY KEY (order_id, product_catalog_number),
    FOREIGN KEY (order_id) REFERENCES Transactions(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_catalog_number) REFERENCES Products(catalog_number) ON DELETE CASCADE
);


-- Insert administrators into Users table
INSERT INTO Users (email, username, password, is_admin) VALUES
('omer@taufashion.com', 'omer', 'omer123', TRUE),
('yarden@taufashion.com', 'yarden', 'yarden123', TRUE),
('ben@taufashion.com', 'ben', 'ben123', TRUE);

-- Insert products into Products table
-- 3 Men's Shirts
INSERT INTO Products (product_name, amount_in_stock, cost, image_url, is_campaign) VALUES
('Men\'s Shirt 1', 50, 49.9, 'https://i.pinimg.com/564x/b9/52/dc/b952dc0a29a5cd3796b726e208b44d90.jpg', FALSE),
('Men\'s Shirt 2', 30, 69.9, 'https://i.pinimg.com/564x/79/e7/36/79e7361fd76c6feee174b59a1b49d60d.jpg', TRUE),
('Men\'s Shirt 3', 20, 89.9, 'https://i.pinimg.com/564x/83/c7/21/83c7217d8a51e9025868350c1d5caf76.jpg', FALSE);

-- 3 Women's Shirts
INSERT INTO Products (product_name, amount_in_stock, cost, image_url, is_campaign) VALUES
('Women\'s Shirt 1', 40, 39.99, 'https://i.pinimg.com/564x/50/ad/84/50ad842eca4400903eccd0f26f85a4f0.jpg', TRUE),
('Women\'s Shirt 2', 25, 59.99, 'https://i.pinimg.com/564x/24/cf/ec/24cfec073859b0677762c92ed99cb957.jpg', FALSE),
('Women\'s Shirt 3', 15, 79.99, 'https://i.pinimg.com/564x/d0/0d/5f/d00d5f6c6ac786e48476a0ffda9d88a1.jpg', FALSE);
