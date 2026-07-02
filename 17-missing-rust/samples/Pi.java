public final class Pi {
  public static void main(String[] args) {
    int n = 355, d = 113, whole = n / d, rem = n % d;
    StringBuilder digits = new StringBuilder();
    for (int i = 0; i < 4; i++) {
      rem *= 10;
      digits.append(rem / d);
      rem %= d;
    }
    System.out.println("hello " + whole + "." + digits + " world!");
  }
}
