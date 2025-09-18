-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 17, 2025 at 11:15 AM
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
(19, 'Áo Phông Bé Trai Túi Hộp', 100000.00, 5, 38, 'Cam, Đen, Đỏ', 'Giao trong 3-5 ngày và freeship đơn từ 498k.\r\nĐổi trả trong vòng 15 ngày.\r\nCam kết bảo mật thông tin khách hàng.', '2025-08-29 09:04:37', 4, 31, 'cf147d1dcbfa817b90e7.webp', 'baad677191558e6fe4f1.webp', 'd46eb8c82bde557eedfa.webp'),
(20, 'Áo Khoác Nam Bomber Da', 1000000.00, 10, 28, 'Ghi Đậm, Đen', 'Giao trong 3-5 ngày và freeship đơn từ 498k.\r\nĐổi trả trong vòng 15 ngày.\r\nCam kết bảo mật thông tin khách hàng.', '2025-08-29 09:07:55', 1, 18, 'b8cdab1235885a900230.webp', 'f65574c452f2845052f2.webp', '99649d47f5166ff9cd20.webp'),
(21, 'Phao Vip Lông Vũ Nam', 1500000.00, 5, 10, 'Ghi Nhạt, Ghi Đậm, Tím Than', 'Giao trong 3-5 ngày và freeship đơn từ 498k.\r\nĐổi trả trong vòng 15 ngày.\r\nCam kết bảo mật thông tin khách hàng.', '2025-08-29 09:10:06', 1, 19, '9f509199a14affdad942.webp', '6326a17e8d0a9f30c054.webp', '21403909ab050330735c.webp'),
(22, 'Giày Cao Gót Cơ Bản Đế Nhỏ', 200000.00, 10, 40, 'Trắng, Nâu, Đen', 'Mặt ngoài: 100% POLYURETHAN\r\n\r\nMặt trong: 100% POLYESTER\r\n\r\nGiày nữ YODY được làm từ Da PU có nhiều ưu điểm như: độ bền cao, tính đàn hồi và độ bền màu tốt.\r\n\r\nTính đàn hồi: Giày da PU có độ đàn hồi tốt, dễ dàng uốn cong và linh hoạt trong quá trình sử dụng.\r\n\r\nThân thiện với môi trường: Da PU thường được xem là thân thiện với môi trường vì nó được sản xuất bằng cách sử dụng các chất liệu tự nhiên hơn so với da thật.\r\n\r\nDễ dàng vệ sinh: Giày da PU dễ dàng vệ sinh và có thể lau chùi bằng một số chất tẩy rửa thông thường và nước.\r\n\r\nTuy nhiên, da PU cũng có một số nhược điểm, bao gồm khả năng chống nước kém hơn so với da thật và có thể dễ dàng bị xước hoặc rách nếu không được sử dụng và bảo quản đúng cách.', '2025-09-08 02:19:34', 3, 34, 'f57b6d09d24147449976.webp', 'e05b2efa57ab2f0ea450.webp', '715773296d04d1bc11ea.webp'),
(23, 'Quần Shorts Lơ Vê Nắp Túi', 450000.00, 35, 4, 'Oliu, Trắng, Be', 'Chất liệu: Tuýt si\r\n\r\nBộ sưu tập Peaceful Summer 2025 - YODY mang đến vẻ đẹp thanh lịch, sự thoải mái và phong cách tinh tế. Với gam màu dịu nhẹ và chất liệu cao cấp, bộ sưu tập gợi lên cảm giác bình yên, tươi mới, như một sự kết nối hài hòa với thiên nhiên.\r\n\r\nƯu điểm chất liệu:\r\n\r\nCo giãn linh hoạt: Spandex giúp vải đàn hồi, thoải mái khi vận động.\r\n\r\nThoáng khí, không bám dính: Kiểu dệt đặc biệt giúp vải luôn nhẹ nhàng trên da.\r\n\r\nThân thiện tự nhiên: Thành phần từ thiên nhiên, an toàn cho da và môi trường.\r\n\r\nĐặc điểm thiết kế:\r\n\r\nPhom dáng rộng rãi: Mang lại cảm giác thoải mái khi mặc.\r\n\r\nChi tiết tinh tế: Hai ly trước, túi nhỏ, túi ẩn tạo điểm nhấn, túi sau hai viền sang trọng, tăng tính thẩm mỹ.', '2025-09-08 02:25:52', 2, 24, '6f42ccd138e4c556ae45.webp', '2b98f4865f6b8c47c6f3.webp', '03832a5d679159fead28.webp'),
(24, 'Mũ Lưỡi Trai Thêu Space (MUU6008)', 100000.00, 3, 59, 'Navy, Xám, Đen', 'Mũ lưỡi trai unisex tiện lợi, khỏe khoắn, sử dụng hàng ngày với nhiều công năng chống nắng, cản gió, làm đẹp. Hình thêu Space tinh tế, sắc nét thêm phần cá tính, đồng thời vải thấm mồ hôi giúp bạn luôn mát mẻ và thoải mái khi thời tiết nắng. Kiểu dáng cơ bản nhưng không kém phần năng động.', '2025-09-08 02:27:42', 1, 21, '06490661fadf0aded8ee.webp', 'e3fa5d0944c5c73027da.webp', 'd5105a92f6e92e2d4ef1.webp'),
(25, 'Bộ Đồ Vải Hiệu Ứng', 200000.00, 2, 22, 'Be, Xám, Xanh', 'Chất liệu: Waffle mềm mại\r\n\r\nThành phần:47.7%Cotton, 47.7%Viscose, 4.6%Spandex\r\n\r\nƯu điểm chất liệu:\r\n\r\nMềm mại & Thoáng khí: Sợi cotton mang lại cảm giác êm ái, giúp da luôn thoáng mát nhờ khả năng thấm hút mồ hôi hiệu quả.\r\n\r\nBề mặt vải mịn màng: Sợi viscose tăng độ mềm mại, giúp vải có độ rủ tự nhiên, tạo cảm giác dễ chịu khi mặc.\r\n\r\nCo giãn linh hoạt: Sợi spandex giúp sản phẩm có độ đàn hồi tốt, giữ form dáng đẹp và thoải mái khi vận động.\r\n\r\nĐặc điểm thiết kế:\r\n\r\nThiết kế basic tiện dụng: Cạp quần bản to giúp ôm vừa vặn, kết hợp dây luồn thắt lưng dễ điều chỉnh, phù hợp với nhiều dáng người.\r\n\r\nPhom Relax trẻ trung: Dáng quần rộng vừa phải, mang lại cảm giác thoải mái, năng động khi mặc.', '2025-09-08 02:29:49', 1, 19, '271ea0d5b2a5c7c1c408.webp', '70c2c2ad159119d84745.webp', '9752dce96f8de7af1c4d.webp');

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
-- Table structure for table `articles`
--

CREATE TABLE `articles` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `content` text NOT NULL,
  `cover_image` varchar(255) DEFAULT 'article-default.jpg',
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL,
  `admin_id` int(11) NOT NULL,
  `status` enum('draft','published','archived') DEFAULT 'draft',
  `slug` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_vietnamese_ci;

--
-- Dumping data for table `articles`
--

INSERT INTO `articles` (`id`, `title`, `content`, `cover_image`, `created_at`, `updated_at`, `admin_id`, `status`, `slug`) VALUES
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
-- Table structure for table `customer_order`
--

CREATE TABLE `customer_order` (
  `id` int(11) NOT NULL,
  `invoice` varchar(20) NOT NULL,
  `status` varchar(20) DEFAULT NULL,
  `address` varchar(200) DEFAULT NULL,
  `customer_id` int(11) NOT NULL,
  `orders` text DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `payment_method` varchar(20) DEFAULT 'cod',
  `payment_status` varchar(20) DEFAULT 'pending',
  `total_price` decimal(10,2) DEFAULT 0.00,
  `vnpay_transaction_id` varchar(50) DEFAULT NULL,
  `vnpay_transaction_no` varchar(50) DEFAULT NULL,
  `amount` decimal(10,2) DEFAULT 0.00,
  `delivery_method` varchar(20) DEFAULT 'home_delivery',
  `pickup_store` varchar(200) DEFAULT ''
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
(1, 'VietHoang', 'Trương Việt', 'Hoàng', 'Hoang@gmail.com', '0971010273', 'Nam', '$2b$12$mGgkL2qb2NC7tMPjvbqhyencLhax6EHxnkF0KUX9Gtz8yHYCSTtaq', '2025-08-19 10:41:26', 0),
(2, 'Bieu', 'Bieu', 'IT', 'BieuIT123@gmail.com', '0971234567', 'Nam', '$2b$12$1izz8H8QF/NyAM2rzgXTqe1nyqxP/EbFxbX8cvZLKOlzPeOGqCWZq', '2025-09-17 04:06:25', 0);

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
-- Indexes for table `articles`
--
ALTER TABLE `articles`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `slug` (`slug`),
  ADD KEY `admin_id` (`admin_id`);

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `articles`
--
ALTER TABLE `articles`
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
-- AUTO_INCREMENT for table `customer_order`
--
ALTER TABLE `customer_order`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=108;

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
-- Constraints for table `articles`
--
ALTER TABLE `articles`
  ADD CONSTRAINT `articles_ibfk_1` FOREIGN KEY (`admin_id`) REFERENCES `admin` (`id`) ON DELETE CASCADE;

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
