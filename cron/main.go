// Copyright 2016 Google Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// Command simple-crontab-controller implements a crontab controller that
// watches for CronTab third party resources and runs a cron control
// loop for each. If the crontab is modified, then the cron loop is
// restarted with the new configuration. If it is deleted then the cron
// loop is stopped.
package main

import (
	"bytes"
	"crypto/sha1"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/robfig/cron"
)

//go:generate go run scripts/gen.go

// TODO: support for multiple namespaces?
const (
	// A path to the Kubernetes Jobs API endpoint.
	jobsEndpoint = "http://%s/apis/extensions/v1beta1/namespaces/%s/jobs"

	// A path to the endpoint for the CronTab custom resources.
	cronTabsEndpoint = "http://%s/apis/alpha.ianlewis.org/v1/namespaces/%s/crontabs"
)

func getEnvDefault(name, def string) string {
	val := os.Getenv(name)
	if val == "" {
		val = def
	}
	return val
}

var (
	pollInterval = flag.Int("poll-interval", 15, "The polling interval in seconds.")
	// The controller connects to the Kubernetes API via localhost. This is either
	// a locally running kubectl proxy or kubectl proxy running in a sidecar container.
	server    = flag.String("server", "127.0.0.1:8001", "The address and port of the Kubernetes API server.")
	namespace = flag.String("namespace", getEnvDefault("NAMESPACE", "default"), "The namespace to use.")
	version   = flag.Bool("version", false, "Show the version number and exit.")
)

// cronServer encapsulates a cron server along with it's crontab
type cronServer struct {
	Server *cron.Cron
	Object cronTab
}

// This is an in-memory map of cron servers that is managed by this controller.
// The map is indexed by the UID of the CronTab object registered in the Kubernetes API.
var cronServers = make(map[string]cronServer, 0)

// lables correspond to labels in the Kubernetes API.
type labels *map[string]string

// objectMeta corresponds to object metadata in the Kubernetes API.
type objectMeta struct {
	Name            string `json:"name"`
	UID             string `json:"uid,omitempty"`
	ResourceVersion string `json:"resourceVersion,omitempty"`
	Labels          labels `json:"labels,omitempty"`
}

type cronTabList struct {
	Items []cronTab `json:"items"`
}

// cronTab represents a JSON object for the CronTab custom resource that we register in the Kubernetes API.
type cronTab struct {
	// The following fields mirror the fields in the third party resource.
	ObjectMeta objectMeta  `json:"metadata"`
	Spec       cronTabSpec `json:"spec"`
}

type cronTabSpec struct {
	Schedule    string          `json:"schedule"`
	JobTemplate jobTemplateSpec `json:"jobTemplate"`
}

// job represents a JSON Job object in the Kubernetes API.
type job struct {
	ObjectMeta objectMeta `json:"metadata"`
	JobSpec    jobSpec    `json:"spec"`
}

// selector represents a JSON selector object in the Kubernetes API.
type selector struct {
	MatchLabels labels `json:"matchLabels,omitempty"`
}

type fieldRef struct {
	FieldPath string `json:"fieldPath,omitempty"`
}

type configMapKeyRef struct {
	Name string `json:"name,omitempty"`
	Key  string `json:"key,omitempty"`
}

type valueFrom struct {
	FieldRef        *fieldRef        `json:"fieldRef,omitempty"`
	ConfigMapKeyRef *configMapKeyRef `json:"configMapKeyRef,omitempty"`
}

type envVar struct {
	Name      string     `json:"name,omitempty"`
	Value     string     `json:"value,omitempty"`
	ValueFrom *valueFrom `json:"valueFrom,omitempty"`
}

type volumeMount struct {
	Name      string `json:"name,omitempty"`
	MountPath string `json:"mountPath,omitempty"`
}

type limits struct {
	Cpu    string `json:"cpu,omitempty"`
	Memory string `json:"memory,omitempty"`
}

type resources struct {
	Limits   *limits `json:"limits,omitempty"`
	Requests *limits `json:"requests,omitempty"`
}

// container represents a JSON container object in the Kubernetes API.
type container struct {
	Name         string        `json:"name,omitempty"`
	Image        string        `json:"image,omitempty"`
	Env          []envVar      `json:"env,omitempty"`
	VolumeMounts []volumeMount `json:"volumeMounts,omitempty"`
	Resources    *resources    `json:"resources,omitempty"`
}

type volumeSecret struct {
	SecretName string `json:"secretName,omitempty"`
}

type volume struct {
	Name   string        `json:"name,omitempty"`
	Secret *volumeSecret `json:"secret,omitempty"`
}

// jobTemplateSpec represents a Job template specification in the Kubernetes API.
type jobTemplateSpec struct {
	Containers    []container `json:"containers,omitempty"`
	RestartPolicy string      `json:"restartPolicy,omitempty"`
	Volumes       []volume    `json:"volumes,omitempty"`
}

// jobTemplate represents a Job template in the Kubernetes API.
type jobTemplate struct {
	ObjectMeta      objectMeta       `json:"metadata"`
	JobTemplateSpec *jobTemplateSpec `json:"spec,omitempty"`
}

// jobSpec represents a Job specification in the Kubernetes API.
type jobSpec struct {
	Selector *selector    `json:"selector,omitempty"`
	Template *jobTemplate `json:"template,omitempty"`
}

// pollCronTabs polls the Kubernetes API and sends the contents
// of the cron job to the given channel when a change is detected.
// An initial version of the object is sent to the channel when first
// starting the poll loop.
func pollCronTabs() {
	first := true

	// Events and errors are not expected to be generated very often so
	// only allow the controller to buffer 100 of each.
	for {
		// Sleep for the poll interval if not the first time around.
		// Do this here so we sleep for the poll interval every time,
		// even after errors occurred.
		if !first {
			time.Sleep(time.Duration(*pollInterval) * time.Second)
		}
		first = false

		resp, err := http.Get(fmt.Sprintf(cronTabsEndpoint, *server, *namespace))
		if err != nil {
			log.Printf("Could not connect to Kubernetes API: %v", err)
			continue
		}
		if resp.StatusCode != http.StatusOK {
			log.Printf("Unexpected status code: %s", resp.Status)
			continue
		}

		decoder := json.NewDecoder(resp.Body)
		var l cronTabList

		err = decoder.Decode(&l)
		if err != nil {
			log.Printf("Could not decode JSON event object: %v", err)
			continue
		}

		// Loop through the returned CrotTab objects and
		// send events for the new versions
		for _, s := range cronServers {
			found := false
			for _, c := range l.Items {
				if c.ObjectMeta.UID == s.Object.ObjectMeta.UID {
					found = true
				}
			}
			if !found {
				removeCronTab(s.Object)
			}
		}

		for _, c := range l.Items {
			found := false
			for _, s := range cronServers {
				if c.ObjectMeta.UID == s.Object.ObjectMeta.UID {
					if c.ObjectMeta.ResourceVersion != s.Object.ObjectMeta.ResourceVersion {
						log.Printf("Updating crontab %s", c.ObjectMeta.Name)
						removeCronTab(s.Object)
						err := addCronTab(c)
						if err != nil {
							log.Printf("Could not create crontab %#v: %v", c, err)
						}
					}
					found = true
				}
			}
			if !found {
				err := addCronTab(c)
				if err != nil {
					log.Printf("Could not create crontab %#v: %v", c, err)
				}
			}
		}
	}
}

// addCronTab creates a cron server for the given cronTab and
// and begins managing it.
func addCronTab(c cronTab) error {
	// We create a new cron server here since there is no way
	// in the github.com/robfig/cron package to remove entries.
	server := cron.New()

	// Support only traditional cronspec
	// Don't support seconds
	spec := c.Spec.Schedule
	if !strings.HasPrefix(c.Spec.Schedule, "@") {
		spec = "0 " + c.Spec.Schedule

	}
	err := server.AddFunc(spec, func() {
		if err := runCronJob(c); err != nil {
			log.Printf("Error running cron job: %v", err)
		}
	})
	if err != nil {
		return fmt.Errorf("error adding crontab: %v", err)
	}

	cronServers[c.ObjectMeta.UID] = cronServer{
		Server: server,
		Object: c,
	}

	server.Start()

	log.Printf("Added crontab: %s", c.ObjectMeta.Name)

	return nil
}

// removeCronTab stops a cron server for the given cronTab and
// stops managing it.
func removeCronTab(c cronTab) {
	if server, ok := cronServers[c.ObjectMeta.UID]; ok {
		server.Server.Stop()
		delete(cronServers, c.ObjectMeta.UID)
		log.Printf("Removed crontab: %s", c.ObjectMeta.Name)
	}
}

// runCronTab executes the a cron job for the given cronTab
// by creating a new Job object in the Kubernetes API.
func runCronJob(c cronTab) error {
	name := makeJobName(c)

	log.Printf("Creating job %s for crontab %s", name, c.ObjectMeta.Name)

	job := job{
		ObjectMeta: objectMeta{
			Name: name,
		},
		JobSpec: jobSpec{
			Selector: &selector{
				MatchLabels: &map[string]string{
					"name": name,
				},
			},
			Template: &jobTemplate{
				ObjectMeta: objectMeta{
					Name: name,
					Labels: &map[string]string{
						"name": name,
					},
				},
				JobTemplateSpec: &c.Spec.JobTemplate,
			},
		},
	}

	j, err := json.Marshal(job)
	if err != nil {
		return fmt.Errorf("could not marshal job to JSON: %s", err)
	}

	url := fmt.Sprintf(jobsEndpoint, *server, *namespace)
	resp, err := http.Post(url, "application/json", bytes.NewReader(j))
	if err != nil {
		return fmt.Errorf("HTTP request failed: %s", err)
	}
	if resp.StatusCode != http.StatusCreated {
		b, err := ioutil.ReadAll(resp.Body)
		var errMsg string
		if err != nil {
			errMsg = "Unknown Error"
		} else {
			errMsg = string(b)
		}

		return fmt.Errorf("post request failed (%s): %s", resp.Status, errMsg)
	}

	return nil
}

// makesJobName creats a unique job name based on the UID of the
// crontab and the current time.
func makeJobName(t cronTab) string {
	hasher := sha1.New()
	fmt.Fprintf(hasher, "%d%10d", t.ObjectMeta.UID, time.Now().UnixNano())

	// Hashes are shortened to 5 characters to keep them reasonably manageable to
	// work with. Names of objects in Kubernetes must be lowercase alphanumeric so
	// the hash value is encoded to hex and changed to lowercase.
	hash := hex.EncodeToString(hasher.Sum(nil))
	return t.ObjectMeta.Name + "-" + strings.ToLower(hash[2:7])
}

func main() {
	flag.Parse()

	if *version {
		fmt.Println(VERSION)
		os.Exit(0)
	}

	log.Printf("Watching for crontab objects...")

	// Get the channel of results from the watch
	pollCronTabs()
}
