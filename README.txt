aws lambda create-function --region us-east-1 --function-name Img_DhashPy --zip-file fileb://ImgDhashPy.zip --role arn:aws:iam::407883137925:role/lambda_basic_execution  --handler Img_Dhash.handler --runtime python2.7 --timeout 15 --memory-size 512

"FunctionArn": "arn:aws:lambda:us-east-1:407883137925:function:Img_DhashPy",

aws lambda create-function --region us-east-1 --function-name Dynamo_PutPy --zip-file fileb://Dynamo_Put.zip --role arn:aws:iam::407883137925:role/lambda_basic_execution  --handler Dynamo_Put.handler --runtime python2.7 --timeout 15 --memory-size 512

"FunctionArn": "arn:aws:lambda:us-east-1:407883137925:function:Dynamo_PutPy",

create Img_Dhash_in SNS topic
subscribe Img_Dhash to it

create Img_Dhash_out
subscribe dynamo_put to it

create Dynamodb Table, `path_md5` should be partition key


update config file

re-update the lambdas with new config

aws lambda update-function-code --region us-east-1 --function-name Img_DhashPy --zip-file fileb://ImgDhashPy.zip


aws lambda update-function-code --region us-east-1 --function-name Dynamo_PutPy --zip-file fileb://Dynamo_Put.zip
