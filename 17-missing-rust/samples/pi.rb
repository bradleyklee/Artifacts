n = 355; d = 113
whole, rem = n.divmod(d)
digits = +""
4.times do
  rem *= 10
  digit, rem = rem.divmod(d)
  digits << digit.to_s
end
puts "hello #{whole}.#{digits} world!"
