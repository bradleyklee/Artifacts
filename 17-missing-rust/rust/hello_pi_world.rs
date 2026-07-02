fn main() {
    let n: u32 = 355;
    let d: u32 = 113;
    let whole = n / d;
    let mut rem = n % d;
    let mut digits = String::new();
    for _ in 0..4 {
        rem *= 10;
        digits.push(char::from(b'0' + (rem / d) as u8));
        rem %= d;
    }
    println!("hello {whole}.{digits} world!");
}
