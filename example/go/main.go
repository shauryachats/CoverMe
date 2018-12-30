package main

func SomeFuncToTest(value int) int {
	if value == 0 {
		// markov
		return -1
	}
	value = value * value
	return value
}
