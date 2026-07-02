#include <stdio.h>

int main(void) {
  int n = 355, d = 113, whole = n / d, rem = n % d;
  char digits[5] = {0};
  for (int i = 0; i < 4; ++i) {
    rem *= 10;
    digits[i] = (char)('0' + rem / d);
    rem %= d;
  }
  printf("hello %d.%s world!\n", whole, digits);
  return 0;
}
