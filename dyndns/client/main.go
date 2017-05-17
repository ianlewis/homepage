// Command dyndns-client is as simple dynamic dns client
// that periodically pings the dynamic dns server to
// update IP address information.

package main

import (
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"
	"os"
	"strings"
	"time"
)

var (
	server  = flag.String("server", stringEnv("SERVER", ""), "The DynDNS server.")
	domain  = flag.String("domain", stringEnv("DOMAIN", ""), "The domain name to update")
	ttl     = flag.String("ttl", stringEnv("TTL", "600"), "The DNS ttl in seconds")
	keyFile = flag.String("key-file", stringEnv("KEY_FILE", ""), "Path to file containing the domain key.")

	interval = flag.String("interval", stringEnv("TTL", "60s"), "The interval between pings to the server")
)

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

func getBody(resp *http.Response) ([]byte, error) {
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	return body, err
}

func main() {
	flag.Parse()

	sleepInterval, err := time.ParseDuration(*interval)
	if err != nil {
		log.Fatal("Bad interval: %v", err)
	}

	keyBytes, err := getFileContents(*keyFile)
	if err != nil {
		log.Fatal("Could not get key: %v", err)
	}
	key := strings.Trim(string(keyBytes), " \t\n")

	for {
		form := url.Values{}
		form.Add("name", *domain)
		form.Add("type", "A")
		form.Add("ttl", *ttl)
		form.Add("data", "__remoteaddr__")
		form.Add("key", key)

		resp, err := http.Post(
			*server+"/api/record/",
			"application/x-www-form-urlencoded",
			strings.NewReader(form.Encode()),
		)
		if err == nil {
			if resp.StatusCode >= 400 {
				body, err := getBody(resp)
				if err != nil {
					log.Printf("Server error no body: %d %v", resp.StatusCode, err)
				} else {
					log.Printf("Server error: %d %s", resp.StatusCode, body)
				}
			}
		} else {
			log.Printf("Error pinging server: %v", err)
		}

		time.Sleep(sleepInterval)
	}
}
