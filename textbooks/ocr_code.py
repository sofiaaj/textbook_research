import boto3
import time

# Document
s3BucketName = "textbook-scans"
folderName = "two_col/"
documentNames = ["1941_Freeman_The_Story_of_Our_Republic.pdf",
"1946 Casner The Story of American Democracy.pdf",
"1952 Muzzey A History of Our Country.pdf",
"1958 Wirth United States History.pdf",
"1963 West Story of Our Country.pdf",
"1965 Gavian United States History.pdf",
"1972 Graff The Free and the Brave.pdf",
"1976 Gruver An American History.pdf",
"1982_Todd_Rise of the American Nation.pdf",
"1987 Garraty The American Nation.pdf",
"1991 O'Connor Exploring American History.pdf",
"1993 King The United States and Its People.pdf",
"1996 Wilson The Pursuit of Liberty Vol 2.pdf",
"1997 Ritchie American History Vol 2.pdf",
"2000 Cayton America Pathways to the Present Vol 1.pdf",
"2000 Garraty The American Nation Vol 2.pdf",
"2001_Stuckey_CallFreedomVol1.pdf",
"2001_Stuckey_CallFreedomVol2.pdf"]


def startJob(s3BucketName, objectName):
    response = None
    client = boto3.client('textract')
    response = client.start_document_text_detection(
    DocumentLocation={
        'S3Object': {
            'Bucket': s3BucketName,
            'Name': objectName
        }
    })

    return response["JobId"]

def isJobComplete(jobId):
    time.sleep(5)
    client = boto3.client('textract')
    response = client.get_document_text_detection(JobId=jobId)
    status = response["JobStatus"]
    print("Job status: {}".format(status))

    while(status == "IN_PROGRESS"):
        time.sleep(5)
        response = client.get_document_text_detection(JobId=jobId)
        status = response["JobStatus"]
        print("Job status: {}".format(status))

    return status

def getJobResults(jobId):

    pages = []

    time.sleep(5)

    client = boto3.client('textract')
    response = client.get_document_text_detection(JobId=jobId)
    
    pages.append(response)
    print("Resultset page recieved: {}".format(len(pages)))
    nextToken = None
    if('NextToken' in response):
        nextToken = response['NextToken']

    while(nextToken):
        time.sleep(5)

        response = client.get_document_text_detection(JobId=jobId, NextToken=nextToken)

        pages.append(response)
        print("Resultset page recieved: {}".format(len(pages)))
        nextToken = None
        if('NextToken' in response):
            nextToken = response['NextToken']

    return pages

for documentName in documentNames:
      print(documentName)
      documentName = folderName + documentName
      jobId = startJob(s3BucketName, documentName)
      print("Started job with id: {}".format(jobId))
      if(isJobComplete(jobId)):
          response = getJobResults(jobId)
      textfileName = "tesseractScans/" + documentName.split('.')[0] + ".txt"
      f = open(textfileName,"x")
      for resultPage in response:
          for item in resultPage["Blocks"]:
              if item["BlockType"] == "LINE":
                  print ('\033[94m' +  item["Text"] + '\033[0m')
                  f.write(item["Text"])
          f.write('\n')
          f.write('\n')

      f.close()
