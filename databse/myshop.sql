-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 29, 2025 at 06:04 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `myshop`
--

-- --------------------------------------------------------

--
-- Table structure for table `addproduct`
--

CREATE TABLE `addproduct` (
  `id` int(11) NOT NULL,
  `name` varchar(80) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `discount` int(11) DEFAULT NULL,
  `stock` int(11) NOT NULL,
  `colors` text NOT NULL,
  `desc` text NOT NULL,
  `pub_date` datetime NOT NULL,
  `category_id` int(11) NOT NULL,
  `brand_id` int(11) NOT NULL,
  `image_1` varchar(150) NOT NULL,
  `image_2` varchar(150) NOT NULL,
  `image_3` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_vietnamese_ci;

--
-- Dumping data for table `addproduct`
--

INSERT INTO `addproduct` (`id`, `name`, `price`, `discount`, `stock`, `colors`, `desc`, `pub_date`, `category_id`, `brand_id`, `image_1`, `image_2`, `image_3`) VALUES
(18, 'Áo Khoác Kid Giả Lông Cừu Cổ Cao', 300000.00, 10, 50, 'Ghi, Nâu, Trắng', 'Giao trong 3-5 ngày và freeship đơn từ 498k.\r\nĐổi trả trong vòng 15 ngày.\r\nCam kết bảo mật thông tin khách hàng.', '2025-08-29 09:00:39', 1, 18, 'b049ba18ceb5c823e3c3.webp', 'c003be7e9f81506ca887.webp', 'f8b1c80e7e963c580b98.webp'),
(19, 'Áo Phông Bé Trai Túi Hộp', 100000.00, 5, 40, 'Cam, Đen, Đỏ', 'Giao trong 3-5 ngày và freeship đơn từ 498k.\r\nĐổi trả trong vòng 15 ngày.\r\nCam kết bảo mật thông tin khách hàng.', '2025-08-29 09:04:37', 4, 31, 'cf147d1dcbfa817b90e7.webp', 'baad677191558e6fe4f1.webp', 'd46eb8c82bde557eedfa.webp'),
(20, 'Áo Khoác Nam Bomber Da', 1000000.00, 10, 30, 'Ghi Đậm, Đen', 'Giao trong 3-5 ngày và freeship đơn từ 498k.\r\nĐổi trả trong vòng 15 ngày.\r\nCam kết bảo mật thông tin khách hàng.', '2025-08-29 09:07:55', 1, 18, 'b8cdab1235885a900230.webp', 'f65574c452f2845052f2.webp', '99649d47f5166ff9cd20.webp'),
(21, 'Phao Vip Lông Vũ Nam', 1500000.00, 5, 10, 'Ghi Nhạt, Ghi Đậm, Tím Than', 'Giao trong 3-5 ngày và freeship đơn từ 498k.\r\nĐổi trả trong vòng 15 ngày.\r\nCam kết bảo mật thông tin khách hàng.', '2025-08-29 09:10:06', 1, 19, '9f509199a14affdad942.webp', '6326a17e8d0a9f30c054.webp', '21403909ab050330735c.webp');

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `username` varchar(80) NOT NULL,
  `email` varchar(120) NOT NULL,
  `password` varchar(180) NOT NULL,
  `profile` varchar(180) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_vietnamese_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`id`, `name`, `username`, `email`, `password`, `profile`) VALUES
(1, 'viethoang', 'viethoang', 'viethoang@gmail.com', '$2a$12$x7wBbhJ3u0Dqn9PlNbW1mOyP6yUJWRdjJpKV1Q1jPMWqPZAEQmLV6', 'profile.jpg');

-- --------------------------------------------------------

--
-- Table structure for table `brand`
--

CREATE TABLE `brand` (
  `id` int(11) NOT NULL,
  `category_id` int(11) NOT NULL,
  `name` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_vietnamese_ci;

--
-- Dumping data for table `brand`
--

INSERT INTO `brand` (`id`, `category_id`, `name`) VALUES
(18, 1, 'Áo Khoác Nam'),
(19, 1, 'Áo Nam'),
(20, 1, 'Quần Nam'),
(21, 1, 'Đồ Thể Thao Nam'),
(22, 2, 'Áo Khoác Nữ'),
(23, 2, 'Áo Nữ'),
(24, 2, 'Quần Nữ'),
(25, 2, 'Đồ thể Thao Nữ'),
(26, 4, 'Giày'),
(27, 3, 'Túi Xách'),
(28, 3, 'Tất'),
(29, 3, 'Ví'),
(30, 4, 'Áo Khoác Trẻ Em'),
(31, 4, 'Áo Trẻ Em'),
(32, 4, 'Quần Trẻ Em');

-- --------------------------------------------------------

--
-- Table structure for table `category`
--

CREATE TABLE `category` (
  `id` int(11) NOT NULL,
  `name` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_vietnamese_ci;

--
-- Dumping data for table `category`
--

INSERT INTO `category` (`id`, `name`) VALUES
(1, 'Nam'),
(2, 'Nữ'),
(3, 'Phụ Kiện'),
(4, 'Trẻ Em');

-- --------------------------------------------------------

--
-- Table structure for table `customer_order`
--

CREATE TABLE `customer_order` (
  `id` int(11) NOT NULL,
  `invoice` varchar(20) NOT NULL,
  `status` varchar(20) DEFAULT NULL,
  `address` varchar(200) DEFAULT NULL,
  `customer_id` int(11) NOT NULL,
  `orders` text DEFAULT NULL,
  `date_created` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_vietnamese_ci;

-- --------------------------------------------------------

--
-- Table structure for table `product`
--

CREATE TABLE `product` (
  `id` int(11) NOT NULL,
  `name` varchar(80) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `discount` int(11) DEFAULT NULL,
  `stock` int(11) NOT NULL,
  `description` text NOT NULL,
  `pub_date` datetime NOT NULL,
  `brand_id` int(11) NOT NULL,
  `category_id` int(11) NOT NULL,
  `image_1` varchar(150) NOT NULL,
  `image_2` varchar(150) NOT NULL,
  `image_3` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_vietnamese_ci;

-- --------------------------------------------------------

--
-- Table structure for table `rate`
--

CREATE TABLE `rate` (
  `id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `register_id` int(11) NOT NULL,
  `time` datetime NOT NULL,
  `desc` text NOT NULL,
  `rate_number` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_vietnamese_ci;

-- --------------------------------------------------------

--
-- Table structure for table `register`
--

CREATE TABLE `register` (
  `id` int(11) NOT NULL,
  `username` varchar(50) DEFAULT NULL,
  `first_name` varchar(50) DEFAULT NULL,
  `last_name` varchar(50) DEFAULT NULL,
  `email` varchar(50) DEFAULT NULL,
  `phone_number` varchar(50) DEFAULT NULL,
  `gender` varchar(5) DEFAULT NULL,
  `password` varchar(200) DEFAULT NULL,
  `date_created` datetime NOT NULL,
  `lock` tinyint(1) DEFAULT NULL
) ;

--
-- Dumping data for table `register`
--

INSERT INTO `register` (`id`, `username`, `first_name`, `last_name`, `email`, `phone_number`, `gender`, `password`, `date_created`, `lock`) VALUES
(1, 'Manh', 'Lê', 'Mạnh', 'xuanmanhitweb1011@gmail.com', '0339134073', 'M', '$2b$12$KzjjXsRaDOKAsuQu3X2jUe5unm3wN3.j6QdH07J//zxzc0dt55RaC', '2020-11-09 03:35:01', 0),
(4, 'NhatMinh', 'Nhật', 'Minh', 'Minh@gmail.com', '0971010273', 'Nam', '$2b$12$mGgkL2qb2NC7tMPjvbqhyencLhax6EHxnkF0KUX9Gtz8yHYCSTtaq', '2025-08-19 10:41:26', 0),
(5, 'Dinh', 'Phan Văn', 'Định', 'Dinh@gmail.com', '0971010271', 'M', '$2b$12$LhdF.CovM8BhBV9OlJ3I1.gEqu4PtxP6V2WwI.hk/2yTmULELyhxy', '2025-08-21 16:43:39', 0);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `addproduct`
--
ALTER TABLE `addproduct`
  ADD PRIMARY KEY (`id`),
  ADD KEY `category_id` (`category_id`),
  ADD KEY `brand_id` (`brand_id`);

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `brand`
--
ALTER TABLE `brand`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`),
  ADD KEY `category_id` (`category_id`);

--
-- Indexes for table `category`
--
ALTER TABLE `category`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `customer_order`
--
ALTER TABLE `customer_order`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `invoice` (`invoice`);

--
-- Indexes for table `product`
--
ALTER TABLE `product`
  ADD PRIMARY KEY (`id`),
  ADD KEY `brand_id` (`brand_id`),
  ADD KEY `category_id` (`category_id`);

--
-- Indexes for table `rate`
--
ALTER TABLE `rate`
  ADD PRIMARY KEY (`id`),
  ADD KEY `product_id` (`product_id`),
  ADD KEY `register_id` (`register_id`);

--
-- Indexes for table `register`
--
ALTER TABLE `register`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `phone_number` (`phone_number`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `addproduct`
--
ALTER TABLE `addproduct`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=22;

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `brand`
--
ALTER TABLE `brand`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;

--
-- AUTO_INCREMENT for table `category`
--
ALTER TABLE `category`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `customer_order`
--
ALTER TABLE `customer_order`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT for table `product`
--
ALTER TABLE `product`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `rate`
--
ALTER TABLE `rate`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `register`
--
ALTER TABLE `register`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `addproduct`
--
ALTER TABLE `addproduct`
  ADD CONSTRAINT `addproduct_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `category` (`id`),
  ADD CONSTRAINT `addproduct_ibfk_2` FOREIGN KEY (`brand_id`) REFERENCES `brand` (`id`);

--
-- Constraints for table `brand`
--
ALTER TABLE `brand`
  ADD CONSTRAINT `brand_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `category` (`id`);

--
-- Constraints for table `product`
--
ALTER TABLE `product`
  ADD CONSTRAINT `product_ibfk_1` FOREIGN KEY (`brand_id`) REFERENCES `brand` (`id`),
  ADD CONSTRAINT `product_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `category` (`id`);

--
-- Constraints for table `rate`
--
ALTER TABLE `rate`
  ADD CONSTRAINT `rate_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `addproduct` (`id`),
  ADD CONSTRAINT `rate_ibfk_2` FOREIGN KEY (`register_id`) REFERENCES `register` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
