package goldenhex

// Hex is an axial coordinate for the point-up hex grid.
type Hex struct {
	Q int
	R int
}

// Directions matches the artifact convention for directions 0..5.
var Directions = [6]Hex{
	{-1, 0},
	{0, -1},
	{1, -1},
	{1, 0},
	{0, 1},
	{-1, 1},
}

func mod6(i int) int {
	i %= 6
	if i < 0 {
		i += 6
	}
	return i
}

func dir(i int) Hex {
	return Directions[mod6(i)]
}

func (h Hex) Add(other Hex) Hex {
	return Hex{Q: h.Q + other.Q, R: h.R + other.R}
}
