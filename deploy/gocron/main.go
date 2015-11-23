// A cron app that will my cron jobs.

package main

import (
	"flag"
	"log"
	"os/exec"
	"io"
	"os"
	"strings"
	"io/ioutil"
	"github.com/robfig/cron"
)

var (
	debugMode = flag.Bool("debug", false, "Enable debug logging.")
)

var (
    Debug   *log.Logger
    Info    *log.Logger
    Warning *log.Logger
    Error   *log.Logger
    Fatal   *log.Logger
)

// Initializes logging. Logging is done to stdout (< ERROR) and sterr (>= ERROR)
// Fatal error messages should use Fatal.Fatal()
func initLogging(d, i, w, e, f io.Writer) {
    Debug = log.New(d, "[DEBUG] ", log.Ldate|log.Ltime|log.Lshortfile)
    Info = log.New(i,   "[INFO]  ", log.Ldate|log.Ltime|log.Lshortfile)
    Warning = log.New(w, "[WARN]  ", log.Ldate|log.Ltime|log.Lshortfile)
    Error = log.New(e, "[ERROR] ", log.Ldate|log.Ltime|log.Lshortfile)
    Fatal = log.New(f, "[FATAL] ", log.Ldate|log.Ltime|log.Lshortfile)
}

// Creates a function that runs a command.
func createCmdFunc(cmd string, args []string) func() {
	return func() {
		c := exec.Command(cmd, args...)
		Info.Println("Running:", cmd, strings.Join(args, " "))
		o, err := c.Output()
		if err != nil {
			Error.Println(err)
			return
		}
		Info.Println("Completed:", cmd, strings.Join(args, " "))
		Debug.Println(string(o))
	}
}

func main() {
	flag.Parse()

	debug := ioutil.Discard
	if *debugMode {
		debug = os.Stdout
	}

	initLogging(debug, os.Stdout, os.Stdout, os.Stderr, os.Stderr)

	server := cron.New()

	// Add necessary cron jobs here.
	server.AddFunc("@daily", createCmdFunc("/kubectl", []string{"create", "-f", "backup.yaml"}))

	server.Start()

	select{}
}
