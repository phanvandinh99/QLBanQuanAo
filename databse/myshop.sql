-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 18, 2025 at 06:13 PM
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
(1, 'Việt Hoàng', 'viethoang', 'viethoang@gmail.com', '$2a$12$x7wBbhJ3u0Dqn9PlNbW1mOyP6yUJWRdjJpKV1Q1jPMWqPZAEQmLV6', 'profile.jpg');

-- --------------------------------------------------------

--
-- Table structure for table `article`
--

CREATE TABLE `article` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `content` text NOT NULL,
  `cover_image` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime DEFAULT NULL,
  `admin_id` int(11) NOT NULL,
  `status` enum('draft','published','archived') DEFAULT NULL,
  `slug` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_vietnamese_ci;

--
-- Dumping data for table `article`
--

INSERT INTO `article` (`id`, `title`, `content`, `cover_image`, `created_at`, `updated_at`, `admin_id`, `status`, `slug`) VALUES
(2, 'Quần tây công sở cao cấp, chuẩn form, giá tốt tại Belluni', 'Ở độ tuổi trung niên, gu ăn mặc không chỉ phục vụ nhu cầu thẩm mỹ mà còn thể hiện phong thái, địa vị và sự tôn trọng dành cho người đối diện. Quần tây công sở là lựa chọn không thể thiếu của nam giới bởi sự chỉn chu, sang trọng và khả năng kết hợp đa dạng.\r\n\r\nI. Tiêu chí lựa chọn quần tây công sở dành cho nam trung niên\r\n1.1. Phom dáng\r\nQuý ông nên ưu tiên quần tây nam ống đứng (straight fit) hoặc regular fit để tạo sự cân đối cho tổng thể. Kiểu ống đứng giúp che đi phần bụng và đùi hơi to, đồng thời vẫn mang lại sự gọn gàng. Bạn nên hạn chế các dáng skinny hay slim fit quá bó vì sẽ vừa kém thoải mái vừa không phù hợp với sự chững chạc của độ tuổi.\r\n\r\n1.2. Chất liệu\r\nChất liệu đóng vai trò quan trọng trong việc tạo nên vẻ đẹp và độ bền của quần tây. Khi mua quần tây nam cho môi trường công sở, các quý ông nên ưu tiên lựa chọn những loại vải cao cấp như wool pha polyester hoặc tuytsi. Đây là những chất liệu giúp quần giữ phom dáng tốt, ít nhăn, bền màu và có độ co giãn nhẹ, mang lại sự thoải mái tối đa suốt cả ngày làm việc, đồng thời duy trì vẻ lịch lãm và chỉn chu.\r\n\r\n1.3. Màu sắc\r\nCác gam màu quần tây nam trung tính và trầm như đen, xanh navy, ghi xám luôn là lựa chọn an toàn cho phong cách công sở. Đây là những tông dễ phối với hầu hết áo sơ mi và vest, mang lại sự chỉn chu và hài hòa. Nếu muốn tạo điểm nhấn mới mẻ, bạn có thể chọn nâu cà phê, be nhạt hoặc xanh rêu, miễn là vẫn giữ được sự trang nhã vốn có.\r\n\r\nQuần tây công sở - Belluni\r\n\r\nMàu sắc phù hợp giúp tổng thể trang phục hài hòa hơn.\r\n\r\n \r\n\r\nII. Nam trung niên nên chọn thiết kế quần tây công sở thế nào?\r\n2.1. Quần tây ống đứng truyền thống\r\nĐây là kiểu dáng kinh điển, không bao giờ lỗi mốt. Phần ống thẳng từ hông xuống gấu quần giúp vóc dáng trông cao hơn và cân đối hơn. Khi kết hợp với áo sơ mi trắng, vest đồng màu và giày da bóng, phong thái của người đàn ông lập tức trở nên nghiêm túc, chuyên nghiệp.\r\n\r\n2.2. Quần tây xếp ly\r\nThiết kế có một hoặc hai ly ở phần trước giúp tạo độ rộng thoải mái cho hông và đùi – rất phù hợp cho những quý ông có vóc dáng đầy đặn hoặc cần ngồi làm việc lâu. Kiểu quần này vừa mang nét cổ điển, vừa tạo sự dễ chịu khi vận động.\r\n\r\n2.3. Quần tây chất liệu cao cấp, ít nhăn\r\nNhững quý ông bận rộn, thường xuyên di chuyển nên chọn quần tây từ vải có khả năng chống nhăn, giữ ly lâu. Điều này đảm bảo quần luôn phẳng phiu dù phải ngồi xe, đi công tác hay tham dự nhiều cuộc họp liên tiếp.', 'AnhBia.png', '2025-09-07 08:31:36', '2025-09-07 08:31:57', 1, 'published', 'quan-tay-cong-so-cao-cap-chuan-form-gia-tot-tai-belluni'),
(3, '6+ mẫu quần sọt nam kaki bán chạy nhất', 'uần sọt nam kaki từ lâu đã trở thành một trong những item luôn hiện diện trong tủ đồ của phái mạnh. Với chất liệu kaki bền bỉ, dễ phối đồ và phù hợp trong nhiều hoàn cảnh, chiếc quần kaki nam này mang lại sự cân bằng giữa tính thời trang và sự thoải mái.\r\n\r\nI. Các kiểu quần sọt nam kaki phổ biến\r\nQuần sọt nam kaki hiện nay có rất nhiều kiểu dáng, phù hợp với nhu cầu và phong cách của từng người. Dưới đây là những mẫu được phái mạnh ưa chuộng nhất:\r\n\r\n1.1. Quần sọt kaki nam trơn\r\nĐây là kiểu quần short kaki cơ bản và phổ biến nhất, phù hợp với hầu hết phong cách ăn mặc. Thiết kế tối giản cùng gam màu trung tính như đen, be, xanh rêu, xám ghi giúp dễ dàng phối với nhiều loại áo như áo thun, áo polo hoặc áo sơ mi. Quần sọt kaki trơn mang đến vẻ ngoài gọn gàng, lịch sự và có thể sử dụng trong nhiều hoàn cảnh: từ đi làm ở môi trường thoải mái cho đến dạo phố cuối tuần\r\n1.2. Quần sọt kaki nam túi hộp\r\nMang hơi hướng năng động, mạnh mẽ, quần sọt kaki túi hộp nổi bật với các ngăn túi lớn ở hai bên. Những chiếc túi này không chỉ giúp đựng các vật dụng nhỏ gọn như điện thoại, ví, chìa khóa… mà còn tạo điểm nhấn cá tính cho trang phục. Đây là lựa chọn lý tưởng cho những muốn mua quần kaki nam để tham gia các hoạt động ngoài trời như dã ngoại, cắm trại hoặc du lịch bụi.\r\n\r\n1.3. Quần sọt kaki nam ngắn trên gối\r\nNếu bạn yêu thích sự trẻ trung và muốn tạo cảm giác mát mẻ trong những ngày hè nóng bức, quần sọt kaki ngắn trên gối chính là gợi ý hoàn hảo. Với chiều dài vừa phải, mẫu quần này giúp khoe đôi chân khỏe khoắn, đồng thời dễ dàng phối cùng áo sơ mi ngắn tay, áo polo hoặc áo tank top để tạo nên set đồ năng động, thoải mái.\r\n\r\n1.4. Quần sọt kaki nam dáng rộng\r\nForm rộng mang lại cảm giác phóng khoáng, thoải mái khi di chuyển, đồng thời thể hiện cá tính thời trang mạnh mẽ. Mẫu quần này đặc biệt được ưa chuộng trong phong cách streetwear. Khi kết hợp cùng giày sneaker và áo oversize, bạn sẽ có một outfit vừa chất vừa hiện đại, thích hợp cho các buổi tụ họp bạn bè hoặc dạo phố.\r\n\r\n1.5. Quần sọt kaki nam lửng (dưới gối)\r\nDài đến giữa bắp chân, kiểu quần này tạo cảm giác lịch sự hơn so với quần ngắn trên gối nhưng vẫn đảm bảo sự thoải mái khi vận động. Đây là lựa chọn dành cho những quý ông muốn giữ nét chững chạc, chỉnh tề nhưng không quá gò bó. Bạn có thể phối cùng áo polo hoặc áo sơ mi linen để tạo phong cách thanh lịch, nhẹ nhàng, rất hợp cho các buổi dạo biển hoặc du lịch nghỉ dưỡng.\r\nII. Hướng dẫn chọn size quần sọt nam kaki chuẩn tại Belluni\r\nĐể chọn size quần sọt nam kaki phù hợp tại Belluni, bạn có thể tham khảo bảng thông số chi tiết theo chiều cao, vòng eo và vòng mông. Bảng size từ 29 đến 37 giúp quý ông dễ dàng lựa chọn mua quần kaki nam vừa vặn, thoải mái khi mặc, giữ phom chuẩn và phong cách lịch lãm trong mọi hoàn cảnh.', 'QuanDui.png', '2025-09-07 08:38:41', '2025-09-08 04:12:57', 1, 'published', '6-mau-quan-sot-nam-kaki-ban-chay-nhat'),
(4, 'Những điều cần biết khi mua quần kaki nam chuẩn phong cách', 'Chiếc quần kaki nam phù hợp giúp bạn trông gọn gàng và mang lại cảm giác thoải mái cả ngày. Chất liệu tốt, phom dáng chuẩn và màu sắc tinh tế là những yếu tố quyết định giá trị thực sự của một chiếc quần. Vậy làm thế nào để mua quần kaki nam vừa đẹp, vừa bền, lại dễ phối đồ trong nhiều hoàn cảnh? Hãy cùng Belluni khám phá bí quyết lựa chọn ngay sau đây.\r\n\r\n \r\n\r\nI. Bí quyết mua quần kaki nam phù hợp\r\n1.1. Xác định rõ mục đích sử dụng\r\nTrước khi quyết định mua quần kaki nam, điều quan trọng là xác định rõ mục đích sử dụng. Một chiếc quần phù hợp với hoàn cảnh sẽ không chỉ giúp bạn cảm thấy tự tin mà còn tôn lên phong cách tổng thể.\r\n\r\nNếu bạn cần quần cho môi trường công sở hoặc những buổi gặp gỡ đối tác, quần kaki trơn với gam màu trung tính như đen, xanh navy hoặc xám sẽ là lựa chọn tối ưu. Kết hợp với phom slim fit hoặc regular fit, bạn sẽ trông lịch lãm và chuyên nghiệp hơn.\r\n\r\nNgược lại, nếu mục đích là dạo phố, đi chơi hay du lịch, bạn có thể ưu tiên những thiết kế trẻ trung, năng động như quần short kaki, túi hộp hoặc jogger. Gam màu sáng sẽ giúp bộ trang phục nổi bật, đồng thời mang lại cảm giác thoải mái khi vận động.\r\n1.2. Chọn phom dáng phù hợp với vóc người\r\nPhom dáng quyết định cách quần ôm sát hoặc thả lỏng trên cơ thể, ảnh hưởng trực tiếp đến sự cân đối tổng thể.\r\n\r\n- Dáng slim fit ôm vừa từ hông xuống mắt cá chân, giúp tôn lên đôi chân thon gọn và tạo cảm giác cao hơn. Đây là lựa chọn lý tưởng cho những người có vóc dáng cân đối.\r\n\r\n- Regular fit mang lại sự thoải mái nhờ độ rộng vừa phải, phù hợp với nhiều dáng người. Kiểu quần này đặc biệt thích hợp nếu bạn ưu tiên sự dễ chịu trong sinh hoạt hằng ngày.\r\n\r\n- Quần kaki jogger với bo chun ở ống quần lại mang hơi hướng thể thao, trẻ trung và dễ kết hợp với nhiều kiểu giày, tạo phong cách đường phố năng động.\r\n\r\n1.3. Ưu tiên chất liệu cao cấp\r\nChất liệu là yếu tố quyết định 80% sự thoải mái và độ bền của quần kaki nam trung niên. Lựa chọn lý tưởng là kaki cotton pha spandex, vừa mềm mại, thoáng khí, vừa co giãn nhẹ để hỗ trợ mọi chuyển động. Loại vải này cũng ít nhăn hơn kaki thuần cotton, giúp bạn giữ được vẻ gọn gàng suốt cả ngày. Với những môi trường nóng ẩm, nên tránh quần quá dày hoặc cứng để không gây bí bách, đồng thời chọn vải có khả năng hút ẩm tốt.', 'QuanKaki.png', '2025-09-07 08:40:02', '2025-09-08 03:28:54', 1, 'published', 'nhung-dieu-can-biet-khi-mua-quan-kaki-nam-chuan-phong-cach');

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
(27, 3, 'Túi Xách'),
(28, 3, 'Tất'),
(29, 3, 'Ví'),
(30, 4, 'Áo Khoác Trẻ Em'),
(31, 4, 'Áo Trẻ Em'),
(32, 4, 'Quần Trẻ Em'),
(34, 3, 'Giày');

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
-- Table structure for table `customer`
--

CREATE TABLE `customer` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `email` varchar(120) NOT NULL,
  `phone_number` varchar(20) NOT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `password` varchar(200) NOT NULL,
  `date_created` datetime NOT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `last_login` datetime DEFAULT NULL
) ;

--
-- Dumping data for table `customer`
--

INSERT INTO `customer` (`id`, `username`, `first_name`, `last_name`, `email`, `phone_number`, `gender`, `password`, `date_created`, `is_active`, `last_login`) VALUES
(1, 'VietHoang', 'Trương Việt', 'Hoàn', 'Hoang@gmail.com', '0971010281', 'F', '$2b$12$mGgkL2qb2NC7tMPjvbqhyencLhax6EHxnkF0KUX9Gtz8yHYCSTtaq', '2025-08-19 10:41:26', 1, NULL),
(2, 'Bieu', 'Bieu', 'IT', 'BieuIT123@gmail.com', '0971234567', 'Nam', '$2b$12$1izz8H8QF/NyAM2rzgXTqe1nyqxP/EbFxbX8cvZLKOlzPeOGqCWZq', '2025-09-17 04:06:25', 1, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `order`
--

CREATE TABLE `order` (
  `id` int(11) NOT NULL,
  `invoice` varchar(20) NOT NULL,
  `status` enum('pending','confirmed','shipping','delivered','cancelled','ready_for_pickup') DEFAULT NULL,
  `payment_status` enum('unpaid','paid','refunded') DEFAULT NULL,
  `customer_id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime DEFAULT NULL,
  `shipping_address` varchar(200) DEFAULT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `payment_method` enum('cod','vnpay') DEFAULT NULL,
  `delivery_method` enum('home_delivery','instore_pickup') DEFAULT NULL,
  `pickup_store` varchar(200) DEFAULT NULL,
  `notes` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_vietnamese_ci;

-- --------------------------------------------------------

--
-- Table structure for table `order_item`
--

CREATE TABLE `order_item` (
  `id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  `discount` int(11) DEFAULT NULL
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
  `image_3` varchar(150) NOT NULL,
  `colors` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_vietnamese_ci;

--
-- Dumping data for table `product`
--

INSERT INTO `product` (`id`, `name`, `price`, `discount`, `stock`, `description`, `pub_date`, `brand_id`, `category_id`, `image_1`, `image_2`, `image_3`, `colors`) VALUES
(18, 'Áo Khoác Kid Giả Lông Cừu Cổ Cao', 300000.00, 10, 50, 'Giao trong 3-5 ngày và freeship đơn từ 498k.\\r\\nĐổi trả trong vòng 15 ngày.\\r\\nCam kết bảo mật thông tin khách hàng.', '2025-08-29 09:00:39', 18, 1, 'b049ba18ceb5c823e3c3.webp', 'c003be7e9f81506ca887.webp', 'f8b1c80e7e963c580b98.webp', 'Ghi, Nâu, Trắng'),
(19, 'Áo Phông Bé Trai Túi Hộp', 100000.00, 5, 29, 'Giao trong 3-5 ngày và freeship đơn từ 498k.\\r\\nĐổi trả trong vòng 15 ngày.\\r\\nCam kết bảo mật thông tin khách hàng.', '2025-08-29 09:04:37', 31, 4, 'cf147d1dcbfa817b90e7.webp', 'baad677191558e6fe4f1.webp', 'd46eb8c82bde557eedfa.webp', 'Cam, Đen, Đỏ'),
(20, 'Áo Khoác Nam Bomber Da', 1000000.00, 10, 26, 'Giao trong 3-5 ngày và freeship đơn từ 498k.\\r\\nĐổi trả trong vòng 15 ngày.\\r\\nCam kết bảo mật thông tin khách hàng.', '2025-08-29 09:07:55', 18, 1, 'b8cdab1235885a900230.webp', 'f65574c452f2845052f2.webp', '99649d47f5166ff9cd20.webp', 'Ghi Đậm, Đen'),
(21, 'Phao Vip Lông Vũ Nam', 1500000.00, 5, 7, 'Giao trong 3-5 ngày và freeship đơn từ 498k.\\r\\nĐổi trả trong vòng 15 ngày.\\r\\nCam kết bảo mật thông tin khách hàng.', '2025-08-29 09:10:06', 19, 1, '9f509199a14affdad942.webp', '6326a17e8d0a9f30c054.webp', '21403909ab050330735c.webp', 'Ghi Nhạt, Ghi Đậm, Tím Than'),
(22, 'Giày Cao Gót Cơ Bản Đế Nhỏ', 200000.00, 10, 40, 'Description here', '2025-09-08 02:19:34', 34, 3, 'f57b6d09d24147449976.webp', 'e05b2efa57ab2f0ea450.webp', '715773296d04d1bc11ea.webp', 'Trắng, Nâu, Đen'),
(23, 'Quần Shorts Lơ Vê Nắp Túi', 450000.00, 35, 3, 'Description here', '2025-09-08 02:25:52', 24, 2, '6f42ccd138e4c556ae45.webp', '2b98f4865f6b8c47c6f3.webp', '03832a5d679159fead28.webp', 'Oliu, Trắng, Be'),
(24, 'Mũ Lưỡi Trai Thêu Space (MUU6008)', 100000.00, 3, 57, 'Description here', '2025-09-08 02:27:42', 21, 1, '06490661fadf0aded8ee.webp', 'e3fa5d0944c5c73027da.webp', 'd5105a92f6e92e2d4ef1.webp', 'Navy, Xám, Đen'),
(25, 'Bộ Đồ Vải Hiệu Ứng', 200000.00, 2, 18, 'Description here', '2025-09-08 02:29:49', 19, 1, '271ea0d5b2a5c7c1c408.webp', '70c2c2ad159119d84745.webp', '9752dce96f8de7af1c4d.webp', 'Be, Xám, Xanh');

-- --------------------------------------------------------

--
-- Table structure for table `rating`
--

CREATE TABLE `rating` (
  `id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `comment` text NOT NULL,
  `rating` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_vietnamese_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `article`
--
ALTER TABLE `article`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_article_slug` (`slug`),
  ADD KEY `ix_article_admin_id` (`admin_id`),
  ADD KEY `ix_article_title` (`title`),
  ADD KEY `ix_article_created_at` (`created_at`),
  ADD KEY `ix_article_status` (`status`),
  ADD KEY `idx_article_status` (`status`),
  ADD KEY `idx_article_created_at` (`created_at`);

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
-- Indexes for table `customer`
--
ALTER TABLE `customer`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `phone_number` (`phone_number`),
  ADD UNIQUE KEY `ix_customer_email` (`email`),
  ADD UNIQUE KEY `ix_customer_username` (`username`),
  ADD KEY `idx_customer_email` (`email`),
  ADD KEY `idx_customer_username` (`username`);

--
-- Indexes for table `order`
--
ALTER TABLE `order`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_order_invoice` (`invoice`),
  ADD KEY `ix_order_customer_id` (`customer_id`),
  ADD KEY `ix_order_created_at` (`created_at`);

--
-- Indexes for table `order_item`
--
ALTER TABLE `order_item`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_order_item_product_id` (`product_id`),
  ADD KEY `ix_order_item_order_id` (`order_id`);

--
-- Indexes for table `product`
--
ALTER TABLE `product`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_product_name` (`name`),
  ADD KEY `idx_product_category` (`category_id`),
  ADD KEY `idx_product_brand` (`brand_id`),
  ADD KEY `idx_product_pub_date` (`pub_date`);

--
-- Indexes for table `rating`
--
ALTER TABLE `rating`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_rating_customer_id` (`customer_id`),
  ADD KEY `ix_rating_product_id` (`product_id`),
  ADD KEY `idx_rating_product` (`product_id`),
  ADD KEY `idx_rating_customer` (`customer_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `article`
--
ALTER TABLE `article`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `brand`
--
ALTER TABLE `brand`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=35;

--
-- AUTO_INCREMENT for table `category`
--
ALTER TABLE `category`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `customer`
--
ALTER TABLE `customer`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `order`
--
ALTER TABLE `order`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT for table `order_item`
--
ALTER TABLE `order_item`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=34;

--
-- AUTO_INCREMENT for table `product`
--
ALTER TABLE `product`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;

--
-- AUTO_INCREMENT for table `rating`
--
ALTER TABLE `rating`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `article`
--
ALTER TABLE `article`
  ADD CONSTRAINT `article_ibfk_1` FOREIGN KEY (`admin_id`) REFERENCES `admin` (`id`);

--
-- Constraints for table `brand`
--
ALTER TABLE `brand`
  ADD CONSTRAINT `brand_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `category` (`id`);

--
-- Constraints for table `order`
--
ALTER TABLE `order`
  ADD CONSTRAINT `order_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`id`);

--
-- Constraints for table `order_item`
--
ALTER TABLE `order_item`
  ADD CONSTRAINT `order_item_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `order` (`id`),
  ADD CONSTRAINT `order_item_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`);

--
-- Constraints for table `product`
--
ALTER TABLE `product`
  ADD CONSTRAINT `product_ibfk_1` FOREIGN KEY (`brand_id`) REFERENCES `brand` (`id`),
  ADD CONSTRAINT `product_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `category` (`id`);

--
-- Constraints for table `rating`
--
ALTER TABLE `rating`
  ADD CONSTRAINT `rating_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`),
  ADD CONSTRAINT `rating_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
