package main

import (
	"flag"
	"io"
	"os"
	"path/filepath"
	"strings"
	"time"
	"fmt"

	"github.com/gocql/gocql"
	log "github.com/sirupsen/logrus"
)

var (
	cassandraAddr = flag.String("db_addr", "database:9042", "Address of the Cassandra server")
)
// "database:9042"

func main() {
	flag.Parse()

	// Connect to Cassandra
	cluster := gocql.NewCluster(*cassandraAddr)
	cluster.Consistency = gocql.Quorum
	cluster.Keyspace = "system" // Use the "system" keyspace to create your keyspace
	cluster.ConnectTimeout = 20 * time.Second // ConnectTimeout set to 2 seconds
	cluster.Timeout = 50 * time.Second        // Timeout set to 5 seconds
	var err error
	var tmpSession *gocql.Session
	for {
		tmpSession, err = cluster.CreateSession()
		if err == nil {
			break
		}
		log.Printf("CreateSession: %v", err)
		time.Sleep(15*time.Second)
	}

	// Create keyspace if not exists
	err = tmpSession.Query(`
		CREATE KEYSPACE IF NOT EXISTS video_processing_db
		WITH replication = {
			'class': 'SimpleStrategy',
			'replication_factor': 1
		}`).Exec()
	if err != nil {
		log.Fatalf("Error creating keyspace: %v", err)
	}
	tmpSession.Close()

	// Reconnect with keyspace
	cluster.Keyspace = "video_processing_db"
	
	var session *gocql.Session

	for {
		session, err = cluster.CreateSession()
		if err == nil {
			break
		}
		log.Printf("CreateSession: %v", err)
		time.Sleep(15 * time.Second)
	}
	defer session.Close()
	log.Printf("Connected OK")

	err = session.Query(`DROP TABLE IF EXISTS files`).Exec()
	if err != nil {
		log.Fatalf("Error deleting files table: %v", err)
	}
	err = session.Query(`DROP TABLE IF EXISTS chunks`).Exec()
	if err != nil {
		log.Fatalf("Error deleting chunks table: %v", err)
	}
	// Create tables if not exist
	err = session.Query(`
		CREATE TABLE IF NOT EXISTS files (
			file_id UUID PRIMARY KEY,
			filename TEXT,
			size BIGINT,
			upload_date TIMESTAMP
		)`).Exec()
	if err != nil {
		log.Fatalf("Error creating files table: %v", err)
	}

	err = session.Query(`CREATE INDEX ON files (filename)`).Exec()
	if err != nil {
		log.Fatalf("Error deleting files table: %v", err)
	}

	err = session.Query(`
		CREATE TABLE IF NOT EXISTS chunks (
			file_id UUID,
			chunk_index INT,
			data BLOB,
			PRIMARY KEY (file_id, chunk_index)
		)`).Exec()
	if err != nil {
		log.Fatalf("Error creating chunks table: %v", err)
	}

	// Now proceed with uploads
	dirPath := "./videos"
	files, err := os.ReadDir(dirPath)
	if err != nil {
		log.Fatalf("Error reading directory: %v", err)
	}

	for _, file := range files {
		if isVideoFile(file.Name()) {
			videoPath := filepath.Join(dirPath, file.Name())
			if err := uploadFile(session, videoPath); err != nil {
				log.Warnf("Failed to upload %s: %v", file.Name(), err)
				continue
			}
			log.Infof("Inserted video: %s", file.Name())
		}
	}
	fmt.Println("Just when I thought I was out, they pull me back in")

}

func uploadFile(session *gocql.Session, path string) error {
	file, err := os.Open(path)
	if err != nil {
		return err
	}
	defer file.Close()

	// Generate file_id
	fileID := gocql.TimeUUID()

	// Get file size
	info, _ := file.Stat()
	size := info.Size()

	// Insert metadata
	if err := session.Query(
		"INSERT INTO files (file_id, filename, size, upload_date) VALUES (?, ?, ?, ?)",
		fileID, info.Name(), size, time.Now(),
	).Exec(); err != nil {
		return err
	}

	// Split into chunks
	// const chunkSize = 4 * 1024 * 1024 // 4MB
	const chunkSize = 255 * 1024 // 255KB
	buf := make([]byte, chunkSize)
	chunkIndex := 0

	for {
		n, err := file.Read(buf)
		if n > 0 {
			chunk := make([]byte, n)
			copy(chunk, buf[:n])
			if err := session.Query(
				"INSERT INTO chunks (file_id, chunk_index, data) VALUES (?, ?, ?)",
				fileID, chunkIndex, chunk,
			).Exec(); err != nil {
				return err
			}
			chunkIndex++
		}
		if err == io.EOF {
			break
		}
		if err != nil {
			return err
		}
	}

	return nil
}

func isVideoFile(fileName string) bool {
	videoExtensions := []string{".mp4"}
	for _, ext := range videoExtensions {
		if strings.HasSuffix(strings.ToLower(fileName), ext) {
			return true
		}
	}
	return false
}
