package main

import (
    "os"
    "strings"
    "bytes"
    "io/ioutil"

    "bitbucket.org/IanLewis/ianlewis-api/logging"
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
				logging.Warning.Println("Could not read file " + fileName)
			}
		}
	}

	return def
}
