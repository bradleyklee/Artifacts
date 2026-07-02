set n 355
set d 113
set whole [expr {$n / $d}]
set rem [expr {$n % $d}]
set digits ""
for {set i 0} {$i < 4} {incr i} {
    set rem [expr {$rem * 10}]
    append digits [expr {$rem / $d}]
    set rem [expr {$rem % $d}]
}
puts "hello $whole.$digits world!"
