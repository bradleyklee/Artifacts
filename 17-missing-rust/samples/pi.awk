BEGIN {
  n = 355; d = 113
  whole = int(n / d); rem = n % d; digits = ""
  for (i = 0; i < 4; i++) {
    rem *= 10; digits = digits int(rem / d); rem %= d
  }
  print "hello " whole "." digits " world!"
}
