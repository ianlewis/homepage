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
		if err != nil {
			if len(o) > 0 {
				Debug.Println(string(o))
			}
			Error.Println(err)
			return
		}
		Info.Println("Completed:", cmd, strings.Join(args, " "))
		Debug.Println(string(o))
	}
}

// See: https://gist.github.com/jmervine/d88c75329f98e09f5c87
func safeSplit(s string) []string {
	split := strings.Split(s, " ")

	var result []string
	var inquote string
	var block string
	for _, i := range split {
		if inquote == "" {
			if strings.HasPrefix(i, "'") || strings.HasPrefix(i, "\"") {
				inquote = string(i[0])
				block = strings.TrimPrefix(i, inquote) + " "
			} else {
				result = append(result, i)
			}
		} else {
			if !strings.HasSuffix(i, inquote) {
				block += i + " "
			} else {
				block += strings.TrimSuffix(i, inquote)
				inquote = ""
				result = append(result, block)
				block = ""
			}
		}
	}

	return result
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
		line := scanner.Text()
		tempParts := r.Split(strings.Trim(line, " \t"), -1)

		// Skip commented out lines
		if strings.HasPrefix(tempParts[0], "#") {
			continue
		}

		var sched, cmd string
		var args []string
		if strings.HasPrefix(tempParts[0], "@every") {
			// This time only split 3 parts.
			// @every day <command>
			tempParts := r.Split(strings.Trim(line, " \t"), 3)
			sched = strings.Join(tempParts[:2], " ")
			parts := safeSplit(tempParts[2])
			cmd = parts[0]
			args = parts[1:]
		} else if strings.HasPrefix(tempParts[0], "@") {
			// Only split into 2 parts.
			// @daily <command>
			tempParts := r.Split(strings.Trim(line, " \t"), 2)
			sched = tempParts[0]
			parts := safeSplit(tempParts[1])
			cmd = parts[0]
			args = parts[1:]
		} else {
			// Split into 6 parts
			// * * * * * <command>
			tempParts := r.Split(strings.Trim(line, " \t"), 6)
			sched = strings.Join(tempParts[:5], " ")
			parts := safeSplit(tempParts[5])
			cmd = parts[0]
			args = parts[1:]
		}

		if *debugMode {
			argsDebug := ""
			for _, a := range args {
				argsDebug += "- " + a + "\n"
			}
			Debug.Printf("Adding:\n\nschedule: %s\ncmd: %s\nargs:\n%s", sched, cmd, argsDebug)
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
