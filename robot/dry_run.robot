*** Settings ***
Library    Process
Library    OperatingSystem
Library    ./resources/optilab_keywords.py

*** Test Cases ***
Valid Design Passes Dry Run
    ${rc}=    Validate Design    designs/demo-ring.yaml
    Should Be Equal As Integers    ${rc}    0
    ${errors}=    Error Count
    Should Be Equal As Integers    ${errors}    0

Broken Design Fails Dry Run
    ${rc}=    Validate Design    designs/bad-dup-lambda.yaml
    Should Not Be Equal As Integers    ${rc}    0
    ${errors}=    Error Count
    Should Be True    ${errors} > 0
