// This package handles syncing with Cloud DNS records.

package sync

import (
	"context"
	"log"
	"sync"
	"time"

	dns "google.golang.org/api/dns/v1"
)

type Syncer interface {
	Run()
	UpdateRecord(dnsName, dnsType string, ttl int64, data []string)
}

type syncer struct {
	s       *dns.Service
	project string
	zone    string
	remote  []*dns.ResourceRecordSet
	managed []*dns.ResourceRecordSet

	pollInterval time.Duration
	syncInterval time.Duration

	timeout time.Duration

	m sync.Mutex
}

func NewSyncer(s *dns.Service, project, managedZone string, pollInterval, syncInterval, apiTimeout time.Duration) Syncer {
	return &syncer{
		s:            s,
		project:      project,
		zone:         managedZone,
		pollInterval: pollInterval,
		syncInterval: syncInterval,
		timeout:      apiTimeout,
	}
}

// UpdateRecord updates a managed record so that it can be synced by the
// sync loop.
func (s *syncer) UpdateRecord(dnsName, dnsType string, ttl int64, data []string) {
	s.m.Lock()
	defer s.m.Unlock()

	for _, r := range s.managed {
		if r.Name == dnsName && r.Type == dnsType {
			r.Ttl = ttl
			r.Rrdatas = data
			return
		}
	}

	s.managed = append(s.managed, &dns.ResourceRecordSet{
		Name:    dnsName,
		Type:    dnsType,
		Ttl:     ttl,
		Rrdatas: data,
	})
}

func needsUpdate(l *dns.ResourceRecordSet, r *dns.ResourceRecordSet) bool {
	if l.Name != r.Name || l.Type != r.Type {
		// Incomparable
		return false
	}

	if l.Ttl != r.Ttl {
		return true
	}

	if len(l.Rrdatas) != len(r.Rrdatas) {
		return true
	}

	for i, d := range l.Rrdatas {
		if d != r.Rrdatas[i] {
			return true
		}
	}

	return false
}

// updateRecordSets() gets a list of the current record sets from Google Cloud DNS and updates the local cache.
func (s *syncer) updateRecordSets() {
	var records []*dns.ResourceRecordSet

	call := s.s.ResourceRecordSets.List(s.project, s.zone)

	ctx := context.Background()
	ctx, cancel := context.WithTimeout(ctx, s.timeout)
	defer cancel()

	if err := call.Pages(ctx, func(page *dns.ResourceRecordSetsListResponse) error {
		for _, v := range page.Rrsets {
			records = append(records, v)
		}
		return nil // NOTE: returning a non-nil error stops pagination.
	}); err != nil {
		log.Printf("Error polling Cloud DNS record sets: %v", err)
	}

	s.m.Lock()
	s.remote = records

	defer s.m.Unlock()
}

// syncRecordSets() syncs managed local record sets with Cloud DNS
func (s *syncer) syncRecordSets() {
	// NOTE: This method cannot be run concurrently. It *will* deadlock.
	var needsSync []*dns.Change

	s.m.Lock()
	for _, m := range s.managed {
		found := false
		for i, r := range s.remote {
			if m.Name == r.Name && m.Type == r.Type {
				found = true

				if needsUpdate(m, r) {
					// Set the remote to be equal to the managed to we don't sync continuously.
					// If syncRecordSet() encounters an error. We will recover after poll loop.
					needsSync = append(needsSync, &dns.Change{
						Additions: []*dns.ResourceRecordSet{m},
						Deletions: []*dns.ResourceRecordSet{r},
					})
					s.remote[i] = m
					break
				}
			}
		}

		if !found {
			// New managed record not present in Cloud DNS
			s.remote = append(s.remote, m)
			needsSync = append(needsSync, &dns.Change{
				Additions: []*dns.ResourceRecordSet{m},
			})
		}
	}
	s.m.Unlock()

	for _, c := range needsSync {
		r := c.Additions[0]
		log.Printf("syncing record %s %s %d %v", r.Name, r.Type, r.Ttl, r.Rrdatas)
		if err := s.syncChange(c); err != nil {
			log.Printf("Error syncing record set %v: %v", r, err)
		}
	}
}

func (s *syncer) syncChange(c *dns.Change) error {
	// TODO: Add timeouts
	ctx := context.Background()
	ctx, cancel := context.WithTimeout(ctx, s.timeout)
	defer cancel()

	_, err := s.s.Changes.Create(s.project, s.zone, c).Context(ctx).Do()
	if err != nil {
		return err
	}

	return nil
}

func (s *syncer) poll() {
	for {
		select {
		case <-time.After(s.pollInterval):
			// Update record sets to reconcile
			s.updateRecordSets()
		}
	}
}

func (s *syncer) sync() {
	for {
		select {
		case <-time.After(s.syncInterval):
			// sync record sets
			s.syncRecordSets()
		}
	}
}

func (s *syncer) run() {
	s.updateRecordSets()
	go s.poll()
	go s.sync()
}

// run() starts the sync and poll loops
func (s *syncer) Run() {
	go s.run()
}
