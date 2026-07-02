let n = 355, d = 113;
let whole = Math.floor(n / d), rem = n % d, digits = "";
for (let i = 0; i < 4; i += 1) {
  rem *= 10;
  digits += Math.floor(rem / d);
  rem %= d;
}
console.log(`hello ${whole}.${digits} world!`);
