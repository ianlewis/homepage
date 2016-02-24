package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/IanLewis/homepage/api/logging"

	"github.com/gorilla/handlers"
	"github.com/gorilla/mux"
	"github.com/rs/cors"
)

var VERSION = "0.6.4"

// Command line options used when starting the server.
var (
	addr         = flag.String("addr", getConfig("ADDRESS", ":8080"), "The address to bind the api server to.")
	certFile     = flag.String("cert", getConfig("API_SERVER_CRT", ""), "HTTPS certificate file")
	keyFile      = flag.String("key", getConfig("API_SERVER_KEY", ""), "HTTPS key file")
	baseUrl      = flag.String("base-url", getConfig("API_SERVER_BASE_URL", ""), "Base URL of the api server")
	debugMode    = flag.Bool("debug", false, "Enable debug mode.")
	printVersion = flag.Bool("version", false, "Print the version and exit.")
)

// Reads the contents of a file
func readFile(path string) (string, error) {
	f, err := os.Open(path)
	if err != nil {
		return "", err
	}
	defer f.Close()
	b, err := ioutil.ReadAll(f)
	if err != nil {
		return "", err
	}
	return strings.Trim(string(b), " \n\r"), nil
}

type JsonError struct {
	Title  string `json:"title"`
	Status string `json:"status"`
}

var NotFound = JsonError{
	"Not Found",
	"404",
}

var ServerError = JsonError{
	"Internal Server Error",
	"500",
}

type Resource struct {
	Id         string            `json:"id"`
	Type       string            `json:"type"`
	Links      map[string]string `json:"links"`
	Attributes interface{}       `json:"attributes"`
}

type Profile struct {
	Name struct {
		GivenNames []string `json:"given_names"`
		FamilyName string   `json:"family_name"`
	} `json:"name"`
	Birthday time.Time `json:"birthday"`
}

var PeopleMap = map[string]Resource{
	"ian": {
		Id:   "ian",
		Type: "ianlewis.org/person",
		Links: map[string]string{
			"self":    "/people/ian",
			"twitter": "https://twitter.com/IanMLewis",
		},
		Attributes: Profile{
			Name: struct {
				GivenNames []string `json:"given_names"`
				FamilyName string   `json:"family_name"`
			}{
				[]string{"Ian", "Matthew"},
				"Lewis",
			},
			// 1981/10/29 22:01 EST
			// 1981/10/30 03:01 UTC
			Birthday: time.Unix(373284060, 0),
		},
	},
	"reiko": {
		Id:   "reiko",
		Type: "ianlewis.org/person",
		Links: map[string]string{
			"self": "/people/reiko",
		},
		Attributes: Profile{
			Name: struct {
				GivenNames []string `json:"given_names"`
				FamilyName string   `json:"family_name"`
			}{
				[]string{"Reiko"},
				"Lewis",
			},
			// 1977/04/24 00:00 JST
			// 1977/10/23 15:00 UTC
			Birthday: time.Unix(230655600, 0),
		},
	},
	"jin": {
		Id:   "jin",
		Type: "ianlewis.org/person",
		Links: map[string]string{
			"self":    "/people/jin",
			"twitter": "https://twitter.com/Jin_tmanchester",
		},
		Attributes: Profile{
			Name: struct {
				GivenNames []string `json:"given_names"`
				FamilyName string   `json:"family_name"`
			}{
				[]string{"Jin"},
				"Lewis",
			},
			// 2009/04/23 00:00 JST
			// 2009/04/22 15:00 UTC
			Birthday: time.Unix(1240412400, 0),
		},
	},
}

// apiHandler wraps the given handler with standard
// middleware for serving API requests.
func apiHandler(h http.Handler) http.Handler {
	// Support CORS (Allow all origins)
	c := cors.New(cors.Options{
		// Allows requests from browsers (API is read-only).
		AllowedHeaders: []string{"Accept", "X-Requested-With"},
		Debug:          *debugMode,
	})
	return c.Handler(h)
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	// TODO: Check dependent services.
	w.Write([]byte("OK"))
}

func versionHandler(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte(VERSION))
}

// The main function for the API server.
func main() {
	flag.Parse()

	// Print the version if requested.
	if *printVersion {
		fmt.Println(VERSION)
		os.Exit(0)
	}

	debug := ioutil.Discard
	if *debugMode {
		debug = os.Stdout
	}

	logging.InitLogging(debug, os.Stdout, os.Stdout, os.Stderr, os.Stderr)

	r := mux.NewRouter().StrictSlash(true)

	// Print a list of urls as hyperlinks.
	r.Handle(*baseUrl+"/", apiHandler(handlers.MethodHandler{
		"GET": http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			enc := json.NewEncoder(w)
			enc.Encode(&struct {
				JsonApi map[string]string `json:"jsonapi"`
				Links   map[string]string `json:"links"`
			}{
				map[string]string{
					"version": "1.0",
				},
				map[string]string{
					"people": "/people/",
				},
			})
		}),
	}))

	// An API handler to get basic info about me.
	r.Handle(*baseUrl+"/people/", apiHandler(handlers.MethodHandler{
		"GET": http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			enc := json.NewEncoder(w)

			p := make([]Resource, 0, len(PeopleMap))
			for _, v := range PeopleMap {
				p = append(p, v)
			}

			enc.Encode(&struct {
				Data []Resource `json:"data"`
			}{
				p,
			})
		}),
	}))

	r.Handle(*baseUrl+"/people/{id}", apiHandler(handlers.MethodHandler{
		"GET": http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			enc := json.NewEncoder(w)
			vars := mux.Vars(r)
			p, ok := PeopleMap[vars["id"]]
			if ok {
				enc.Encode(&p)
			} else {
				w.WriteHeader(404)
				enc.Encode(&NotFound)
			}
		}),
	}))

	r.HandleFunc("/_status/healthz", healthHandler)
	r.HandleFunc("/_status/version", versionHandler)

	logging.Info.Printf("API service listening on %s...", *addr)

	// Add handler middleware for logging.
	h := handlers.CombinedLoggingHandler(logging.LogWriter{logging.Info}, r)

	// Support GZip Compression
	h = handlers.CompressHandler(h)

	s := &http.Server{
		Addr:    *addr,
		Handler: h,
	}
	if *certFile != "" && *keyFile != "" {
		log.Fatal(s.ListenAndServeTLS(*certFile, *keyFile))
	} else {
		log.Fatal(s.ListenAndServe())
	}
}
