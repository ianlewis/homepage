package main

import (
	"io/ioutil"
	"os"
	"strings"
)

// Writes out the version
func main() {
	out, _ := os.Create("version.go")
	f, _ := os.Open("VERSION")
	b, _ := ioutil.ReadAll(f)

	out.WriteString("package main\n\n")
	out.WriteString("const VERSION = `")
	out.WriteString(strings.Trim(string(b), " \n\r"))
	out.WriteString("`\n")
}
