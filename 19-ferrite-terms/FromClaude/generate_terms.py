"""
Regenerates claude_terms_S21_S60.txt from ferrite.py.
Usage: python3 generate_terms.py
Requires ferrite.py in the same directory.
"""
from ferrite import F

def main():
    lines = []
    for N in [4, 6, 8, 10]:
        vals = [str(F(N, S)) for S in range(21, 61)]
        lines.append(f"N={N}; S=21..60: " + ",".join(vals))
    content = "\n".join(lines) + "\n"
    with open("claude_terms_S21_S60.txt", "w") as f:
        f.write(content)
    print(content)

if __name__ == "__main__":
    main()
