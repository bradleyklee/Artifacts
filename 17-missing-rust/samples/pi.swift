let n = 355
let d = 113
let whole = n / d
var rem = n % d
var digits = ""
for _ in 0..<4 {
    rem *= 10
    digits += String(rem / d)
    rem %= d
}
print("hello \(whole).\(digits) world!")
