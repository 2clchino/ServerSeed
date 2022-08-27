package main

import (
	"bytes"
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
	Id   int    `json:"id"`
	Name string `json:"name"`
}

type PostData struct {
	Name string `json:"name"`
	Pass string `json:"pass"`
}

type ScoreData struct {
	Token string `json:"token"`
	Score int    `json:"score"`
}

var score_board map[string]int

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
	score_board = make(map[string]int)
	http.HandleFunc("/data", GetData)
	http.HandleFunc("/user/reg", RegUser)
	http.HandleFunc("/wio/score", AddScore)
	http.HandleFunc("/wio/reg", RegTerm)
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
		rn_data.Id = i
		rn_data.Name = "Dammy"
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

func RegTerm(w http.ResponseWriter, r *http.Request) {
	var rn_data ScoreData
	rn_data.Score = 0
	rn_data.Token = CreateID()
	score_board[rn_data.Token] = rn_data.Score
	w.Header().Set("Content-Type", "application/json;charset=utf-8")
	data, _ := json.Marshal(rn_data)
	log.Printf(string(data))
	_, err := fmt.Fprint(w, string(data))
	if err != nil {
		return
	}
}

func RegUser(w http.ResponseWriter, r *http.Request) {
	if err := r.ParseForm(); err != nil {
		log.Printf("Faild to Parse POST request")
		return
	}
	bufbody := new(bytes.Buffer)
	bufbody.ReadFrom(r.Body)
	body := bufbody.String()
	var post_data PostData
	if err := json.Unmarshal([]byte(body), &post_data); err != nil {
		panic(err)
	}
	log.Printf(post_data.Name, post_data.Pass)
	var rn_datas []ReturnData
	var rn_data ReturnData
	rn_data.Id = 0
	rn_data.Name = post_data.Name
	rn_datas = append(rn_datas, rn_data)
	w.Header().Set("Content-Type", "application/json;charset=utf-8")
	data, _ := json.Marshal(rn_datas)
	log.Printf(string(data))
	_, err := fmt.Fprint(w, string(data))
	if err != nil {
		return
	}
}

func AddScore(w http.ResponseWriter, r *http.Request) {
	if err := r.ParseForm(); err != nil {
		log.Printf("Faild to Parse POST request")
		return
	}
	bufbody := new(bytes.Buffer)
	bufbody.ReadFrom(r.Body)
	body := bufbody.String()
	var post_data ScoreData
	if err := json.Unmarshal([]byte(body), &post_data); err != nil {
		panic(err)
	}
	log.Printf(post_data.Token, post_data.Score)
	_, isThere := score_board[post_data.Token]
	if isThere {
		if post_data.Score > score_board[post_data.Token] {
			score_board[post_data.Token] = post_data.Score
		}
	} else {
		score_board[post_data.Token] = post_data.Score
	}

	var rn_data ScoreData
	rn_data.Token = post_data.Token
	rn_data.Score = score_board[post_data.Token]
	w.Header().Set("Content-Type", "application/json;charset=utf-8")
	data, _ := json.Marshal(rn_data)
	log.Printf(string(data))
	_, err := fmt.Fprint(w, string(data))
	if err != nil {
		return
	}
}
