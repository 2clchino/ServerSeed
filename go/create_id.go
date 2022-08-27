package main

import (
	"errors"
	"math/rand"

	"github.com/oklog/ulid/v2"

	"time"
)

var (
	t       = time.Unix(1000000, 0)
	entropy = ulid.Monotonic(rand.New(rand.NewSource(t.UnixNano())), 0)
)

func generateUlid() ulid.ULID {
	return ulid.MustNew(ulid.Timestamp(t), entropy)
}

func CreateID() string {
	return generateUlid().String()
}

func Validation(id string) error {
	if len(id) != ulid.EncodedSize {
		return errors.New("Unique ID generator validation error: length is not match")
	}
	return nil
}
