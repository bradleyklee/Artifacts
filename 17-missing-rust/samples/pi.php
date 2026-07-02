<?php
$n = 355; $d = 113;
$whole = intdiv($n, $d); $rem = $n % $d; $digits = "";
for ($i = 0; $i < 4; $i++) {
    $rem *= 10;
    $digits .= intdiv($rem, $d);
    $rem %= $d;
}
echo "hello $whole.$digits world!\n";
