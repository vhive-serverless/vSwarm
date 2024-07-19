// MIT License

// Copyright (c) 2024 EASE lab

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

package main

import (
	"context"
	"flag"
	"strings"

	log "github.com/sirupsen/logrus"
	"path/filepath"

	// "encoding/base64"
	"os"

	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/gridfs"
	"go.mongodb.org/mongo-driver/mongo/options"
)

var (
	database_address = flag.String("db_addr", "mongodb://image-rotate-database:27017", "Address of the data-base server")
)

func main() {
	flag.Parse()

	// Connect to MongoDB
	client, err := mongo.Connect(context.Background(), options.Client().ApplyURI(*database_address))
	if err != nil {
		log.Fatalf("Error connecting to MongoDB: %v", err)
	}
	defer func() {
		if err = client.Disconnect(context.Background()); err != nil {
			log.Fatalf("Disconnect error: %v", err)
		}
	}()

	dbName := "image_db"
	// collection := client.Database(dbName).Collection("images")

	bucket, err := gridfs.NewBucket(
		client.Database(dbName),
	)
	if err != nil {
		log.Fatalf("Error using GridFS: %v", err)
	}

	dirPath := "./images"
	files, err := os.ReadDir(dirPath)
	if err != nil {
		log.Fatalf("Error finding files: %v", err)
	}

	for _, file := range files {

		if isImageFile(file.Name()) {

			imagePath := filepath.Join(dirPath, file.Name())
			imageFile, err := os.ReadFile(imagePath)
			if err != nil {
				log.Warnf("Error reading file: %v", err)
				continue
			}

			uploadStream, err := bucket.OpenUploadStream(file.Name())
			defer func() {
				if err = uploadStream.Close(); err != nil {
					log.Fatalf("Disconnect error: %v", err)
				}
			}()
			if err != nil {
				log.Warnf("Error creating GridFS upload stream for file %q: %v", imagePath, err)
				continue
			}

			_, err = uploadStream.Write(imageFile)
			if err != nil {
				log.Warnf("Error uploading file %q to GridFS: %v", imagePath, err)
				continue
			}

			log.Print("Inserted image:", file.Name())
		}
	}

}

func isImageFile(fileName string) bool {
	imageExtensions := []string{".jpg", ".jpeg", ".png"}
	for _, ext := range imageExtensions {
		if strings.HasSuffix(strings.ToLower(fileName), ext) {
			return true
		}
	}
	return false
}
