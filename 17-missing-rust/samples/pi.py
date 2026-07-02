n, d = 355, 113
whole, rem = divmod(n, d)
digits = []
for _ in range(4):
    rem *= 10
    digit, rem = divmod(rem, d)
    digits.append(str(digit))
print(f"hello {whole}.{''.join(digits)} world!")
