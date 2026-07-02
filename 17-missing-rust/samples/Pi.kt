fun main() {
    val n = 355
    val d = 113
    val whole = n / d
    var rem = n % d
    val digits = StringBuilder()
    repeat(4) {
        rem *= 10
        digits.append(rem / d)
        rem %= d
    }
    println("hello $whole.$digits world!")
}
