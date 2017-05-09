// A phone call forwarding app that uses Twilio
// for the dialer and Firebase as the backing datastore.

package main

import (
	"encoding/xml"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"math/rand"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/zabawaba99/fireauth"
	"github.com/zabawaba99/firego"
)

//go:generate go run scripts/gen.go

// lastReadinessCheck is a Time object containing a timestamp of the last successful readiness check.
var lastReadinessCheck time.Time

var Firebase *firego.Firebase

type TwiML struct {
	XMLName xml.Name `xml:"Response"`
	Dial    Number   `xml:",omitempty"`
	Say     string   `xml:",omitempty"`
}

type Number struct {
	Number []string
}

type CallHistory struct {
	Sid      string `json:"sid"`
	Time     int64  `json:"time"`
	From     string `json:"from"`
	To       string `json:"to"`
	Duration int64  `json:"duration"`
}

// Read configuration from a Kubernetes secrets compatible
// envdir directory or from environment variables.
func getConfig(key, def string) string {
	val := os.Getenv(key)
	if val != "" {
		return val
	}

	return def
}

func getConfigDuration(key string, def time.Duration) time.Duration {
	val := os.Getenv(key)
	if val != "" {
		d, err := time.ParseDuration(val)
		if err != nil {
			log.Printf("Invalid value in environment variable %s: %s", key, val)
			return def
		}
		return d
	}

	return def
}

var (
	addr            = flag.String("addr", ":8080", "The address to listen on.")
	firebaseUriPath = flag.String("firebase-uri-path", getConfig("FIREBASE_URI_PATH", "/etc/twilio-forwarder/firebase-uri"), "The path to a file containing the firebase URI.")
	secretPath      = flag.String("secret-path", getConfig("FIREBASE_SECRET_PATH", "/etc/twilio-forwarder/firebase-secret"), "The path a file containing the firebase secret to use for authentication.")
	healthFreq      = flag.Duration("health-freq", getConfigDuration("HEALTH_DURATION", 5*time.Minute), "How often readiness checks should hit the database.")
	version         = flag.Bool("version", false, "Show the version number and exit.")
)

// Reads the Firebase URI
func readUri() string {
	f, err := os.Open(*firebaseUriPath)
	if err != nil {
		log.Fatal("Could not open Firebase URI file: %v", err)
	}
	defer f.Close()
	b, err := ioutil.ReadAll(f)
	if err != nil {
		log.Fatal("Could not read Firebase URI file: %v", err)
	}
	return strings.Trim(string(b), " \n\r")
}

// Reads the secret for use with Firebase
func readSecret() string {
	f, err := os.Open(*secretPath)
	if err != nil {
		log.Fatal("Could not open secret file: %v", err)
	}
	defer f.Close()
	b, err := ioutil.ReadAll(f)
	if err != nil {
		log.Fatal("Could not read secret file: %v", err)
	}
	return strings.Trim(string(b), " \n\r")
}

// Connect to Firebase
func connectFirebase() {
	uri := readUri()

	log.Printf("Connecting to %s", uri)

	Firebase = firego.New(uri, nil)
}

// Authenticate the Firebase connection
func authFirebase() {
	secret := readSecret()

	log.Printf("Generating new Firebase token")

	gen := fireauth.New(secret)
	token, err := gen.CreateToken(fireauth.Data{"uid": "1"}, nil)
	if err != nil {
		log.Fatal("Could not create Firebase auth token: %v", err)
	}

	Firebase.Auth(token)
}

func getNumberKey(num string) string {
	return strings.TrimLeft(num, "+0")
}

func createCallHistory(sid, from, to string) (*CallHistory, error) {
	history := &CallHistory{
		Sid:      sid,
		Time:     time.Now().Unix(),
		From:     from,
		To:       to,
		Duration: 0,
	}

	key := getNumberKey(to)
	if err := Firebase.Child("numbers").Child(key).Child("history").Child(sid).Set(&history); err != nil {
		return nil, err
	}

	return history, nil
}

func finishCallHistory(sid, to string, duration int64) error {
	key := getNumberKey(to)
	if err := Firebase.Child("numbers").Child(key).Child("history").Child(sid).Child("duration").Set(duration); err != nil {
		return err
	}
	return nil
}

// The request handler for a call. Forwards to the appropriate number.
func callForwardHandler(w http.ResponseWriter, r *http.Request) {
	// Validate the request method.
	if r.Method != "POST" {
		log.Printf("%s method not allowed.", r.Method)
		http.Error(w, "Method not allowed.", http.StatusMethodNotAllowed)
		return
	}

	sid := r.PostFormValue("CallSid") // The unique Id of the call
	to := r.PostFormValue("To")       // The phone number that was dialed
	from := r.PostFormValue("From")   // The phone number where the call came from

	// Validate the post values
	if sid == "" || to == "" || from == "" {
		log.Println("Required parameters not present.")
		http.Error(w, "Required parameters not present.", http.StatusBadRequest)
		return
	}

	log.Printf("Received call from %s to %s\n", from, to)

	// Get the numbers to forward to.
	var forwardTo []string
	// Trim the leading plus symbol and zeros
	key := getNumberKey(to)
	if err := Firebase.Child("numbers").Child(key).Child("forward").Value(&forwardTo); err != nil {
		log.Println("Error getting data from Firebase: ", err)
		http.Error(w, "An error occurred.", http.StatusBadRequest)
		return
	}

	if len(forwardTo) == 0 {
		twiml := TwiML{Say: "I'm sorry. Your call was directed at an invalid number and could not be completed."}
		writeTwiML(twiml, w)
		return
	}

	log.Printf("Forwarding call to %s\n", forwardTo)

	if _, err := createCallHistory(sid, from, to); err != nil {
		log.Printf("Error creating call history: %v", err)
		twiml := TwiML{Say: "I'm sorry. Your call could not be completed. Please call back again later."}
		writeTwiML(twiml, w)
		return
	}

	twiml := TwiML{
		Dial: Number{Number: forwardTo},
	}
	writeTwiML(twiml, w)
}

// The callback URL to record info about the call.
func callFinishedHandler(w http.ResponseWriter, r *http.Request) {
	// Record info about the call
	sid := r.PostFormValue("CallSid") // The unique Id of the call
	to := r.PostFormValue("To")       // The phone number that was dialed
	from := r.PostFormValue("From")   // The phone number where the call came from
	if sid == "" || to == "" || from == "" {
		log.Println("Required parameters not present.")
		http.Error(w, "Required parameters not present.", http.StatusBadRequest)
		return
	}

	duration, err := strconv.ParseInt(r.PostFormValue("CallDuration"), 10, 64)
	if err != nil {
		log.Printf("Could not parse call duration: %v", duration)
		http.Error(w, "Bad call duration.", http.StatusBadRequest)
		return
	}

	err = finishCallHistory(sid, to, duration)
	if err != nil {
		log.Printf("Could not finish call history: %v", err)
		http.Error(w, "Internal Error.", http.StatusInternalServerError)
		return
	}

	log.Printf("Finished call from %s to %s\n", from, to)

	// Return empty 200 OK response.
}

// The fallback URL to record errors.
func callErrorHandler(w http.ResponseWriter, r *http.Request) {
	errorCode := r.FormValue("ErrorCode")
	errorUrl := r.FormValue("ErrorUrl")
	if errorCode != "" && errorUrl != "" {
		log.Printf("Error %s at url: %v", errorCode, errorUrl)
	} else if errorUrl != "" {
		log.Printf("Unknown error at url: %v", errorUrl)
	} else {
		log.Printf("Unknown error")
	}

	// TODO: Record error info.

	// TODO: Support other languages?
	twiml := TwiML{Say: "I'm sorry. Your call could not be completed. Please call back again later."}
	writeTwiML(twiml, w)
}

// A utility function to write a TwiML response.
func writeTwiML(twiml TwiML, w http.ResponseWriter) {
	rawxml, err := xml.MarshalIndent(twiml, "", "  ")
	if err != nil {
		errMsg := err.Error()
		log.Printf("Internal Server Error: %s\n", errMsg)
		http.Error(w, errMsg, http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/xml")
	w.Write(rawxml)
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("OK"))
}

func readinessHandler(w http.ResponseWriter, r *http.Request) {
	if time.Since(lastReadinessCheck) > *healthFreq {
		healthz := Firebase.Child("healthz")
		var getVal *int64
		if err := healthz.Set(rand.Int63()); err != nil {
			log.Printf("Could not write to Firebase: %v", err)
			http.Error(w, "firebase: Could not write to Firebase.", http.StatusInternalServerError)
			return
		}
		if err := healthz.Value(&getVal); err != nil {
			log.Printf("Could not read from Firebase: %v", err)
			http.Error(w, "firebase: Could not read from Firebase.", http.StatusInternalServerError)
			return
		}
		lastReadinessCheck = time.Now()
	}
	w.Write([]byte("OK"))
}

func versionHandler(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte(VERSION))
}

func main() {
	flag.Parse()

	if *version {
		fmt.Println(VERSION)
		os.Exit(0)
	}

	connectFirebase()
	// Generate new auth tokens every 24 hours.
	go func() {
		for {
			authFirebase()
			time.Sleep(24 * time.Hour)
		}
	}()

	// The TwiML API handlers.
	http.HandleFunc("/api/v1/request", callForwardHandler)
	http.HandleFunc("/api/v1/fallback", callErrorHandler)
	http.HandleFunc("/api/v1/callback", callFinishedHandler)

	http.HandleFunc("/_status/healthz", healthHandler)
	http.HandleFunc("/_status/readiness", readinessHandler)
	http.HandleFunc("/_status/version", versionHandler)

	// TODO: Admin interface

	log.Printf("Listening on %s...", *addr)
	log.Fatal(http.ListenAndServe(*addr, nil))
}
