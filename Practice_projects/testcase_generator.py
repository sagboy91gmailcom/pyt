import json


with open ("sample_requirement.txt","r") as file:
    requirement_text=file.read()


    data1= {'requirement':requirement_text, 
            'positive_test_cases': [
            {
            "id" : "P1",
            "description":"Login with valid email and valid password should be successful",
            "expected_result":"login should be successful"
            }
         ],
            'negative_test_cases': [
    "Login with invalid email and valid password should fail",
    "Login with valid email and invalid password should fail",
    "Login with blank email and blank password should fail"],
            'edge_test_cases': [
    "Login with leading and trailing spaces in email should be handled correctly",
    "Login with very long email input should be handled correctly",
    "Login with password containing special characters should be handled correctly"]}


with open ("output.json","w") as file:
    json.dump(data1,file,indent=4)