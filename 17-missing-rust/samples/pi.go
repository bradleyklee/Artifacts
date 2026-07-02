package main

import "fmt"

func main() {
	n, d := 355, 113
	whole, rem := n/d, n%d
	digits := ""
	for i := 0; i < 4; i++ {
		rem *= 10
		digits += fmt.Sprint(rem / d)
		rem %= d
	}
	fmt.Printf("hello %d.%s world!\n", whole, digits)
}
