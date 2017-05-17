// Command dyndns-server is as simple dynamic dns server
// that uses client certificate authentication to verify
// clients and updates records in Google Cloud DNS.

package main

import (
	"bytes"
	"crypto/tls"
	"crypto/x509"
	"flag"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strings"
)

var (
	addr    = flag.String("addr", getConfig("ADDR", ":8080"), "Address to bind to")
	caCert  = flag.String("cert", getConfig("CA_CERT", ""), "CA certificate file")
	keyFile = flag.String("key", getConfig("PRIVATE_KEY", ""), "Private key file")

	config = flag.String("config", getConfig("CONFIG", ""), "Path to config JSON file")
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

func handleRecords(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodPost {
		host := r.PostFormValue("host")
		ttl := r.PostFormValue("ttl")

		addr := strings.Split(r.RemoteAddr, ":")
		log.Printf("%s %s %s", host, ttl, addr[0])
		// TODO
		return
	}
	http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("OK"))
}

func main() {
	flag.Parse()

	// Load our CA certificate
	ca, err := ioutil.ReadFile(*caCert)
	if err != nil {
		log.Fatal("Unable to open ca cert", err)
	}

	certPool := x509.NewCertPool()
	// TODO: Add client certs
	certPool.AppendCertsFromPEM(ca)

	tlsConfig := &tls.Config{
		// Reject any TLS certificate that cannot be validated
		ClientAuth: tls.RequireAndVerifyClientCert,
		// Ensure that we only use our "CA" to validate certificates
		ClientCAs: certPool,
		// PFS because we can but this will reject client with RSA certificates
		CipherSuites: []uint16{tls.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256},
		// Force it server side
		PreferServerCipherSuites: true,
		// TLS 1.2 because we can
		MinVersion: tls.VersionTLS12,
	}

	tlsConfig.BuildNameToCertificate()

	http.HandleFunc("/api/records/", handleRecords)
	http.HandleFunc("/healthz", healthHandler)

	httpServer := &http.Server{
		Addr:      *addr,
		TLSConfig: tlsConfig,
	}

	log.Printf("Listening on %s...", *addr)
	log.Fatal(httpServer.ListenAndServeTLS(*caCert, *keyFile))
}
