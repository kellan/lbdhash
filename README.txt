an aws lambda function for extracting identifying info from photos on aws

calculates sha256, a perceptual hash (dhash), and extracts exif info

ImgDhashPy.zip contains Pillow compiled for aws lambda and a few other dependencies

# Working with Lambda

to update zip with changes to the labmda function

`zip -g ImgDhashPy.zip Img_Dhash.py`

to upload zip (the first time)

`aws lambda create-function --function-name <name> --zip-file fileb://ImgDhashPy.zip --role arn:aws:iam::407883137925:role/lambda_basic_execution  --handler Img_Dhash.handler --runtime python2.7 --timeout 15 --memory-size 512

to update zip

`aws lambda update-function-code --function-name <name> --zip-file fileb://ImgDhashPy.zip`
