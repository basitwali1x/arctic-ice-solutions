#!/usr/bin/env python3

import requests
import os

def test_excel_import():
    """Test the Excel import functionality directly"""
    
    file_path = "/home/ubuntu/attachments/29eaa1ae-7e6d-4a83-9bcf-a0d8177d108c/West+La+Ice+Customer+List.xlsx"
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    url = "http://localhost:8000/api/import/excel"
    
    login_url = "http://localhost:8000/api/auth/login"
    login_data = {"username": "manager", "password": "dev-password-change-in-production"}
    
    try:
        print("Logging in...")
        login_response = requests.post(login_url, json=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            return
            
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print("Testing Excel import...")
        
        with open(file_path, 'rb') as f:
            files = {"files": ("West+La+Ice+Customer+List.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            response = requests.post(url, files=files, headers=headers)
        
        print(f"Import status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("Import successful!")
            result = response.json()
            print(f"Summary: {result}")
        else:
            print(f"Import failed with status {response.status_code}")
            print(f"Error details: {response.text}")
            
    except Exception as e:
        print(f"Error during import test: {e}")

if __name__ == "__main__":
    test_excel_import()
