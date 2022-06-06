package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"time"
	"github.com/joho/godotenv"
	"gorm.io/driver/mysql"
	"gorm.io/gorm"
)

type ItemData struct {
	gorm.Model
	Id        int       `gorm:"column:id"`
	Name      string    `gorm:"column:name"`
	CreatedAt time.Time `gorm:"column:created_at"`
	UpdatedAt time.Time `gorm:"column:updated_at"`
	DeletedAt time.Time `gorm:"column:deleted_at"`
}

type ReturnData struct {
	Id        		int       	`json:"id"`
	Name     		string  	`json:"name"`
}

func main() {
	var err error
	day_format := "2006-01-02"
	day := time.Now().Format(day_format)

	logfile, err := os.OpenFile("./logs/"+day+".log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0666)
	if err != nil {
		panic("cannnot open test.log:" + err.Error())
	}
	defer logfile.Close()
	log.SetOutput(io.MultiWriter(logfile, os.Stdout))

	log.SetFlags(log.Ldate | log.Ltime)
	err = godotenv.Load(fmt.Sprintf(".env"))
	if err != nil {
		log.Printf("Failed to Load .env")
	}
	http.HandleFunc("/data", GetData)
	log.Fatal(http.ListenAndServe(":8082", nil))
	log.Printf("Server Started.")
}

func ConnectDB() *gorm.DB {
	var dbConnectInfo = fmt.Sprintf(
		`%s:%s@tcp(%s:%s)/%s?charset=utf8&parseTime=True&loc=Local`,
		os.Getenv("DB_USERNAME"),
		os.Getenv("DB_PASSWORD"),
		os.Getenv("DB_HOST"),
		os.Getenv("DB_PORT"),
		os.Getenv("DB_DATABASE"),
	)
	fmt.Printf("%s\n", dbConnectInfo)
	db, err := gorm.Open(mysql.Open(dbConnectInfo), &gorm.Config{})
	if err != nil {
		panic("failed to connect database")
	} else {
		log.Printf("Success to connect DB")
	}
	return db
}

func GetData(w http.ResponseWriter, r *http.Request) {
	var rn_datas []ReturnData
	for i := 0; i < 5; i++ {
		var rn_data ReturnData
		rn_data.Id=i
		rn_data.Name="Dammy"
		rn_datas = append(rn_datas, rn_data)
	}
	w.Header().Set("Content-Type", "application/json;charset=utf-8")
	data, _ := json.Marshal(rn_datas)
	log.Printf(string(data))
	_, err := fmt.Fprint(w, string(data))
	if err != nil {
		return
	}
}