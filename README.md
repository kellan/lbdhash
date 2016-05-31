an aws lambda function for extracting identifying info from photos on aws

calculates sha256, a perceptual hash (dhash), and extracts exif info

ImgDhashPy.zip contains Pillow compiled for aws lambda and a few other dependencies

# Why

I've uploaded a bunch of photos to S3 over the years, in a couple of different buckets, I wanted to find the duplicates, and also detect if I had time ranges where there were missing photos.

I'm also intrigued by hosted software which is nearly free when you aren't using it.  Obviously lambdas you only pay for execution, while you can ramp down the throughput capacity on a DynamoDb table to the point where it costs you < $1/month, ramp it back up when you want to search it.

Finally the idea of SNS as a shared event bus tying together AWS services is intriguing, if, um, half-baked.

# Install

create the Img_Dhash zip
`zip -g ImgDhashPy.zip Img_Dhash.py config.py`

create the lambda and upload the zip.

optionally create the Dynamo_Put.zip if you want to store the results of the crawl in Dynamo, and create the lambda

`zip -g Dynamo_Put.zip Dynamo_Put.py config.py`

either invoke the lambdas directly, or

1. create an Img_Dhash_in and Img_Dhash_out SNS topic
2. subscribe Img_Dhash to Img_Dhash_in
3. subscribe Dynamo_Put to Img_Dhash_out
4. create a DynamoDb table
5. update config.py, and then update the lambdas with new config

# Working with Lambda

to update zip with changes to the labmda function

`zip -g ImgDhashPy.zip Img_Dhash.py`

to upload zip (the first time)

`aws lambda create-function --function-name <name> --zip-file fileb://ImgDhashPy.zip --role arn:aws:iam::<some-id>:role/lambda_basic_execution  --handler Img_Dhash.handler --runtime python2.7 --timeout 15 --memory-size 512`

to update zip

`aws lambda update-function-code --function-name <name> --zip-file fileb://ImgDhashPy.zip`
