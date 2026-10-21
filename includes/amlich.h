#pragma once
// Vietnamese lunar calendar, after Ho Ngoc Duc's algorithm (https://www.informatik.uni-leipzig.de/~duc/amlich/).
#include <cmath>

namespace amlich {

static const double PI = 3.14159265358979323846;

inline long jd_from_date(int dd, int mm, int yy) {
  int a = (14 - mm) / 12;
  long y = yy + 4800 - a;
  int m = mm + 12 * a - 3;
  long jd = dd + (153 * m + 2) / 5 + 365 * y + y / 4 - y / 100 + y / 400 - 32045;
  if (jd < 2299161)
    jd = dd + (153 * m + 2) / 5 + 365 * y + y / 4 - 32083;
  return jd;
}

inline long new_moon_day(long k, double tz) {
  double T = k / 1236.85, T2 = T * T, T3 = T2 * T, dr = PI / 180;
  double jd1 = 2415020.75933 + 29.53058868 * k + 0.0001178 * T2 - 0.000000155 * T3;
  jd1 += 0.00033 * sin((166.56 + 132.87 * T - 0.009173 * T2) * dr);
  double M = 359.2242 + 29.10535608 * k - 0.0000333 * T2 - 0.00000347 * T3;
  double Mpr = 306.0253 + 385.81691806 * k + 0.0107306 * T2 + 0.00001236 * T3;
  double F = 21.2964 + 390.67050646 * k - 0.0016528 * T2 - 0.00000239 * T3;
  double c1 = (0.1734 - 0.000393 * T) * sin(M * dr) + 0.0021 * sin(2 * dr * M);
  c1 = c1 - 0.4068 * sin(Mpr * dr) + 0.0161 * sin(dr * 2 * Mpr);
  c1 = c1 - 0.0004 * sin(dr * 3 * Mpr);
  c1 = c1 + 0.0104 * sin(dr * 2 * F) - 0.0051 * sin(dr * (M + Mpr));
  c1 = c1 - 0.0074 * sin(dr * (M - Mpr)) + 0.0004 * sin(dr * (2 * F + M));
  c1 = c1 - 0.0004 * sin(dr * (2 * F - M)) - 0.0006 * sin(dr * (2 * F + Mpr));
  c1 = c1 + 0.0010 * sin(dr * (2 * F - Mpr)) + 0.0005 * sin(dr * (2 * Mpr + M));
  double deltat = T < -11 ? 0.001 + 0.000839 * T + 0.0002261 * T2 - 0.00000845 * T3 - 0.000000081 * T * T3
                          : -0.000278 + 0.000265 * T + 0.000262 * T2;
  return (long) floor(jd1 + c1 - deltat + 0.5 + tz / 24);
}

inline int sun_longitude(long jdn, double tz) {
  double T = (jdn - 2451545.5 - tz / 24) / 36525, T2 = T * T, dr = PI / 180;
  double M = 357.52910 + 35999.05030 * T - 0.0001559 * T2 - 0.00000048 * T * T2;
  double L0 = 280.46645 + 36000.76983 * T + 0.0003032 * T2;
  double DL = (1.914600 - 0.004817 * T - 0.000014 * T2) * sin(dr * M);
  DL += (0.019993 - 0.000101 * T) * sin(dr * 2 * M) + 0.000290 * sin(dr * 3 * M);
  double L = (L0 + DL) * dr;
  L -= PI * 2 * floor(L / (PI * 2));
  return (int) floor(L / PI * 6);
}

inline long lunar_month11(int yy, double tz) {
  long off = jd_from_date(31, 12, yy) - 2415021;
  long k = (long) floor(off / 29.530588853);
  long nm = new_moon_day(k, tz);
  if (sun_longitude(nm, tz) >= 9)
    nm = new_moon_day(k - 1, tz);
  return nm;
}

inline int leap_month_offset(long a11, double tz) {
  long k = (long) floor((a11 - 2415021.076998695) / 29.530588853 + 0.5);
  int last, i = 1;
  int arc = sun_longitude(new_moon_day(k + i, tz), tz);
  do {
    last = arc;
    i++;
    arc = sun_longitude(new_moon_day(k + i, tz), tz);
  } while (arc != last && i < 14);
  return i - 1;
}

struct Lunar {
  int day, month, year;
  bool leap;
};

inline Lunar solar_to_lunar(int dd, int mm, int yy, double tz = 7.0) {
  long day_number = jd_from_date(dd, mm, yy);
  long k = (long) floor((day_number - 2415021.076998695) / 29.530588853);
  long month_start = new_moon_day(k + 1, tz);
  if (month_start > day_number)
    month_start = new_moon_day(k, tz);
  long a11 = lunar_month11(yy, tz), b11 = a11;
  int lunar_year;
  if (a11 >= month_start) {
    lunar_year = yy;
    a11 = lunar_month11(yy - 1, tz);
  } else {
    lunar_year = yy + 1;
    b11 = lunar_month11(yy + 1, tz);
  }
  int lunar_day = day_number - month_start + 1;
  int diff = (int) floor((month_start - a11) / 29.0);
  bool leap = false;
  int lunar_month = diff + 11;
  if (b11 - a11 > 365) {
    int leap_diff = leap_month_offset(a11, tz);
    if (diff >= leap_diff) {
      lunar_month = diff + 10;
      if (diff == leap_diff)
        leap = true;
    }
  }
  if (lunar_month > 12)
    lunar_month -= 12;
  if (lunar_month >= 11 && diff < 4)
    lunar_year -= 1;
  return {lunar_day, lunar_month, lunar_year, leap};
}

// Year names (Can Chi). *_ascii variants are for the LED font, which has no Vietnamese glyphs.
inline const char *can(int y) {
  static const char *const n[] = {"Canh", "Tân", "Nhâm", "Quý", "Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ"};
  return n[y % 10];
}
inline const char *chi(int y) {
  static const char *const n[] = {"Thân", "Dậu", "Tuất", "Hợi", "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi"};
  return n[y % 12];
}
inline const char *can_ascii(int y) {
  static const char *const n[] = {"Canh", "Tan", "Nham", "Quy", "Giap", "At", "Binh", "Dinh", "Mau", "Ky"};
  return n[y % 10];
}
inline const char *chi_ascii(int y) {
  static const char *const n[] = {"Than", "Dau", "Tuat", "Hoi", "Ty", "Suu", "Dan", "Mao", "Thin", "Ty", "Ngo", "Mui"};
  return n[y % 12];
}

}  // namespace amlich
