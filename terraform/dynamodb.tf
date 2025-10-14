resource "aws_dynamodb_table" "aws_credentials" {
  name           = "aima-aws-credentials"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Project = "AI-Meeting-Assistant"
    Owner   = "Aditi Vakeel"
  }
}
