use strict;
use warnings;
my ($n, $d) = (355, 113);
my $whole = int($n / $d);
my $rem = $n % $d;
my $digits = '';
for (1 .. 4) {
  $rem *= 10;
  $digits .= int($rem / $d);
  $rem %= $d;
}
print "hello $whole.$digits world!\n";
