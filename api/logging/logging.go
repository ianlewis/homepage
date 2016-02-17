package logging

import (
    "io"
    "log"
)

// These are the various loggers. We export these externally
// so they can be used for logging throughout the application.
// InitLogging() must be called to initialize these loggers.
var (
    Debug   *log.Logger
    Info    *log.Logger
    Warning *log.Logger
    Error   *log.Logger
    Fatal   *log.Logger
)


// Initializes logging. Logging is done to stdout (< ERROR) and sterr (>= ERROR)
// Fatal error messages should use Fatal.Fatal()
func InitLogging(d, i, w, e, f io.Writer) {
    Debug = log.New(d, "[DEBUG] ", log.Ldate|log.Ltime|log.Lshortfile)
    Info = log.New(i,   "[INFO]  ", log.Ldate|log.Ltime|log.Lshortfile)
    Warning = log.New(w, "[WARN]  ", log.Ldate|log.Ltime|log.Lshortfile)
    Error = log.New(e, "[ERROR] ", log.Ldate|log.Ltime|log.Lshortfile)
    Fatal = log.New(f, "[FATAL] ", log.Ldate|log.Ltime|log.Lshortfile)
}

// A simple io.Writer wrapper around a logger so that we can use
// the logger as an io.Writer
type LogWriter struct { *log.Logger }
func (w LogWriter) Write(b []byte) (int, error) {
      w.Printf("%s", b)
      return len(b), nil
}
