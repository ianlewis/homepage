// Command dyndns-client is as simple dynamic dns client
// that periodically pings the dynamic dns server to
// update IP address information.

package main

import (
	"bytes"
	"crypto/tls"
	"crypto/x509"
	"flag"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"
	"os"
	"strings"
	"time"
)

var (
	server   = flag.String("server", getConfig("SERVER", ""), "The DynDNS server.")
	caCert   = flag.String("ca", getConfig("CA_CERT", ""), "The ca certificate file")
	certFile = flag.String("cert", getConfig("CLIENT_CERT", ""), "The client certificate file")
	keyFile  = flag.String("key", getConfig("PRIVATE_KEY", ""), "Private key file")

	host = flag.String("host", getConfig("HOST", ""), "The host to update")
	ttl  = flag.String("ttl", getConfig("TTL", "600s"), "The DNS ttl")

	interval = flag.String("interval", getConfig("TTL", "60s"), "The interval between pings to the server")
)

// Read configuration from a Kubernetes secrets compatible
// envdir directory or from environment variables.
func getConfig(key, def string) string {
	val := os.Getenv(key)
	if val != "" {
		return val
	}

	envdir := os.Getenv("ENVDIR_PATH")
	if envdir != "" {
		fileName := envdir + "/" + strings.Replace(strings.ToLower(key), "_", "-", -1)
		fd, err := os.Open(fileName)
		if err == nil {
			buf, err := ioutil.ReadAll(fd)
			if err != nil {
				n := bytes.Index(buf, []byte{0})
				return string(buf[:n])
			} else {
				log.Printf("Could not read file '%s'", fileName)
			}
		}
	}

	return def
}

func getBody(resp *http.Response) (string, error) {
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	return string(body), err
}

func main() {
	flag.Parse()

	// Load our TLS key pair to use for authentication
	cert, err := tls.LoadX509KeyPair(*certFile, *keyFile)
	if err != nil {
		log.Fatalln("Unable to load cert", err)
	}

	// Load our CA certificate
	clientCACert, err := ioutil.ReadFile(*caCert)
	if err != nil {
		log.Fatal("Unable to open cert", err)
	}

	clientCertPool := x509.NewCertPool()
	clientCertPool.AppendCertsFromPEM(clientCACert)

	tlsConfig := &tls.Config{
		Certificates: []tls.Certificate{cert},
		RootCAs:      clientCertPool,
	}

	tlsConfig.BuildNameToCertificate()

	transport := &http.Transport{TLSClientConfig: tlsConfig}
	client := &http.Client{Transport: transport}

	sleepInterval, err := time.ParseDuration(*interval)
	if err != nil {
		log.Fatal("bad interval: %v", err)
	}

	for {
		form := url.Values{}
		form.Add("host", *host)
		form.Add("ttl", *ttl)
		resp, err := client.Post(
			"https://"+*server+"/api/records/",
			"application/x-www-form-urlencoded",
			strings.NewReader(form.Encode()),
		)
		if err == nil {
			if resp.StatusCode > 400 {
				body, err := getBody(resp)
				if err != nil {
					log.Printf("server error no body: %s %v", resp.StatusCode, err)
				} else {
					log.Printf("server error: %s %s", resp.StatusCode, body)
				}
			}
		} else {
			log.Printf("error pinging server: %v", err)
		}

		time.Sleep(sleepInterval)
	}
}
