// Command dyndns-server is as simple dynamic dns server
// that uses client certificate authentication to verify
// clients and updates records in Google Cloud DNS.

// TODO: At some point turn this into a proper DDNS server.

package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"

	"golang.org/x/oauth2/google"
	dns "google.golang.org/api/dns/v1"

	"github.com/IanLewis/homepage/dyndns/server/sync"
)

//go:generate go run scripts/gen.go

var (
	addr       = flag.String("addr", stringEnv("ADDR", ":8080"), "Address to bind to")
	configFile = flag.String("config", stringEnv("CONFIG", ""), "Path to config JSON file")

	project        = flag.String("project", stringEnv("PROJECT_ID", ""), "Google Cloud Platform project Id.")
	managedZone    = flag.String("zone", stringEnv("MANAGED_ZONE", ""), "Name of the Cloud DNS Managed Zone.")
	serviceAccount = flag.String("service-account", stringEnv("SERVICE_ACCOUNT_JSON", ""), "Path to service-account.json file for Google Cloud DNS")
	insecure       = flag.Bool("insecure", false, "Run in insecure mode..")
	version        = flag.Bool("version", false, "Print the version and exit.")
)

type domain struct {
	Name string `json:"name"`
	Key  string `json:"key"`
}

type serverConfig struct {
	Domains []domain `json:"domains"`
}

var syncer sync.Syncer
var config serverConfig

var cloudDnsScopes = []string{
	dns.CloudPlatformScope,
	dns.CloudPlatformReadOnlyScope,
	dns.NdevClouddnsReadonlyScope,
	dns.NdevClouddnsReadwriteScope,
}

var managedRecords []*dns.ResourceRecordSet

// Read configuration from a Kubernetes configmap/secrets compatible
// envdir directory or from environment variables.
func stringEnv(key, def string) string {
	val := os.Getenv(key)
	if val != "" {
		return val
	}

	return def
}

func getFileContents(pathToFile string) ([]byte, error) {
	// Open file
	f, err := os.Open(pathToFile)
	if err != nil {
		return []byte{}, fmt.Errorf("Could not open %s: %v", pathToFile, err)
	}
	defer f.Close()

	contents, err := ioutil.ReadAll(f)
	if err != nil {
		return []byte{}, fmt.Errorf("Could not read %s: %v", f, err)
	}

	return contents, nil
}

func getServerConfig(pathToJson string) (serverConfig, error) {
	var cfg serverConfig

	jsonContents, err := getFileContents(pathToJson)
	if err != nil {
		return cfg, err
	}

	err = json.Unmarshal(jsonContents, &cfg)
	if err != nil {
		return cfg, fmt.Errorf("Could not load %s: %v", pathToJson, err)
	}

	return cfg, nil
}

func getDNSClient(pathToJson string) (*dns.Service, error) {
	jsonContents, err := getFileContents(pathToJson)
	if err != nil {
		return nil, err
	}

	config, err := google.JWTConfigFromJSON(jsonContents, cloudDnsScopes...)
	if err != nil {
		return nil, fmt.Errorf("Could not load %s: %v", pathToJson, err)
	}

	ctx := context.Background()
	client := config.Client(ctx)

	service, err := dns.New(client)
	if err != nil {
		return nil, fmt.Errorf("Could not create Google Cloud DNS client: %v", err)
	}

	return service, nil
}

func getRemoteAddr(r *http.Request) string {
	forwardedFor := strings.Split(r.Header.Get("X-Forwarded-For"), ",")
	remoteAddr := strings.Trim(forwardedFor[0], " ")
	if remoteAddr == "" {
		remoteAddr = r.RemoteAddr
	}

	i := strings.LastIndex(remoteAddr, ":")
	if i == -1 {
		return remoteAddr
	}
	return remoteAddr[:i]
}

func wrap(f http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		proto := r.Header.Get("X-Forwarded-Proto")
		if proto != "https" && !*insecure {
			url := r.URL
			url.Host = r.Host
			url.Scheme = "https"
			http.Redirect(w, r, url.String(), http.StatusMovedPermanently)
			return
		}
		f(w, r)
	}
}

// recordHandler handles requests from clients to update a DNS record.
func recordHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodPost {
		dnsName := r.PostFormValue("name")
		dnsType := r.PostFormValue("type")
		ttlStr := r.PostFormValue("ttl")
		data := r.PostFormValue("data")
		key := r.PostFormValue("key")

		if !strings.HasSuffix(dnsName, ".") {
			dnsName = dnsName + "."
		}

		ttl, err := strconv.ParseInt(ttlStr, 10, 64)
		if err != nil {
			log.Printf("Bad ttl for domain %s: %s", dnsName, ttlStr)
			http.Error(w, "Bad ttl", http.StatusBadRequest)
		}

		if data == "__remoteaddr__" {
			data = getRemoteAddr(r)
		}

		for _, domain := range config.Domains {
			// Clients can alter subdomains of domain they have access to
			if domain.Name+"." == dnsName || strings.HasSuffix(dnsName, "."+domain.Name+".") {
				if domain.Key == key {
					// OK to update.
					syncer.UpdateRecord(dnsName, dnsType, ttl, []string{data})
					return
				} else {
					log.Printf("Bad key for domain %s: %s", dnsName, key)
					http.Error(w, "Bad key", http.StatusBadRequest)
					return
				}
			}
		}

		log.Printf("Bad domain %s", dnsName)
		http.Error(w, "Bad domain", http.StatusBadRequest)
		return
	}
	http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
}

func notFound(w http.ResponseWriter, r *http.Request) {
	http.Error(w, "Not Found", http.StatusNotFound)
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("OK"))
}

func main() {
	flag.Parse()

	if *version {
		fmt.Println(VERSION)
		return
	}

	if *project == "" {
		log.Fatal("-project is required.")
	}

	if *managedZone == "" {
		log.Fatal("-zone is required")
	}

	service, err := getDNSClient(*serviceAccount)
	if err != nil {
		log.Fatal(err)
	}

	cfg, err := getServerConfig(*configFile)
	if err != nil {
		log.Fatal(err)
	}
	config = cfg

	// Start the syncer in the background.
	syncer = sync.NewSyncer(service, *project, *managedZone, 2*time.Minute, 10*time.Second, 5*time.Second)
	syncer.Run()

	http.HandleFunc("/_status/healthz", healthHandler)
	http.HandleFunc("/api/record/", wrap(recordHandler))
	http.HandleFunc("/", wrap(notFound))

	if *insecure {
		log.Printf("WARNING: Running in insecure mode!")
	}
	log.Printf("Listening on %s...", *addr)
	log.Fatal(http.ListenAndServe(*addr, nil))
}
