package main

import "testing"

func TestSomeFuncToTest(t *testing.T) {
	val := SomeFuncToTest(5)
	if val != 25 {
		t.Error("Failed test!")
	}
	// val = SomeFuncToTest(0)
}
