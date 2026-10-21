#pragma once
// Days of the year shown on the clock. Names and greetings follow the stock firmware's built-in list;
// Mùng 1 / Rằm of every lunar month are new.
#include <string>
#include "amlich.h"

namespace events {

struct Day {
  unsigned char day, month;
  const char *text;
};

static const Day SOLAR[] = {
    {1, 1, "Tết Dương Lịch - Chúc Mừng Năm Mới!"},
    {9, 1, "Ngày Học Sinh - Sinh Viên Việt Nam"},
    {3, 2, "Ngày thành lập Đảng Cộng Sản Việt Nam"},
    {14, 2, "Ngày Lễ Tình Nhân"},
    {27, 2, "Ngày Thầy thuốc Việt Nam"},
    {8, 3, "Ngày Quốc tế Phụ nữ"},
    {20, 3, "Ngày Quốc tế Hạnh phúc"},
    {22, 3, "Ngày Nước sạch Thế giới"},
    {26, 3, "Ngày thành lập Đoàn Thanh niên Cộng sản Hồ Chí Minh"},
    {27, 3, "Ngày Thể thao Việt Nam"},
    {28, 3, "Ngày thành lập Lực Lượng Dân Quân Tự Vệ"},
    {21, 4, "Ngày Sách Việt Nam"},
    {22, 4, "Ngày Trái đất"},
    {30, 4, "Ngày giải phóng Miền Nam thống nhất đất nước"},
    {1, 5, "Ngày Quốc tế lao động"},
    {7, 5, "Ngày chiến thắng Điện Biên Phủ"},
    {15, 5, "Ngày thành lập Đội Thiếu niên Tiền phong Hồ Chí Minh"},
    {19, 5, "Ngày sinh của Chủ tịch Hồ Chí Minh"},
    {1, 6, "Ngày Quốc tế Thiếu nhi"},
    {5, 6, "Ngày Bác Hồ ra đi tìm đường cứu nước - Ngày Môi trường Thế giới"},
    {28, 6, "Ngày Gia Đình Việt Nam"},
    {27, 7, "Ngày Thương binh Liệt sĩ"},
    {10, 8, "Ngày vì nạn nhân chất độc màu da cam"},
    {19, 8, "Ngày Cách mạng tháng Tám thành công - Ngày thành lập CAND Việt Nam"},
    {2, 9, "Ngày Quốc khánh - Kỷ niệm ngày Chủ tịch Hồ Chí Minh đọc tuyên ngôn độc lập"},
    {7, 9, "Ngày thành lập Đài Truyền hình Việt Nam"},
    {10, 10, "Ngày giải phóng thủ đô"},
    {13, 10, "Ngày Doanh nhân Việt Nam"},
    {14, 10, "Ngày thành lập Hội Nông dân Việt Nam"},
    {15, 10, "Ngày Truyền thống Hội Liên hiệp Thanh niên Việt Nam"},
    {20, 10, "Ngày Phụ nữ Việt Nam"},
    {9, 11, "Ngày Pháp luật Việt Nam"},
    {19, 11, "Ngày Quốc Tế Nam Giới"},
    {20, 11, "Ngày Nhà giáo Việt Nam"},
    {22, 12, "Ngày thành lập Quân đội Nhân dân Việt Nam"},
    {24, 12, "Đêm Giáng Sinh"},
    {25, 12, "Lễ Giáng Sinh"},
};

static const Day LUNAR[] = {
    {1, 1, "Mùng 1 Tết Nguyên Đán - Chúc Mừng Năm Mới, Vạn Sự Như Ý!"},
    {2, 1, "Mùng 2 Tết Nguyên Đán - Vạn Sự Như Ý, An Khang Thịnh Vượng!"},
    {3, 1, "Mùng 3 Tết Nguyên Đán - Vạn Sự Như Ý!"},
    {15, 1, "Rằm tháng Giêng - Tết Nguyên Tiêu"},
    {10, 3, "Ngày Giỗ Tổ Hùng Vương - Tưởng nhớ công ơn dựng nước của các Vua Hùng"},
    {5, 5, "Tết Đoan Ngọ"},
    {15, 7, "Rằm tháng Bảy - Lễ Vu Lan"},
    {15, 8, "Tết Trung Thu"},
    {23, 12, "Ngày Đưa Ông Táo Về Trời"},
};

inline std::string lunar_month_name(int m) {
  if (m == 1) return "Giêng";
  if (m == 12) return "Chạp";
  return std::to_string(m);
}

// Today's events joined with " - ", or "" when there are none
inline std::string today(int d, int m, const amlich::Lunar &l) {
  std::string out;
  auto add = [&out](const std::string &s) {
    if (!out.empty()) out += " - ";
    out += s;
  };
  bool lunar_named = false;
  if (!l.leap) {
    for (const auto &e : LUNAR)
      if (e.day == l.day && e.month == l.month) {
        add(e.text);
        lunar_named = true;
      }
  }
  if (!lunar_named && (l.day == 1 || l.day == 15))
    add(std::string(l.day == 1 ? "Mùng 1" : "Rằm") + " tháng " + lunar_month_name(l.month) +
        (l.leap ? " nhuận" : ""));
  for (const auto &e : SOLAR)
    if (e.day == d && e.month == m) add(e.text);
  return out;
}

}  // namespace events
