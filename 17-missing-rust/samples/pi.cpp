#include <cstdio>

int main() {
  int n = 355, d = 113, whole = n / d, rem = n % d;
  char digits[5] = {};
  for (int i = 0; i < 4; ++i) {
    rem *= 10;
    digits[i] = static_cast<char>('0' + rem / d);
    rem %= d;
  }
  std::printf("hello %d.%s world!\n", whole, digits);
}
