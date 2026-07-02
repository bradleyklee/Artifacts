program pi_probe
  implicit none
  integer :: n, d, whole, rem, i
  character(len=4) :: digits

  n = 355; d = 113
  whole = n / d; rem = mod(n, d)
  do i = 1, 4
    rem = rem * 10
    write(digits(i:i), '(I1)') rem / d
    rem = mod(rem, d)
  end do
  write (*, '(A,I1,A,A,A)') 'hello ', whole, '.', digits, ' world!'
end program pi_probe
