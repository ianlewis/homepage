// A cron app that will my cron jobs.

package main

import (
	"bufio"
	"flag"
	"io"
	"io/ioutil"
	"log"
	"os"
	"os/exec"
	"regexp"
	"strings"

	"github.com/robfig/cron"
)

var (
	debugMode  = flag.Bool("debug", false, "Enable debug logging.")
	configPath = flag.String("conf", "/crontab", "Path to the crontab config.")
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
	Info = log.New(i, "[INFO]  ", log.Ldate|log.Ltime|log.Lshortfile)
	Warning = log.New(w, "[WARN]  ", log.Ldate|log.Ltime|log.Lshortfile)
	Error = log.New(e, "[ERROR] ", log.Ldate|log.Ltime|log.Lshortfile)
	Fatal = log.New(f, "[FATAL] ", log.Ldate|log.Ltime|log.Lshortfile)
}

// Creates a function that runs a command.
func createCmdFunc(cmd string, args []string) func() {
	return func() {
		c := exec.Command(cmd, args...)
		Info.Println("Running:", cmd, strings.Join(args, " "))
		o, err := c.CombinedOutput()
		if len(o) > 0 {
			Debug.Println(string(o))
		}
		if err != nil {
			Error.Println(err)
			return
		}
		Info.Println("Completed:", cmd, strings.Join(args, " "))
		Debug.Println(string(o))
	}
}

// Parses the config file and starts the server.
func startCron() error {
	c, err := os.Open(*configPath)
	if err != nil {
		return err
	}
	defer c.Close()

	server := cron.New()

	scanner := bufio.NewScanner(c)

	r := regexp.MustCompile("\\s")

	for scanner.Scan() {
		line := r.Split(strings.Trim(scanner.Text(), " \t"), -1)

		var sched, cmd string
		var args []string
		if strings.HasPrefix(line[0], "@every") {
			sched = strings.Join(line[:2], " ")
			cmd = line[2]
			args = line[3:]
		} else if strings.HasPrefix(line[0], "@") {
			sched = line[0]
			cmd = line[1]
			args = line[2:]
		} else {
			sched = strings.Join(line[:5], " ")
			cmd = line[5]
			args = line[6:]
		}

		// Make the schedule have minute not second resolution.
		server.AddFunc("0 "+sched, createCmdFunc(cmd, args))
	}

	server.Start()

	return nil
}

func main() {
	flag.Parse()

	debug := ioutil.Discard
	if *debugMode {
		debug = os.Stdout
	}

	initLogging(debug, os.Stdout, os.Stdout, os.Stderr, os.Stderr)

	err := startCron()
	if err != nil {
		Error.Fatal("Could not start cron:", err)
	}

	select {}
}
