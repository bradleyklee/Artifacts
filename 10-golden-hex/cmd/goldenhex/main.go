package main

import (
	"flag"
	"fmt"
	"os"
	"strings"

	"goldenhex/goldenhex"
)

func main() {
	if len(os.Args) < 2 {
		usage()
		os.Exit(2)
	}

	var err error
	switch os.Args[1] {
	case "counts":
		err = runCounts(os.Args[2:])
	case "sequence":
		err = runSequence(os.Args[2:], false)
	case "differences":
		err = runSequence(os.Args[2:], true)
	default:
		usage()
		os.Exit(2)
	}
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func runCounts(args []string) error {
	fs := flag.NewFlagSet("counts", flag.ExitOnError)
	maxN := fs.Int("n", 40, "largest n to print")
	table := fs.Bool("table", false, "print D, H, objects, and cell counts")
	if err := fs.Parse(args); err != nil {
		return err
	}

	rows := goldenhex.CountTable(*maxN)
	if *table {
		fmt.Println("n,D_dimers,H_hexagons,objects,hexagonal_cells")
		for _, row := range rows {
			fmt.Printf("%d,%s,%s,%s,%s\n", row.N, row.Dimers.String(), row.Hexagons.String(), row.Objects.String(), row.HexagonalCells.String())
		}
		return nil
	}

	parts := make([]string, len(rows))
	for i, row := range rows {
		parts[i] = row.HexagonalCells.String()
	}
	fmt.Println(strings.Join(parts, ", "))
	return nil
}

func runSequence(args []string, differences bool) error {
	fs := flag.NewFlagSet("sequence", flag.ExitOnError)
	level := fs.Int("level", 6, "finite substitution level")
	if err := fs.Parse(args); err != nil {
		return err
	}

	seq, err := goldenhex.ReplaySequence(*level)
	if err != nil {
		return err
	}
	if differences {
		parts := make([]string, len(seq))
		parts[0] = "—"
		for i := 1; i < len(seq); i++ {
			parts[i] = fmt.Sprint(seq[i] - seq[i-1])
		}
		fmt.Println(strings.Join(parts, ", "))
		return nil
	}

	parts := make([]string, len(seq))
	for i, value := range seq {
		parts[i] = fmt.Sprint(value)
	}
	fmt.Println(strings.Join(parts, ", "))
	return nil
}

func usage() {
	fmt.Fprintln(os.Stderr, "usage: goldenhex <counts|sequence|differences> [options]")
	fmt.Fprintln(os.Stderr, "  counts      [-n 40] [-table]")
	fmt.Fprintln(os.Stderr, "  sequence    [-level 6]")
	fmt.Fprintln(os.Stderr, "  differences [-level 6]")
}
