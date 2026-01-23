package main

import (
	"encoding/json"
	"errors"
	"io"
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"time"
)

// const dataDir = "/home/rd/opdir/slow_http"
const dataDir = "/Users/liupeng/workspace/examples/go/slow_http"
type DBConfig struct {
	URL           string `json:"url"`
	Port          any    `json:"port"`
	Database      string `json:"database"`
	ConnectionURL string `json:"connectionUrl"`
}

type CustomResponse struct {
	ExistSlowSql         bool `json:"existSlowSql"`
	RetCode              int  `json:"retCode"`
	RetMsg               string `json:"retMsg"`
	RootCauseSlowSqlList any  `json:"rootCauseSlowSqlList,omitempty"`
}

// 添加端口验证函数
func isValidPort(port any) bool {
	switch v := port.(type) {
	case float64:
		return v > 0 && v <= 65535
	case string:
		if p, err := strconv.Atoi(v); err == nil {
			return p > 0 && p <= 65535
		}
		return false
	case int:
		return v > 0 && v <= 65535
	default:
		return false
	}
}

// 检查Python结果是否包含错误
func hasErrorInPythonResult(result any) (bool, string) {
	switch v := result.(type) {
	case map[string]any:
		// 如果是单个字典，检查是否有error字段
		if errorMsg, exists := v["error"]; exists {
			if msg, ok := errorMsg.(string); ok {
				return true, msg
			}
			return true, "Unknown error occurred"
		}
	case []any:
		// 如果是数组，检查每个元素
		for i, item := range v {
			if itemMap, ok := item.(map[string]any); ok {
				if errorMsg, exists := itemMap["error"]; exists {
					if msg, ok := errorMsg.(string); ok {
						return true, fmt.Sprintf("Error in item %d: %s", i, msg)
					}
					return true, fmt.Sprintf("Error in item %d: Unknown error", i)
				}
			}
		}
	}
	return false, ""
}

func hasWarnInPythonResult(result any) (bool, string) {
	switch v := result.(type) {
	case map[string]any:
		if errorMsg, exists := v["warnn"]; exists {
			if msg, ok := errorMsg.(string); ok {
				return true, msg
			}
			return true, "no slow log!"
		}
	}
	return false, ""
}

func main() {
	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
	})

	http.HandleFunc("/processlist", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")

		if r.Method != "POST" {
			errorResp := CustomResponse{
				ExistSlowSql: false,
				RetCode:      999999,
				RetMsg:       "Only POST allowed",
			}
			json.NewEncoder(w).Encode(errorResp)
			return
		}

		body, err := io.ReadAll(r.Body)
		if err != nil {
			errorResp := CustomResponse{
				ExistSlowSql: false,
				RetCode:      999999,
				RetMsg:       "Failed to read request body",
			}
			json.NewEncoder(w).Encode(errorResp)
			return
		}

		var params []DBConfig
		if err := json.Unmarshal(body, &params); err != nil {
			errorResp := CustomResponse{
				ExistSlowSql: false,
				RetCode:      999999,
				RetMsg:       "Invalid JSON array: " + err.Error(),
			}
			json.NewEncoder(w).Encode(errorResp)
			return
		}

		for i, config := range params {
			if config.URL == "" || config.Database == "" {
				errorResp := CustomResponse{
					ExistSlowSql: false,
					RetCode:      999999,
					RetMsg:       "Missing required fields in record " + strconv.Itoa(i+1),
				}
				json.NewEncoder(w).Encode(errorResp)
				return
			}

			if !isValidPort(config.Port) {
				errorResp := CustomResponse{
					ExistSlowSql: false,
					RetCode:      999999,
					RetMsg:       "Invalid port number in record " + strconv.Itoa(i+1),
				}
				json.NewEncoder(w).Encode(errorResp)
				return
			}
		}

		timestamp := strconv.FormatInt(time.Now().UnixNano(), 10)
		filename := filepath.Join(dataDir, timestamp+".json")

		inputJSON, _ := json.Marshal(params)
		if err := os.WriteFile(filename, inputJSON, 0644); err != nil {
			errorResp := CustomResponse{
				ExistSlowSql: false,
				RetCode:      999999,
				RetMsg:       "Failed to write file: " + err.Error(),
			}
			json.NewEncoder(w).Encode(errorResp)
			return
		}

		cmd := exec.Command("python", "processlist.py", filename)
		output, err := cmd.Output()
		if err != nil {
			var exitErr *exec.ExitError
			errorMsg := err.Error()
			if errors.As(err, &exitErr) {
				errorMsg = string(exitErr.Stderr)
			}
			
			errorResp := CustomResponse{
				ExistSlowSql: false,
				RetCode:      999999,
				RetMsg:       "Python script execution failed: " + errorMsg,
			}
			json.NewEncoder(w).Encode(errorResp)
			return
		}

		var pythonResult any
		if err := json.Unmarshal(output, &pythonResult); err != nil {
			errorResp := CustomResponse{
				ExistSlowSql: false,
				RetCode:      999999,
				RetMsg:       "Failed to parse Python output: " + err.Error(),
			}
			json.NewEncoder(w).Encode(errorResp)
			return
		}

		// 检查Python结果是否包含错误
		if hasError, errorMsg := hasErrorInPythonResult(pythonResult); hasError {
			errorResp := CustomResponse{
				ExistSlowSql: false,
				RetCode:      999999,
				RetMsg:       "Python script returned error: " + errorMsg,
			}
			json.NewEncoder(w).Encode(errorResp)
			return
		}

		if hasError, errorMsg := hasWarnInPythonResult(pythonResult); hasError {
			errorResp := CustomResponse{
				ExistSlowSql: false,
				RetCode:      000000,
				RetMsg:       "Python script get slowlog warnning: " + errorMsg,
			}
			json.NewEncoder(w).Encode(errorResp)
		    defer os.Remove(filename)
			return
		}

		successResp := CustomResponse{
			ExistSlowSql: true,
			RetCode:      000000,
			RetMsg:       "success",
			RootCauseSlowSqlList: pythonResult,
		}
		json.NewEncoder(w).Encode(successResp)
		defer os.Remove(filename)
	})

	http.ListenAndServe(":8080", nil)
}