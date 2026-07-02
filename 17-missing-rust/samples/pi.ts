let n: number = 355;
let d: number = 113;
let whole: number = Math.floor(n / d);
let rem: number = n % d;
let digits: string = "";
for (let i: number = 0; i < 4; i += 1) {
  rem *= 10;
  digits += Math.floor(rem / d).toString();
  rem %= d;
}
console.log(`hello ${whole}.${digits} world!`);
