#IMport json 
#   - I want to use Pythons built-in JSON library
#   - WE need this because our project save the data into a json file
import json

#Read requiremtnt from file
#   - open(...) opens the file
#   - "sample_requirement.txt" is the file name
#   - "r" means read mode
#   - as file gives the opened file a temporary name
#   - file.read() reads the full content
#   - requirement_text stores the requirement text
with open ("Practice_projects/sample_requirement.txt","r") as file:
    requirement_text=file.read()
    #This is important because later the AI will read requirements from a file
    #, not from a hardcoded text

# Create structured test case data
# created a dictionary called data1
data1= {'requirement':requirement_text, 
            'positive_test_cases': [
                {
                        "id": "P1",
                        "description": "Login with valid email and valid password",
                        "expected_result": "Login should be successful"
                },
                {
                        "id": "P2",
                        "description": "User logs in with valid credentials",
                        "expected_result": "User should be redirected to account page after successful login"
                }],
            'negative_test_cases': [
                {
                        "id": "N1",
                        "description": "Login with invalid email and valid password",
                        "expected_result": "Login should not be successful"
                },
                {
                        "id": "N2",
                        "description": "Login with valid email and invalid password",
                        "expected_result": "Login should not be successful"
                }],
            'edge_test_cases': [
                {
                        "id": "E1",
                        "description": "Login with leading and trailing spaces in email",
                        "expected_result": "Should show error"
                },
                {
                        "id": "E2",
                        "description": "Login with password containing special characters",
                        "expected_result": "Should show Error"
                }
                ]}
 
#Add 1 Function to call test groups
test_case_groups = {
    "Positive Test Cases": data1["positive_test_cases"],
    "Negative Test Cases": data1["negative_test_cases"],
    "Edge Test Cases": data1["edge_test_cases"]
}

#Saving data to output.json
# open output.json
# "w" means write mode
# json.dump(...) writes Python data into a JSON file
# indent=4 makes it readable with spacing

# So this converts your Python dictionary into a clean JSON file.

# This is important because in real projects we often save generated test cases, reports, AI outputs, and validation results in JSON.
with open ("output.json","w") as file:
    json.dump(data1,file,indent=4)


#creating a resuable function named printtc that accepts a heading and a list of test cases.
def printtc(heading, test_cases):
      #print heading and count here:\
      print(heading,':', len(test_cases))

      #loop through test_cases here
      for test_case in test_cases:
        print(f"{test_case['id']} - {test_case['description']},\nExpected Result : {test_case['expected_result']}\n")
     


#Validation function
#Check whether every test case has the required fields.
def validate_test_cases(heading,test_cases):
    # create required_fields list here
    # Every test case must have 3 keys
    required_fields = ['id','description','expected_result']
    #Missing flag- At beginning, assume nothing is missing
    #if we later find a missing field, we change it to True
    missing_found=False

    # loop through each test_case, check one test case at a time
    for test_case in test_cases:
        #get test case id safely. get id if it exists. if not, use "UNKNOWN"
        test_case_id = test_case.get("id", "UNKNOWN")

        # loop through each field
        for field in required_fields:
            # check if field exists in test_case, if its not present in this test cases, print an error.
            if (field not in test_case):
                print(f"{heading} - Test Case: {test_case_id}, Missing field: {field}")
                missing_found = True
            elif (test_case[field] == ""):
                #check if test _case[field] is empty
                print(f"{heading} - Test Case: {test_case_id}, Empty_field: {field}")
                missing_found = True     
    #if validation passes , print heading with sucess message
    if not missing_found:
        print(heading, "Validation passed: No validation issues found")


#add loop to print test cases
for heading, test_cases in test_case_groups.items():
     #call print_test_cases here:
    printtc(heading, test_cases)

#Add loop to validate test groups
for heading, test_cases in test_case_groups.items():
    #call validate_test_cases here:
    validate_test_cases(heading, test_cases)

